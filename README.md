![Contributors][contributors-shield]
![Forks][forks-shield]
![Stargazers][stars-shield]
![Issues][issues-shield]
[![LinkedIn][linkedin-shield]](https://www.linkedin.com/in/louisanhtran/)



<!-- Logo of website -->
<div align="center">

  <img src="https://effvision.com/wp-content/uploads/2024/06/artificial-intelligence-new-technology-science-futuristic-abstract-human-brain-ai-technology-cpu-central-processor-unit-chipset-big-data-machine-learning-cyber-mind-domination-generative-ai-scaled-1.jpg" width="500">

</div>

<!-- Introduction of project -->

<div align="center">
  
# LLM-Powered Contextual Search & Summarization

</div>

<h2 align="center" style="text-decoration: none;">Document processing AI Application</h2>

## About The Application :

This application is designed to efficiently process contextual and semantic search, as well as summarization, on large PDF documents. The list of main features offered by the application is shown below:

- [x] Indexing large documents efficiently using parallel processing and a distributed vector database.
- [x] Allowing accurate semantic search (not just keyword-based) on those documents.
- [x] A well-designed AI pipeline for optimizing costs by reducing unnecessary LLM calls.
- [x] Caching responses using an in-memory DB (Redis) to minimize costs and enhance user experience.
- [x] PDF documents are encrypted and securely stored in an AWS S3 bucket.
- [x] A clean and user-friendly interface built with Streamlit.

## Built With

This section outlines the technologies and tools used to develop the application.

* Backend: ![fastapi-shield][fastapi-shield]
* Frontend: ![fastapi-shield][streamlit-shield]
* AI/ML Framework: ![fastapi-shield][langchain-shield]
* LLM Provider: OpenAI
* Chat model: gpt-4o
* Embedding model: text-embedding-ada-002
* Vector database: Pinecone
* PDF Document storage: AWS S3 Bucket
* Caching: Redis
* Parsing large PDFs document: PyMuPDF

## Main components:

- API Endpoints are defined under [API Endpoints](https://github.com/LouisAnhTran/llm-powered-contextual-search-and-summarization-backend/blob/main/src/api/v1/app.py)
- Document indexing pipeline is defined under [Document Indexing Pipeline](https://github.com/LouisAnhTran/llm-powered-contextual-search-and-summarization-backend/blob/main/src/gen_ai/rag/doc_processing.py)
- Handling of LLM API calls and Chaining are managed and defined under [LLM API Calls + Chaining](https://github.com/LouisAnhTran/llm-powered-contextual-search-and-summarization-backend/blob/main/src/gen_ai/rag/chat_processing.py)
- Prompt templates are defined under [Prompt Templates](https://github.com/LouisAnhTran/llm-powered-contextual-search-and-summarization-backend/blob/main/src/gen_ai/rag/prompt_template.py)
- All constant variables needed to run the application are defined under [Configurations](https://github.com/LouisAnhTran/llm-powered-contextual-search-and-summarization-backend/blob/main/src/config.py)

<!-- GETTING STARTED -->
## Getting Started


### Prerequisites

1. Poetry:
  - Use the follow command to check whether poetry is installed in your machine
```
poetry --version
```
  - If poetry is not yet installed in your machine, please follow the link below to install Poetry, which is a common tool for dependency management and packaging in Python, specially for AI Applications.
[Poetry](https://python-poetry.org/docs/)

2. Docker:
  - Install Docker to run Redis server container later for caching LLM responses.
[Docker](https://docs.docker.com/engine/install/)

3. Clone the project to your local machine.

  ``` 
  git clone https://github.com/LouisAnhTran/llm-powered-contextual-search-and-summarization-backend.git
  ```


### Installation

1. Add the .env File:
- Place the .env file in the main project folder.
- It should contain all necessary credentials, including the AWS Access Key, OpenAI API Key, Pinecone API Key, etc.

2. Install Dependencies:
  ```sh
  poetry install
  ```

3. Create an Python virtual environment 

  ```sh
  poetry shell
  ```

4. Run the application
  ```sh
  poetry run python main.py   
  ```

5. Run the Redis server as a Docker container for caching LLM respone
- Open another terminal and type in following command
  ```sh
  docker run -d --name redis -p 6379:6379 redis      
  ```

6. Viewing API Endpoins through Swagger UI
- Right now the application should be up and running at port 8080. Click on [SwaggerUI](http://localhost:8080/docs) to view the list of all API endpoints.

7. Open Frontend
- Access the following repo to set up and run the Frontend of the application. [Frontend Repo](https://github.com/LouisAnhTran/llm-powered-contextual-search-and-summarization-frontend)



## Architecture: 

### System Architecture:
   
![Screenshot 2025-02-15 at 12 20 59 AM](https://github.com/user-attachments/assets/6c1596c7-355a-45a2-8844-8c2f2f243850)

### Flow diagrams:

1. Semantic Search:

2. Contextual Summarization:

<!-- ACKNOWLEDGMENTS -->
## References:

- ![FastAPI](https://fastapi.tiangolo.com/)

- ![Redis](https://redis.io/)

- ![Pipecone](https://www.pinecone.io/)





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png


[fastapi-shield]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[streamlit-shield]: https://img.shields.io/badge/-Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white
[langchain-shield]: https://img.shields.io/badge/LangChain-ffffff?logo=langchain&logoColor=green











