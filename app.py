
import streamlit as st
import io
import re
from collections import Counter
from pypdf import PdfReader

# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="DocuGenius AI",
    page_icon="📚",
    layout="wide"
)

# =====================================
# PURPLE AND DARK BLUE THEME
# =====================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #10172F, #172554, #241447);
    color: white;
}

.stApp h1, .stApp h2, .stApp h3,
.stApp h4, .stApp p, .stApp label,
.stApp li {
    color: white !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #3B0764, #172554);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.title {
    text-align: center;
    color: #C4B5FD !important;
    font-size: 44px;
    font-weight: 800;
}

.subtitle {
    text-align: center;
    color: #BFDBFE !important;
    font-size: 19px;
}

.card {
    background: linear-gradient(135deg, #31245D, #1E3260);
    padding: 25px;
    border-radius: 16px;
    border: 1px solid #8064D6;
    box-shadow: 0 5px 18px rgba(0,0,0,0.3);
    margin-bottom: 15px;
}

.card h3 {
    color: #C4B5FD !important;
}

.card p {
    color: white !important;
}

.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(90deg, #7C3AED, #2563EB);
    color: white !important;
    border: none;
    border-radius: 10px;
    font-weight: bold;
}

.stTextInput input,
.stTextArea textarea {
    background-color: white !important;
    color: #111827 !important;
    border: 2px solid #8B5CF6 !important;
    border-radius: 8px;
}

[data-testid="stFileUploader"] {
    background: #26345C;
    border: 1px solid #8064D6;
    border-radius: 12px;
    padding: 12px;
}

[data-testid="stMetric"] {
    background: #292653;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #8064D6;
}

[data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {
    color: white !important;
}

hr {
    border-color: #6D5BA6;
}

</style>
""", unsafe_allow_html=True)


# =====================================
# SESSION STATE
# =====================================

defaults = {
    "document_text": "",
    "document_name": "",
    "page_count": 0,
    "chat_history": [],
    "summary": "",
    "file_signature": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =====================================
# TEXT PROCESSING
# =====================================

STOPWORDS = {
    "the", "is", "a", "an", "and", "or", "of", "to",
    "in", "on", "for", "with", "what", "which", "who",
    "when", "where", "why", "how", "are", "was", "were",
    "be", "been", "being", "this", "that", "these",
    "those", "it", "its", "as", "at", "by", "from",
    "do", "does", "did", "can", "could", "would",
    "should", "about", "explain", "tell", "me"
}


def tokenize(text):
    words = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())
    return [word for word in words if word not in STOPWORDS]


def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 20]


# =====================================
# PDF EXTRACTION
# =====================================

def extract_pdf(uploaded_file):

    pdf_bytes = uploaded_file.getvalue()

    reader = PdfReader(io.BytesIO(pdf_bytes))

    pages_text = []

    for number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""

        if text.strip():
            pages_text.append(
                f"PAGE {number}\n{text}"
            )

    document_text = "\n\n".join(pages_text)

    if not document_text.strip():
        raise ValueError(
            "No readable text found. The PDF may be scanned."
        )

    return document_text, len(reader.pages)


# =====================================
# QUESTION ANSWERING
# =====================================

def ask_question(question, document_text):

    sentences = split_sentences(document_text)

    question_words = set(tokenize(question))

    if not question_words:
        return "Please enter a meaningful question."

    scored_sentences = []

    for sentence in sentences:

        sentence_words = set(tokenize(sentence))

        common_words = question_words.intersection(sentence_words)

        if common_words:

            score = len(common_words) / len(question_words)

            scored_sentences.append((score, sentence))

    scored_sentences.sort(
        key=lambda x: x[0],
        reverse=True
    )

    if not scored_sentences:
        return (
            "The answer is not available in the uploaded document."
        )

    best_answers = [
        sentence
        for score, sentence in scored_sentences[:3]
        if score > 0
    ]

    return " ".join(best_answers)


# =====================================
# DOCUMENT SUMMARY
# =====================================

def generate_summary(document_text):

    sentences = split_sentences(document_text)

    if not sentences:
        return "No readable sentences found in the document."

    words = tokenize(document_text)

    word_frequency = Counter(words)

    scored_sentences = []

    for index, sentence in enumerate(sentences):

        sentence_words = tokenize(sentence)

        score = sum(
            word_frequency[word]
            for word in sentence_words
        )

        if sentence_words:
            score = score / len(sentence_words)

        scored_sentences.append((score, index, sentence))

    scored_sentences.sort(
        key=lambda x: x[0],
        reverse=True
    )

    top_sentences = sorted(
        scored_sentences[:5],
        key=lambda x: x[1]
    )

    summary = "\n\n".join(
        sentence for score, index, sentence in top_sentences
    )

    return summary


# =====================================
# SIDEBAR
# =====================================

st.sidebar.markdown(
    """
    <h1 style='text-align:center;color:#C4B5FD;'>
    📚 DocuGenius AI
    </h1>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

st.sidebar.subheader("📂 Upload PDF")

uploaded_file = st.sidebar.file_uploader(
    "Choose your PDF document",
    type=["pdf"]
)


# =====================================
# PROCESS PDF
# =====================================

if uploaded_file is not None:

    signature = (
        uploaded_file.name,
        uploaded_file.size
    )

    if st.session_state.file_signature != signature:

        try:

            with st.spinner("Reading PDF document..."):

                text, pages = extract_pdf(uploaded_file)

                st.session_state.document_text = text
                st.session_state.document_name = uploaded_file.name
                st.session_state.page_count = pages
                st.session_state.file_signature = signature

                st.session_state.chat_history = []
                st.session_state.summary = ""

            st.sidebar.success("PDF uploaded successfully!")

        except Exception as error:

            st.sidebar.error(str(error))


# =====================================
# NAVIGATION
# =====================================

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "💬 Document Q&A",
        "📝 Document Summary",
        "📖 Document Reader",
        "ℹ️ About Project"
    ]
)


