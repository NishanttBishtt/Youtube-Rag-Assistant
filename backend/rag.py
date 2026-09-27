from transcript import fetch_transcript
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings, ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from prompts import RAG_PROMPT
from config import EMBEDDING_MODEL, LLM_MODEL, TOP_K
import numpy as np

class VideoRAG:
    def __init__(self, video_id):
        self.docs = fetch_transcript(video_id)
        if not self.docs:
            raise ValueError(f"Could not retrieve English transcript for video ID: {video_id}")
        self.embeddings = HuggingFaceEmbeddings(model=EMBEDDING_MODEL)
        self.retriever = self.create_retriever(self.docs)
        self.subtitle_cache = self.build_subtitle_cache(self.docs)
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

# BUILDING SUBTITLE CACHE
    def build_subtitle_cache(self, docs):
        """
        Precompute subtitle embeddings once during initialization.
        Returns a dict keyed by chunk start time, each value is a list of
        {text, start, embedding} for that chunk's subtitles.
        """
        cache = {}
        for doc in docs:
            chunk_start = doc.metadata["start"]
            subtitles = doc.metadata.get("subtitles", [])
            if not subtitles:
                continue

            texts = [s["text"] for s in subtitles]
            vectors = self.embeddings.embed_documents(texts)

            cache[chunk_start] = []
            for i, sub in enumerate(subtitles):
                cache[chunk_start].append({
                    "text": sub["text"],
                    "start": sub["start"],
                    "embedding": np.array(vectors[i])
                })

        return cache

# CREATING RETRIEVER
    def create_retriever(self, docs):
        self.vector_store = FAISS.from_documents(docs, self.embeddings)

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

# REFINE TIMESTAMP
    def refine_timestamp(self, doc, query_embedding):
        """
        Given a retrieved chunk and the query embedding,
        find the subtitle with highest cosine similarity
        and return its start time.
        """
        chunk_start = doc.metadata["start"]
        cached_subs = self.subtitle_cache.get(chunk_start)

        if not cached_subs:
            return int(chunk_start)

        best_score = -1
        best_start = chunk_start

        for sub in cached_subs:
            sub_emb = sub["embedding"]
            # cosine similarity
            dot = np.dot(query_embedding, sub_emb)
            norm = np.linalg.norm(query_embedding) * np.linalg.norm(sub_emb)
            if norm > 0:
                score = dot / norm
            else:
                score = 0

            if score > best_score:
                best_score = score
                best_start = sub["start"]

        return int(best_start)


    def get_sources(self, docs, query_embedding):
        sources = []
        seen = set()

        for doc in docs:
            seconds = self.refine_timestamp(doc, query_embedding)

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
        # One query embedding for timestamp refinement
        query_embedding = np.array(self.embeddings.embed_query(question))

        answer = (RAG_PROMPT | self.llm | StrOutputParser()).invoke({
            "context" : context,
            "question" : question
        })

        return{
            "answer" : answer,
            "sources" : self.get_sources(retrieved_docs, query_embedding)
        }
