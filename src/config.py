from dotenv import load_dotenv
import os

load_dotenv()

PORT=int(os.getenv("PORT"))
AWS_ACCESS_KEY=os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY=os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME=os.getenv("AWS_BUCKET_NAME")
AWS_REGION=os.getenv("AWS_REGION")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
MAIN_TENANT=os.getenv("MAIN_TENANT")

    

