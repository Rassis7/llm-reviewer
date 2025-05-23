# AI Code reviewer (LLM & RAG) 🤖

This project is a smart code reviewer that uses Large Language Models (LLM) and Retrieval-Augmented Generation (RAG) techniques to help software developers continuously improve code quality.
This tool analyzes code blocks and returns suggestions, identifies inadequate standards, and suggests best development practices.

## Main features ⚡️

- **Auto Code Analyzer:**  
  Uses advanced language models to perform code reviews, identifying inconsistencies, potential bugs, and necessary refactoring.

- **Suggestions Based in Context:**  
  Using RAG, the system is able to retrieve important information (e.g., project standards, documentation, and good practices) and return custom recommendations based on the project context.

- **Customization and Extensibility:**  
  The project was developed with extensibility in mind, allowing users to adjust parameters, improve language models, and expand features when necessary.

## What is RAG? 🤨

Retrieval-Augmented Generation (RAG) integrates retrieval mechanisms with generative models. It first fetches contextually relevant external information, then leverages this data to produce enhanced, accurate, and informed responses—allowing AI to generate context-aware outputs beyond its static training data.

<img src="docs/rag.png" />

## Running Application 👀

### Code documentations

You need add your code documentations in `llm_reviewer/docs`

> ⚠️ Important: Your documentations should be in `.pdf`

### Environment file

After that, you must add the information in `.env`, like:

```
API_URL=http://localhost:11434 // Or another URL
API_KEY= // Your LLM api key (if necessary)
DB_PATH=vectorstore/db // Or another path
COLLECTION_NAME=good-code // Or name for your VectorStore BD
GIT_TOKEN= // Gitlab token
GIT_BASE_URL= // Base url for the GitLab project
GIT_PROJECT_ID= // Project ID
GIT_MERGE_REQUEST_IID= // Merge Request number
CODE_MODEL= // Some llm code model
CONVERSATION_MODEL= // Some llm conversation model
```

> ⚠️ Important: Now this application now supports GitLab

## Stack 🧩

- **Language:** Python, Poetry and LangChain
- **AI Models:** Using LLMs for natural language processing and RAG to retrieve answers based on a knowledge base.

## Project 🏎️

### Install poetry

To get started, you need [Poetry](https://python-poetry.org/). It's recommended to install it using [pipx](https://pipx.pypa.io/stable/).

Follow this [installation guide](https://pipx.pypa.io/stable/installation/) to set up `pipx`.

Once `pipx` is installed, use the following command to install Poetry:

```bash
pipx install poetry
```

That's it! Poetry is now installed on your machine. 🚀

### Virtual Environment (venv)

> You need `python3` with minimum version `@3.12.4`

Start venv

```bash
poetry env use python3
```

---

If you recived follow error:

```
The currently activated Python version 3.X.X is not supported by the project (3.12.4).
Trying to find and use a compatible version.
```

Install `pyenv`:

Macos

```bash
brew install pyenv
```

Unix System:

```bash
curl https://pyenv.run | bash
```

After install `python@3.12.4`

```bash
pyenv install 3.12.4
```

Use version in project

```bash
pyenv local 3.12.4
poetry env use $(pyenv which python)
```

### Install deps

```bash
poetry install
```

> if .env not works, you run follow command:

```bash
poetry self add poetry-plugin-dotenv
```

### Run project

```bash
poetry run dev
```

### Run with local LLM (Extra)

You can download [ollama](https://ollama.com/) to run locally.

Start ollama server in terminal:

```bash
ollama serve
```

Download or run some llm model:

```bash
ollama run LLM_MODEL_NAME
```

## TODO 📋

### Must Have

- [x] Allow the use of more than one model
- [x] Use various types of embeddings
- [ ] Enable dynamic uploading of the rules file
- [x] UI to add and view review infos

### Nice to Have

- [ ] Add AI agent (next feature)
- [ ] Function to add the new file to the RAG
- [ ] Improve the parameters for each LLM
