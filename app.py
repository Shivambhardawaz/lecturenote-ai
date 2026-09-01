"""
LectureNote AI — Pure Python Streamlit Application
==================================================
Converts lecture recordings into structured notes, key points, definitions, quizzes, and flashcards.

Workflow: Upload Lecture → Speech-to-Text → Generate Study Material → Review → Practice
"""

import os
import json
import re
import time
import base64
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

SUPPORTED_EXTENSIONS = ["mp3", "wav", "m4a", "mp4", "aac", "flac", "ogg"]
MAX_FILE_SIZE_MB = 200

# ─────────────────────────────────────────────
# SAMPLE LECTURE DATA (Instant Demo Mode)
# ─────────────────────────────────────────────

SAMPLE_TRANSCRIPT = """Introduction to Machine Learning — Lecture Transcript

Welcome everyone to today's lecture. We're going to be covering the fundamentals of Machine Learning, which forms the bedrock of modern artificial intelligence.

Machine learning is a subfield of artificial intelligence that enables computer systems to learn from data and improve their performance on tasks without being explicitly programmed for each task. The key idea here is that instead of writing fixed rules, we expose the system to examples and let it figure out the patterns by itself.

There are three main paradigms in machine learning. The first is Supervised Learning. In supervised learning, we train a model on a labeled dataset — meaning the training examples come with correct answers. The model learns a mapping from inputs to outputs. Classic examples include email spam detection, where emails are labeled as spam or not spam, and image classification, where images are labeled with the objects they contain.

The second paradigm is Unsupervised Learning. Here, we have data without any labels. The goal is to discover hidden structure or patterns in the data. Clustering algorithms like K-Means are a great example — they group data points into clusters based on similarity, without any predefined categories. Another technique is dimensionality reduction using methods like Principal Component Analysis, or PCA, which compresses high-dimensional data into fewer dimensions while preserving important variance.

The third paradigm is Reinforcement Learning. In this setting, an agent interacts with an environment and learns by receiving rewards or penalties. The agent aims to maximize cumulative reward over time. This is the approach behind breakthrough applications like AlphaGo, which mastered the game of Go, and modern robotics.

Now let's discuss some fundamental concepts. A feature is an individual measurable property or characteristic of the data. For example, in a housing price prediction model, features might include the number of bedrooms, the square footage, and the neighborhood. Choosing good features — a process called feature engineering — is critical to building effective models.

The model is the mathematical function that maps inputs to outputs. Common model families include linear regression, which fits a straight line through data points; decision trees, which split the data based on feature thresholds; neural networks, which are inspired by the human brain and consist of layers of interconnected nodes; and support vector machines, which find an optimal separating hyperplane between classes.

Overfitting is one of the most important concepts to understand. A model that overfits has learned the training data too well — it memorizes noise and specific patterns in the training set rather than generalizing to new data. To combat overfitting, we use techniques such as regularization, dropout in neural networks, and cross-validation to properly evaluate model performance.

The bias-variance tradeoff is closely related to overfitting. High bias means the model is too simple and underfits the data — it doesn't capture the underlying pattern. High variance means the model is too complex and overfits — it captures noise. Good machine learning practice involves finding the right balance between bias and variance.

The training process involves feeding data into the model, computing a loss function that measures how wrong the predictions are, and then using an optimization algorithm — typically gradient descent — to adjust the model's parameters to reduce the loss. This cycle repeats many times until the model converges.

To evaluate a model, we split our dataset into at least two parts: a training set and a test set. The model never sees the test set during training, so it provides an unbiased estimate of how the model will perform on real, unseen data. Common evaluation metrics include accuracy for classification, mean squared error for regression, and the F1 score when dealing with imbalanced classes.

Data preprocessing is another essential step. Real-world data is often messy — it may contain missing values, outliers, inconsistent formatting, and varying scales. Techniques like normalization and standardization put features on the same scale, which is important for many algorithms. Handling missing data through imputation ensures we don't lose valuable training examples.

In recent years, deep learning — a subfield of machine learning that uses neural networks with many layers — has revolutionized fields such as computer vision, natural language processing, and speech recognition. Convolutional neural networks excel at image tasks. Recurrent neural networks and transformers are designed for sequential data like text and speech.

To summarize today's lecture: machine learning allows systems to learn from data. We covered the three main paradigms — supervised, unsupervised, and reinforcement learning. We discussed critical concepts like features, models, overfitting, the bias-variance tradeoff, the training loop, and evaluation. We also touched on the importance of data preprocessing and the rise of deep learning. In the next lecture, we'll dive into a hands-on implementation using Python's scikit-learn library.

Thank you for your attention today.
"""