# =====================================
# DASHBOARD
# =====================================

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="title">📚 DocuGenius AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Intelligent Document Question Answering System'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")

    st.markdown("## ✨ Welcome!")

    st.write(
        "Upload your PDF document and ask questions. "
        "DocuGenius AI helps you understand your document."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown("""
        <div class="card">
        <h3>📄 PDF Upload</h3>
        <p>Upload PDF documents and extract text.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown("""
        <div class="card">
        <h3>🤖 Document Q&A</h3>
        <p>Ask questions and find relevant answers.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown("""
        <div class="card">
        <h3>📝 Summary</h3>
        <p>Generate automatic document summaries.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if st.session_state.document_text:

        st.success("PDF is ready!")

        col1, col2 = st.columns(2)

        col1.metric(
            "Total Pages",
            st.session_state.page_count
        )

        col2.metric(
            "Extracted Characters",
            f"{len(st.session_state.document_text):,}"
        )

        st.info(
            f"Document: {st.session_state.document_name}"
        )

    else:

        st.info("Upload a PDF from the sidebar to get started.")


# =====================================
# DOCUMENT Q&A
# =====================================

elif page == "💬 Document Q&A":

    st.title("💬 Ask Your Document")

    if not st.session_state.document_text:

        st.warning("Please upload a PDF first.")

    else:

        st.success(
            f"Loaded: {st.session_state.document_name}"
        )

        with st.form("question_form"):

            question = st.text_input(
                "Your Question",
                placeholder="What is the main purpose of this document?"
            )

            submit = st.form_submit_button("🚀 Ask Question")

        if submit:

            if not question.strip():

                st.warning("Please enter a question.")

            else:

                answer = ask_question(
                    question,
                    st.session_state.document_text
                )

                st.session_state.chat_history.append({
                    "question": question,
                    "answer": answer
                })

        st.markdown("---")

        st.subheader("🤖 Document Answer")

        if st.session_state.chat_history:

            for item in reversed(st.session_state.chat_history):

                st.markdown(
                    f"**Question:** {item['question']}"
                )

                st.success(item["answer"])

                st.markdown("---")

        else:

            st.info("Your answer will appear here.")

        if st.button("🗑️ Clear Answer History"):

            st.session_state.chat_history = []

            st.rerun()


# =====================================
# DOCUMENT SUMMARY
# =====================================

elif page == "📝 Document Summary":

    st.title("📝 Document Summary")

    if not st.session_state.document_text:

        st.warning("Please upload a PDF first.")

    else:

        st.success(
            f"Document: {st.session_state.document_name}"
        )

        if st.button("✨ Generate Summary"):

            with st.spinner("Generating summary..."):

                st.session_state.summary = generate_summary(
                    st.session_state.document_text
                )

        if st.session_state.summary:

            st.markdown("---")

            st.subheader("📌 Document Summary")

            st.write(st.session_state.summary)

            st.download_button(
                "⬇️ Download Summary",
                data=st.session_state.summary,
                file_name="document_summary.txt",
                mime="text/plain"
            )


# =====================================
# DOCUMENT READER
# =====================================

elif page == "📖 Document Reader":

    st.title("📖 Document Reader")

    if not st.session_state.document_text:

        st.warning("Please upload a PDF first.")

    else:

        st.success(
            f"Reading: {st.session_state.document_name}"
        )

        st.metric(
            "Total Pages",
            st.session_state.page_count
        )

        st.text_area(
            "Extracted Document Text",
            value=st.session_state.document_text,
            height=500
        )


# =====================================
# ABOUT PROJECT
# =====================================

elif page == "ℹ️ About Project":

    st.title("ℹ️ About DocuGenius AI")

    st.markdown("""
    ## 📚 DocuGenius AI

    **Intelligent Document Question Answering System**

    DocuGenius AI is a document processing application
    that helps users understand PDF documents.

    ### ✨ Main Features

    - PDF Upload
    - PDF Text Extraction
    - Document Question Answering
    - Relevant Sentence Matching
    - Automatic Extractive Summary
    - Document Reader
    - Answer History
    - Summary Download

    ### 💻 Technologies Used

    - Python
    - Streamlit
    - PyPDF
    - Python Text Processing

    ### 🎓 Project Category

    Document Processing Application
    """)


# =====================================
# FOOTER
# =====================================

st.sidebar.markdown("---")

st.sidebar.caption(
    "Made with ❤️ using Python and Streamlit"
)
