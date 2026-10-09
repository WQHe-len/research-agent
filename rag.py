import os

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


DB_PATH = "vector_db"


def get_embeddings():

    return HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5",
    model_kwargs={
        "device": "cpu"
    },
    encode_kwargs={
        "normalize_embeddings": True
    }
)


def create_vector_db():

    loader = TextLoader(
        "data/industry.txt",
        encoding="utf-8"
    )

    documents = loader.load()


    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )


    docs = splitter.split_documents(
        documents
    )


    db = FAISS.from_documents(
        docs,
        get_embeddings()
    )


    db.save_local(DB_PATH)

    return db



def load_vector_db():

    if not os.path.exists(DB_PATH):

        return create_vector_db()


    return FAISS.load_local(
        DB_PATH,
        get_embeddings(),
        allow_dangerous_deserialization=True
    )



def search_knowledge(query):

    db = load_vector_db()


    results = db.similarity_search(
        query,
        k=3
    )


    return results