SAMPLE_STUDY_MATERIAL = {
    "summary": {
        "overview": "This lecture provides a comprehensive introduction to machine learning (ML), covering its core definition, the three primary paradigms (Supervised, Unsupervised, Reinforcement Learning), fundamental concepts like features, models, overfitting, the bias-variance tradeoff, the training cycle, model evaluation, and an introduction to deep learning.",
        "main_concepts": [
            "Machine Learning: Subfield of AI where algorithms learn patterns from data rather than following hardcoded rules.",
            "Supervised Learning: Learning input-to-output mappings using labeled training datasets (e.g., spam filters, image recognition).",
            "Unsupervised Learning: Finding intrinsic structures and patterns in unlabeled data (e.g., K-Means clustering, PCA dimensionality reduction).",
            "Reinforcement Learning: Agents learning optimal decision policies through reward signals from an environment.",
            "The Training Cycle: Passing data → calculating loss → adjusting parameters via gradient descent until convergence."
        ],
        "detailed_notes": [
            "Features are measurable attributes of data; feature engineering is decisive for model accuracy.",
            "Core model families include linear regression, decision trees, support vector machines (SVMs), and neural networks.",
            "Overfitting occurs when a model memorizes training noise; prevented using regularization, dropout, and cross-validation.",
            "Bias-Variance Tradeoff: High bias leads to underfitting, while high variance leads to overfitting.",
            "Datasets are divided into training sets (for model learning) and unseen test sets (for unbiased validation).",
            "Evaluation metrics vary by task: Accuracy and F1-Score for classification, Mean Squared Error (MSE) for regression.",
            "Data preprocessing (normalization, standardization, missing value imputation) is vital before training.",
            "Deep learning utilizes deep multi-layered architectures: CNNs for vision, Transformers/RNNs for sequential data."
        ],
        "takeaways": [
            "ML allows computers to discover patterns directly from empirical data.",
            "Master the differences between Supervised, Unsupervised, and Reinforcement learning.",
            "Always validate models on a separate test set to detect and prevent overfitting.",
            "Balance the tradeoff between bias (simplicity) and variance (complexity).",
            "Quality preprocessing and feature selection are just as crucial as model selection.",
            "Deep learning powers modern breakthroughs in computer vision and natural language processing."
        ]
    },
    "key_points": [
        "Machine learning enables systems to learn from data without explicit task-by-task programming.",
        "Supervised learning requires labeled datasets with known ground-truth targets.",
        "Unsupervised learning discovers hidden clusters and structures in unlabeled datasets.",
        "Reinforcement learning trains autonomous agents to maximize cumulative environment rewards.",
        "Features represent measurable data properties, and feature engineering directly influences model quality.",
        "Popular model families include linear regression, decision trees, SVMs, and neural networks.",
        "Overfitting happens when models learn training noise and fail to generalize to new data.",
        "Regularization, dropout, and cross-validation are standard defenses against overfitting.",
        "The bias-variance tradeoff balances model simplicity against complex over-parameterization.",
        "Gradient descent is the primary optimization algorithm driving model parameter updates.",
        "Models are evaluated on isolated test sets using metrics like accuracy, MSE, and F1-score.",
        "Data preprocessing (cleaning, scaling, imputation) is required before model training.",
        "Deep learning employs multi-layered neural networks to excel at vision and language tasks."
    ],
    "definitions": [
        {"term": "Machine Learning", "definition": "A branch of artificial intelligence where algorithms learn patterns from empirical data and improve task performance without explicit rule-based programming."},
        {"term": "Supervised Learning", "definition": "A machine learning paradigm where the algorithm is trained on labeled data with known inputs and expected outputs."},
        {"term": "Unsupervised Learning", "definition": "A learning paradigm where the model discovers patterns, clusters, or relationships in data without predefined labels."},
        {"term": "Reinforcement Learning", "definition": "A paradigm where an agent learns optimal behavior through trial and error by interacting with an environment and receiving rewards or penalties."},
        {"term": "Feature", "definition": "An individual measurable variable or property used as input for a machine learning model."},
        {"term": "Overfitting", "definition": "A modeling error where an algorithm fits the training dataset too closely, capturing noise and performing poorly on unseen data."},
        {"term": "Bias-Variance Tradeoff", "definition": "The tension between error introduced by simplistic model assumptions (bias) and sensitivity to training data fluctuations (variance)."},
        {"term": "Gradient Descent", "definition": "An iterative optimization algorithm that adjusts parameters in the direction of steepest descent to minimize the loss function."},
        {"term": "Loss Function", "definition": "A mathematical objective function measuring the discrepancy between a model's predictions and actual ground truth values."},
        {"term": "K-Means Clustering", "definition": "An unsupervised algorithm that partitions data points into K clusters based on Euclidean distance to cluster centroids."},
        {"term": "Principal Component Analysis (PCA)", "definition": "A dimensionality reduction method that projects high-dimensional data onto orthogonal axes preserving maximum variance."},
        {"term": "Regularization", "definition": "Techniques such as L1 (Lasso) and L2 (Ridge) penalties added to loss functions to discourage excessive model complexity."},
        {"term": "Deep Learning", "definition": "A subfield of machine learning based on artificial neural networks with multiple representation learning layers."},
        {"term": "Convolutional Neural Network (CNN)", "definition": "A specialized neural network architecture using convolutional layers to capture spatial patterns in visual data."}
    ],
    "quiz": [
        {
            "question": "What is the core definition of Machine Learning?",
            "options": [
                "Writing explicit hardcoded rules for every possible task scenario",
                "Algorithms learning patterns from data to perform tasks without explicit programming",
                "A hardware architecture specialized for graphical computation",
                "A relational database management system"
            ],
            "answer": 1,
            "explanation": "Machine learning enables systems to learn and improve from data patterns rather than requiring hardcoded rules for every scenario."
        },
        {
            "question": "Which machine learning paradigm requires labeled training data?",
            "options": [
                "Unsupervised Learning",
                "Reinforcement Learning",
                "Supervised Learning",
                "Self-Organizing Maps"
            ],
            "answer": 2,
            "explanation": "Supervised learning relies on labeled input-output pairs to train predictive models."
        },
        {
            "question": "What problem occurs when a model learns training data noise and fails on new data?",
            "options": [
                "Underfitting",
                "Overfitting",
                "Feature Engineering",
                "Dimensionality Reduction"
            ],
            "answer": 1,
            "explanation": "Overfitting occurs when a model memorizes specific training data noise instead of learning generalizable patterns."
        },
        {
            "question": "Which optimization algorithm is standard for adjusting model weights to minimize loss?",
            "options": [
                "K-Means",
                "PCA",
                "Gradient Descent",
                "Binary Search"
            ],
            "answer": 2,
            "explanation": "Gradient descent iteratively adjusts parameters in the direction that minimizes the loss function."
        },
        {
            "question": "Why must a separate test set be preserved during training?",
            "options": [
                "To accelerate gradient descent convergence",
                "To provide an unbiased assessment of model performance on unseen data",
                "To generate synthetic features automatically",
                "To increase training loss"
            ],
            "answer": 1,
            "explanation": "An isolated test set provides an unbiased estimate of how well the model generalizes to unseen real-world data."
        },
        {
            "question": "Which of the following is an example of Unsupervised Learning?",
            "options": [
                "Classifying emails as spam or not spam using labeled examples",
                "Clustering customers into behavioral segments using K-Means",
                "Teaching a robot to balance via reward signals",
                "Predicting house prices from labeled historical sale prices"
            ],
            "answer": 1,
            "explanation": "K-Means groups data into clusters based on inherent similarity without requiring predefined target labels."
        },
        {
            "question": "What does high bias in a machine learning model typically indicate?",
            "options": [
                "The model is overly complex and memorizes noise",
                "The model is too simple and underfits the underlying structure",
                "The training loss is exactly zero",
                "The dataset has too many features"
            ],
            "answer": 1,
            "explanation": "High bias reflects overly simplistic assumptions, causing the model to underfit and miss true patterns."
        },
        {
            "question": "What is the primary function of Principal Component Analysis (PCA)?",
            "options": [
                "Compressing high-dimensional data into fewer dimensions while preserving variance",
                "Supervised image segmentation",
                "Computing gradient descent learning rates",
                "Generating reinforcement learning policies"
            ],
            "answer": 0,
            "explanation": "PCA reduces data dimensionality by projecting features onto principal components that capture maximum variance."
        },
        {
            "question": "Which neural network architecture is tailored for computer vision and image processing?",
            "options": [
                "Convolutional Neural Network (CNN)",
                "Recurrent Neural Network (RNN)",
                "Linear Regression",
                "Decision Tree"
            ],
            "answer": 0,
            "explanation": "CNNs use spatial convolutional filters, making them the standard architecture for image and video analysis."
        },
        {
            "question": "Why is data preprocessing (e.g., normalization, missing value imputation) necessary?",
            "options": [
                "It is optional; modern models handle messy data automatically",
                "Real-world data often has varying scales, missing entries, and outliers that harm model training",
                "It reduces any dataset to a single feature column",
                "It converts supervised problems into unsupervised ones"
            ],
            "answer": 1,
            "explanation": "Data preprocessing ensures consistent scaling and data cleanliness, which are critical for model convergence and accuracy."
        }
    ],
    "flashcards": [
        {"front": "What is Machine Learning?", "back": "A subfield of AI where computer systems learn patterns from data and improve performance without being explicitly programmed."},
        {"front": "Name the three primary Machine Learning paradigms.", "back": "1. Supervised Learning (labeled data)\n2. Unsupervised Learning (unlabeled data)\n3. Reinforcement Learning (reward/penalty signals)"},
        {"front": "What is Overfitting?", "back": "When a model learns training noise and details too closely, leading to poor generalization on new, unseen data."},
        {"front": "Explain the Bias-Variance Tradeoff.", "back": "High Bias = Underfitting (model is too simple).\nHigh Variance = Overfitting (model captures noise).\nGoal: Optimal balance minimizing total error."},
        {"front": "What is Gradient Descent?", "back": "An iterative optimization algorithm that updates parameters in the direction that minimizes the loss function."},
        {"front": "What is a Feature?", "back": "An individual measurable property or variable of the input data used by the model for prediction."},
        {"front": "What is K-Means Clustering?", "back": "An unsupervised algorithm that groups data points into K clusters based on similarity to nearest cluster centroids."},
        {"front": "What is PCA (Principal Component Analysis)?", "back": "A dimensionality reduction technique that compresses data while preserving maximum variance/information."},
        {"front": "Why is an isolated test set necessary?", "back": "Because the model never trains on it, giving an unbiased measure of real-world generalization performance."},
        {"front": "What is Deep Learning?", "back": "A subfield of ML using multi-layered artificial neural networks for complex tasks like vision and NLP."},
        {"front": "What is a Loss Function?", "back": "A mathematical formula calculating the error between model predictions and true targets; minimized during training."},
        {"front": "What is Regularization?", "back": "Techniques (e.g., L1/L2 penalties, dropout) that constrain model complexity to prevent overfitting."}
    ]
}

