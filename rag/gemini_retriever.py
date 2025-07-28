#!/usr/bin/env python3

import os
import pandas as pd
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from difflib import SequenceMatcher
import re

load_dotenv()

class GeminiFAQRetriever:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        self.llm = GoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.7,
            max_output_tokens=500
        )
        
        self.faq_data = self.load_faq_data()
        print(f"✅ Loaded {len(self.faq_data)} FAQ entries for Gemini retriever")
        
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question", "user_language"],
            template="""
You are a helpful customer support assistant for a taxi/ride-hailing service. 
Use the following FAQ context to answer the user's question accurately and helpfully.

FAQ Context:
{context}

User Question: {question}
Detected Language: {user_language}

Instructions:
1. Answer in the same language as the user's question
2. Be concise but comprehensive
3. If the exact answer isn't in the FAQ, provide the most relevant information
4. Be friendly and professional
5. If you cannot find relevant information, politely say so and suggest contacting support

Answer:
"""
        )
    
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
    
    def detect_language(self, text):
        try:
            from langdetect import detect
            lang = detect(text)
            return 'Arabic' if lang == 'ar' else 'English'
        except:
            arabic_chars = re.findall(r'[\u0600-\u06FF]', text)
            return 'Arabic' if arabic_chars else 'English'
    
    def similarity(self, a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def find_relevant_context(self, user_question, max_context=5):
        if not self.faq_data:
            return ""
        
        scored_faqs = []
        user_question_clean = re.sub(r'[^\w\s]', '', user_question.lower())
        user_words = set(user_question_clean.split())
        
        for item in self.faq_data:
            question_similarity = self.similarity(user_question_clean, item['question'])
            
            faq_words = set((item['question'] + ' ' + item['answer']).lower().split())
            word_overlap = len(user_words.intersection(faq_words)) / max(len(user_words), 1)
            
            combined_score = (question_similarity * 0.6) + (word_overlap * 0.4)
            
            scored_faqs.append({
                'score': combined_score,
                'question': item['question'],
                'answer': item['answer']
            })
        
        scored_faqs.sort(key=lambda x: x['score'], reverse=True)
        top_faqs = scored_faqs[:max_context]
        
        context_parts = []
        for i, faq in enumerate(top_faqs, 1):
            if faq['score'] > 0.1:
                context_parts.append(f"FAQ {i}:\nQ: {faq['question']}\nA: {faq['answer']}")
        
        return "\n\n".join(context_parts)
    
    def get_answer(self, user_question):
        try:
            user_language = self.detect_language(user_question)
            
            context = self.find_relevant_context(user_question)
            
            if not context:
                return "I'm sorry, I couldn't find relevant information in our FAQ. Please contact our support team for assistance."
            
            prompt = self.prompt_template.format(
                context=context,
                question=user_question,
                user_language=user_language
            )
            
            response = self.llm.invoke(prompt)
            
            if hasattr(response, 'content'):
                return response.content.strip()
            else:
                return str(response).strip()
            
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            return self.fallback_simple_answer(user_question)
    
    def fallback_simple_answer(self, user_question):
        if not self.faq_data:
            return "Sorry, I don't have access to the knowledge base right now."
        
        best_match = None
        best_score = 0
        threshold = 0.3
        
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
            return best_match['answer']
        else:
            return "I'm sorry, I couldn't find a relevant answer to your question. Could you please rephrase or ask something else?"

def test_gemini_retriever():
    try:
        retriever = GeminiFAQRetriever()
        
        test_questions = [
            "How do I book a taxi?",
            "What payment methods do you accept?",
            "كيف يمكنني حجز سيارة؟",
            "How much does a ride cost?"
        ]
        
        print("🧪 Testing Gemini FAQ Retriever:")
        print("=" * 50)
        
        for question in test_questions:
            print(f"\nQ: {question}")
            answer = retriever.get_answer(question)
            print(f"A: {answer}")
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_gemini_retriever() 