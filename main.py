from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
import os
from dotenv import load_dotenv
from models.schemas import ChatRequest, ChatResponse, WebhookMessage
from agents.customer_agent import run_agent
from utils.whatsapp import send_whatsapp_reply_meta, verify_webhook, parse_whatsapp_message
from utils.language import detect_language

load_dotenv()

app = FastAPI(title="Taxi Customer Support Chatbot", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Taxi Customer Support Chatbot API is running!"}

@app.get("/webhook")
async def verify_webhook_endpoint(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"), 
    hub_verify_token: str = Query(alias="hub.verify_token")
):
    challenge = verify_webhook(hub_mode, hub_verify_token, hub_challenge)
    if challenge:
        return PlainTextResponse(challenge)
    else:
        raise HTTPException(status_code=403, detail="Webhook verification failed")

@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    try:
        data = await request.json()
        print(f"Received webhook data: {data}")
        
        message_data = parse_whatsapp_message(data)
        
        if not message_data:
            return {"status": "no_message"}
        
        user_id = message_data["user_id"]
        user_message = message_data["message"]
        user_name = message_data["user_name"]
        
        print(f"Processing message from {user_name} ({user_id}): {user_message}")
        
        response = run_agent(user_id, user_message)
        
        success = send_whatsapp_reply_meta(user_id, response)
        
        if success:
            return {"status": "message_sent", "response": response}
        else:
            return {"status": "message_failed", "response": response}
            
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    try:
        response = run_agent(chat_request.user_id, chat_request.message)
        language = detect_language(chat_request.message)
        
        return ChatResponse(
            reply=response,
            language=language
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 