# ─────────────────────────────────────────────
# API CREDENTIALS & PROVIDER DETECTION
# ─────────────────────────────────────────────

def get_api_key():
    """Check st.secrets first, then environment variables."""
    if hasattr(st, "secrets"):
        try:
            if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
                return st.secrets["GEMINI_API_KEY"]
            if "AI_API_KEY" in st.secrets and st.secrets["AI_API_KEY"]:
                return st.secrets["AI_API_KEY"]
            if "OPENAI_API_KEY" in st.secrets and st.secrets["OPENAI_API_KEY"]:
                return st.secrets["OPENAI_API_KEY"]
        except Exception:
            pass
    return (
        os.getenv("GEMINI_API_KEY") or
        os.getenv("AI_API_KEY") or
        os.getenv("OPENAI_API_KEY") or
        None
    )


def get_api_provider():
    """Return active provider ('gemini' or 'openai')."""
    if hasattr(st, "secrets"):
        try:
            if "GEMINI_API_KEY" in st.secrets or "AI_API_KEY" in st.secrets:
                return "gemini"
            if "OPENAI_API_KEY" in st.secrets:
                return "openai"
        except Exception:
            pass
    if os.getenv("GEMINI_API_KEY") or os.getenv("AI_API_KEY"):
        return "gemini"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    return None

