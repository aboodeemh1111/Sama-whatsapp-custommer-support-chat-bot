#!/usr/bin/env python3

"""
Simple test script to test the chatbot functionality without OpenAI API
Uses simple text matching from the CSV data
"""

import pandas as pd
from difflib import SequenceMatcher
import re

class SimpleChatBot:
    def __init__(self):
        """Initialize the simple chatbot with CSV data"""
        self.faq_data = self.load_faq_data()
        print(f"✅ Loaded {len(self.faq_data)} FAQ entries")
    
    def load_faq_data(self):
        """Load FAQ data from CSV file"""
        try:
            df = pd.read_csv('bot-data.csv')
            print(f"📊 CSV columns: {list(df.columns)}")
            
            # Convert to list of dictionaries for easier processing
            faq_data = []
            for _, row in df.iterrows():
                # Handle different possible column names
                question = ""
                answer = ""
                
                # Try different column name variations
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
    
    def find_best_answer(self, user_question, threshold=0.3):
        """Find the best matching answer for a user question"""
        if not self.faq_data:
            return "Sorry, I don't have access to the knowledge base right now."
        
        best_match = None
        best_score = 0
        
        # Clean user question
        user_question_clean = re.sub(r'[^\w\s]', '', user_question.lower())
        
        for item in self.faq_data:
            # Calculate similarity with the question
            question_similarity = self.similarity(user_question_clean, item['question'])
            
            # Also check if key words from user question are in the FAQ question or answer
            user_words = set(user_question_clean.split())
            faq_words = set((item['question'] + ' ' + item['answer']).lower().split())
            word_overlap = len(user_words.intersection(faq_words)) / max(len(user_words), 1)
            
            # Combined score
            combined_score = (question_similarity * 0.7) + (word_overlap * 0.3)
            
            if combined_score > best_score and combined_score > threshold:
                best_score = combined_score
                best_match = item
        
        if best_match:
            return f"{best_match['answer']}\n\n(Confidence: {best_score:.2f})"
        else:
            return "I'm sorry, I couldn't find a relevant answer to your question. Could you please rephrase or ask something else?"
    
    def chat(self):
        """Start an interactive chat session"""
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
                print("Bot: Please ask me something!")
                continue
            
            # Get response
            response = self.find_best_answer(user_input)
            print(f"Bot: {response}")
            print()

def main():
    """Main function to run the simple test"""
    print("🚀 Starting Simple ChatBot Test")
    print("=" * 50)
    
    # Initialize chatbot
    bot = SimpleChatBot()
    
    if not bot.faq_data:
        print("❌ No FAQ data loaded. Please check your bot-data.csv file.")
        return
    
    # Show some sample questions
    print("\n📋 Sample questions from your knowledge base:")
    for i, item in enumerate(bot.faq_data[:5]):  # Show first 5
        print(f"{i+1}. {item['question'][:80]}...")
    
    if len(bot.faq_data) > 5:
        print(f"... and {len(bot.faq_data) - 5} more questions")
    
    print("\n" + "=" * 50)
    
    # Test with a few sample questions
    test_questions = [
        "How much does a ride cost?",
        "How can I book a taxi?",
        "What are your working hours?",
        "Do you accept credit cards?"
    ]
    
    print("🧪 Testing with sample questions:")
    print("-" * 30)
    
    for question in test_questions:
        print(f"\nQ: {question}")
        answer = bot.find_best_answer(question)
        print(f"A: {answer}")
    
    print("\n" + "=" * 50)
    
    # Start interactive chat
    try:
        bot.chat()
    except KeyboardInterrupt:
        print("\n\nBot: Chat interrupted. Goodbye! 👋")

if __name__ == "__main__":
    main() 