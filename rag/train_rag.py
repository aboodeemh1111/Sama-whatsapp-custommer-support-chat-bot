import pandas as pd
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from dotenv import load_dotenv

load_dotenv()

def create_faq_index():
    """
    Create FAISS index from bot-data.csv using latest OpenAI models
    """
    try:
        # Read the CSV file
        df = pd.read_csv('bot-data.csv')
        print(f"Loaded {len(df)} Q&A pairs from bot-data.csv")
        
        # Create documents from Q&A pairs
        documents = []
        for index, row in df.iterrows():
            question = str(row['question']).strip()
            answer = str(row['answer']).strip()
            
            # Skip empty rows
            if not question or not answer or question == 'nan' or answer == 'nan':
                continue
            
            # Create a document that combines question and answer for better retrieval
            content = f"Question: {question}\nAnswer: {answer}"
            doc = Document(
                page_content=content,
                metadata={
                    "question": question,
                    "answer": answer,
                    "id": index,
                    "source": "taxi_faq"
                }
            )
            documents.append(doc)
        
        print(f"Created {len(documents)} valid documents from FAQ data")
        
        if len(documents) == 0:
            print("Error: No valid documents found in the CSV file")
            return False
        
        # Create embeddings using the latest model
        embeddings = OpenAIEmbeddings(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="text-embedding-3-small",  # Latest, cost-effective embedding model
            dimensions=1536  # Optimal dimensions for the model
        )
        
        print("Creating vector embeddings...")
        
        # Create FAISS vector store with improved settings
        vectorstore = FAISS.from_documents(
            documents, 
            embeddings,
            distance_strategy="COSINE"  # Use cosine similarity for better semantic matching
        )
        
        # Save the vector store locally
        vectorstore.save_local("taxi_faq_index")
        
        print("✅ FAISS index created and saved successfully!")
        print(f"📊 Index contains {len(documents)} documents")
        print("🚀 Ready to use with the chatbot!")
        
        return True
        
    except FileNotFoundError:
        print("❌ Error: bot-data.csv file not found!")
        print("Please make sure the bot-data.csv file is in the current directory.")
        return False
    except Exception as e:
        print(f"❌ Error creating FAQ index: {e}")
        return False

def test_retrieval():
    """Test the retrieval system with sample queries"""
    try:
        embeddings = OpenAIEmbeddings(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="text-embedding-3-small"
        )
        
        vectorstore = FAISS.load_local(
            "taxi_faq_index", 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        
        # Test queries
        test_queries = [
            "How do I book a taxi?",
            "كيف أحجز تاكسي؟",
            "What payment methods do you accept?",
            "Cancel my ride"
        ]
        
        print("\n🧪 Testing retrieval system:")
        print("=" * 50)
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            docs = vectorstore.similarity_search(query, k=2)
            for i, doc in enumerate(docs, 1):
                print(f"  Result {i}: {doc.metadata['question'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing retrieval: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Creating FAQ knowledge base...")
    print("=" * 50)
    
    success = create_faq_index()
    
    if success:
        print("\n🧪 Running retrieval tests...")
        test_retrieval()
        print("\n✅ Setup completed successfully!")
    else:
        print("\n❌ Setup failed. Please check the errors above.") 