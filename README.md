# WhatsApp Customer Support Chatbot

Hey there! 👋 This is a smart WhatsApp chatbot I built for taxi companies to handle customer support automatically. It's pretty cool - it can chat with customers in both Arabic and English, remember conversations, and actually understand what people are asking about.

The bot uses some neat AI tech like OpenAI's GPT models and has a backup system with Google Gemini, so it's pretty reliable. I've also thrown in a web interface so you can test it out easily.

## What it can do

- Chat intelligently using OpenAI's latest models (no more robotic responses!)
- Search through your FAQ database to give accurate answers
- Handle both Arabic and English conversations seamlessly
- Remember what customers talked about before
- Connect directly to WhatsApp Business
- Fall back gracefully when things go wrong (because they sometimes do)
- Let you test everything through a nice web interface
- Work with multiple AI providers so you're never stuck

## Getting Started

Alright, let's get this thing running! Don't worry, I've made it pretty straightforward.

### Step 1: Get the code

```bash
git clone https://github.com/aboodeemh1111/Sama-whatsapp-custommer-support-chat-bot.git
cd Sama-whatsapp-custommer-support-chat-bot
pip install -r requirements.txt
```

### Step 2: Set up your secrets

You'll need to create a `.env` file (don't worry, I've set it up so it won't accidentally get committed to git). Here's what goes in it:

```bash
OPENAI_API_KEY=your_openai_api_key_here
MONGO_URI=mongodb://localhost:27017/taxi_chatbot
META_TOKEN=your_whatsapp_business_token
META_PHONE_NUMBER_ID=your_phone_number_id
WEBHOOK_VERIFY_TOKEN=your_custom_verify_token
GEMINI_API_KEY=your_gemini_api_key_here
```

Pro tip: You can skip the Gemini key if you want - it's just a backup AI system.

### Step 3: Let the magic happen

```bash
python setup.py
```

This script does all the boring setup work for you:

- Makes sure you didn't miss any important settings
- Builds the AI knowledge base from your FAQ data
- Tests everything to make sure it's working

### Step 4: Fire it up

```bash
python main.py
```

Your bot will be running at `http://localhost:8000`. Pretty neat, right?

### Step 5: Connect to WhatsApp (the fun part!)

First, you'll need to expose your local server to the internet. I recommend ngrok:

```bash
ngrok http 8000
```

Then head over to the Meta Developer Console and set up your webhook:

- Webhook URL: `https://your-ngrok-url.ngrok.io/webhook`
- Verify Token: whatever you put in your `.env` file

And that's it! Your bot should be ready to chat.

## What you can do with it

Once it's running, here are the endpoints you can hit:

- `GET /` - Just a simple "hey, I'm alive" check
- `GET /webhook` - WhatsApp uses this to verify your bot
- `POST /webhook` - Where all the WhatsApp magic happens
- `POST /chat` - Want to test without WhatsApp? Use this
- `GET /health` - Check if everything's still working properly

## How it's organized

I tried to keep things clean and logical. Here's what's where:

```
Sama-whatsapp-custommer-support-chat-bot/
├── main.py                 # The main FastAPI server
├── web_app.py             # A nice web interface for testing
├── setup.py               # Run this first - it sets everything up
├── requirements.txt       # All the Python packages you need
├── bot-data.csv          # Your FAQ data goes here
├── agents/
│   └── customer_agent.py  # The brain of the operation
├── rag/
│   ├── retriever.py       # Smart FAQ searching
│   ├── train_rag.py       # Builds the AI knowledge base
│   └── gemini_retriever.py # Backup AI system
├── db/
│   └── mongodb.py         # Handles conversation memory
├── models/
│   └── schemas.py         # Data structure definitions
├── utils/
│   ├── language.py        # Figures out if someone's speaking Arabic or English
│   └── whatsapp.py        # Talks to WhatsApp
├── templates/
│   └── chat.html          # The web interface design
└── data/                  # Where MongoDB stores stuff
```

## Testing it out

I've built in several ways to test this thing, because let's face it - debugging chatbots can be a pain.

### Quick API test

Want to see if the bot responds? Try this:

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "message": "How do I book a taxi?"}'
```

### Web interface (my personal favorite)

```bash
python web_app.py
```

Then open `http://localhost:5000` in your browser. You'll get a nice chat interface where you can test everything without needing WhatsApp.

### Full system check

```bash
python test_system.py
```

This runs through everything - API connections, database, language detection, the works.

### No-frills testing

If you don't have API keys set up yet, you can still test the basic FAQ matching:

```bash
python simple_test.py
```

## Configuration stuff

### The environment variables you need

Here's what each thing in your `.env` file does:

| What it's called       | What it does                          | Do you need it?       |
| ---------------------- | ------------------------------------- | --------------------- |
| `OPENAI_API_KEY`       | Makes the AI responses actually smart | Absolutely            |
| `MONGO_URI`            | Where to store conversation history   | Yes                   |
| `META_TOKEN`           | Your WhatsApp Business API token      | Yes                   |
| `META_PHONE_NUMBER_ID` | Your WhatsApp phone number            | Yes                   |
| `WEBHOOK_VERIFY_TOKEN` | A secret word for webhook security    | Yes                   |
| `GEMINI_API_KEY`       | Backup AI (Google's Gemini)           | Nah, but nice to have |

### Setting up your FAQ data

The bot learns from a CSV file called `bot-data.csv`. It's pretty simple:

```csv
question,answer
"How do I book a taxi?","Open the app, enter pickup/dropoff locations..."
"هل يمكنني حجز سيارة مسبقًا؟","نعم، اضغط على زر 'الجدولة'..."
```

Just two columns - questions your customers ask, and how you want the bot to respond. Mix Arabic and English however you want.

## Getting it live

### For development and testing

Just use ngrok like I showed you earlier. It's perfect for testing and showing off to your team.

### For the real deal

When you're ready to go live, here's what I'd recommend:

1. **Pick a cloud platform** - Railway and Render are super easy, AWS if you want more control
2. **Set up your environment variables** in whatever platform you choose
3. **Get a proper MongoDB instance** - MongoDB Atlas is great and has a free tier
4. **Domain and SSL** - Most platforms handle this automatically now
5. **Keep an eye on it** - Set up some basic monitoring so you know if things break

Honestly, Railway is probably your easiest bet. Just connect your GitHub repo and it pretty much deploys itself.

## How it all works together

I built this with a few key pieces that work together pretty nicely:

### The AI stuff

- **Main brain**: OpenAI's GPT-4o-mini does the heavy lifting for smart responses
- **Backup brain**: Google Gemini kicks in if OpenAI is having a bad day
- **Smart search**: FAISS vector database finds the right FAQ answers quickly
- **Language smarts**: Automatically figures out if someone's writing in Arabic or English

### The backend

- **FastAPI**: Handles all the WhatsApp webhook stuff (fast and reliable)
- **Flask**: Powers the web interface for testing
- **MongoDB**: Remembers conversations so the bot doesn't forget what you talked about
- **LangChain**: Ties all the AI pieces together nicely

### The connections

- **WhatsApp Business API**: How messages get in and out
- **Meta's webhook system**: Verifies everything is legit
- **Smart matching**: Finds the right answers even when people ask questions differently

## When things go wrong

Because they will, and that's okay! Here's how to fix the most common issues:

### "FAISS index not found" or similar AI errors

The setup script probably didn't finish properly. Just run:

```bash
python setup.py
```

### "OpenAI API error"

Either your API key is wrong, or you've hit your usage limit. Check:

- Your `OPENAI_API_KEY` in the `.env` file
- Your OpenAI account to make sure you have credits

### "MongoDB connection failed"

MongoDB isn't running or your connection string is wrong:

- Make sure MongoDB is actually running
- Double-check your `MONGO_URI` in `.env`

### "WhatsApp webhook verification failed"

This usually means your tokens don't match:

- Make sure `WEBHOOK_VERIFY_TOKEN` in `.env` matches what you put in Meta Console
- Check that your ngrok URL is still working (they change every time you restart ngrok)

### Debug helpers

I built in some tools to help you figure out what's broken:

```bash
# Check if your environment variables look right
python check_env.py

# Test everything at once
python test_system.py

# Just test the FAQ matching
python simple_test.py

# Quick health check
curl http://localhost:8000/health
```

### Logs

Everything important gets printed to the console. If you're deploying to production, you'll probably want to set up proper logging, but for development this works fine.

## The cool stuff it does

### Speaks both languages

The bot automatically detects whether someone is writing in Arabic or English and responds in the same language. No need to set anything up - it just works.

### Remembers conversations

Thanks to MongoDB, the bot actually remembers what you talked about before. So if a customer asks a follow-up question, it has context.

### Never breaks (well, tries not to)

I built in multiple fallback systems:

- OpenAI fails? Try Google Gemini
- Gemini fails? Fall back to simple text matching
- Everything fails? At least give a helpful error message

### Easy to test

I got tired of having to test through WhatsApp every time, so I built multiple ways to test:

- Web interface for quick testing
- API endpoints for automated testing
- Simple text matching for when you don't have API keys set up

## Want to contribute?

Cool! Here's how:

1. Fork this repo
2. Make a branch for your changes
3. Do your thing
4. Test it (please!)
5. Send me a pull request

## A few important notes

- **Don't commit your `.env` file** - I've already set up `.gitignore` to prevent this, but just saying
- **Watch your API usage** - OpenAI charges per token, so keep an eye on costs
- **Use HTTPS in production** - Most deployment platforms handle this automatically
- **Consider rate limiting** - Especially if this gets popular

## Performance stuff

I've tried to make this reasonably fast:

- FAISS for quick FAQ searches
- MongoDB connection pooling
- Async handling with FastAPI
- Caching where it makes sense

## Need help?

1. Check the troubleshooting section above
2. Run the test scripts to see what's broken
3. If you're a taxi company using this, call 920000000 😉

## License

MIT License - do whatever you want with it, just don't blame me if something breaks.

---

_Built because customer support shouldn't suck_ ❤️
