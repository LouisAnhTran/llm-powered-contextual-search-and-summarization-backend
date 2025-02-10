from fastapi import APIRouter, HTTPException, File, UploadFile, Request, Header
import logging
import time 
from datetime import datetime, timedelta 
from typing import Optional
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import fitz
from io import BytesIO
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI


from src.models.requests import (
    ChatMessagesRequest)
from src.config import (
    AWS_ACCESS_KEY,
    AWS_SECRET_ACCESS_KEY,
    AWS_BUCKET_NAME,
    AWS_REGION,
    MAIN_TENANT
)
from src.utils.exceptions import return_error_param
from src.gen_ai.rag.pinecone_operation import (
    retrieve_top_k_similar_search_from_vector_db
)
from src.utils.aws_operation import (
    get_file
)
from src.gen_ai.rag.doc_processing import (
    init_pinecone_and_doc_indexing
)
from src.gen_ai.rag.chat_processing import (
    generate_standalone_query,
    generate_system_response
)

api_router = APIRouter()

# init s3 client
s3_client = boto3.client('s3', 
                         aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION)

#init llm 
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

embedding_model=OpenAIEmbeddings(
    model='text-embedding-ada-002'
)


@api_router.post("/upload_document_and_trigger_indexing")
async def upload_file(request: Request,
                      file: UploadFile = File(...)):

    folder_name=f"{MAIN_TENANT}/"

    # check if file is valid
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail={"File must be a PDF"})

    try:
        # Read file content
        file_content = await file.read()

        # Open the PDF file using PyMuPDF from the in-memory bytes
        pdf_document = fitz.open(stream=BytesIO(file_content), filetype="pdf")
        
        # Get the number of pages
        num_pages = pdf_document.page_count

        logging.info("num_pages: ",num_pages)
        
        # Get the file size
        file_size = len(file_content)

        logging.info("file_size: ",file_size)

        s3_dockey=f"{folder_name}{file.filename}"
        
        logging.info("start uploading pdf document to s3 bucket")

        # Upload file to S3
        s3_client.put_object(
            Bucket=AWS_BUCKET_NAME,
            Key=s3_dockey,
            Body=file_content,
            ContentType=file.content_type
        )
        
        logging.info("uploading pdf document to s3 bucket successfully")

    except NoCredentialsError:
        raise HTTPException(status_code=403, detail="AWS credentials not found")
    except PartialCredentialsError:
        raise HTTPException(status_code=403, detail="Incomplete AWS credentials")
    except Exception as e:
        raise HTTPException(
            status_code=return_error_param(e,"status_code"), 
            detail=return_error_param(e,"detail"))
        
    # start indexing the document
    logging.info("start_pinecone_indexing")
    
    # retrieve pdf from aws
    file_content= get_file(
        s3_client=s3_client,
        doc_key=s3_dockey
    )[0]

    logging.info("file_content: ",file_content)

    # run pinecone indexing pineline
    # try:
    init_pinecone_and_doc_indexing(
        username=MAIN_TENANT,
        doc_key=s3_dockey,
        file_bytes=file_content,
        embedding_model=embedding_model
    )
    # except Exception as e:
    #     raise HTTPException(status_code=500,
    #                         detail="We encouter error when spinning up chat engine for this document")
    
    logging.info(f"successully indexed pdf document {file.filename}")
        
    return {"message": "File uploaded and indexed successfully", 
            "filename": file.filename}


