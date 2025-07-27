import requests
import os
import json
from typing import Dict, Any

def send_whatsapp_reply_meta(to: str, message: str) -> bool:
    """
    Send a WhatsApp message using Meta Cloud API
    """
    try:
        url = f"https://graph.facebook.com/v18.0/{os.getenv('META_PHONE_NUMBER_ID')}/messages"
        
        headers = {
            "Authorization": f"Bearer {os.getenv('META_TOKEN')}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print(f"Message sent successfully to {to}")
            return True
        else:
            print(f"Failed to send message: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        return False

def verify_webhook(mode: str, token: str, challenge: str) -> str:
    """
    Verify the webhook for WhatsApp
    """
    verify_token = os.getenv("WEBHOOK_VERIFY_TOKEN")
    
    if mode == "subscribe" and token == verify_token:
        print("Webhook verified successfully!")
        return challenge
    else:
        print("Webhook verification failed!")
        return ""

def parse_whatsapp_message(data: Dict[Any, Any]) -> Dict[str, str]:
    """
    Parse incoming WhatsApp webhook data
    """
    try:
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        
        if "messages" in value:
            message = value["messages"][0]
            contact = value["contacts"][0]
            
            return {
                "user_id": message["from"],
                "user_name": contact["profile"]["name"],
                "message": message["text"]["body"],
                "message_id": message["id"],
                "timestamp": message["timestamp"]
            }
    except (KeyError, IndexError) as e:
        print(f"Error parsing WhatsApp message: {e}")
        return {}
    
    return {}