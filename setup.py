#!/usr/bin/env python3
"""
Setup script for the Taxi Customer Support Chatbot
Run this script to initialize the RAG knowledge base and test all components
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Check if all required environment variables are set"""
    load_dotenv()
    
    required_vars = [
        "OPENAI_API_KEY",
        "MONGO_URI", 
        "META_TOKEN",
        "META_PHONE_NUMBER_ID",
        "WEBHOOK_VERIFY_TOKEN"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith("your_") or value == "":
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing or invalid environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease update your .env file with the correct values.")
        print("Example .env file:")
        print("OPENAI_API_KEY=sk-...")
        print("MONGO_URI=mongodb://localhost:27017/taxi_chatbot")
        print("META_TOKEN=your_whatsapp_token")
        print("META_PHONE_NUMBER_ID=your_phone_number_id")
        print("WEBHOOK_VERIFY_TOKEN=your_custom_verify_token")
        return False
    
    print("✅ All environment variables are set!")
    return True

def check_openai_connection():
    """Test OpenAI API connection"""
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
            max_tokens=10
        )
        
        response = llm.invoke("Hello")
        print("✅ OpenAI API connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        print("Please check your OPENAI_API_KEY in the .env file")
        return False

def create_rag_index():
    """Create the RAG knowledge base index"""
    try:
        print("🔄 Creating RAG knowledge base from bot-data.csv...")
        
        # Import and run the training script
        from rag.train_rag import create_faq_index
        
        success = create_faq_index()
        if success:
            print("✅ RAG knowledge base created successfully!")
            return True
        else:
            print("❌ Failed to create RAG knowledge base")
            return False
            
    except Exception as e:
        print(f"❌ Error creating RAG index: {e}")
        return False

def test_components():
    """Test if all components are working"""
    try:
        print("🔄 Testing system components...")
        
        # Test database connection
        try:
            from db.mongodb import mongodb
            # Try a simple operation
            mongodb.conversations.find_one()
            print("✅ Database connection successful")
        except Exception as e:
            print(f"⚠️  Database connection issue: {e}")
            print("   Make sure MongoDB is running")
        
        # Test language detection
        from utils.language import detect_language
        lang_en = detect_language("Hello, how are you?")
        lang_ar = detect_language("مرحبا، كيف حالك؟")
        print(f"✅ Language detection working (EN: {lang_en}, AR: {lang_ar})")
        
        # Test RAG retriever
        from rag.retriever import search_knowledge_base
        result = search_knowledge_base("How do I book a taxi?")
        if len(result) > 20:  # Reasonable response length
            print("✅ RAG retriever working")
        else:
            print("⚠️  RAG retriever may have issues")
        
        # Test agent
        from agents.customer_agent import run_agent
        response = run_agent("test_user_setup", "Hello")
        if len(response) > 10:
            print("✅ Customer agent working")
        else:
            print("⚠️  Customer agent may have issues")
        
        print("🎉 Component testing completed!")
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def display_next_steps():
    """Display next steps for the user"""
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("=" * 60)
    print("\n📋 Next steps:")
    print("1. 🚀 Start the server:")
    print("   python main.py")
    print("\n2. 🌐 Expose your local server (in another terminal):")
    print("   ngrok http 8000")
    print("\n3. ⚙️  Configure WhatsApp webhook:")
    print("   - Go to Meta Developer Console")
    print("   - Set webhook URL: https://your-ngrok-url.ngrok.io/webhook")
    print("   - Set verify token: (value from your .env file)")
    print("\n4. 🧪 Test your chatbot:")
    print("   - Send a message to your WhatsApp Business number")
    print("   - Or test via: http://localhost:8000/chat")
    print("\n5. 📊 Monitor logs:")
    print("   - Check the console for incoming messages and responses")
    print("\n💡 Troubleshooting:")
    print("   - Check .env file for correct API keys")
    print("   - Ensure MongoDB is running")
    print("   - Verify ngrok is exposing port 8000")
    print("   - Test with: curl http://localhost:8000/health")

def main():
    """Main setup function"""
    print("🚀 Setting up WhatsApp Customer Support Chatbot")
    print("Using latest OpenAI API (v1.97.1) and LangChain (v0.3.28)")
    print("=" * 60)
    
    # Step 1: Check environment
    print("\n📋 Step 1: Checking environment variables...")
    if not check_environment():
        sys.exit(1)
    
    # Step 2: Test OpenAI connection
    print("\n🔌 Step 2: Testing OpenAI API connection...")
    if not check_openai_connection():
        sys.exit(1)
    
    # Step 3: Create RAG index
    print("\n🧠 Step 3: Creating knowledge base...")
    if not create_rag_index():
        print("⚠️  RAG index creation failed, but continuing...")
    
    # Step 4: Test components
    print("\n🧪 Step 4: Testing system components...")
    test_components()  # Continue even if some tests fail
    
    # Step 5: Display next steps
    display_next_steps()

if __name__ == "__main__":
    main() 