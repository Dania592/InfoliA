import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS

class RagModule:
    def __init__(self):
        self.model_path = "BAAI/bge-m3"
        model_kwargs = {"device": "cpu"}
        encode_kwargs = {"normalize_embeddings": True}
        self.embedding = HuggingFaceEmbeddings(
            model_name=self.model_path,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=150,
            separators=['.']
        )

    def load_pdf_text(self, path_to_pdf):
        if not os.path.exists(path_to_pdf):
            raise FileNotFoundError
        loader = PyPDFLoader(path_to_pdf)
        documents = loader.load()
        return documents

    def create_faiss_db(self, pdf_paths, vectorstor_path):
        documents = []
        for pdf_path in pdf_paths:
            document = self.load_pdf_text(pdf_path)
            documents.extend(document)

        chunks = self.text_splitter.split_documents(documents)
        vectorstore = FAISS.from_documents(chunks, self.embedding)
        vectorstore.save_local(vectorstor_path)


    def add_pdf(self, path_to_pdf, vectorstor_path):

        if not os.path.exists(vectorstor_path):
            self.create_faiss_db([path_to_pdf], vectorstor_path)
        else:
            existing_db = FAISS.load_local(vectorstor_path, self.embedding, allow_dangerous_deserialization=True)
            new_doc = self.load_pdf_text(path_to_pdf)
            new_chunks = self.text_splitter.split_documents(new_doc)
            existing_db.add_documents(new_chunks)
            existing_db.save_local(vectorstor_path)

    def search_faiss(self, question, vectorstor_path,  nb_answers= 2 ):
        if not os.path.exists(vectorstor_path):

            return
        else:
            vector_db = FAISS.load_local(vectorstor_path, self.embedding, allow_dangerous_deserialization=True)
            results = vector_db.similarity_search(question, k=nb_answers)
            return results







