import streamlit as st
import re
import io
from collections import Counter
from difflib import get_close_matches
from pypdf import PdfReader

# =====================================================
# PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="DocuGenius AI",
    page_icon="📘",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #090B25, #171044, #25145A);
    color: white;
}
[data-testid="stSidebar"] {
    background: #160D38;
}
h1, h2, h3, h4, p, label {
    color: white !important;
}
.card {
    background: #25184F;
    padding: 22px;
    border-radius: 15px;
    border: 1px solid #6545B5;
    margin-bottom: 15px;
}
.answer-box {
    background: #201747;
    border-left: 5px solid #9B70FF;
    padding: 20px;
    border-radius: 10px;
    color: white;
    margin-top: 12px;
}
.stButton > button {
    background: linear-gradient(90deg, #7139D5, #3158C9);
    color: white;
    border: none;
    border-radius: 9px;
    padding: 10px 20px;
    font-weight: bold;
}
.stButton > button:hover {
    background: #8B5CF6;
    color: white;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background-color: white;
    color: black;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATE
# =====================================================
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "file_name" not in st.session_state:
    st.session_state.file_name = ""
if "history" not in st.session_state:
    st.session_state.history = []

# =====================================================
# BUILT-IN QUESTION AND ANSWER DATABASE
# Add more questions using the same format.
# =====================================================
AI_KNOWLEDGE = {
    "what is a dataset in ai":
        "A dataset is a collection of data used to train, validate, or test an AI model.",
    "what is artificial intelligence":
        "Artificial Intelligence (AI) is a branch of computer science that enables machines to perform tasks that normally require human intelligence.",
    "what is ai":
        "Artificial Intelligence (AI) is technology that enables machines to perform tasks that normally require human intelligence.",
    "what is machine learning":
        "Machine Learning is a branch of AI that allows computers to learn from data and improve their performance without being explicitly programmed.",
    "what is deep learning":
        "Deep Learning is a subset of machine learning that uses artificial neural networks to learn from large amounts of data.",
    "what is supervised learning":
        "Supervised learning is a type of machine learning where a model is trained using labeled data.",
    "what is unsupervised learning":
        "Unsupervised learning is a type of machine learning where a model learns patterns from unlabeled data.",
    "what is reinforcement learning":
        "Reinforcement learning is a type of machine learning in which an agent learns by interacting with an environment and receiving rewards or penalties.",
    "what is neural network":
        "A neural network is a computing model inspired by the human brain that learns patterns from data.",
    "what is natural language processing":
        "Natural Language Processing (NLP) is a field of AI that enables computers to understand, interpret, and generate human language.",
    "what is computer vision":
        "Computer vision is a field of AI that enables computers to understand and analyze images and videos.",
    "what is an algorithm":
        "An algorithm is a step-by-step procedure used to solve a problem or perform a specific task.",
    "what is chatbot":
        "A chatbot is a software application that communicates with users through text or voice.",
    "what is generative ai":
        "Generative AI is a type of artificial intelligence that creates new content such as text, images, audio, and videos.",
    "what is training data":
        "Training data is the information used to teach a machine learning model to recognize patterns and make predictions.",
    "what is testing data":
        "Testing data is a separate dataset used to evaluate how well a trained machine learning model performs on unseen data.",
    "what is validation data":
        "Validation data is used to evaluate a machine learning model during training and help tune its parameters.",
    "what is classification":
        "Classification is a machine learning task that assigns data to predefined categories or classes.",
    "what is regression":
        "Regression is a machine learning technique used to predict continuous numerical values.",
    "what is overfitting":
        "Overfitting occurs when a machine learning model learns the training data too closely and performs poorly on new data.",
    "what is underfitting":
        "Underfitting occurs when a machine learning model is too simple to understand the patterns in the training data.",
    "what is an epoch":
        "An epoch is one complete pass of the entire training dataset through a machine learning model.",
    "what is a feature":
        "A feature is an individual measurable property or characteristic used as input for a machine learning model.",
    "what is a label":
        "A label is the correct output or target value associated with a data sample in supervised learning.",
    "what is data science":
        "Data Science is a field that uses scientific methods, statistics, and programming to extract useful information from data.",
    "what is python":
        "Python is a high-level, interpreted programming language known for its simple syntax and wide range of applications.",
    "what is artificial neural network":
        "An Artificial Neural Network (ANN) is a computational model inspired by the structure and working of the human brain.",
    "what is big data":
        "Big Data refers to extremely large and complex datasets that require advanced tools and techniques for processing and analysis.",
    "what is data mining":
        "Data Mining is the process of discovering useful patterns, relationships, and information from large datasets.",
    "what is model training":
        "Model training is the process of teaching a machine learning model using data so it can make predictions or decisions.",
    "what is prediction":
        "Prediction is the process of using a trained model to estimate an outcome based on new input data.",
    "what is accuracy":
        "Accuracy is the proportion of correct predictions made by a machine learning model out of all predictions.",
    "what is precision":
        "Precision measures how many of the positive predictions made by a model are actually positive.",
    "what is recall":
        "Recall measures how many actual positive cases a model correctly identifies.",
    "what is an ai model":
        "An AI model is a computational system trained on data to recognize patterns, make predictions, or perform intelligent tasks.",
    "what is tensorflow":
        "TensorFlow is an open-source machine learning framework used to build and train AI models.",
    "what is pandas":
        "Pandas is a Python library used for data manipulation and analysis.",
    "what is numpy":
        "NumPy is a Python library used for numerical computing and working with arrays.",
    "what is streamlit":
        "Streamlit is a Python framework used to create interactive web applications, especially for data science and machine learning projects.",
    "what is a prompt":
        "A prompt is an instruction or input given to an AI system to generate a response or perform a task.",
    "what is robotics":
        "Robotics is a field of engineering and computer science that focuses on designing, building, and operating robots.",
    "what is automation":
        "Automation is the use of technology to perform tasks with minimal human intervention."
}

# =====================================================
# TEXT PROCESSING
# =====================================================
STOP_WORDS = {
    "what", "is", "are", "the", "a", "an", "of", "in", "on",
    "and", "to", "for", "how", "does", "do", "explain", "define",
    "tell", "me", "about", "can", "you", "give", "describe",
    "with", "from", "this", "that", "it", "its", "which", "who"
}

def normalize_question(text):
    text = re.sub(r"[^a-zA-Z0-9 ]", "", text.lower())
    return " ".join(text.split())

def tokenize(text):
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [word for word in words if word not in STOP_WORDS and len(word) > 1]

def split_sentences(text):
    text = re.sub(r"\s+", " ", text)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [sentence.strip() for sentence in sentences if len(sentence.strip()) > 15]

# =====================================================
# PDF TEXT EXTRACTION
# =====================================================
def extract_pdf_text(uploaded_file):
    try:
        reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
        extracted = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted.append(page_text)
        return "\n".join(extracted).strip()
    except Exception as error:
        st.error(f"PDF reading error: {error}")
        return ""

# =====================================================
# QUESTION ANSWERING
# =====================================================
def answer_question(question, document_text=""):
    clean_question = normalize_question(question)

    if not clean_question:
        return "Please enter a meaningful question."

    # First, check the built-in question database.
    if clean_question in AI_KNOWLEDGE:
        return AI_KNOWLEDGE[clean_question]

    # Then, look for a closely matching saved question.
    matches = get_close_matches(
        clean_question, list(AI_KNOWLEDGE.keys()), n=1, cutoff=0.80
    )
    if matches:
        return AI_KNOWLEDGE[matches[0]]

    # If no database answer is found, search the uploaded PDF.
    if document_text.strip():
        question_words = set(tokenize(question))
        scored_sentences = []

        for index, sentence in enumerate(split_sentences(document_text)):
            sentence_words = set(tokenize(sentence))
            score = sum(3 for word in question_words if word in sentence_words)
            if score > 0:
                scored_sentences.append((score, index, sentence))

        if scored_sentences:
            scored_sentences.sort(key=lambda item: item[0], reverse=True)
            selected = scored_sentences[:3]
            selected.sort(key=lambda item: item[1])
            return " ".join(item[2] for item in selected)

    return (
        "Sorry, I could not find the answer in the built-in database "
        "or the uploaded PDF. Try another question or add this question "
        "and its answer to the AI_KNOWLEDGE dictionary in app.py."
    )

# =====================================================
# DOCUMENT SUMMARY
# =====================================================
def generate_summary(text, number_of_sentences=5):
    sentences = split_sentences(text)

    if not sentences:
        return "No readable text is available to summarize."

    if len(sentences) <= number_of_sentences:
        return " ".join(sentences)

    frequencies = Counter(tokenize(text))
    scored = []

    for index, sentence in enumerate(sentences):
        words = tokenize(sentence)
        if words:
            score = sum(frequencies[word] for word in words) / len(words)
            scored.append((score, index, sentence))

    best = sorted(scored, key=lambda item: item[0], reverse=True)
    best = best[:number_of_sentences]
    best.sort(key=lambda item: item[1])

    return " ".join(item[2] for item in best)

# =====================================================
# SIDEBAR NAVIGATION
# =====================================================
st.sidebar.title("📘 DocuGenius AI")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Ask AI", "Document Summary", "Document Reader", "About Project"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "Ask questions using the built-in knowledge database, "
    "or upload a PDF to search its content."
)

# =====================================================
# DASHBOARD
# =====================================================
if page == "Dashboard":
    st.title("📘 DocuGenius AI")
    st.subheader("Your Smart AI Question Answer Assistant")

    st.markdown("""
    <div class="card">
        <h2>Welcome to DocuGenius AI!</h2>
        <p>
        Ask questions and get answers from the built-in knowledge database.
        You can also upload PDF documents, search their content,
        generate summaries, and read extracted text.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="card">
            <h3>🤖 Ask AI</h3>
            <p>Ask questions and get answers from the built-in database.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <h3>📄 PDF Upload</h3>
            <p>Upload a PDF and extract readable text.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
            <h3>📝 Summary</h3>
            <p>Generate a short summary of your PDF document.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Upload Your PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Upload and Process PDF"):
            extracted_text = extract_pdf_text(uploaded_file)

            if extracted_text:
                st.session_state.pdf_text = extracted_text
                st.session_state.file_name = uploaded_file.name
                st.success("PDF uploaded and processed successfully!")
                st.info(
                    f"File: {uploaded_file.name} | "
                    f"Characters extracted: {len(extracted_text)}"
                )
            else:
                st.error(
                    "No readable text was found. The PDF may be scanned "
                    "or image-based."
                )

    if st.session_state.pdf_text:
        st.success(f"Currently loaded: {st.session_state.file_name}")

# =====================================================
# ASK AI
# =====================================================
elif page == "Ask AI":
    st.title("🤖 Ask DocuGenius AI")
    st.write("Enter a question below to get an answer.")

    st.info("You can ask general AI questions without uploading a PDF.")

    question = st.text_input(
        "Enter your question",
        placeholder="Example: What is a dataset in AI?"
    )

    if st.button("Get Answer"):
        if question.strip():
            answer = answer_question(question, st.session_state.pdf_text)

            st.markdown("### Answer")
            st.markdown(
                f'<div class="answer-box">{answer}</div>',
                unsafe_allow_html=True
            )

            st.session_state.history.append({
                "question": question,
                "answer": answer
            })
        else:
            st.warning("Please enter a question.")

    st.markdown("### Example Questions")
    examples = [
        "What is a dataset in AI?",
        "What is machine learning?",
        "What is deep learning?",
        "What is supervised learning?",
        "What is a neural network?",
        "What is artificial intelligence?"
    ]
    for example in examples:
        st.write("•", example)

    if st.session_state.history:
        st.markdown("---")
        st.markdown("### Question History")

        for item in reversed(st.session_state.history):
            with st.expander(item["question"]):
                st.write(item["answer"])

        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()

# =====================================================
# DOCUMENT SUMMARY
# =====================================================
elif page == "Document Summary":
    st.title("📝 Document Summary")

    if not st.session_state.pdf_text:
        st.warning("Please upload a PDF from the Dashboard first.")
    else:
        st.success(f"Document loaded: {st.session_state.file_name}")

        number = st.slider(
            "Number of sentences in summary",
            min_value=3,
            max_value=15,
            value=5
        )

        if st.button("Generate Summary"):
            summary = generate_summary(st.session_state.pdf_text, number)
            st.markdown("### Document Summary")
            st.markdown(
                f'<div class="answer-box">{summary}</div>',
                unsafe_allow_html=True
            )

# =====================================================
# DOCUMENT READER
# =====================================================
elif page == "Document Reader":
    st.title("📖 Document Reader")

    if not st.session_state.pdf_text:
        st.warning("Please upload a PDF from the Dashboard first.")
    else:
        st.success(f"Reading: {st.session_state.file_name}")
        st.text_area(
            "Extracted PDF Content",
            value=st.session_state.pdf_text,
            height=500
        )

# =====================================================
# ABOUT PROJECT
# =====================================================
elif page == "About Project":
    st.title("ℹ️ About DocuGenius AI")

    st.markdown("""
    <div class="card">
        <h2>Project Introduction</h2>
        <p>
        DocuGenius AI is a question-answering application developed
        using Python and Streamlit. It answers supported questions
        using a built-in knowledge database and can also extract
        and search text from uploaded PDF documents.
        </p>

        <h3>Main Features</h3>
        <ul>
            <li>Built-in question and answer database</li>
            <li>Ask questions without uploading a PDF</li>
            <li>PDF document upload and text extraction</li>
            <li>Question answering from PDF content</li>
            <li>Document summarization</li>
            <li>Document reader</li>
            <li>Question history</li>
        </ul>

        <h3>Technology Used</h3>
        <ul>
            <li>Python</li>
            <li>Streamlit</li>
            <li>PyPDF</li>
            <li>Regular Expressions</li>
            <li>Python Fuzzy Matching</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.caption(
        "This no-API version uses predefined answers, fuzzy matching, "
        "and PDF keyword matching. It is not a live generative AI model."
    )

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.markdown(
    "<center>© 2026 DocuGenius AI | Smart AI Assistant</center>",
    unsafe_allow_html=True
)