# ─────────────────────────────────────────────
# SPEECH-TO-TEXT ENGINE
# ─────────────────────────────────────────────

def transcribe_audio(uploaded_file) -> str:
    """Transcribe uploaded audio/video using configured API."""
    provider = get_api_provider()
    api_key = get_api_key()

    if not api_key:
        raise ValueError("No API key configured. Please set GEMINI_API_KEY or OPENAI_API_KEY.")

    file_bytes = uploaded_file.read()

    if provider == "gemini":
        return _transcribe_gemini(file_bytes, uploaded_file.name, api_key)
    elif provider == "openai":
        return _transcribe_openai(file_bytes, uploaded_file.name, api_key)
    else:
        raise ValueError("Unsupported AI provider.")


def _transcribe_gemini(file_bytes: bytes, filename: str, api_key: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    mime_map = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".mp4": "video/mp4",
        ".aac": "audio/aac",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac",
    }
    mime_type = mime_map.get(ext, "audio/mpeg")
    audio_b64 = base64.b64encode(file_bytes).decode("utf-8")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [
                {"inline_data": {"mime_type": mime_type, "data": audio_b64}},
                {"text": (
                    "Please transcribe this lecture recording accurately. "
                    "Produce a clean, well-formatted transcript with proper punctuation and paragraphs. "
                    "Return ONLY the transcript text without commentary."
                )}
            ]
        }],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 8192}
    }

    resp = requests.post(url, json=payload, timeout=120)
    if resp.status_code != 200:
        raise RuntimeError(f"Gemini API error ({resp.status_code}): {resp.text[:300]}")
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def _transcribe_openai(file_bytes: bytes, filename: str, api_key: str) -> str:
    url = "https://api.openai.com/v1/audio/transcriptions"
    files = {"file": (filename, file_bytes), "model": (None, "whisper-1")}
    headers = {"Authorization": f"Bearer {api_key}"}
    resp = requests.post(url, headers=headers, files=files, timeout=120)
    if resp.status_code != 200:
        raise RuntimeError(f"OpenAI Whisper error ({resp.status_code}): {resp.text[:300]}")
    return resp.json().get("text", "").strip()

# ─────────────────────────────────────────────
# AI GENERATION ENGINE
# ─────────────────────────────────────────────

def _call_ai(prompt: str, temperature: float = 0.3) -> str:
    provider = get_api_provider()
    api_key = get_api_key()
    if not api_key:
        raise ValueError("No API key configured.")

    if provider == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": 4096}
        }
        resp = requests.post(url, json=payload, timeout=90)
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini error ({resp.status_code}): {resp.text[:300]}")
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    elif provider == "openai":
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": 4096
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=90)
        if resp.status_code != 200:
            raise RuntimeError(f"OpenAI error ({resp.status_code}): {resp.text[:300]}")
        return resp.json()["choices"][0]["message"]["content"].strip()
    raise ValueError("No active AI provider.")


def _parse_json(text: str):
    clean = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    clean = re.sub(r"```\s*$", "", clean.strip(), flags=re.MULTILINE)
    return json.loads(clean.strip())


def generate_summary(transcript: str) -> dict:
    prompt = f"""Based ONLY on this lecture transcript, generate structured study notes.
Transcript:
\"\"\"
{transcript}
\"\"\"

Return ONLY valid JSON with this exact structure:
{{
  "overview": "<2-3 sentence overview>",
  "main_concepts": ["<concept 1>", "<concept 2>", ...],
  "detailed_notes": ["<note 1>", "<note 2>", ...],
  "takeaways": ["<takeaway 1>", "<takeaway 2>", ...]
}}
"""
    return _parse_json(_call_ai(prompt))


def generate_key_points(transcript: str) -> list:
    prompt = f"""Extract 5-15 numbered key points from this lecture transcript.
Transcript:
\"\"\"
{transcript}
\"\"\"

Return ONLY valid JSON as a string array:
["<point 1>", "<point 2>", ...]
"""
    return _parse_json(_call_ai(prompt))


def generate_definitions(transcript: str) -> list:
    prompt = f"""Extract technical terms and student-friendly definitions from this lecture transcript.
Transcript:
\"\"\"
{transcript}
\"\"\"

Return ONLY valid JSON as an array of objects:
[
  {{"term": "<term>", "definition": "<definition>"}}
]
"""
    return _parse_json(_call_ai(prompt))


