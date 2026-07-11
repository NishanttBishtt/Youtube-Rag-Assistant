from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag import VideoRAG

app = FastAPI(
    title='youtube rag API',
    version='1.0.0'
) 

class AskRequest(BaseModel):
    video_id : str
    question : str

video_cache = {}

@app.post("/ask")
def ask(request : AskRequest):
    try:
        if request.video_id not in video_cache:
            video_cache[request.video_id] = VideoRAG(request.video_id)

        rag = video_cache[request.video_id]
        result = rag.ask(request.question)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = str(e)
        )
