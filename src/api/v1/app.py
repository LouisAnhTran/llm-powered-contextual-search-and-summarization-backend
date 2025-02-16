from fastapi import APIRouter, HTTPException, File, UploadFile, Request, Depends
import logging
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import fitz
from io import BytesIO
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from pinecone import Pinecone
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as redis
import time
import os

from src.models.requests import (
    ChatMessagesRequest
)
from src.config import (
    AWS_ACCESS_KEY,
    AWS_SECRET_ACCESS_KEY,
    AWS_BUCKET_NAME,
    AWS_REGION,
    MAIN_TENANT,
    PINECONE_API_KEY,
    PINECONE_INDEX
)
from src.utils.exceptions import return_error_param
from src.utils.aws_operation import (
    get_file
)
from src.gen_ai.rag.doc_processing import (
    init_pinecone_and_doc_indexing
)
from src.gen_ai.rag.chat_processing import (
    generate_standalone_query,
    generate_semantic_search_response,
    generate_summarized_response
)

api_router = APIRouter()


# INITIALIZATION OF LLMS, CLOUD SERVICE AND VECTOR DB

# init s3 client to make API calls for using AWS services
s3_client = boto3.client('s3', 
                         aws_access_key_id=AWS_ACCESS_KEY, 
                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY, 
                         region_name=AWS_REGION)

# init LLM, I am using gpt-4o for this project
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# init embedding model, I am 'text-embedding-ada-002' model from Open AI
embedding_model=OpenAIEmbeddings(
    model='text-embedding-ada-002'
)

# init connection to Pipecone Vector DB index
pinecone_instance = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pinecone_instance.Index(PINECONE_INDEX)



# DEFINE API ENDPOINS

# Initialize Redis on FastAPI startup
@api_router.on_event("startup")
async def startup():
    redis_client = redis.Redis(host="localhost", port=6379, db=0)
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")

# Dependency to get Redis backend
async def get_redis_cache():
    return FastAPICache.get_backend()

# Define an API endpoint to fetch all uploaded PDF documents belonging to a user
@api_router.get("/get_uploaded_documents")
async def get_all_uploaded_pdf_documents_belong_to_user():
    
    # Set the S3 bucket name where documents are stored
    bucket_name = AWS_BUCKET_NAME
    
     # Define the subfolder prefix for the user, ensuring it includes a trailing slash
    subfolder_prefix = f"{MAIN_TENANT}/"  
    
    try:
        # Retrieve a list of objects (files) from the specified S3 bucket and subfolder
        response = s3_client.list_objects_v2(
            Bucket=bucket_name, 
            Prefix=subfolder_prefix
        )

         # Check if any documents exist under the specified prefix
        if 'Contents' in response:
            # Extract document names 
            document_names = [obj['Key'] for obj in response['Contents']]
            
            # Remove the folder prefix and keep only the actual document names
            document_names_without_slash=[item.split("/")[1] for item in document_names]
            
            logging.info(f"Document names: {document_names_without_slash}")
            
            # Return the list of document names as a response
            return {"response": document_names_without_slash}
        
        # If no documents are found, return an empty list
        return {"response":[]}


    except Exception as e:
        # Handle exceptions by returning an appropriate HTTP error response
        raise HTTPException(
            status_code=return_error_param(e,"status_code"), 
            detail=return_error_param(e,"detail")
        )
        

# Define an API endpoint to upload a PDF file and trigger document indexing process and store embeddings in Pipecone 
@api_router.post("/upload_document_and_trigger_indexing")
async def upload_file(request: Request,
                      file: UploadFile = File(...)):
    
    # Define the folder name in S3 where the file will be stored
    folder_name=f"{MAIN_TENANT}/"

    # Validate if the uploaded file is a PDF
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

        # Upload the file to the S3 bucket
        s3_client.put_object(
            Bucket=AWS_BUCKET_NAME,
            Key=s3_dockey,
            Body=file_content,
            ContentType=file.content_type
        )
        
        logging.info("uploading pdf document to s3 bucket successfully")
        
    # Handle different AWS credential errors
    except NoCredentialsError:
        raise HTTPException(
            status_code=403, 
            detail="AWS credentials not found")
    except PartialCredentialsError:
        raise HTTPException(
            status_code=403, 
            detail="Incomplete AWS credentials")
    except Exception as e:
        raise HTTPException(
            status_code=return_error_param(e,"status_code"), 
            detail=return_error_param(e,"detail"))
        
    # START INDEXING THE UPLOADED DOCUMENT
    logging.info("start_pinecone_indexing")
    
    # Retrieve the uploaded PDF content from AWS S3
    file_content= get_file(
        s3_client=s3_client,
        doc_key=s3_dockey
    )[0]

    logging.info("file_content: ",file_content)

    # Run the Pinecone indexing pipeline for the document
    try:
        init_pinecone_and_doc_indexing(
            username=MAIN_TENANT,  # Tenant name 
            doc_key=s3_dockey,   # Document path in S3
            file_bytes=file_content,  # File content in bytes
            embedding_model=embedding_model,
            pc=pinecone_instance
        )
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail="We encouter error when spinning up chat engine for this document")
    
    logging.info(f"successully indexed pdf document {file.filename}")
        
    return {"message": "File uploaded and indexed successfully", 
            "filename": file.filename}

