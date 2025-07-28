#!/usr/bin/env python3

import pandas as pd
from difflib import SequenceMatcher
import re

class SimpleChatBot:
    def __init__(self):
        self.faq_data = self.load_faq_data()
        print(f"✅ Loaded {len(self.faq_data)} FAQ entries")
    
    def load_faq_data(self):
        try:
            df = pd.read_csv('bot-data.csv')
            print(f"📊 CSV columns: {list(df.columns)}")
            
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
    
    def find_best_answer(self, user_question, threshold=0.3):
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
            return f"{best_match['answer']}\n\n(Confidence: {best_score:.2f})"
        else:
            return "I'm sorry, I couldn't find a relevant answer to your question. Could you please rephrase or ask something else?"
    
    def chat(self):
        print("\n🤖 Simple WhatsApp Customer Support Bot")
        print("=" * 50)
        print("Type 'quit' or 'exit' to end the conversation")
        print("Type 'help' to see available commands")
        print()
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Bot: Goodbye! Have a great day! 👋")
                break
            elif user_input.lower() == 'help':
                print("Bot: Available commands:")
                print("  - Ask any question about our taxi service")
                print("  - Type 'quit' or 'exit' to end")
                print("  - Type 'stats' to see knowledge base stats")
                continue
            elif user_input.lower() == 'stats':
                print(f"Bot: I have {len(self.faq_data)} FAQ entries in my knowledge base.")
                continue
            elif not user_input:
                print("Bot: Please ask 