# WhatsApp Customer Support Chatbot

A sophisticated WhatsApp chatbot for taxi app customer support using LangChain, OpenAI, MongoDB, and Meta Cloud API.

## Features

- 🤖 **AI-Powered Responses** using OpenAI GPT-3.5
- 🔍 **RAG (Retrieval-Augmented Generation)** for accurate FAQ answers
- 🌐 **Multi-language Support** (Arabic & English)
- 💾 **Conversation Memory** with MongoDB
- 📱 **WhatsApp Integration** via Meta Cloud API
- 🚀 **FastAPI Backend** with async support

## Quick Start

### 1. Clone and Install

```bash
git clone <your-repo>
cd taxi_chatbot
pip install -r requirements.txt
```

### 2. Environment Setup

Copy `.env` file and update with your API keys:

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

Required environment variables:

- `OPENAI_API_KEY` - Your OpenAI API key
- `MONGO_URI` - MongoDB connection string
- `META_TOKEN` - WhatsApp Business API token
- `META_PHONE_NUMBER_ID` - Your WhatsApp phone number ID
- `WEBHOOK_VERIFY_TOKEN` - Custom token for webhook verification

### 3. Initialize the System

```bash
python setup.py
```

This will:

- ✅ Check your environment variables
- 🔄 Create RAG knowledge base from `bot-data.csv`
- 🧪 Test all components

### 4. Start the Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### 5. Setup WhatsApp Webhook

1. **Expose your local server:**

   ```bash
   ngrok http 8000
   ```

2. **Configure webhook in Meta Developer Console:**
   - Webhook URL: `https://your-ngrok-url.ngrok.io/webhook`
   - Verify Token: (use the value from your `.env` file)

## API Endpoints

- `GET /` - Health check
- `GET /webhook` - WhatsApp webhook verification
- `POST /webhook` - WhatsApp message handling
- `POST /chat` - Direct chat endpoint for testing
- `GET /health` - Service health status

## Project Structure

```
taxi_chatbot/
├── main.py                 # FastAPI application
├── setup.py               # Setup and initialization script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── bot-data.csv          # FAQ data for RAG
├── agents/
│   └── customer_agent.py  # LangChain agent logic
├── rag/
│   ├── retriever.py       # RAG retrieval system
│   └── train_rag.py       # RAG training script
├── db/
│   └── mongodb.py         # Database operations
├── models/
│   └── schemas.py         # Pydantic models
└── utils/
    ├── language.py        # Language detection
    └── whatsapp.py        # WhatsApp API integration
```

## Testing

### Test the Chat Endpoint

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "message": "How do I book a taxi?"}'
```

### Test WhatsApp Integration

Send a message to your WhatsApp Business number after setting up the webhook.

## Deployment

### Local Development

- Use `ngrok` to expose your local server
- Perfect for testing and development

### Production Deployment

- Deploy to **Railway**, **Render**, or **AWS EC2**
- Set up proper environment variables
- Use a production MongoDB instance
- Configure domain and SSL certificates

## FAQ Data Format

The system uses `bot-data.csv` with the following format:

```csv
question,answer
"How do I book a taxi?","Open the app, enter pickup/dropoff locations..."
"هل يمكنني حجز سيارة مسبقًا؟","نعم، اضغط على زر 'الجدولة'..."
```

## Troubleshooting

### Common Issues

1. **"FAISS index not found"**

   - Run `python setup.py` to create the knowledge base

2. **"OpenAI API error"**

   - Check your `OPENAI_API_KEY` in `.env`
   - Ensure you have sufficient API credits

3. **"MongoDB connection failed"**

   - Verify `MONGO_URI` in `.env`
   - Ensure MongoDB is running

4. **"WhatsApp webhook verification failed"**
   - Check `WEBHOOK_VERIFY_TOKEN` matches Meta Console
   - Ensure webhook URL is accessible

### Logs and Debugging

The application logs important events to the console. For production, consider using proper logging configuration.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
