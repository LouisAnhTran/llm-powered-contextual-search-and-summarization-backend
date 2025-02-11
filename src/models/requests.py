
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class SingleChatMessageRequest(BaseModel):
    role:  str=Field(
        example="user"
    )
    content: str=Field(
        example="Tell me the overview of this document"
    )
    timestamp: datetime = Field(
        example="2023-07-17T12:34:56"
    )

class ChatMessagesRequest(BaseModel):
    list_of_messages: List[SingleChatMessageRequest] = Field(
        example=[
            {
                "role": "user",
                "content": "Tell me the overview of this document",
                "timestamp": "2023-07-17T12:34:56"
            },
            {
                "role": "assistant",
                "content": "The document is about is Programming language concept and compiler design",
                "timestamp": "2023-07-17T12:35:10"
            },
             {
                "role": "user",
                "content": "What is the compiler relationship to Programming language concept",
                "timestamp": "2023-07-17T12:35:15"
            }
        ]
    )
    preferred_response_length: Optional[str] = Field(default="medium", example="short")
 