@api_router.get("/fetch_messages/{doc_name}")
async def retrieve_messages_from_pinecone(
    doc_name: str,
    authorization: Optional[str] = Header(None)
    ):
    logging.info("hello_in_fetch")

    username='louis_anh_tran'

    logging.info("username: ",username)

    # check if we indexing for this document or not
    result=query_by_username_dockey(
        username=username,
        doc_key=f"{username}/{doc_name}",
        query="test",
        top_k=1
    )


    logging.info("result_query_pinecone: ",result)

    if result:
        all_messages=await fetch_all_messages(
            username=username,
            docname=doc_name
        )

        logging.info("all_messages: ",all_messages)

        return {"data":all_messages}

    else:
        # to do
        logging.info("start_pinecone_indexing")
        # retrieve pdf from aws
        file_content= get_file(
            s3_client=s3_client,
            doc_key=f"{username}/{doc_name}"
        )[0]

        logging.info("file_content: ",file_content)

        # run pinecone indexing pineline
        try:
            init_pinecone_and_doc_indexing(
            username=username,
            doc_key=f"{username}/{doc_name}",
            file_bytes=file_content,
            embedding_model=embedding_model
        )
        except Exception as e:
            raise HTTPException(status_code=500,
                                detail="We encouter error when spinning up chat engine for this document")
        
    return {"data":[]}

@api_router.post("/semantic_search/{doc_name}")
async def generate_result_for_semantic_search(
    doc_name: str,
    request: ChatMessagesRequest
):
    logging.info("doc name: ",doc_name)
    
    # Parameters
    bucket_name = AWS_BUCKET_NAME
    subfolder_prefix = f"{MAIN_TENANT}/"  # Include trailing slash
    
    try:

        # List objects under the subfolder
        response = s3_client.list_objects_v2(Bucket=bucket_name, 
                                    Prefix=subfolder_prefix)

        # Extract and print document names
        if 'Contents' in response:
            document_names = [obj['Key'] for obj in response['Contents']]
            logging.info(f"Document names: {document_names}")
            
            if subfolder_prefix+doc_name not in document_names:
                raise HTTPException(
                    status_code=404,
                     detail=f"Document name {doc_name} does not exists in S3 bucket"
                )
                
        else:
            raise HTTPException(
                status_code=404,
                detail=f"This sub path contain no documents"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=return_error_param(e,"status_code"), 
            detail=return_error_param(e,"detail")
        )
        
    # implement semantic search
  
    user_query=request.list_of_messages[-1]
    history_messages=request.list_of_messages[:-1]

    logging.info("user_query: ",user_query)
    logging.info("history_messages: ",history_messages)

    if not history_messages:
        standalone_query=user_query.content
    else:
        standalone_query=generate_standalone_query(
            llm=llm,
            user_query=user_query,
            history_messages=history_messages
        )
    

    result=await generate_system_response(
            llm=llm,
            embedding_model=embedding_model,
            standalone_query=standalone_query,
            username=MAIN_TENANT,
            history_messages=history_messages,
            doc_key=f"{MAIN_TENANT}/{doc_name}",
            top_k=1,
    )
    
    return {"data":"okie"}
   

        
    

# Example endpoint to fetch and return a PDF from S3
@api_router.get("/get-pdf/{file_name}")
def get_pdf(file_name: str, authorization: Optional[str] = Header(None)):
    
    logging.info("authorization: ",authorization)

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization token")

    access_token = authorization.split("Bearer ")[1]

    logging.info("Access token: %s", access_token)

    if access_token is None:
        raise HTTPException(status_code=401, detail="Access token is missing")

    # Verify the token and get the username
    username = decode_access_token(access_token)

    logging.info("username: ",username)

    url=f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{username}/{file_name}"

    return {"data":url}

 
# Example endpoint to fetch and return a PDF from S3
@api_router.get("/all_docs")
async def get_all_documents_user(authorization: Optional[str] = Header(None)):
    
    logging.info("authorization: ",authorization)

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization token")

    access_token = authorization.split("Bearer ")[1]

    logging.info("Access token: %s", access_token)

    if access_token is None:
        raise HTTPException(status_code=401, detail="Access token is missing")

    # Verify the token and get the username
    username = decode_access_token(access_token)

    logging.info("username: ",username)

    result=await retrieve_all_docs_user(
        username=username
    )

    time.sleep(4)


    logging.info("result ",result)

    
    return {"data":result,"message":"Fetched all files successfully"}


