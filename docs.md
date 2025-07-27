# WhatsApp Customer Support Chatbot Development Guide

This documentation is a guide for developers using **Cursor** or any IDE to implement a WhatsApp-based customer support chatbot for a taxi app company using:

- **LangGraph / LangChain** (Agent + Tools)
- **MongoDB** (Conversation memory + storage)
- **FastAPI + Pydantic** (Backend)
- **RAG Tool** (FAQ answer retrieval)
- **Multi-language support** (LangDetect)
- **OpenAI API** (for AI responses and embedding)
- **Meta Cloud API** (WhatsApp integration)

---

## 📁 Project Structure

```bash
/taxi_chatbot/
├── main.py                     # FastAPI entrypoint
├── agents/
│   └── customer_agent.py       # Agent logic with memory & tools
├── rag/
│   └── retriever.py            # RAG (FAQ-based answering)
├── db/
│   └── mongodb.py              # MongoDB database client
├── models/
│   └── schemas.py              # Pydantic models
├── utils/
│   └── language.py             # Language detection
└── requirements.txt
```

---

## 1. Setup Environment

### Install Required Libraries

```bash
pip install fastapi uvicorn pymongo pydantic langchain openai faiss-cpu langdetect python-dotenv
```

### Setup Environment Variables (e.g., .env)

```
OPENAI_API_KEY=your_openai_key
MONGO_URI=mongodb://localhost:27017/
META_TOKEN=your_meta_token
META_PHONE_NUMBER_ID=your_number_id
```

---

## 2. MongoDB Integration

### db/mongodb.py

- `get_user_history(user_id)` – fetch chat history for memory
- `save_message(user_id, msg, response)` – store chat messages

---

## 3. Language Detection

### utils/language.py

Use `langdetect` to identify user language:

```python
def detect_language(text):
    return detect(text)
```

---

## 4. Retrieval-Augmented Generation (RAG)

### rag/retriever.py

- Load a FAISS vector index from FAQ documents.
- Embed using OpenAI Embeddings.
- Search relevant context to answer user questions.

```python
def search_knowledge_base(query: str):
    vectorstore = FAISS.load_local("taxi_faq_index", OpenAIEmbeddings())
    retriever = vectorstore.as_retriever()
    qa = RetrievalQA.from_chain_type(llm=ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY")), retriever=retriever)
    return qa.run(query)
```

---

## 5. LangChain Agent with Memory

### agents/customer_agent.py

```python
def run_agent(user_id, message):
    history = get_user_history(user_id)
    memory = ConversationBufferMemory(return_messages=True)
    memory.chat_memory.add_user_message("\n".join(history))

    tools = [
        Tool(name="TaxiFAQSearch", func=search_knowledge_base, description="Taxi FAQ tool")
    ]

    agent = initialize_agent(tools, ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY")), agent="zero-shot-react-description", memory=memory)
    return agent.run(message)
```

---

## 6. FastAPI Webhook

### main.py

Handles WhatsApp incoming messages:

```python
@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    data = await request.json()
    msg = data['message']['text']
    user_id = data['user']['id']

    lang = detect_language(msg)
    response = run_agent(user_id, msg)
    save_message(user_id, msg, response)

    # Send message via Meta Cloud API
    send_whatsapp_reply_meta(user_id, response)
    return {"reply": response}
```

---

## 7. WhatsApp API Integration

### Meta Cloud API Example

```python
import requests
import os

def send_whatsapp_reply_meta(to, message):
    url = f"https://graph.facebook.com/v18.0/{os.getenv('META_PHONE_NUMBER_ID')}/messages"
    headers = {
        "Authorization": f"Bearer {os.getenv('META_TOKEN')}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    requests.post(url, headers=headers, json=payload)
```

---

## 8. Pydantic Models

### models/schemas.py

```python
class ChatRequest(BaseModel):
    user_id: str
    message: str
```

---

## 9. RAG Training Notes

- Collect your internal taxi FAQ documents.
- Convert them into chunks using LangChain.
- Use OpenAI Embeddings to embed.
- Store in FAISS vector store locally.

---

## 10. Deployment

- Use **ngrok** to test webhooks locally.
- Host on **Render**, **Railway**, or **EC2**.
- Add background task support for large response handling if needed.

---

## ✅ Summary

| Feature            | Tech Used            |
| ------------------ | -------------------- |
| Agent Reasoning    | LangChain Agent      |
| Memory             | MongoDB + LangChain  |
| Multilingual       | LangDetect           |
| Answer Retrieval   | FAISS + RAG + OpenAI |
| API Layer          | FastAPI + Pydantic   |
| Messaging Channel  | Meta Cloud API       |
| AI/Embedding Model | OpenAI API           |

---

### ⚙️ Next Steps for Cursor Users:

- Clone the repo
- Set up `.env`
- Run FAISS indexing for FAQs
- Start FastAPI locally
- Test WhatsApp webhook with ngrok
- Iterate module by module inside Cursor

---

If you need help generating the FAISS index or API credentials setup, reach out to your lead or platform support.
