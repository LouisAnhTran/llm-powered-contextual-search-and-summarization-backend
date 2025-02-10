
from typing import List
import json
import logging
import textstat

from langchain.memory import ChatMessageHistory
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.embeddings import OpenAIEmbeddings
from datetime import datetime
from langchain_openai import ChatOpenAI

from src.gen_ai.rag.pinecone_operation import (
    retrieve_top_k_similar_search_from_vector_db
)
from src.gen_ai.rag.prompt_template import (
    CONDENSE_HISTORY_TO_STANDALONE_QUERY_TEMPLATE,
    CONVERSATION_WITH_REFERENCES_TEMPLATE
)
from src.models.requests import (
    SingleChatMessageRequest
)
from src.config import (
    CLARITY_SCORE_FOR_READABILITY
)


def format_chat_history(chat_history: List[SingleChatMessageRequest]) -> ChatMessageHistory:
    """Converts chat history from ChatbotSingleMessage to ChatMessageHistory for usage with langchain
    Args:
        chat_history (List[ChatbotSingleMessage]): Previous chat history containing sender and content
    Returns:
        ChatMessageHistory: Formatted chat history compatible with LangChain
    """
    chat_history_formatted = ChatMessageHistory()
    
    for message in chat_history:
        if message.role == "user":
            chat_history_formatted.add_user_message(message.content)
        elif message.role == "system":
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
        history_messages: List[SingleChatMessageRequest]):
    
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


async def generate_system_response(
        llm: ChatOpenAI,
        embedding_model: OpenAIEmbeddings,
        standalone_query: str,
        username: str,
        history_messages: List[SingleChatMessageRequest],
        doc_key: str,
        top_k: int
):
    logging.info("inside_generate_system_respons")
    
    similar_results=retrieve_top_k_similar_search_from_vector_db(
        username=username,
        doc_key=doc_key,
        query=standalone_query,
        top_k=top_k,
        embedding_model=embedding_model
    )

    logging.info("similar_results: ",similar_results)
    
    similarity_score=similar_results[0]['score']
    
    logging.info("similarity score ",similarity_score)

    all_texts=[chunk['metadata']['text'] for chunk in similar_results]

    logging.info("all_texts: ",all_texts)
    
    clarity_score=textstat.flesch_reading_ease(" ".join(all_texts))
    
    logging.info("clarity_score: ",clarity_score)
    
    if clarity_score < CLARITY_SCORE_FOR_READABILITY:
        
        formatted_chat_history=format_chat_history(
            chat_history=history_messages
        )

        chat_template = PromptTemplate.from_template(CONVERSATION_WITH_REFERENCES_TEMPLATE)
        
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
        
        return all_texts[0]
