import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

DOCS_PATH = "docs"
store = {}
docs_content = ""

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def load_documents():
    global docs_content
    all_text = []
    for file in sorted(os.listdir(DOCS_PATH)):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(DOCS_PATH, file))
            pages = loader.load()
            for page in pages:
                all_text.append(page.page_content)
    docs_content = "\n\n---\n\n".join(all_text)
    return docs_content

def build_chain(content):
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""Eres el agente de onboarding de 30X. Tu única fuente de información son los siguientes documentos internos de la organización.

DOCUMENTOS:
{content}

Reglas estrictas:
1. Responde SOLO con información de los documentos. No inventes nada.
2. Si la pregunta no está cubierta en los documentos, responde: "Esa información no está en los documentos de onboarding. Te recomiendo preguntarle directamente al Chief of Staff."
3. Recuerda el contexto de la conversación. Si el usuario ya mencionó su área, no le preguntes de nuevo.
4. Responde en español, de forma clara y directa.
5. Para bloqueos técnicos o preguntas no documentadas, indica que la persona indicada es el Chief of Staff."""),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])

    chain = prompt | llm | StrOutputParser()

    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="history"
    )

    return chain_with_history