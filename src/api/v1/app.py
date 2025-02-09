from fastapi import APIRouter, HTTPException, File, UploadFile, Request, Header
import logging
import time 
from datetime import datetime, timedelta 
from typing import Optional
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import fitz
from io import BytesIO
from fastapi.responses import StreamingResponse
import io
from langchain_community.chat_models import AzureChatOpenAI
from fastapi.responses import StreamingResponse
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI


from src.models.requests import (
    ChatMessagesRequest)
from src.config import (
    AWS_ACCESS_KEY,
    AWS_SECRET_ACCESS_KEY,
    AWS_BUCKET_NAME,
    AWS_REGION
)
from src.utils.exceptions import return_error_param
from src.gen_ai.rag.pinecone_operation import (
    query_by_username_dockey
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

openaiembeddings=OpenAIEmbeddings(
    model='text-embedding-3-large'
)


@api_router.post("/uploadfile")
async def upload_file(request: Request,
                      file: UploadFile = File(...)):

    folder_name="staple_ai_client/"

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

        logging.info("pass_this_stage")

        # Upload file to S3
        s3_client.put_object(
            Bucket=AWS_BUCKET_NAME,
            Key=s3_dockey,
            Body=file_content,
            ContentType=file.content_type
        )

        return {"message": "File uploaded successfully", "filename": file.filename}
    except NoCredentialsError:
        raise HTTPException(status_code=403, detail="AWS credentials not found")
    except PartialCredentialsError:
        raise HTTPException(status_code=403, detail="Incomplete AWS credentials")
    except Exception as e:
        raise HTTPException(
            status_code=return_error_param(e,"status_code"), 
            detail=return_error_param(e,"detail"))
    

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
            file_bytes=file_content
        )
        except Exception as e:
            raise HTTPException(status_code=500,
                                detail="We encouter error when spinning up chat engine for this document")
        
    return {"data":[]}

@api_router.post("/generate_response/{doc_name}")
async def retrieve_messages_from_pinecone(
    doc_name: str,
    request: ChatMessagesRequest,
    ):
   
    logging.info("start_pinecone_indexing")
    # retrieve pdf from aws
    file_content= get_file(
        s3_client=s3_client,
        doc_key=f"staple_ai_client/{doc_name}"
    )[0]

    logging.info("file_content: ",file_content)

    # run pinecone indexing pineline
    # try:
    init_pinecone_and_doc_indexing(
        username="staple_ai_client",
        doc_key=f"staple_ai_client/{doc_name}",
        file_bytes=file_content
    )
    # except Exception as e:
    #     raise HTTPException(status_code=500,
    #                         detail="We encouter error when spinning up chat engine for this document")
        
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


