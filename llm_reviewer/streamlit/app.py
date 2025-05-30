import streamlit as st
import sys
import os
import torch

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_reviewer.streamlit.cache import get_all, set, get
from llm_reviewer.app import run_review, save_vector_store_documents

# To remove error: RuntimeError: no running event loop
torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)]
torch.classes.__path__ = []

st.set_page_config(
    page_title="Revisor de código com IA", page_icon="🤖", layout="centered"
)


def add_git_project(name, api_key, project_id):
    set(
        {"name": name, "api_key": api_key, "project_id": project_id},
        f"git_projects:{project_id}",
    )
    st.rerun()


@st.dialog("Adicionar novo projeto Git")
def add_project_modal():
    name = st.text_input(
        "Nome do projeto",
        key="name",
    )
    api_key = st.text_input("API Key do projeto", type="password", key="api_key")
    project_id = st.text_input("Id do projeto", key="project_id")

    submit = st.button("Salvar")
    if submit and name and api_key and project_id:
        add_git_project(name, api_key, project_id)
        st.success("Projeto adicionado com sucesso!")


@st.dialog("Documentações de código")
def handle_documentations():
    target = os.path.join(os.path.dirname(__file__), "../docs")
    files = os.listdir(target)

    if files:
        st.subheader("Arquivos existentes")
        for f in files:
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.write(f"• {f}")
            with col2:
                if st.button("🗑️", key=f"del_{f}"):
                    os.remove(os.path.join(target, f))
                    col1.success(f"Arquivo `{f}` deletado com sucesso.")

    else:
        st.info("Nenhum arquivo nesta pasta ainda.")

    st.markdown("---")

    uploaded = st.file_uploader(
        "Fazer upload de documentações", accept_multiple_files=True
    )
    file_name = ""
    if uploaded:
        for file in uploaded:
            path = os.path.join(target, file.name)
            with open(path, "wb") as out:
                file_name = file.name
                out.write(file.getbuffer())
        st.success(f"{len(uploaded)} arquivo(s) enviado(s) para `{target}`!")

        update_context = st.button("Atualizar contexto")
        if update_context:
            try:
                st.warning(
                    "O contexto da LLM está sendo atualizado, por favor aguarde..."
                )

                save_vector_store_documents(file_name)
                st.success("Contexto atualizado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao atualizar o contexto: {e}")


with st.sidebar:
    st.header("Configurações")

    openai_key = get("openai_key")
    openai_key_value = openai_key if openai_key is not None else os.environ["API_KEY"]
    open_ai_api_key = st.text_input(
        "OpenAi Api Key",
        key="open_ai_api_key",
        type="password",
        value=openai_key_value,
    )

    repos = get_all("git_projects")
    if repos:
        options = map(lambda x: x["name"], repos)

        git_project = st.selectbox(
            label="Selecione o projeto que deseja revisar",
            options=options,
        )

        selected_repo = next((repo for repo in repos if repo["name"] == git_project))

    st.write("Adicione um novo projeto Git")
    if st.button("Adicionar"):
        add_project_modal()

    st.divider()
    st.write(
        "Adicione documentações e padrões de código para a IA usar como base no processo de revisão."
    )

    if st.button("Ver documentações"):
        handle_documentations()


with st.container():

    st.title("LLM Reviewer 💬")
    st.markdown(
        """
        ### 💡 Como usar
        - Adicione o seu projeto GIT, o ID do Pull Request e se for necessário a API key da OpenAI na barra lateral.
        - Adicione as documentações e padrões de código para a IA usar como base no processo de revisão.
        - O revisor usa LLM + RAG para identificar bugs, sugerir refatorações e aplicar boas práticas baseadas nas documentações fornecidas.
        - Para entender sobre o projeto acesse [Github](https://github.com/Rassis7/llm-reviewer)
    """
    )

    st.divider()
    pull_request_id = st.number_input(
        "Digite o ID do Pull Request",
        key="pull_request_id",
        value=None,
        step=1,
    )

    is_enabled = (
        pull_request_id and selected_repo["api_key"] and selected_repo["project_id"]
    )

    is_post_comment = st.checkbox(
        "Postar comentário no Pull Request",
        key="post_pull_request_comment",
        value=os.environ["POST_PULL_REQUEST_COMMENT"] == "true",
    )

    if st.button("Revisar código"):
        if not is_enabled:
            st.warning("Preencha todos os campos para revisar o código.")
        else:

            if open_ai_api_key:
                os.environ["API_KEY"] = open_ai_api_key

            os.environ["POST_PULL_REQUEST_COMMENT"] = str(is_post_comment)
            os.environ["GIT_TOKEN"] = selected_repo["api_key"]
            os.environ["GIT_PROJECT_ID"] = selected_repo["project_id"]
            os.environ["GIT_MERGE_REQUEST_IID"] = str(pull_request_id)
            try:
                response = run_review()
                response_container = st.container(border=True)
                if response:
                    response_container.empty()
                    with response_container.container():
                        response_container.markdown(response)
            except Exception as e:
                st.write("❌ Erro ao revisar o código:", e)
