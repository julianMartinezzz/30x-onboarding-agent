import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

DOCS_PATH = "docs"
CHROMA_PATH = "chroma_db"
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    if os.path.exists(CHROMA_PATH) and os.listdir(CHROMA_PATH):
        return Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

    docs = []
    for file in os.listdir(DOCS_PATH):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(DOCS_PATH, file))
            docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    vectorstore = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=CHROMA_PATH
    )
    return vectorstore

def build_chain(vectorstore):
    llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2
   )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Eres el agente de onboarding de 30X. Tu única fuente de información son los documentos internos de la organización.

Reglas estrictas:
1. Responde SOLO con información de los documentos. No inventes nada.
2. Si la pregunta no está cubierta en los documentos, responde: "Esa información no está en los documentos de onboarding. Te recomiendo preguntarle directamente al Chief of Staff."
3. Recuerda el contexto de la conversación. Si el usuario ya mencionó su área, no le preguntes de nuevo.
4. Responde en español, de forma clara y directa.
5. Para bloqueos técnicos o preguntas no documentadas, indica que la persona indicada es el Chief of Staff.

Contexto de los documentos:
{context}"""),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])

    def get_context(input):
        docs = retriever.invoke(input["question"])
        return "\n\n".join([d.page_content for d in docs])

    chain = (
        RunnablePassthrough.assign(context=get_context)
        | prompt
        | llm
        | StrOutputParser()
    )

    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="history"
    )

    return chain_with_history