import os
import pinecone
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
from pinecone import Pinecone
import logging

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index = pc.Index(os.getenv("PINECONE_INDEX"))

def retrieve_top_k_similar_search_from_vector_db(
        username:str, 
        doc_key: str,
        query: str,
        top_k: int,
        embedding_model: OpenAIEmbeddings
):
    embedding_query=embedding_model.embed_query(query)
    
    print("len of emdedding query: ",len(embedding_query))
    
    results=index.query(
        vector=embedding_query,
        filter={
            "username": {"$eq": username},
            "doc_key": doc_key
        },
        top_k=top_k,
        include_metadata=True
    )
    
    logging.info("results_similar_search ",results)
    
    return results['matches']

    