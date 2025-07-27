#!/usr/bin/env python3
"""
Test script to verify all system components work correctly
"""

import os
from dotenv import load_dotenv

def test_environment():
    """Test if environment variables are set"""
    load_dotenv()
    
    required_vars = ["OPENAI_API_KEY"]
    optional_vars = ["MONGO_URI", "META_TOKEN", "META_PHONE_NUMBER_ID", "WEBHOOK_VERIFY_TOKEN"]
    
    print("🔍 Testing Environment Variables:")
    print("=" * 50)
    
    missing_required = []
    for var in required_vars:
        value = os.getenv(var)
        if value and not value.startswith("your_") and len(value) > 10:
            print(f"✅ {var}: Set correctly")
        else:
            print(f"❌ {var}: Missing or invalid")
            missing_required.append(var)
    
    for var in optional_vars:
        value = os.getenv(var)
        if value and not value.startswith("your_"):
            print(f"✅ {var}: Set")
        else:
            print(f"⚠️  {var}: Not set (optional for testing)")
    
    return len(missing_required) == 0

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n🔌 Testing OpenAI Connection:")
    print("=" * 50)
    
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
            max_tokens=10
        )
        
        response = llm.invoke("Say 'test'")
        print("✅ OpenAI API connection successful!")
        print(f"   Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        return False

def test_database_connection():
    """Test MongoDB connection"""
    print("\n🗄️ Testing Database Connection:")
    print("=" * 50)
    
    try:
        from db.mongodb import mongodb
        
        if mongodb.client:
            print("✅ MongoDB connection successful!")
            print(f"   Database: {mongodb.db.name}")
            return True
        else:
            print("⚠️  MongoDB not connected (will work without persistence)")
            return True
            
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("   The system will work without message persistence")
        return True

def test_language_detection():
    """Test language detection"""
    print("\n🌐 Testing Language Detection:")
    print("=" * 50)
    
    try:
        from utils.language import detect_language
        
        # Test English
        lang_en = detect_language("Hello, how are you?")
        print(f"✅ English detection: '{lang_en}'")
        
        # Test Arabic
        lang_ar = detect_language("مرحبا، كيف حالك؟")
        print(f"✅ Arabic detection: '{lang_ar}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Language detection failed: {e}")
        return False

def test_faq_retriever():
    """Test FAQ retrieval system"""
    print("\n🧠 Testing FAQ Retrieval System:")
    print("=" * 50)
    
    try:
        from rag.retriever import search_knowledge_base
        
        # Test English query
        result_en = search_knowledge_base("How do I book a taxi?")
        print(f"✅ English FAQ query successful!")
        print(f"   Response: {result_en[:100]}...")
        
        # Test Arabic query
        result_ar = search_knowledge_base("كيف أحجز تاكسي؟")
        print(f"✅ Arabic FAQ query successful!")
        print(f"   Response: {result_ar[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ FAQ retrieval failed: {e}")
        return False

def test_customer_agent():
    """Test customer support agent"""
    print("\n🤖 Testing Customer Support Agent:")
    print("=" * 50)
    
    try:
        from agents.customer_agent import run_agent
        
        # Test with a simple query
        response = run_agent("test_user", "Hello, I need help")
        print(f"✅ Customer agent working!")
        print(f"   Response: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Customer agent failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing WhatsApp Customer Support Chatbot System")
    print("=" * 60)
    
    tests = [
        ("Environment Setup", test_environment),
        ("OpenAI Connection", test_openai_connection),
        ("Database Connection", test_database_connection),
        ("Language Detection", test_language_detection),
        ("FAQ Retrieval", test_faq_retriever),
        ("Customer Agent", test_customer_agent),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your system is ready to go!")
        print("\nNext steps:")
        print("1. Run: python main.py")
        print("2. Test at: http://localhost:8000/chat")
        print("3. API docs: http://localhost:8000/docs")
    else:
        print(f"\n⚠️  {len(results) - passed} tests failed. Please check the errors above.")
        if not results[0][1]:  # Environment test failed
            print("\n🔑 Make sure to create your .env file with:")
            print("OPENAI_API_KEY=your_actual_openai_key_here")

if __name__ == "__main__":
    main() 