def generate_quiz(transcript: str) -> list:
    prompt = f"""Generate 5-10 multiple choice questions based entirely on this lecture transcript.
Transcript:
\"\"\"
{transcript}
\"\"\"

Return ONLY valid JSON as an array of objects:
[
  {{
    "question": "<question text>",
    "options": ["<opt A>", "<opt B>", "<opt C>", "<opt D>"],
    "answer": <0-3 integer index of correct option>,
    "explanation": "<brief explanation>"
  }}
]
"""
    return _parse_json(_call_ai(prompt))


def generate_flashcards(transcript: str) -> list:
    prompt = f"""Generate 8-15 flashcards for memorization from this lecture transcript.
Transcript:
\"\"\"
{transcript}
\"\"\"

Return ONLY valid JSON as an array of objects:
[
  {{"front": "<question/concept>", "back": "<answer/explanation>"}}
]
"""
    return _parse_json(_call_ai(prompt))

# ─────────────────────────────────────────────
# EXPORT FORMATTERS
# ─────────────────────────────────────────────

def format_summary_txt(summary: dict, topic: str) -> str:
    lines = [f"LECTURENOTE AI — STUDY NOTES\nLecture: {topic}\n" + "=" * 60, ""]
    lines += ["LECTURE OVERVIEW", "-" * 40, summary.get("overview", ""), ""]
    lines += ["MAIN CONCEPTS", "-" * 40]
    for c in summary.get("main_concepts", []):
        lines.append(f"  • {c}")
    lines += ["", "DETAILED NOTES", "-" * 40]
    for n in summary.get("detailed_notes", []):
        lines.append(f"  • {n}")
    lines += ["", "IMPORTANT TAKEAWAYS", "-" * 40]
    for t in summary.get("takeaways", []):
        lines.append(f"  • {t}")
    return "\n".join(lines)


def format_key_points_txt(key_points: list, topic: str) -> str:
    lines = [f"LECTURENOTE AI — KEY POINTS\nLecture: {topic}\n" + "=" * 60, ""]
    for i, pt in enumerate(key_points, 1):
        lines.append(f"{i:02d}. {pt}\n")
    return "\n".join(lines)


def format_definitions_txt(definitions: list, topic: str) -> str:
    lines = [f"LECTURENOTE AI — DEFINITIONS & GLOSSARY\nLecture: {topic}\n" + "=" * 60, ""]
    for d in definitions:
        lines.append(f"[{d['term']}]\n  {d['definition']}\n")
    return "\n".join(lines)


def format_quiz_txt(quiz: list, topic: str) -> str:
    lines = [f"LECTURENOTE AI — QUIZ\nLecture: {topic}\n" + "=" * 60, ""]
    for i, q in enumerate(quiz, 1):
        lines.append(f"Q{i}. {q['question']}")
        for j, opt in enumerate(q["options"]):
            marker = "✓" if j == q["answer"] else " "
            lines.append(f"  [{marker}] {chr(65+j)}) {opt}")
        lines.append(f"  Explanation: {q['explanation']}\n")
    return "\n".join(lines)


def format_flashcards_txt(flashcards: list, topic: str) -> str:
    lines = [f"LECTURENOTE AI — FLASHCARDS\nLecture: {topic}\n" + "=" * 60, ""]
    for i, fc in enumerate(flashcards, 1):
        lines.append(f"Card {i}\n  FRONT: {fc['front']}\n  BACK:  {fc['back']}\n")
    return "\n".join(lines)


def format_full_pack_txt(topic, transcript, summary, key_points, definitions, quiz, flashcards) -> str:
    sections = [
        f"LECTURENOTE AI — COMPLETE STUDY PACK\nLecture: {topic}\n" + "=" * 60,
        format_summary_txt(summary, topic),
        format_key_points_txt(key_points, topic),
        format_definitions_txt(definitions, topic),
        format_quiz_txt(quiz, topic),
        format_flashcards_txt(flashcards, topic),
        f"TRANSCRIPT\n" + "-" * 40 + "\n" + transcript
    ]
    return "\n\n" + ("\n\n" + "=" * 60 + "\n\n").join(sections)

# ─────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────

def init_session_state():
    defaults = {
        "processing_done": False,
        "transcript": None,
        "summary": None,
        "key_points": None,
        "definitions": None,
        "quiz": None,
        "flashcards": None,
        "lecture_topic": "",
        "quiz_current_q": 0,
        "quiz_answers": {},
        "quiz_submitted": False,
        "quiz_score": 0,
        "card_index": 0,
        "card_show_back": False,
        "current_page": "home",
        "using_sample": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_results():
    keys = [
        "processing_done", "transcript", "summary", "key_points", "definitions",
        "quiz", "flashcards", "quiz_current_q", "quiz_answers", "quiz_submitted",
        "quiz_score", "card_index", "card_show_back", "using_sample"
    ]
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]
    init_session_state()

