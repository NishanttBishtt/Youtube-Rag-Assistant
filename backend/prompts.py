from langchain_core.prompts import PromptTemplate

RAG_PROMPT = PromptTemplate(
    template="""
    You are a helpful AI assistant.

    Answer the user's question using ONLY the transcript context.

    Provide a clear explanation.

    Do NOT invent information.

    If the answer is not present, say:
    "I couldn't find the answer in the current video's transcript."

    Transcript:
    {context}

    Question:
    {question}

    Answer:
    """,
    input_variables=["context", "question"]
)