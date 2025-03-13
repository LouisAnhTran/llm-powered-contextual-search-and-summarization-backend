from typing import List
import logging
import textstat
from langchain.memory import ChatMessageHistory
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from pinecone import Index

from src.gen_ai.rag.pinecone_operation import (
    retrieve_top_k_similar_search_from_vector_db
)
from src.gen_ai.rag.prompt_template import (
    CONDENSE_HISTORY_TO_STANDALONE_QUERY_TEMPLATE,
    PERFORM_SEMANTIC_SEARCH_WITH_CONTEXT_TEMPLATE,
    SUMMARIZE_SIMILAR_PASSAGE_INTO_CONCISE_RESPONSE_TEMPLATE,
    LLM_GENERATED_SUMMARY_FALLBACK
)
from src.models.requests import (
    SingleChatMessageRequest
)
from src.config import (
    CLARITY_SCORE_FOR_READABILITY,
    SIMILARITY_SEARCH_THRESHOLD
)


def format_chat_history(
    chat_history: List[SingleChatMessageRequest]
) -> ChatMessageHistory:
    """Converts chat history from ChatbotSingleMessage to ChatMessageHistory for usage with langchain

    Args:
        chat_history (List[SingleChatMessageRequest]): Previous chat history containing sender and content

    Returns:
        ChatMessageHistory: Formatted chat history compatible with LangChain
    """
    
    chat_history_formatted = ChatMessageHistory()
    
    for message in chat_history:
        if message.role == "user":
            chat_history_formatted.add_user_message(message.content)
        elif message.role == "assistant":
            # revert output format
            chat_history_formatted.add_ai_message(
                message=message.content
            )
        else:
            logging.info("sender of this message is not valid")
            
    logging.info("chat_history_formatted: ",chat_history_formatted)

    return chat_history_formatted

def generate_standalone_query(
        llm: ChatOpenAI,
        user_query: SingleChatMessageRequest,
        history_messages: List[SingleChatMessageRequest]) -> str:
    """   
    Generates a standalone query from a user query and the chat history using LLM.

    Args:
        llm (ChatOpenAI): large language model
        user_query (SingleChatMessageRequest): user query
        history_messages (List[SingleChatMessageRequest]): history of messages

    Returns:
        str: user standalone query
    """
    
    logging.info("inside generate_standalone_query")
    
    formatted_chat_history=format_chat_history(
        chat_history=history_messages
    )
    
    logging.info("formatted_chat_history: ",formatted_chat_history)

    question_generator_template = PromptTemplate.from_template(
        CONDENSE_HISTORY_TO_STANDALONE_QUERY_TEMPLATE
    )

    chain = LLMChain(llm=llm, prompt=question_generator_template)

    response=chain(
        {"chat_history": format_chat_history,"question":user_query}, return_only_outputs=True
    )

    logging.info("standalone_query: ",response['text'])

    return response['text']


