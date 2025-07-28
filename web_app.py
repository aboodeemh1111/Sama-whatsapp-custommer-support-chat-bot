#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify
import pandas as pd
from difflib import SequenceMatcher
import re
import os
from dotenv import load_dotenv

try:
    from rag.gemini_retriever import GeminiFAQRetriever
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

load_dotenv()

app = Flask(__name__)

class WebChatBot:
    def __init__(self):
        self.faq_data = self.load_faq_data()
        self.gemini_retriever = None
        
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
        api_key = os.getenv("GEMINI_API_KEY")
        return api_key and not api_key.startswith("your_") and len(api_key) > 10
    
    def load_faq_data(self):
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
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def simple_find_answer(self, user_question,