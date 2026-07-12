from youtube_transcript_api import YouTubeTranscriptApi
from langchain_core.documents import Document
from config import WINDOW_SIZE

def fetch_transcript(video_id: str) -> list[Document]:
    """
    Fetches a YouTube transcript and converts it into
    LangChain Documents grouped into time windows.
    """
    try:
        transcript_list = YouTubeTranscriptApi().fetch(video_id, languages=['en'])
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return []

    if not transcript_list:
        return []

    docs = []
    current_text = []
    current_subtitles = []
    window_start = transcript_list[0].start

    for snippet in transcript_list:
        # if current subtitle belongs to current window
        if snippet.start - window_start < WINDOW_SIZE:
            current_text.append(snippet.text)
            current_subtitles.append({"text": snippet.text, "start": snippet.start})
        else:
            if current_text:
                docs.append(
                    Document(
                        page_content=" ".join(current_text),
                        metadata={
                            "start": window_start,
                            "video_id": video_id,
                            "subtitles": current_subtitles
                        }
                    )
                )
            current_text = [snippet.text]
            current_subtitles = [{"text": snippet.text, "start": snippet.start}]
            window_start = snippet.start

    # add last window
    if current_text:
        docs.append(
            Document(
                page_content=" ".join(current_text),
                metadata={
                    "start": window_start,
                    "video_id": video_id,
                    "subtitles": current_subtitles
                }
            )
        )

    return docs


