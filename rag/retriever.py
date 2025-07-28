import os
import pandas as pd
import re
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from difflib import SequenceMatcher

load_dotenv()

class FAQRetriever:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=500
        )
        
        self.faq_data = []
        self._load_faq_data()
    
    def _load_faq_data(self):
        try:
            df = pd.read_csv('bot-data.csv')
            self.faq_data = []
            
            for _, row in df.iterrows():
                question = str(row['question']).strip()
                answer = str(row['answer']).strip()
                
                if question != 'nan' and answer != 'nan':
                    self.faq_data.append({
                        'question': question,
                        'answer': answer,
                        'question_lower': question.lower(),
                        'keywords': self._extract_keywords(question)
                    })
            
            print(f"FAQ retriever loaded {len(self.faq_data)} Q&A pairs successfully!")
            
        except Exception as e:
            print(f"Error loading FAQ data: {e}")
            self.faq_data = []
    
    def _extract_keywords(self, text):
        stop_words = {'how', 'what', 'where', 'when', 'why', 'do', 'does', 'can', 'could', 'would', 'should',
                     'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
                     'كيف', 'ماذا', 'أين', 'متى', 'لماذا', 'هل', 'يمكن', 'في', 'على', 'إلى', 'من', 'مع'}
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords
    
    def _calculate_similarity(self, query, faq_item):
        query_lower = query.lower()
        question_lower = faq_item['question_lower']
        
        text_similarity = SequenceMatcher(None, query_lower, question_lower).ratio()
        
        query_keywords = set(self._extract_keywords(query))
        faq_keywords = set(faq_item['keywords'])
        
        if query_keywords and faq_keywords:
            keyword_similarity = len(query_keywords.intersection(faq_keywords)) / len(query_keywords.union(faq_keywords))
        else:
            keyword_similarity = 0
        
        return (text_similarity * 0.6) + (keyword_similarity * 0.4)
    
    def _find_best_matches(self, query, top_k=3):
        if not self.faq_data:
            return []
        
        similarities = []
        for faq_item in self.faq_data:
            similarity = self._calculate_similarity(query, faq_item)
            similarities.append((similarity, faq_item))
        
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        good_matches = [(score, item) for score, item in similarities if score > 0.1]
        
        return good_matches[:top_k]
    
    def search_knowledge_base(self, query: str) -> str:
        try:
            if not self.faq_data:
                return "I'm sorry, but I cannot access the knowledge base right now. Please contact our support team at 920000000."
            
            matches = self._find_best_matches(query)
            
            if not matches:
                if any(word in query.lower() for word in ['مرحبا', 'hello', 'hi', 'السلام']):
                    return "مرحباً بك! كيف يمكنني مساعدتك اليوم؟ / Hello! How can I help you today?"
                else:
                    return "I'm sorry, I don't have specific information about that. Please contact our customer support at 920000000 for assistance. / أعتذر، ليس لدي معلومات محددة حول ذلك. يرجى الاتصال بخدمة العملاء على 920000000."
            
            best_score, best_match = matches[0]
            
            if best_score > 0.5:
                return best_match['answer']
            else:
                context = "\n".join([f"Q: {item['question']}\nA: {item['answer']}" for _, item in matches])
                
                prompt_template = """You are a helpful customer support agent for a taxi app company in Saudi Arabia.
                Based on the following FAQ context, answer the user's question. If you cannot find a direct answer,
                provide helpful general information and suggest contacting support at 920000000.

                Always respond in the same language as the question. If Arabic, respond in Arabic. If English, respond in English.

                FAQ Context:
                {context}

                User Question: {question}

                Helpful Answer:"""
                
                prompt = PromptTemplate(
                    template=prompt_template,
                    input_variables=["context", "question"]
                )
                
                formatted_prompt = prompt.format(context=context, question=query)
                response = self.llm.invoke(formatted_prompt)
                return response.content
            
        except Exception as e:
            print(f"Error searching knowledge base: {e}")
            return "I'm experiencing technical difficulties. Please contact our support team at 920000000. / أواجه صعوبات تقنية. يرجى الاتصال بفريق الدعم على 920000000."

faq_retriever = FAQRetriever()

def search_knowledge_base(query: str) -> str:
    return faq_retriever.search_knowledge_base(query) 