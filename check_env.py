#!/usr/bin/env python3

"""
Simple script to check environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Checking Environment Variables")
print("=" * 50)

# Check Gemini API Key
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    # Mask the key for security
    masked_key = gemini_key[:8] + "*" * (len(gemini_key) - 12) + gemini_key[-4:] if len(gemini_key) > 12 else "***masked***"
    print(f"✅ GEMINI_API_KEY found: {masked_key}")
    
    # Check if it's the placeholder
    if gemini_key.startswith("your_") or gemini_key.startswith("AIza-your"):
        print("❌ API key appears to be a placeholder. Please update with your real key.")
    elif len(gemini_key) < 30:
        print("❌ API key seems too short. Please check your key.")
    else:
        print("✅ API key format looks correct")
else:
    print("❌ GEMINI_API_KEY not found")

# Check other variables
mongo_uri = os.getenv("MONGO_URI")
if mongo_uri:
    print(f"✅ MONGO_URI found: {mongo_uri[:20]}...")
else:
    print("⚠️  MONGO_URI not found (optional)")

print("\n" + "=" * 50)
print("📁 Current working directory:", os.getcwd())
print("📄 Files in current directory:")
for file in os.listdir("."):
    if file.startswith(".env"):
        print(f"  ✅ {file}")
    elif file.endswith((".py", ".csv", ".md")):
        print(f"  📄 {file}")

print("\n" + "=" * 50)
print("🔧 To fix issues:")
print("1. Make sure you have a .env file in the project root")
print("2. The .env file should contain: GEMINI_API_KEY=your-actual-gemini-key-here")
print("3. Make sure there are no extra spaces or quotes around the key")
print("4. Get your Gemini API key from: https://makersuite.google.com/app/apikey") 