
##  What This Is

This repo is a functional showcase of a **real-time voice/text chatbot** built on top of **LiveKit** and any AI model.  
I just used **Gemini**, but you could use OpenAI's model as well also Anthropic's model could be better, or anything desired.  

It’s **clean, readable, and forkable** — made for devs who actually care about code that works and has a bit of soul.  

It handles all the boring glue: receiving audio/text from LiveKit, forwarding it to an LLM, and streaming responses back in real time.  

No over-engineering, no "AI magic" nonsense — just proper **modular Python**.  

---

##  Highlights (tl;dr)

- Real-time **voice and text chat** using LiveKit  
- Works with **Gemini, OpenAI, or literally any model** with an API key  
- **Clean Python code** — easy to fork, debug, or replace parts of  
- Minimal dependencies and **.env-based config** — no 500-line setup rituals  

---

##  Files You Actually Care About

| File       | Purpose                                                                 |
|------------|-------------------------------------------------------------------------|
| `main.py`  | Main brain. Starts the bot, connects LiveKit + model.                   |
| `api.py`   | Optional REST helpers for testing and integrations.                     |
| `.env`     | Where your secrets live (don’t commit it cuz dats just fool's play).    |
| `LICENSE`  | Apache-2.0 — basically: use it, don’t be evil.                          |

---

##  Requirements

- Python 3.10+ (**3.11 runs slightly faster if you like milliseconds**)  
- A **LiveKit project** (Cloud or self-hosted)  
- A **Gemini API key** or any LLM key you prefer  
- **Never forget PIP !!** (No one does :p)  

 **Pro tip:** keep your keys in `.env` — not in the code or not even in your README.

---

##  Setup (Quick Start)

1. **Clone the repo**
   ```bash
   git clone https://github.com/NeilhancyDev78/chat-bot-for-wot.git
   cd chat-bot-for-wot
   
2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate    
   pip install --upgrade pip
   
3. **Create a .env file**
   ```bash
   # LiveKit
   LIVEKIT_API_KEY=your_livekit_key
   LIVEKIT_API_SECRET=your_livekit_secret
   LIVEKIT_URL=wss://your-livekit-server.example.com

   # Model
   YOUR_API_KEY=j_xa_tei_haal_na_abaa!

4. **Run the bot**
   ```bash
   python main.py

---

##  How It Works 
- You or someone joins a LiveKit room

- The bot gets your audio/text stream

- If it’s audio, it’s transcribed to text (Whisper, Gemini STT, etc.)

- That text gets sent to the LLM (Gemini, OpenAI, whatever you picked)

- The model’s reply is sent back — as text or speech.

---

##  License

- Apache-2.0 — use it, remix it, meme it. Just don’t sue me if it gains consciousness.
- If you break something, at least leave a funny commit message.

---

##  And lastly

- You'll be running a live AI chatbot yayy !!
> If it crashes — congrats, you’re a developer now !
> Open an issue, flex your logs, and we’ll roast/debug it together.

- Fork it. Break it. Make it better.


---




