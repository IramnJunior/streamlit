from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import TokenTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from dotenv import load_dotenv
load_dotenv()

loader = PyPDFDirectoryLoader("data/")

data = loader.load()

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

text_splitter = TokenTextSplitter(
    chunk_size=350,
    chunk_overlap=100
)

documents = text_splitter.split_documents(data)


vector_store = FAISS.from_documents(documents, embeddings)
vector_store.save_local("faiss", "faiss_database")

retriever = vector_store.as_retriever()

def get_rag_response(question: str) -> list:
    rag_response = retriever.invoke(question)
    print(rag_response[0].page_content)
    return rag_response