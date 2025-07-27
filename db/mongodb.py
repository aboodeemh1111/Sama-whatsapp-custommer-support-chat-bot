import os
from pymongo import MongoClient
from typing import List, Dict, Any
from datetime import datetime

class MongoDB:
    def __init__(self):
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        try:
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            # Test the connection
            self.client.server_info()
            
            # Extract database name from URI or use default
            if "mongodb+srv://" in mongo_uri or "mongodb://" in mongo_uri:
                # For Atlas URIs, extract database name or use default
                if "/" in mongo_uri.split("@")[-1]:
                    db_name = mongo_uri.split("/")[-1].split("?")[0]
                    if db_name:
                        self.db = self.client[db_name]
                    else:
                        self.db = self.client.taxi_chatbot
                else:
                    self.db = self.client.taxi_chatbot
            else:
                self.db = self.client.taxi_chatbot
                
            self.conversations = self.db.conversations
            self.messages = self.db.messages
            print(f"✅ Connected to MongoDB: {self.db.name}")
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            print("Please check your MONGO_URI in the .env file")
            # Create a fallback that won't crash the app
            self.client = None
            self.db = None
            self.conversations = None
            self.messages = None

    def get_user_history(self, user_id: str, limit: int = 10) -> List[str]:
        """
        Retrieve chat history for a user to maintain conversation context
        """
        try:
            if not self.messages:
                return []
                
            messages = self.messages.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit * 2)  # Get both user and bot messages
            
            history = []
            for msg in reversed(list(messages)):
                if msg.get("message_type") == "user":
                    history.append(f"User: {msg['content']}")
                else:
                    history.append(f"Assistant: {msg['content']}")
            
            return history[-limit:] if len(history) > limit else history
        except Exception as e:
            print(f"Error fetching user history: {e}")
            return []

    def save_message(self, user_id: str, user_message: str, bot_response: str, language: str = "en"):
        """
        Save both user message and bot response to maintain conversation history
        """
        try:
            if not self.messages or not self.conversations:
                print("MongoDB not connected - messages not saved")
                return
                
            timestamp = datetime.utcnow()
            
            # Save user message
            self.messages.insert_one({
                "user_id": user_id,
                "content": user_message,
                "message_type": "user",
                "language": language,
                "timestamp": timestamp
            })
            
            # Save bot response
            self.messages.insert_one({
                "user_id": user_id,
                "content": bot_response,
                "message_type": "bot",
                "language": language,
                "timestamp": timestamp
            })
            
            # Update conversation summary
            self.conversations.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "last_interaction": timestamp,
                        "language": language
                    },
                    "$inc": {"message_count": 2}
                },
                upsert=True
            )
            
        except Exception as e:
            print(f"Error saving message: {e}")

# Create a global instance
mongodb = MongoDB()

# Convenience functions for backward compatibility
def get_user_history(user_id: str, limit: int = 10) -> List[str]:
    return mongodb.get_user_history(user_id, limit)

def save_message(user_id: str, user_message: str, bot_response: str, language: str = "en"):
    mongodb.save_message(user_id, user_message, bot_response, language) 