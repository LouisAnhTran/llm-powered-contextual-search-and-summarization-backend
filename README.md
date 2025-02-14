![Contributors][contributors-shield]
![Forks][forks-shield]
![Stargazers][stars-shield]
![Issues][issues-shield]
![MIT License][license-shield]
![LinkedIn][linkedin-shield]



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

This application is designed to efficiently process contextual and semantic search, as well as summarization, on large PDF documents. The list of main features offered by the application is below:

- [x] Indexing large documents efficiently using parallel processing and a distributed vector database.
- [x] Allowing accurate semantic search (not just keyword-based) on those documents.
- [x] A well-designed AI pipeline for optimizing costs by reducing unnecessary LLM calls.
- [x] Caching responses using an in-memory DB (Redis) to minimize costs and enhance user experience.
- [x] PDF documents are encrypted and securely stored in an AWS S3 bucket.
- [x] A clean and user-friendly interface built with Streamlit.

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>


## Built With

This section outlines the technologies and tools used to develop the application.

* Backend: [![fastapi-shield][fastapi-shield]][JQuery-url]
* Frontend: [![fastapi-shield][streamlit-shield]][JQuery-url]
* AI/ML Framework: [![fastapi-shield][langchain-shield]][JQuery-url]
* LLM Provider: OpenAI
* Chat model: gpt-4o
* Embedding model: ext-embedding-ada-002
* Vector database: Pinecone
* PDF Document storage: AWS S3 Bucket
* Caching: Redis
* Parsing large PDFs document: PyMuPDF

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
  ```sh
  docker run -d --name redis -p 6379:6379 redis      
  ```

6. Viewing API Endpoins through Swagger UI
- Right now the application should be up and running at port 8080. Click on [SwaggerUI](http://localhost:8080/docs) to view the list of all API endpoints.


<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Add Changelog
- [x] Add back to top links
- [x] Add Additional Templates w/ Examples
- [x] Add "components" document to easily copy & paste sections of the readme
- [x] Multi-language Support


See the [open issues](https://github.com/othneildrew/Best-README-Template/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Your Name - [@your_twitter](https://twitter.com/your_username) - email@example.com

Project Link: [https://github.com/your_username/repo_name](https://github.com/your_username/repo_name)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* [Choose an Open Source License](https://choosealicense.com)
* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
* [Malven's Flexbox Cheatsheet](https://flexbox.malven.co/)
* [Malven's Grid Cheatsheet](https://grid.malven.co/)
* [Img Shields](https://shields.io)
* [GitHub Pages](https://pages.github.com)
* [Font Awesome](https://fontawesome.com)
* [React Icons](https://react-icons.github.io/react-icons/search)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



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
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 

[fastapi-shield]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[streamlit-shield]: https://img.shields.io/badge/-Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white
[langchain-shield]: https://img.shields.io/badge/LangChain-ffffff?logo=langchain&logoColor=green











