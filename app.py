
import streamlit as st
import re
import io
from collections import Counter
from pypdf import PdfReader

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="DocuGenius AI",
    page_icon="📘",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #090B25, #171044, #25145A);
    color: white;
}

[data-testid="stSidebar"] {
    background: #160D38;
}

h1, h2, h3, p, label {
    color: white !important;
}

.card {
    background: #25184F;
    padding: 22px;
    border-radius: 15px;
    border: 1px solid #6545B5;
    margin-bottom: 15px;
}

.stButton > button {
    background: linear-gradient(90deg, #7139D5, #3158C9);
    color: white;
    border: none;
    border-radius: 9px;
    padding: 10px 20px;
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

.answer-box {
    background: #201747;
    border-left: 5px solid #9B70FF;
    padding: 18px;
    border-radius: 10px;
    color: white;
    margin-top: 12px;
}
</style>
""", unsafe_allow_html=True)


# ---------------- SESSION STATE ----------------

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "file_name" not in st.session_state:
    st.session_state.file_name = ""

if "history" not in st.session_state:
    st.session_state.history = []


# ---------------- PDF TEXT EXTRACTION ----------------

def extract_pdf_text(uploaded_file):
    try:
        pdf_bytes = uploaded_file.getvalue()
        reader = PdfReader(io.BytesIO(pdf_bytes))

        text = ""

        for page_number, page in enumerate(reader.pages):
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text.strip()

    except Exception as e:
        st.error(f"PDF reading error: {e}")
        return ""


# ---------------- TEXT PROCESSING ----------------

STOP_WORDS = {
    "what", "is", "are", "the", "a", "an", "of",
    "in", "on", "and", "to", "for", "how", "does",
    "do", "explain", "define", "tell", "me", "about",
    "can", "you", "give", "describe", "with", "from",
    "this", "that", "it", "its", "which", "who"
}


def tokenize(text):
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())

    return [
        word for word in words
        if word not in STOP_WORDS and len(word) > 1
    ]


def split_sentences(text):
    text = re.sub(r"\s+", " ", text)

    sentences = re.split(r"(?<=[.!?])\s+", text)

    return [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) > 15
    ]


# ---------------- IMPROVED QUESTION ANSWERING ----------------

def answer_question(question, document_text):

    if not document_text.strip():
        return "Please upload a PDF document first."

    question_words = tokenize(question)

    if not question_words:
        return "Please enter a meaningful question."

    sentences = split_sentences(document_text)

    if not sentences:
        return "No readable text was found in the PDF."

    scored_sentences = []

    for index, sentence in enumerate(sentences):

        sentence_words = tokenize(sentence)
        sentence_set = set(sentence_words)

        score = 0

        # Match important question words
        for word in question_words:

            if word in sentence_set:
                score += 3

            # Partial word matching
            elif any(
                len(word) > 4 and
                len(existing) > 4 and
                (word.startswith(existing[:5]) or
                 existing.startswith(word[:5]))
                for existing in sentence_set
            ):
                score += 1

        # Give extra score for exact phrase matches
        if question.lower().rstrip("?") in sentence.lower():
            score += 5

        # Give extra score to sentences containing key terms
        if score > 0:
            scored_sentences.append((score, index, sentence))

    if not scored_sentences:
        return (
            "Sorry, the answer was not found in the uploaded PDF. "
            "Try asking the question using different keywords."
        )

    # Sort sentences by relevance
    scored_sentences.sort(
        key=lambda item: item[0],
        reverse=True
    )

    # Select the best matching sentences
    selected = scored_sentences[:3]

    # Keep the original document order
    selected.sort(key=lambda item: item[1])

    answer = " ".join(
        sentence for score, index, sentence in selected
    )

    return answer


# ---------------- DOCUMENT SUMMARY ----------------

def generate_summary(text, number_of_sentences=5):

    sentences = split_sentences(text)

    if not sentences:
        return "No text available to summarize."

    if len(sentences) <= number_of_sentences:
        return " ".join(sentences)

    words = tokenize(text)
    word_frequency = Counter(words)

    sentence_scores = []

    for index, sentence in enumerate(sentences):

        sentence_words = tokenize(sentence)

        if not sentence_words:
            continue

        score = sum(
            word_frequency[word]
            for word in sentence_words
        ) / len(sentence_words)

        sentence_scores.append((score, index, sentence))

    best_sentences = sorted(
        sentence_scores,
        key=lambda item: item[0],
        reverse=True
    )[:number_of_sentences]

    best_sentences.sort(key=lambda item: item[1])

    return " ".join(
        sentence for score, index, sentence in best_sentences
    )


# ---------------- SIDEBAR NAVIGATION ----------------

st.sidebar.title("📘 DocuGenius AI")

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Document Q&A",
        "Document Summary",
        "Document Reader",
        "About Project"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("Your PDF processing is performed locally.")


# ---------------- DASHBOARD ----------------

if page == "Dashboard":

    st.title("📘 DocuGenius AI")
    st.subheader("Your Smart PDF Assistant")

    st.markdown("""
    <div class="card">
        <h2>Welcome to DocuGenius AI!</h2>
        <p>
        Upload your PDF documents, ask questions,
        generate summaries and read document content
        easily with this application.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="card">
            <h3>📄 PDF Upload</h3>
            <p>Upload and extract PDF document text.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <h3>❓ Document Q&A</h3>
            <p>Ask questions and find answers in your PDF.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
            <h3>📝 Summary</h3>
            <p>Generate a short summary of your document.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Upload Your PDF")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"]
    )

    if uploaded_file is not None:

        if st.button("Upload and Process PDF"):

            extracted_text = extract_pdf_text(uploaded_file)

            if extracted_text:

                st.session_state.pdf_text = extracted_text
                st.session_state.file_name = uploaded_file.name

                st.success("PDF uploaded successfully!")

                st.info(
                    f"File: {uploaded_file.name} | "
                    f"Characters extracted: {len(extracted_text)}"
                )

            else:
                st.error(
                    "No readable text found. "
                    "The PDF may be scanned or image-based."
                )

    if st.session_state.pdf_text:
        st.success(
            f"Currently loaded: {st.session_state.file_name}"
        )


