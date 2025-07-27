#!/usr/bin/env python3

"""
Web interface for the WhatsApp Customer Support Chatbot
Works with both simple text matching and OpenAI-powered responses
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
from difflib import SequenceMatcher
import re
import os
from dotenv import load_dotenv

# Try to import Gemini components (optional)
try:
    from rag.gemini_retriever import GeminiFAQRetriever
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

load_dotenv()

app = Flask(__name__)

class WebChatBot:
    def __init__(self):
        """Initialize the web chatbot"""
        self.faq_data = self.load_faq_data()
        self.gemini_retriever = None
        
        # Try to initialize Gemini retriever if available and API key is set
        if GEMINI_AVAILABLE and self.is_gemini_key_valid():
            try:
                self.gemini_retriever = GeminiFAQRetriever()
                print("✅ Gemini-powered retriever initialized")
            except Exception as e:
                print(f"⚠️ Gemini retriever failed to initialize: {e}")
                print("📝 Falling back to simple text matching")
        else:
            print("📝 Using simple text matching (Gemini not available or API key not set)")
    
    def is_gemini_key_valid(self):
        """Check if Gemini API key is valid"""
        api_key = os.getenv("GEMINI_API_KEY")
        return api_key and not api_key.startswith("your_") and len(api_key) > 10
    
    def load_faq_data(self):
        """Load FAQ data from CSV file"""
        try:
            df = pd.read_csv('bot-data.csv')
            faq_data = []
            
            for _, row in df.iterrows():
                question = ""
                answer = ""
                
                for col in df.columns:
                    col_lower = col.lower().strip()
                    if 'question' in col_lower or 'q' == col_lower:
                        question = str(row[col]).strip()
                    elif 'answer' in col_lower or 'a' == col_lower or 'response' in col_lower:
                        answer = str(row[col]).strip()
                
                if question and answer and question != 'nan' and answer != 'nan':
                    faq_data.append({
                        'question': question,
                        'answer': answer
                    })
            
            return faq_data
        except Exception as e:
            print(f"❌ Error loading FAQ data: {e}")
            return []
    
    def similarity(self, a, b):
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def simple_find_answer(self, user_question, threshold=0.3):
        """Find answer using simple text matching"""
        if not self.faq_data:
            return "Sorry, I don't have access to the knowledge base right now."
        
        best_match = None
        best_score = 0
        
        user_question_clean = re.sub(r'[^\w\s]', '', user_question.lower())
        
        for item in self.faq_data:
            question_similarity = self.similarity(user_question_clean, item['question'])
            
            user_words = set(user_question_clean.split())
            faq_words = set((item['question'] + ' ' + item['answer']).lower().split())
            word_overlap = len(user_words.intersection(faq_words)) / max(len(user_words), 1)
            
            combined_score = (question_similarity * 0.7) + (word_overlap * 0.3)
            
            if combined_score > best_score and combined_score > threshold:
                best_score = combined_score
                best_match = item
        
        if best_match:
            return {
                'answer': best_match['answer'],
                'confidence': best_score,
                'method': 'Simple Text Matching'
            }
        else:
            return {
                'answer': "I'm sorry, I couldn't find a relevant answer to your question. Could you please rephrase or ask something else?",
                'confidence': 0,
                'method': 'Simple Text Matching'
            }
    
    def get_response(self, user_question):
        """Get response using available method (Gemini or simple matching)"""
        if self.gemini_retriever:
            try:
                response = self.gemini_retriever.get_answer(user_question)
                return {
                    'answer': response,
                    'confidence': 0.95,  # High confidence for Gemini
                    'method': 'Google Gemini'
                }
            except Exception as e:
                print(f"Gemini error: {e}")
                return self.simple_find_answer(user_question)
        else:
            return self.simple_find_answer(user_question)

# Initialize the chatbot
chatbot = WebChatBot()

@app.route('/')
def home():
    """Main chat interface"""
    return render_template('chat.html', 
                         total_faqs=len(chatbot.faq_data),
                         gemini_available=chatbot.gemini_retriever is not None)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """API endpoint for chat messages"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'error': 'Empty message',
                'response': 'Please ask me something!'
            })
        
        # Handle special commands
        if user_message.lower() in ['help', '/help']:
            return jsonify({
                'response': 'I can help you with questions about our taxi service. Ask me anything!',
                'method': 'Command',
                'confidence': 1.0
            })
        
        if user_message.lower() in ['stats', '/stats']:
            return jsonify({
                'response': f'I have {len(chatbot.faq_data)} FAQ entries in my knowledge base. Using {"Google Gemini" if chatbot.gemini_retriever else "Simple Text Matching"}.',
                'method': 'Command',
                'confidence': 1.0
            })
        
        # Get response from chatbot
        result = chatbot.get_response(user_message)
        
        return jsonify({
            'response': result['answer'],
            'confidence': result['confidence'],
            'method': result['method']
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'response': 'Sorry, something went wrong. Please try again.'
        })

@app.route('/api/status')
def status():
    """API endpoint to check system status"""
    return jsonify({
        'status': 'running',
        'total_faqs': len(chatbot.faq_data),
        'gemini_available': chatbot.gemini_retriever is not None,
        'method': 'Google Gemini' if chatbot.gemini_retriever else 'Simple Text Matching'
    })

if __name__ == '__main__':
    print("🚀 Starting WhatsApp Customer Support Chatbot Web Interface")
    print("=" * 60)
    print(f"📊 Loaded {len(chatbot.faq_data)} FAQ entries")
    print(f"🤖 Using: {'Google Gemini' if chatbot.gemini_retriever else 'Simple Text Matching'}")
    print("🌐 Open http://localhost:5000 in your browser")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 