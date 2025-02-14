
import os
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from pinecone import Pinecone
import itertools
import logging
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

from src.config import (
    PINECONE_INDEX
)


def extract_text_from_pdf(
    file_bytes: bytes):
    """Extracts text content from a PDF file given its byte stream.

    This function loads a PDF document from a byte stream and extracts text 
    from all pages, concatenating them into a single string.

    Args:
        file_bytes (bytes): The byte representation of the PDF file.

    Returns:
        str: The extracted text content from the PDF.
    """
    
    doc = fitz.open(
        stream=file_bytes, 
        filetype="pdf")
    
    text = ""
    
    for page in doc:
        text += page.get_text()
        
    return text


def chunk_text(text: str,
               chunk_size=512,
               chunk_overlap=50):
    """
    Splits a given text into smaller chunks using a recursive character-based text splitter.

    Args:
        text (str): The input text to be split.
        chunk_size (int, optional): The maximum size of each text chunk. Default is 512.
        chunk_overlap (int, optional): The number of overlapping characters between consecutive chunks. Default is 50.

    Returns:
        list: A list of text chunks.
    """
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap)
    
    chunks_doc = splitter.split_text(text)
    
    return chunks_doc


def chunks(iterable, 
           batch_size=100):
    """
    Splits an iterable into smaller chunks of a specified size.

    Args:
        iterable (iterable): The input iterable to be split into chunks.
        batch_size (int, optional): The maximum size of each chunk. Default is 100.

    Yields:
        tuple: A tuple containing a chunk of the iterable.
    """
    
    it = iter(iterable)
    
    chunk = tuple(itertools.islice(it, batch_size))
    
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))


def create_iterable_vectors(username: str,
                            doc_key: str,
                            file_bytes: bytes,
                            embedding_model) -> list:
    """
    Processes a PDF file to generate chunked text embeddings with metadata.

    Args:
        username (str): The username associated with the document.
        doc_key (str): A unique identifier for the document.
        file_bytes (bytes): The PDF file content in byte format.
        embedding_model: An embedding model used to generate vector embeddings.

    Returns:
        list: A list of dictionaries containing vector embeddings and metadata
    
    """
    # Extract text from PDF
    text=extract_text_from_pdf(file_bytes)
    
    # Chunk the text into smaller parts
    chunk_docs=chunk_text(text)
    
    # Function to generate embeddings 
    vectors=[embedding_model.embed_query(chunk) for chunk in chunk_docs]
    
    # Construct the iterable vector with metadata
    iterable_vector=[
        {
            "id":f"{doc_key}_{i}",
            "values":vector,
            "metadata":
                {
                    "username":username,
                    "doc_key":doc_key,
                    "text":chunk_text
                }
        }
        for i,(chunk_text,vector) in enumerate(list(zip(chunk_docs,vectors)))
    ]
    
    return iterable_vector


def init_pinecone_and_doc_indexing(username: str,
                                   doc_key: str,
                                   file_bytes: bytes,
                                   embedding_model,
                                   pc) -> None:
    
    """
    Initializes Pinecone indexing and upserts document embeddings.

    Args:
        username (str): The username associated with the document.
        doc_key (str): A unique identifier for the document.
        file_bytes (bytes): The PDF file content in byte format.
        embedding_model: The embedding model used to generate vector embeddings.
        pc: The Pinecone client instance.

    Returns:
        None
    """
    
    with pc.Index(PINECONE_INDEX, pool_threads=30) as index:
        
        iterable_vector=create_iterable_vectors(
            username=username,
            doc_key=doc_key,
            file_bytes=file_bytes,
            embedding_model=embedding_model)
        
        logging.info("Embedding of document is completed, now proceed to upserting embeddings to Pinecone DB")
        
        # Send requests in parallel
        async_results = [
            index.upsert(
                vectors=ids_vectors_chunk, 
                async_req=True
            )
            for ids_vectors_chunk in chunks(iterable_vector, batch_size=100)
        ]
        
        # Wait for and retrieve responses (this raises in case of error)
        [async_result.get() for async_result in async_results]
    
    logging.info("index_stats: ",index.describe_index_stats())
    