# ---------------- DOCUMENT Q&A ----------------

elif page == "Document Q&A":

    st.title("❓ Document Question & Answer")

    if not st.session_state.pdf_text:

        st.warning(
            "Please upload a PDF from the Dashboard first."
        )

    else:

        st.success(
            f"Document loaded: {st.session_state.file_name}"
        )

        question = st.text_input(
            "Enter your question",
            placeholder="Example: What is supervised learning?"
        )

        if st.button("Get Answer"):

            if question.strip():

                answer = answer_question(
                    question,
                    st.session_state.pdf_text
                )

                st.markdown(
                    f"""
                    <div class="answer-box">
                        <h3>Answer</h3>
                        {answer}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.session_state.history.append(
                    {
                        "question": question,
                        "answer": answer
                    }
                )

            else:
                st.warning("Please enter a question.")

        if st.session_state.history:

            st.markdown("### Question History")

            for item in reversed(st.session_state.history):

                with st.expander(item["question"]):
                    st.write(item["answer"])


# ---------------- DOCUMENT SUMMARY ----------------

elif page == "Document Summary":

    st.title("📝 Document Summary")

    if not st.session_state.pdf_text:

        st.warning(
            "Please upload a PDF from the Dashboard first."
        )

    else:

        st.success("Document is ready for summarization.")

        number = st.slider(
            "Number of sentences in summary",
            min_value=3,
            max_value=15,
            value=5
        )

        if st.button("Generate Summary"):

            summary = generate_summary(
                st.session_state.pdf_text,
                number
            )

            st.markdown(
                f"""
                <div class="answer-box">
                    <h3>Document Summary</h3>
                    {summary}
                </div>
                """,
                unsafe_allow_html=True
            )


# ---------------- DOCUMENT READER ----------------

elif page == "Document Reader":

    st.title("📖 Document Reader")

    if not st.session_state.pdf_text:

        st.warning(
            "Please upload a PDF from the Dashboard first."
        )

    else:

        st.success(
            f"Reading: {st.session_state.file_name}"
        )

        st.text_area(
            "Extracted PDF Content",
            value=st.session_state.pdf_text,
            height=500
        )


# ---------------- ABOUT PROJECT ----------------

elif page == "About Project":

    st.title("ℹ️ About DocuGenius AI")

    st.markdown("""
    <div class="card">
        <h2>Project Introduction</h2>
        <p>
        DocuGenius AI is a PDF assistant application developed
        using Python and Streamlit. It allows users to upload
        PDF files, extract text, ask questions, and generate
        short summaries.
        </p>

        <h3>Main Features</h3>
        <ul>
            <li>PDF document upload</li>
            <li>Text extraction from PDF</li>
            <li>Question answering using keyword matching</li>
            <li>Document summarization</li>
            <li>Document reading</li>
            <li>Question history</li>
        </ul>

        <h3>Technology Used</h3>
        <ul>
            <li>Python</li>
            <li>Streamlit</li>
            <li>PyPDF</li>
            <li>Regular Expressions</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.caption(
        "Note: This version uses local text processing, "
        "not a generative AI model. Its answers depend on "
        "the readable text extracted from the uploaded PDF."
    )


# ---------------- FOOTER ----------------

st.markdown("---")

st.markdown(
    "<center>© 2026 DocuGenius AI | PDF Assistant</center>",
    unsafe_allow_html=True
)