async def generate_semantic_search_response(
        llm: ChatOpenAI,
        embedding_model: OpenAIEmbeddings,
        standalone_query: str,
        username: str,
        history_messages: List[SingleChatMessageRequest],
        doc_key: str,
        top_k: int,
        pinecone_index
) -> str:
    """ Generates a semantic search response based on a user query and relevant document context using LLM


    Args:
        llm (ChatOpenAI): large language model
        embedding_model (OpenAIEmbeddings): embedding model
        standalone_query (str): user standalone query
        username (str): username 
        history_messages (List[SingleChatMessageRequest]): history messages
        doc_key (str): unique document key
        top_k (int): k most similar documents in vector db
        pinecone_index (Index): index that host the vector db

    Returns:
        str: result for semantic search
    """
    
    logging.info("inside_generate_system_respons")
    
    # Retrieve the top-k (k=1 in this case) most similar search results from the vector database
    similar_results=retrieve_top_k_similar_search_from_vector_db(
        username=username,
        doc_key=doc_key,
        query=standalone_query,
        top_k=top_k,
        embedding_model=embedding_model,
        pinecone_index=pinecone_index
    )
    
    all_texts=None
    
    # if top similar passage is retrieved succesfully
    if similar_results: 
        logging.info("similar_results: ",similar_results)
        
        # Extract similarity score of the top retrieved result
        similarity_score=similar_results[0]['score']
        logging.info("similarity score ",similarity_score)
        
        # Extract the text content from the retrieved search results
        all_texts=[chunk['metadata']['text'] for chunk in similar_results]
        logging.info("all_texts: ",all_texts)
        
        
        logging.info("SIMILARITY_SEARCH_THRESHOLD: ",SIMILARITY_SEARCH_THRESHOLD)
        logging.info("CLARITY_SCORE_FOR_READABILITY: ",CLARITY_SCORE_FOR_READABILITY)
        
        # if similarity score of the most similar passage is higher than our predefined threshold, we found the relevant passage containing information for semantic search
        if similarity_score >= SIMILARITY_SEARCH_THRESHOLD:
            
            # we then compute the clarity score using textstat library to see if the retrieved passage is easy to read for user
            clarity_score=textstat.flesch_reading_ease(" ".join(all_texts))
            
            logging.info("clarity_score: ",clarity_score)
            
            # if the clarity score is less than our predefine threshold, we ask LLM to rephrase to add clarity 
            if clarity_score < CLARITY_SCORE_FOR_READABILITY:
                
                formatted_chat_history=format_chat_history(
                    chat_history=history_messages
                )

                chat_template = PromptTemplate.from_template(PERFORM_SEMANTIC_SEARCH_WITH_CONTEXT_TEMPLATE)
                
                chain = LLMChain(llm=llm, prompt=chat_template)
                
                result = chain(
                    {
                        "context": all_texts,
                        "chat_history": formatted_chat_history,
                        "question": standalone_query,
                    },
                    return_only_outputs=True
                )
                
                logging.info("result_semantic_search: ",result['text'])

                return result['text']
        
            else:
                # otherwise the passage is clear and readable, we straight away return response to user without making LLM call
                return " ".join(all_texts)
            

    # if similarity score of the most similar passage is less than our predefined threshold, implying that we can not find relavant information in our document to answer user query,so we will use fallback LLM-generated summary 
    logging.info("No relavant passage is found based on user query")
    logging.info("Trigger fallback LLM-generated summary")
    
    formatted_chat_history=format_chat_history(
            chat_history=history_messages
    )

    chat_template = PromptTemplate.from_template(LLM_GENERATED_SUMMARY_FALLBACK)
    
    chain = LLMChain(llm=llm, prompt=chat_template)
    
    result = chain(
        {
            "context": all_texts if all_texts else "",
            "chat_history": formatted_chat_history,
            "question": standalone_query,
        },
        return_only_outputs=True
    )
    
    logging.info("result_semantic_search_fall_back: ",result['text'])

    return result['text']
    
    
async def generate_summarized_response(
        llm: ChatOpenAI,
        embedding_model: OpenAIEmbeddings,
        standalone_query: str,
        username: str,
        history_messages: List[SingleChatMessageRequest],
        doc_key: str,
        top_k: int,
        preferred_response_length: str,
        pinecone_index
):
    """  Generates a summarized response based on a user query and relevant document context.


    Args:
        llm (ChatOpenAI): large language model
        embedding_model (OpenAIEmbeddings): embedding model
        standalone_query (str): user standalone query
        username (str): username must be unique
        history_messages (List[SingleChatMessageRequest]): history messages between user and system
        doc_key (str): unique document key
        top_k (int): k most similar documents in vector db
        preferred_response_length (str): user preffered length of response

    Returns:
        str: the summarized response from LLM
    """
    
    logging.info("inside_generate_summarized_response")
    
    # Retrieve the top-k (k=5 in this case) most similar search results from the vector database
    similar_results=retrieve_top_k_similar_search_from_vector_db(
        username=username,
        doc_key=doc_key,
        query=standalone_query,
        top_k=top_k,
        embedding_model=embedding_model,
        pinecone_index=pinecone_index
    )

    logging.info("similar_results: ",similar_results)
    
    # Extract the text content from the retrieved search results
    all_texts=[chunk['metadata']['text'] for chunk in similar_results]
    logging.info("all_texts: ",all_texts)
    
    formatted_chat_history=format_chat_history(
        chat_history=history_messages
    )

    chat_template = PromptTemplate.from_template(SUMMARIZE_SIMILAR_PASSAGE_INTO_CONCISE_RESPONSE_TEMPLATE)
    
    chain = LLMChain(llm=llm, prompt=chat_template)
    

    result = chain(
        {
            "context": all_texts,
            "chat_history": formatted_chat_history,
            "question": standalone_query,
            "preferred_response_length": preferred_response_length
        },
        return_only_outputs=True
    )
    
    logging.info("result_summary: ",result['text'])

    return result['text']


   
