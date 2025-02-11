CONDENSE_HISTORY_TO_STANDALONE_QUERY_TEMPLATE = """Given the following conversation and a follow up question, determine if the new follow up question has any reference to the following conversation.
If yes, rephrase the follow up question to be a standalone question that captures the relevant information.
Standalone question should be as comprehensive as possible to preserve the context and history. Follow up question contain it, this, or that, try to understand it refers to and put the exact terms in the standalone question
If not, return the original question.
----------
CHAT HISTORY: {chat_history}
----------
FOLLOWUP QUESTION: {question}
----------
Standalone question:"""

PERFORM_SEMANTIC_SEARCH_WITH_CONTEXT_TEMPLATE = """
You are a friendly expert to answer questions based on the provided context and references. 
 
Instructions:
1. Use clear language.
2. Present answer clearly and concisely based on the provided context. 
3. Use Markdown formatting to enhance readability with headings, list items, paraphragh. Apply headings, lists, and appropriate line spacing where necessary.
3. Strictly use provided context to answer question, don't use your external knowledge.

----------
Context from the original source that could be used to help answer the question:
{context}

----------
Chat History:
{chat_history}

----------
Question:
{question}

----------
Response (in correct formatting):
"""

SUMMARIZE_SIMILAR_PASSAGE_INTO_CONCISE_RESPONSE_TEMPLATE = """
You are a friendly expert to answer questions based on the provided context and references. 
 
Instructions:
1. Use clear language and present answer clearly and concisely based on the provided context. 
2. Summarize many provided references into a passage while preserving the meaning.
3. Use Markdown formatting to enhance readability with headings, list items, paraphragh. Apply headings, lists, and appropriate line spacing where necessary.
4. Strictly use provided context to answer question, don't use your external knowledge.
5. The length of your response should be align with user's preferred response length
----------
References from original document:
{context}

----------
User preferred response length:
{preferred_response_length}

----------
Chat History:
{chat_history}

----------
Question:
{question}

----------
Response (in correct formatting):
"""