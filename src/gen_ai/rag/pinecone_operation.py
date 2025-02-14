from langchain.embeddings import OpenAIEmbeddings
import logging


def retrieve_top_k_similar_search_from_vector_db(
        username:str, 
        doc_key: str,
        query: str,
        top_k: int,
        embedding_model: OpenAIEmbeddings,
        pinecone_index
        
):
    embedding_query=embedding_model.embed_query(query)
    
    logging.info("len of emdedding query: ",len(embedding_query))
    
    results=pinecone_index.query(
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

    