import os

from transformers import pipeline

from core.model.rag_module import RagModule


class LlmModule:
    def __init__(self):
        self.model = pipeline("text2text-generation", model="google/flan-t5-large")
        self.rag = RagModule()

    def build_prompt(self, context, question):
        prompt = f"""
    Tu es un assistant intelligent qui répond avec précision aux questions en utilisant les informations fournies. 
    Utilise uniquement le contexte donné ci-dessous pour formuler ta réponse.

    ### Contexte :
    {context}

    ### Question :
    {question}

    ### Réponse :
    """
        return prompt

    def generate_response(self, question, faiss_path):
        if not os.path.exists(faiss_path):
            return "Base FAISS NotFound : " + faiss_path

        results = self.rag.search_faiss(question, faiss_path)
        context = ""
        sources = ""
        for result in results:
            context += result.page_content + "\n"
            sources += "Source : " + result.metadata['source'] + ", page : " + str(result.metadata['page']) + "\n"

        prompt = f"Réponds à la question en utilisant ces informations :\n\n{context}\n\nQuestion: {question}\nRéponse:"

        responses = self.model(prompt, max_length=200, do_sample=True, temperature=0.7)
        result = ""
        for response in responses:
            result += response['generated_text']


        result += "\n\n" + sources
        return result


