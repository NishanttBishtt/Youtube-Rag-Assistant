# 🎥 YouTube RAG Assistant

> An AI-powered Chrome Extension that lets you ask questions about the currently playing YouTube video and instantly jump to the exact timestamp where the answer is discussed.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![LangChain](https://img.shields.io/badge/LangChain-RAG-orange)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20DB-red)
![Chrome Extension](https://img.shields.io/badge/Chrome-Extension-yellow)

---

##  Overview

Long YouTube lectures often contain valuable information, but finding a specific concept can be time-consuming.

**YouTube RAG Assistant** solves this problem by transforming any YouTube video into an AI-powered, searchable knowledge base.

Simply open a YouTube video, launch the Chrome extension, ask a question in natural language, and receive:

- ✅ AI-generated answers
- ✅ Relevant timestamps
- ✅ One-click navigation to the exact moment in the video
- ✅ Persistent chat history for each video

---

##  Features

- 🎥 Automatically detects the currently opened YouTube video
- 💬 Ask natural language questions about the video
- 🧠 Retrieval-Augmented Generation (RAG)
- 🔎 Semantic search using FAISS vector database
- ⏱️ Timestamp-aware answers
- ▶️ Clickable timestamps that seek the currently playing video
- 💾 Per-video persistent chat history
- ⚡ Cached vector stores for faster follow-up questions
- 🐳 Dockerized FastAPI backend

---

##  Architecture

```
Chrome Extension
        │
        ▼
FastAPI Backend
        │
        ▼
YouTube Transcript API
        │
        ▼
Window-based Transcript Chunking
        │
        ▼
HuggingFace Embeddings
        │
        ▼
FAISS Vector Store
        │
        ▼
Retriever
        │
        ▼
HuggingFace LLM
        │
        ▼
Structured JSON Response
        │
        ▼
Chrome Extension UI
```

---

##  Tech Stack

### Backend

- FastAPI
- LangChain
- FAISS
- HuggingFace Embeddings
- HuggingFace Inference API
- YouTube Transcript API
- Python

### Frontend

- Chrome Extension (Manifest V3)
- HTML
- CSS
- JavaScript

### AI

- Retrieval-Augmented Generation (RAG)
- Semantic Search
- Vector Embeddings
- Similarity Retrieval

---

##  Project Structure

```
youtube-rag-assistant/
│
├── backend/
│   ├── app.py
│   ├── rag.py
│   ├── transcript.py
│   ├── prompts.py
│   ├── config.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── extension/
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   ├── content.js
│   └── icons/
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

##  Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/youtube-rag-assistant.git

cd youtube-rag-assistant
```

---

### 2. Configure environment variables

Create a `.env` file inside the backend folder.

```env
HF_TOKEN=your_huggingface_api_token
```

---

### 3. Run using Docker

```bash
docker compose up --build
```

The backend will be available at:

```
http://localhost:8000
```

---

##  Load the Chrome Extension

1. Open Chrome
2. Go to

```
chrome://extensions
```

3. Enable **Developer Mode**
4. Click **Load unpacked**
5. Select the `extension` folder

---

##  Demo

### Ask Questions

> "Explain Backpropagation"

↓

AI generates an answer.

↓

Displays relevant timestamps.

↓

Click a timestamp.

↓

The current YouTube video jumps directly to that moment.

---

##  Future Improvements

- Multi-language transcript support
- Streaming responses
- Video summarization
- Playlist-level RAG
- Cloud deployment
- Chrome Web Store release

---

##  Contributing

Contributions, issues, and feature requests are welcome.

Feel free to fork the repository and submit a pull request.

---

##  License

This project is licensed under the MIT License.

---

## 👨 Author

**Nishant Bisht**

If you found this project useful, consider giving it a ⭐ on GitHub!