@api_router.post("/semantic_search/{doc_name}")
async def generate_result_for_semantic_search(
    doc_name: str,
    request: ChatMessagesRequest,
    cache: RedisBackend = Depends(get_redis_cache)
):
    logging.info("doc name: ",doc_name)
    logging.info("request_semantic_search: ",request.list_of_messages)
    
    # check if the response for this query has been cached
    try: 
        key_redis=doc_name+"#"+request.list_of_messages[-1].content.replace(" ","").lower()
        value=await cache.get(key_redis)
        if value:
            time.sleep(1)
            logging.info("redis cache hit, immediately return response")
            return {"response":value}
        
        logging.info("redis cache miss")
    except Exception as e:
        logging.info("There is error with Redis server, can not do caching")
        
    # Define parameters for accessing the S3 bucket
    bucket_name = AWS_BUCKET_NAME
    subfolder_prefix = f"{MAIN_TENANT}/"  # Include trailing slash
    
    try:
        # Fetch the list of documents stored under the subfolder in S3
        response = s3_client.list_objects_v2(Bucket=bucket_name, 
                                    Prefix=subfolder_prefix)

        # If documents exist in the specified subfolder, extract their names
        if 'Contents' in response:
            document_names = [obj['Key'] for obj in response['Contents']]
            logging.info(f"Document names: {document_names}")
            
            # Check if the requested document exists in the list
            if subfolder_prefix+doc_name not in document_names:
                raise HTTPException(
                    status_code=404,
                     detail=f"Document name {doc_name} does not exists in S3 bucket"
                )
                
        else:
            # If no documents are found in the subfolder, raise an error
            raise HTTPException(
                status_code=404,
                detail=f"This sub path contain no documents"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=return_error_param(e,"status_code"), 
            detail=return_error_param(e,"detail")
        )
        
    # IMPLEMENT SEMANTIC SEARCH
    
     # Extract the latest user query and conversation history
    user_query=request.list_of_messages[-1]
    history_messages=request.list_of_messages[:-1]

    logging.info("user_query: ",user_query)
    logging.info("history_messages: ",history_messages)
    logging.info("len_history_messages: ",len(history_messages))
    
    # If there are no previous messages, use the user query directly
    if not history_messages:
        standalone_query=user_query.content
    else:
        # Generate a standalone query using the chat history and user query using LLM
        standalone_query=generate_standalone_query(
            llm=llm,
            user_query=user_query,
            history_messages=history_messages
        )
    
    # Perform semantic search to retrieve relevant information from the document
    result_semantic_search=await generate_semantic_search_response(
            llm=llm,
            embedding_model=embedding_model,
            standalone_query=standalone_query,
            username=MAIN_TENANT,
            history_messages=history_messages,
            doc_key=f"{MAIN_TENANT}/{doc_name}",
            top_k=1,
            pinecone_index=pinecone_index
    )
    
    # cache the LLM response to Redis cache
    try: 
        await cache.set(key_redis,result_semantic_search,expire=600)
        logging.info("cached LLM response")
    except Exception as e:
        logging.info("There is error with Redis server, can not cache LLM response")
    
    return {"response":result_semantic_search}
   

@api_router.post("/generate_summarization/{doc_name}")
async def generate_result_for_semantic_search(
    doc_name: str,
    request: ChatMessagesRequest,
    cache: RedisBackend = Depends(get_redis_cache)
):
    logging.info("doc name: ",doc_name)
    logging.info("preferred_response_length: ",request.preferred_response_length)
    logging.info("request_generate_summarization: ",request.list_of_messages)
    
    # check if the response for this query has been cached
    try: 
        key_redis=doc_name+"#"+request.list_of_messages[-1].content.replace(" ","").lower()
        value=await cache.get(key_redis)
        if value:
            time.sleep(1)
            logging.info("redis cache hit, immediately return response")
            return {"response":value}
        
        logging.info("redis cache miss")
    except Exception as e:
        logging.info("There is error with Redis server, can not do caching")
    
    # Define parameters for accessing the S3 bucket
    bucket_name = AWS_BUCKET_NAME
    subfolder_prefix = f"{MAIN_TENANT}/"  # Include trailing slash
    
    try:
        # Fetch the list of documents stored under the subfolder in S3
        response = s3_client.list_objects_v2(Bucket=bucket_name, 
                                    Prefix=subfolder_prefix)

        # If documents exist in the specified subfolder, extract their names
        if 'Contents' in response:
            document_names = [obj['Key'] for obj in response['Contents']]
            logging.info(f"Document names: {document_names}")
            
            # Check if the requested document exists in the list
            if subfolder_prefix+doc_name not in document_names:
                raise HTTPException(
                    status_code=404,
                     detail=f"Document name {doc_name} does not exists in S3 bucket"
                )
                
        else:
            # If no documents are found in the subfolder, raise an error
            raise HTTPException(
                status_code=404,
                detail=f"This sub path contain no documents"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=return_error_param(e,"status_code"), 
            detail=return_error_param(e,"detail")
        )
        
    # IMPLEMENT SUMMARIZATION
    
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
    

    result_summarized_response=await generate_summarized_response(
            llm=llm,
            embedding_model=embedding_model,
            standalone_query=standalone_query,
            username=MAIN_TENANT,
            history_messages=history_messages,
            doc_key=f"{MAIN_TENANT}/{doc_name}",
            top_k=5,
            preferred_response_length=request.preferred_response_length,
            pinecone_index=pinecone_index
    )
    
    # cache the LLM response to Redis cache
    try: 
        await cache.set(key_redis,result_summarized_response,expire=600)
        logging.info("cached LLM response")
    except Exception as e:
        logging.info("There is error with Redis server, can not cache LLM response")
    
    return {"response":result_summarized_response}

