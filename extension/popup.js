document.addEventListener('DOMContentLoaded', () => {
  const videoIdEl = document.getElementById('videoId');
  const statusDotEl = document.getElementById('statusDot');
  const questionInput = document.getElementById('questionInput');
  const askBtn = document.getElementById('askBtn');
  const loader = document.getElementById('loader');
  const errorBox = document.getElementById('errorBox');
  const chatHistory = document.getElementById('chatHistory');
  const clearBtn = document.getElementById('clearBtn');

  let activeTabId = null;
  let activeVideoId = null;
  let chatItems = [];

  // Helper: HTML Escaping to prevent HTML injection
  function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
      tag => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
        '"': '&quot;'
      }[tag] || tag)
    );
  }

  // Load chat history from chrome local storage
  async function loadChat(videoId) {
    try {
      const result = await chrome.storage.local.get(videoId);
      return result[videoId] || [];
    } catch (e) {
      console.error('Error loading chat:', e);
      return [];
    }
  }

  // Save chat history to chrome local storage
  async function saveChat(videoId, chat) {
    try {
      await chrome.storage.local.set({
        [videoId]: chat
      });
    } catch (e) {
      console.error('Error saving chat:', e);
    }
  }

  // 1. Get current active tab and extract YouTube Video ID
  chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
    if (!tabs || tabs.length === 0) {
      showError('Could not find active browser tab.');
      return;
    }

    const tab = tabs[0];
    activeTabId = tab.id;
    const url = tab.url;

    if (!url) {
      showError('Please navigate to a YouTube video.');
      return;
    }

    const videoId = getYouTubeVideoId(url);

    if (videoId) {
      activeVideoId = videoId;
      videoIdEl.innerText = `Video ID: ${videoId}`;
      statusDotEl.classList.add('active');
      questionInput.removeAttribute('disabled');
      askBtn.removeAttribute('disabled');
      questionInput.focus();

      // Load saved chat history
      chatItems = await loadChat(videoId);
      renderChatHistory();
    } else {
      showError('No active YouTube video detected. Please open a YouTube video page.');
    }
  });

  // 2. Extract video ID helper
  function getYouTubeVideoId(url) {
    try {
      const urlObj = new URL(url);
      if (urlObj.hostname.includes('youtube.com')) {
        return urlObj.searchParams.get('v');
      } else if (urlObj.hostname.includes('youtu.be')) {
        // e.g. https://youtu.be/dQw4w9WgXcQ -> pathname is "/dQw4w9WgXcQ"
        return urlObj.pathname.substring(1);
      }
    } catch (e) {
      console.error('URL parsing error:', e);
    }
    return null;
  }

  // 3. UI Error Helper
  function showError(message) {
    errorBox.innerText = message;
    errorBox.style.display = 'block';
    loader.style.display = 'none';
    chatHistory.innerHTML = '';
    clearBtn.style.display = 'none';
  }

  // 4. Handle Submit action
  async function handleAsk() {
    const question = questionInput.value.trim();
    if (!question || !activeVideoId) return;

    // Reset view states
    errorBox.style.display = 'none';
    loader.style.display = 'flex';
    questionInput.disabled = true;
    askBtn.disabled = true;

    // Scroll to show loader
    window.scrollTo(0, document.body.scrollHeight);

    try {
      const response = await fetch('http://127.0.0.1:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          video_id: activeVideoId,
          question: question
        })
      });

      if (!response.ok) {
        let errDetail = 'Failed to get answer from backend.';
        try {
          const errData = await response.json();
          errDetail = errData.detail || errDetail;
        } catch (_) {}
        throw new Error(errDetail);
      }

      const data = await response.json();
      
      // Save query response to history list
      chatItems.push({
        question: question,
        answer: data.answer,
        sources: data.sources || []
      });
      await saveChat(activeVideoId, chatItems);

      // Render updated list
      renderChatHistory();

      // Clear input
      questionInput.value = '';
    } catch (error) {
      showError(error.message || 'Server error. Is your FastAPI server running?');
    } finally {
      questionInput.disabled = false;
      askBtn.disabled = false;
      loader.style.display = 'none';
      questionInput.focus();
    }
  }

  // 5. Render list of chat history elements
  function renderChatHistory() {
    chatHistory.innerHTML = '';

    if (chatItems.length > 0) {
      clearBtn.style.display = 'block';

      chatItems.forEach(item => {
        // A. Question bubble
        const qBubble = document.createElement('div');
        qBubble.className = 'chat-bubble-user';
        qBubble.innerHTML = `
          <div class="question-prefix">Question</div>
          <div class="question-content">${escapeHTML(item.question)}</div>
        `;
        chatHistory.appendChild(qBubble);

        // B. Answer card
        const aCard = document.createElement('div');
        aCard.className = 'card chat-answer-card';

        const ansSection = document.createElement('div');
        ansSection.className = 'answer-section';
        ansSection.innerHTML = `
          <div class="section-title">Answer</div>
          <div class="answer-text">${escapeHTML(item.answer)}</div>
        `;
        aCard.appendChild(ansSection);

        // Sources section (only if present)
        if (item.sources && item.sources.length > 0) {
          const sourcesSec = document.createElement('div');
          sourcesSec.className = 'sources-section';
          sourcesSec.innerHTML = `<div class="section-title">Jump to Sources</div>`;

          const sourcesList = document.createElement('div');
          sourcesList.className = 'sources-list';

          item.sources.forEach(src => {
            const btn = document.createElement('button');
            btn.className = 'timestamp-btn';
            btn.innerText = src.timestamp;
            btn.title = `Jump to ${src.timestamp}`;
            btn.addEventListener('click', () => {
              chrome.tabs.sendMessage(activeTabId, {
                action: 'seek',
                seconds: src.seconds
              });
            });
            sourcesList.appendChild(btn);
          });

          sourcesSec.appendChild(sourcesList);
          aCard.appendChild(sourcesSec);
        }

        chatHistory.appendChild(aCard);
      });
    } else {
      clearBtn.style.display = 'none';
    }

    // Scroll to latest message at bottom
    setTimeout(() => {
      window.scrollTo(0, document.body.scrollHeight);
    }, 50);
  }

  // 6. Clear history action
  clearBtn.addEventListener('click', async () => {
    if (!activeVideoId) return;
    if (confirm('Are you sure you want to clear chat history for this video?')) {
      chatItems = [];
      await saveChat(activeVideoId, []);
      renderChatHistory();
    }
  });

  // 7. Event Listeners
  askBtn.addEventListener('click', handleAsk);
  questionInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  });
});