# ─────────────────────────────────────────────
# UI VIEWS (PURE PYTHON & STREAMLIT NATIVE)
# ─────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.title("🎓 LectureNote AI")
        st.caption("Your lecture. Organized for learning.")
        st.divider()

        # Navigation
        nav = st.radio(
            "Navigation",
            options=["🏠 Home", "ℹ️ About"],
            label_visibility="collapsed"
        )
        if nav == "🏠 Home" and st.session_state.current_page != "home":
            st.session_state.current_page = "home"
            st.rerun()
        elif nav == "ℹ️ About" and st.session_state.current_page != "about":
            st.session_state.current_page = "about"
            st.rerun()

        st.divider()

        # API Key status
        api_key = get_api_key()
        provider = get_api_provider()

        if api_key:
            name = "Google Gemini" if provider == "gemini" else "OpenAI"
            st.success(f"**API Key Active**\n\nProvider: {name}")
        else:
            st.warning("**No API Key Found**\n\nUse Demo Mode or set `GEMINI_API_KEY`.")

        st.divider()
        st.markdown("**Supported Formats**")
        st.caption("MP3 · WAV · M4A · MP4 · AAC · FLAC · OGG")


def render_home():
    st.title("Turn lectures into clear study material.")
    st.markdown(
        "Upload any audio or video recording from your class, seminar, or meeting "
        "and automatically generate organized notes, key points, glossary terms, interactive quizzes, and flashcards."
    )

    if not get_api_key():
        st.info("💡 **Demo Ready**: You can test the application instantly using the **Load Sample Lecture** button below without an API key.")

    st.write("")

    # Main Upload Box
    with st.container(border=True):
        st.subheader("🎙️ Upload Lecture")
        st.caption("Select an audio or video file from your computer (MP3, WAV, M4A, MP4, AAC, FLAC, OGG — up to 200MB)")

        uploaded_file = st.file_uploader(
            "Upload lecture recording",
            type=SUPPORTED_EXTENSIONS,
            label_visibility="collapsed"
        )

        lecture_topic = st.text_input(
            "Lecture Topic (optional)",
            placeholder="e.g. Introduction to Machine Learning"
        )

        st.write("")
        col1, col2 = st.columns([1, 1])

        with col1:
            btn_generate = st.button("🎓 Generate Study Material", type="primary", use_container_width=True)

        with col2:
            btn_sample = st.button("📄 Load Sample Lecture", use_container_width=True)

    # ── Handle Sample Demo ──
    if btn_sample:
        reset_results()
        with st.status("Loading sample lecture...", expanded=True) as status:
            st.write("Loading pre-processed lecture data...")
            time.sleep(0.3)
            st.session_state.transcript = SAMPLE_TRANSCRIPT
            st.session_state.summary = SAMPLE_STUDY_MATERIAL["summary"]
            st.session_state.key_points = SAMPLE_STUDY_MATERIAL["key_points"]
            st.session_state.definitions = SAMPLE_STUDY_MATERIAL["definitions"]
            st.session_state.quiz = SAMPLE_STUDY_MATERIAL["quiz"]
            st.session_state.flashcards = SAMPLE_STUDY_MATERIAL["flashcards"]
            st.session_state.lecture_topic = "Introduction to Machine Learning"
            st.session_state.processing_done = True
            st.session_state.using_sample = True
            st.session_state.current_page = "results"
            status.update(label="Sample lecture ready!", state="complete")
        st.rerun()

    # ── Handle Real Upload ──
    if btn_generate:
        if uploaded_file is None:
            st.warning("📂 Please upload a lecture recording to continue.")
            return

        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            st.error(f"⚠️ File is too large ({file_size_mb:.1f} MB). Maximum supported size is {MAX_FILE_SIZE_MB} MB.")
            return

        if not get_api_key():
            st.error("🔑 No API key found. Please configure `GEMINI_API_KEY` in `.env` or Streamlit Secrets.")
            return

        topic = lecture_topic.strip() or uploaded_file.name
        reset_results()
        st.session_state.lecture_topic = topic

        try:
            with st.status("Processing your lecture...", expanded=True) as status:
                st.write("✅ Lecture file received")

                st.write("⏳ Converting speech to text with AI...")
                transcript = transcribe_audio(uploaded_file)
                if not transcript or len(transcript.strip()) < 40:
                    raise ValueError("Transcript is empty or recording contains no recognizable speech.")
                st.session_state.transcript = transcript
                st.write("✅ Speech-to-text complete")

                st.write("⏳ Generating structured study notes...")
                summary = generate_summary(transcript)
                st.session_state.summary = summary
                st.write("✅ Study notes generated")

                st.write("⏳ Extracting key points and glossary definitions...")
                key_points = generate_key_points(transcript)
                definitions = generate_definitions(transcript)
                st.session_state.key_points = key_points
                st.session_state.definitions = definitions
                st.write("✅ Key points and definitions extracted")

                st.write("⏳ Creating practice quiz...")
                quiz = generate_quiz(transcript)
                st.session_state.quiz = quiz
                st.write("✅ Practice quiz created")

                st.write("⏳ Creating study flashcards...")
                flashcards = generate_flashcards(transcript)
                st.session_state.flashcards = flashcards
                st.write("✅ Flashcards ready")

                st.session_state.processing_done = True
                st.session_state.current_page = "results"
                status.update(label="Study material ready!", state="complete")

        except ValueError as e:
            st.error(f"⚠️ {e}")
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Please try a shorter recording.")
        except requests.exceptions.ConnectionError:
            st.error("🌐 Network connection error. Please check your internet.")
        except json.JSONDecodeError:
            st.error("⚠️ Error parsing AI response. Please try again.")
        except Exception as e:
            st.error(f"⚠️ An unexpected error occurred: {str(e)[:250]}")
            return

        if st.session_state.processing_done:
            st.rerun()


