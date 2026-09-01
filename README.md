# LectureNote AI

> **Turn lectures into clear study material.**

Upload a lecture recording and automatically transform it into organized notes, quizzes, and flashcards — powered by AI.

---

## Features

- 🎙️ **Speech-to-Text** — Converts audio/video lectures to a clean transcript (via Google Gemini or OpenAI Whisper)
- 📝 **Smart Study Notes** — Overview, main concepts, detailed bullet notes, and key takeaways
- 🔑 **Key Points** — Numbered list of the most important lecture points (5–15)
- 📖 **Glossary & Definitions** — Technical terms defined in student-friendly language
- ✏️ **Practice Quiz** — 5–10 interactive multiple-choice questions with scoring and explanations
- 🃏 **Flashcards** — 8–15 flip-card study aids with front/back navigation
- ⬇️ **Download Everything** — Export transcript, notes, quiz, and flashcards as `.txt` files
- 📄 **Demo Mode** — Try the app instantly with a built-in sample lecture — no API key needed

---

## Project Structure

```
LectureNote AI/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── README.md           # This file
```

---

## Installation

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up your environment

Copy `.env.example` to `.env` and add your API key:

```bash
cp .env.example .env
```

Then open `.env` and fill in your key:

```
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 3. Run the application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## Getting an API Key

### Google Gemini (Recommended — Free tier available)

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **Create API Key**
4. Copy the key into your `.env` file as `GEMINI_API_KEY`

### OpenAI (Alternative)

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an API key
3. Copy the key into your `.env` file as `OPENAI_API_KEY`

> **Note:** If no API key is configured, you can still use the **Load Sample Lecture** button to explore all features of the app instantly.

---

## Supported Audio/Video Formats

| Format | Extension |
|--------|-----------|
| MP3    | `.mp3`    |
| WAV    | `.wav`    |
| M4A    | `.m4a`    |
| MP4    | `.mp4`    |
| AAC    | `.aac`    |
| FLAC   | `.flac`   |
| OGG    | `.ogg`    |

---

## How It Works

1. **Upload** your lecture audio or video file (or click "Load Sample Lecture")
2. Click **Generate Study Material**
3. The app:
   - Transcribes the audio using AI speech-to-text
   - Generates organized study notes, key points, and definitions
   - Creates an interactive multiple-choice quiz
   - Generates flashcards for spaced repetition study
4. Navigate results using the six study tabs
5. **Download** any or all materials as `.txt` files

---

## Technology Stack

- **Python 3.8+**
- **Streamlit** — UI framework
- **Google Gemini API** — Speech-to-text + AI generation (primary)
- **OpenAI API** — Whisper STT + GPT-4o-mini (alternative)
- **python-dotenv** — Environment variable management

---

## Security

- ✅ API keys are read from environment variables only
- ✅ No credentials are hard-coded in the source
- ✅ The `.env` file should never be committed to version control

Add `.env` to your `.gitignore`:

```
.env
```

---

## License

MIT — Free to use, modify, and distribute.
