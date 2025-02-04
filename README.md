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

## Running Application (Example) 👀

### Files

-> [Good Coding Practices](llm_reviewer/files/good-code.md)

-> [Pull Request](llm_reviewer/files/pull-request.txt)

### Response

<img src="docs/example.png" />

## Stack 🧩

- **Language:** Python, Poetry and LangChain
- **AI Models:** Using LLMs for natural language processing and RAG to retrieve answers based on a knowledge base.

## Project 🏎️

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

```bash
docker-compose up
```

> after run project

```bash
poetry run dev
```

## TODO 📋

### Must Have

- [x] Allow the use of more than one model
- [x] Use various types of embeddings
- [ ] Add AI agent (next feature)
- [ ] Enable dynamic uploading of the rules file
- [ ] Split the DIFF file into individual diffs (by checking the token count)

### Nice to Have

- [ ] Function to add the new file to the RAG
- [ ] Visual interface
- [ ] Improve the parameters for each LLM