def render_results():
    topic = st.session_state.lecture_topic
    is_demo = st.session_state.get("using_sample", False)

    col_back, col_title = st.columns([1, 4])
    with col_back:
        if st.button("← New Lecture", use_container_width=True):
            reset_results()
            st.session_state.current_page = "home"
            st.rerun()

    with col_title:
        demo_tag = " *(Sample Lecture)*" if is_demo else ""
        st.subheader(f"📖 {topic}{demo_tag}")

    st.caption("Status: Ready for revision • 6 Study Sections Available")

    # 6 Native Streamlit Tabs
    tab_transcript, tab_notes, tab_key_points, tab_definitions, tab_quiz, tab_flashcards = st.tabs([
        "📄 Transcript",
        "📝 Study Notes",
        "🔑 Key Points",
        "📖 Definitions",
        "✏️ Practice Quiz",
        "🃏 Flashcards"
    ])

    # ── TAB 1: TRANSCRIPT ──
    with tab_transcript:
        st.markdown("### Lecture Transcript")
        st.text_area(
            "Complete Transcript",
            value=st.session_state.transcript,
            height=350,
            disabled=True,
            label_visibility="collapsed"
        )
        col_dl, col_exp = st.columns([1, 1])
        with col_dl:
            st.download_button(
                "⬇️ Download Transcript (.txt)",
                data=st.session_state.transcript,
                file_name=f"transcript_{topic.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_exp:
            with st.expander("📋 View & Copy Raw Text"):
                st.code(st.session_state.transcript, language=None)

    # ── TAB 2: STUDY NOTES ──
    with tab_notes:
        summary = st.session_state.summary

        with st.container(border=True):
            st.markdown("#### 📋 Lecture Overview")
            st.write(summary.get("overview", ""))

        with st.container(border=True):
            st.markdown("#### 💡 Main Concepts")
            for c in summary.get("main_concepts", []):
                st.markdown(f"- **{c}**")

        with st.container(border=True):
            st.markdown("#### 📝 Detailed Notes")
            for n in summary.get("detailed_notes", []):
                st.markdown(f"- {n}")

        with st.container(border=True):
            st.markdown("#### ⭐ Important Takeaways")
            for t in summary.get("takeaways", []):
                st.markdown(f"- {t}")

        st.download_button(
            "⬇️ Download Study Notes (.txt)",
            data=format_summary_txt(summary, topic),
            file_name=f"notes_{topic.replace(' ', '_')}.txt",
            mime="text/plain"
        )

    # ── TAB 3: KEY POINTS ──
    with tab_key_points:
        st.markdown("### Key Points")
        key_points = st.session_state.key_points
        for i, pt in enumerate(key_points, 1):
            with st.container(border=True):
                col_n, col_p = st.columns([1, 15])
                with col_n:
                    st.markdown(f"### `{i:02d}`")
                with col_p:
                    st.write(pt)

        st.download_button(
            "⬇️ Download Key Points (.txt)",
            data=format_key_points_txt(key_points, topic),
            file_name=f"key_points_{topic.replace(' ', '_')}.txt",
            mime="text/plain"
        )

    # ── TAB 4: DEFINITIONS ──
    with tab_definitions:
        st.markdown("### Glossary & Definitions")
        definitions = st.session_state.definitions
        for d in definitions:
            with st.container(border=True):
                st.markdown(f"**{d.get('term', '')}**")
                st.write(d.get("definition", ""))

        st.download_button(
            "⬇️ Download Glossary (.txt)",
            data=format_definitions_txt(definitions, topic),
            file_name=f"definitions_{topic.replace(' ', '_')}.txt",
            mime="text/plain"
        )

    # ── TAB 5: QUIZ ──
    with tab_quiz:
        quiz = st.session_state.quiz
        if not quiz:
            st.info("No quiz questions available.")
        else:
            total_q = len(quiz)

            if st.session_state.quiz_submitted:
                score = st.session_state.quiz_score
                pct = int((score / total_q) * 100)
                st.metric("Final Score", f"{score} / {total_q}", f"{pct}% Correct")

                for i, q in enumerate(quiz):
                    u_ans = st.session_state.quiz_answers.get(i)
                    correct = q["answer"]
                    is_correct = u_ans == correct

                    with st.container(border=True):
                        st.markdown(f"**Question {i+1}: {q['question']}**")
                        if is_correct:
                            st.success(f"✅ Correct! Your answer: {q['options'][u_ans]}")
                        else:
                            st.error(f"❌ Your answer: {q['options'][u_ans] if u_ans is not None else 'Unanswered'}")
                            st.info(f"💡 Correct answer: **{q['options'][correct]}**")
                            st.caption(f"Explanation: {q.get('explanation', '')}")

                col_retake, col_dlq = st.columns([1, 1])
                with col_retake:
                    if st.button("🔄 Retake Quiz", use_container_width=True):
                        st.session_state.quiz_current_q = 0
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_score = 0
                        st.rerun()
                with col_dlq:
                    st.download_button(
                        "⬇️ Download Quiz (.txt)",
                        data=format_quiz_txt(quiz, topic),
                        file_name=f"quiz_{topic.replace(' ', '_')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            else:
                curr_q = st.session_state.quiz_current_q
                q_data = quiz[curr_q]

                st.progress((curr_q + 1) / total_q)
                st.caption(f"Question {curr_q + 1} of {total_q}")

                with st.container(border=True):
                    st.markdown(f"### Question {curr_q + 1}")
                    st.markdown(f"**{q_data['question']}**")

                    opts = q_data["options"]
                    prev_ans = st.session_state.quiz_answers.get(curr_q)

                    selected = st.radio(
                        "Options",
                        options=opts,
                        index=prev_ans if prev_ans is not None else None,
                        key=f"quiz_radio_q_{curr_q}",
                        label_visibility="collapsed"
                    )

                    if selected is not None:
                        st.session_state.quiz_answers[curr_q] = opts.index(selected)

                col_p, col_n, col_s = st.columns([1, 1, 1])
                with col_p:
                    if curr_q > 0:
                        if st.button("← Previous", use_container_width=True):
                            st.session_state.quiz_current_q -= 1
                            st.rerun()
                with col_n:
                    if curr_q < total_q - 1:
                        if st.button("Next →", use_container_width=True):
                            st.session_state.quiz_current_q += 1
                            st.rerun()
                with col_s:
                    if curr_q == total_q - 1 or len(st.session_state.quiz_answers) == total_q:
                        if st.button("✔ Submit Quiz", type="primary", use_container_width=True):
                            calc_score = sum(
                                1 for i, q in enumerate(quiz)
                                if st.session_state.quiz_answers.get(i) == q["answer"]
                            )
                            st.session_state.quiz_score = calc_score
                            st.session_state.quiz_submitted = True
                            st.rerun()

    # ── TAB 6: FLASHCARDS ──
    with tab_flashcards:
        flashcards = st.session_state.flashcards
        if not flashcards:
            st.info("No flashcards available.")
        else:
            total_cards = len(flashcards)
            idx = st.session_state.card_index
            show_back = st.session_state.card_show_back
            card = flashcards[idx]

            st.progress((idx + 1) / total_cards)
            st.caption(f"Card {idx + 1} of {total_cards}")

            with st.container(border=True):
                if show_back:
                    st.info("💡 **Answer / Explanation**")
                    st.markdown(f"### {card['back']}")
                else:
                    st.markdown("❓ **Question / Prompt**")
                    st.markdown(f"### {card['front']}")

            col_cp, col_cf, col_cn = st.columns([1, 2, 1])
            with col_cp:
                if idx > 0:
                    if st.button("← Previous", key="fc_btn_prev", use_container_width=True):
                        st.session_state.card_index -= 1
                        st.session_state.card_show_back = False
                        st.rerun()
            with col_cf:
                label = "🙈 Hide Answer" if show_back else "👁️ Show Answer"
                if st.button(label, type="primary", key="fc_btn_flip", use_container_width=True):
                    st.session_state.card_show_back = not show_back
                    st.rerun()
            with col_cn:
                if idx < total_cards - 1:
                    if st.button("Next →", key="fc_btn_next", use_container_width=True):
                        st.session_state.card_index += 1
                        st.session_state.card_show_back = False
                        st.rerun()

            st.write("")
            col_rst, col_dlf = st.columns([1, 1])
            with col_rst:
                if st.button("↩ Restart Flashcards", use_container_width=True):
                    st.session_state.card_index = 0
                    st.session_state.card_show_back = False
                    st.rerun()
            with col_dlf:
                st.download_button(
                    "⬇️ Download Flashcards (.txt)",
                    data=format_flashcards_txt(flashcards, topic),
                    file_name=f"flashcards_{topic.replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

    # ── DOWNLOAD CENTER ──
    st.divider()
    with st.expander("📦 **Download Complete Study Pack**", expanded=False):
        st.write("Export all study materials, notes, flashcards, and transcript in one comprehensive package.")
        full_pack = format_full_pack_txt(
            topic,
            st.session_state.transcript,
            st.session_state.summary,
            st.session_state.key_points,
            st.session_state.definitions,
            st.session_state.quiz,
            st.session_state.flashcards
        )
        st.download_button(
            "⬇️ Download Complete Study Pack (.txt)",
            data=full_pack,
            file_name=f"study_pack_{topic.replace(' ', '_')}.txt",
            mime="text/plain",
            type="primary",
            use_container_width=True
        )


def render_about():
    st.title("About LectureNote AI")
    st.markdown("LectureNote AI transforms spoken lectures into organized study assets for efficient student revision.")

    with st.container(border=True):
        st.subheader("🎙️ Speech-to-Text")
        st.write("Transcribes long-form audio/video lecture recordings using multimodal AI models.")

    with st.container(border=True):
        st.subheader("📝 Structured Notes & Summaries")
        st.write("Generates comprehensive overviews, core concepts, granular notes, and essential revision takeaways.")

    with st.container(border=True):
        st.subheader("🔑 Key Points & Technical Glossary")
        st.write("Extracts numbered high-impact insights and clear definitions for all technical terminology.")

    with st.container(border=True):
        st.subheader("✏️ Interactive Practice Quiz")
        st.write("Generates multiple-choice assessment questions with real-time scoring, explanations, and retakes.")

    with st.container(border=True):
        st.subheader("🃏 Memorization Flashcards")
        st.write("Provides interactive digital flashcards to support spaced repetition and active recall study sessions.")

# ─────────────────────────────────────────────
# MAIN APPLICATION ENTRY POINT
# ─────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="LectureNote AI",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_session_state()
    render_sidebar()

    page = st.session_state.current_page
    if page == "about":
        render_about()
    elif page == "results" and st.session_state.processing_done:
        render_results()
    else:
        render_home()


if __name__ == "__main__":
    main()
