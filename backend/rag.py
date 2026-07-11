from transcript import fetch_transcript
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings, ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from prompts import RAG_PROMPT
from config import EMBEDDING_MODEL, LLM_MODEL, TOP_K

class VideoRAG:
    def __init__(self, video_id):
        self.docs = fetch_transcript(video_id)
        if not self.docs:
            raise ValueError(f"Could not retrieve English transcript for video ID: {video_id}")
        self.retriever = self.create_retriever(self.docs)
        llm = HuggingFaceEndpoint(
            repo_id=LLM_MODEL,
            task="text-generation",
            max_new_tokens=512,
            temperature=0.2,
            do_sample=False
        )
        self.llm = ChatHuggingFace(
            llm=llm
        )
        self.chain = self.create_chain()

# CREATING RETRIEVER
    def create_retriever(self, docs):
        embeddings = HuggingFaceEmbeddings(
        model = EMBEDDING_MODEL
    )
        self.vector_store = FAISS.from_documents(docs, embeddings)

        retriever = self.vector_store.as_retriever(
            search_type = "similarity",
            search_kwargs = {'k' : TOP_K}
        )

        return retriever

# DOCUMENT FORMATTER
    def format_docs(self, retrieved_docs):
        context = ""
        for doc in retrieved_docs:

            start = int(doc.metadata["start"])

            hours = start // 3600
            minutes = (start % 3600) // 60
            seconds = start % 60

            if hours > 0:
                timestamp = f"{hours:02}:{minutes:02}:{seconds:02}"
            else:
                timestamp = f"{minutes:02}:{seconds:02}"

            context += f"[{timestamp}]\n{doc.page_content}\n\n"
        return context

# BUILDING CHAIN
    def create_chain(self):
        parallel_chain = RunnableParallel({
            "context" : self.retriever | RunnableLambda(self.format_docs),
            "question" : RunnablePassthrough()
        })
        parser = StrOutputParser()

        chain = parallel_chain | RAG_PROMPT | self.llm | parser

        return chain 


    def get_sources(self, docs):
        sources = []
        seen = set()

        for doc in docs:
            seconds = int(doc.metadata['start'])

            if seconds in seen:
                continue

            seen.add(seconds)

            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60

            if hours:
                timestamp = f"{hours:02}:{minutes:02}:{secs:02}"
            else:
                timestamp = f"{minutes:02}:{secs:02}"

            sources.append({
                "timestamp" : timestamp,
                "seconds" : seconds
            })
        
        return sources

    
    def ask(self, question:str):
        retrieved_docs = self.retriever.invoke(question)
        context = self.format_docs(retrieved_docs)

        answer = (RAG_PROMPT | self.llm | StrOutputParser()).invoke({
            "context" : context,
            "question" : question
        })

        return{
            "answer" : answer,
            "sources" : self.get_sources(retrieved_docs)
        }



