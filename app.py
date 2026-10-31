
import streamlit as st
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Page configuration
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🧠",
    layout="wide"
)

# Custom design
st.markdown("""
<style>
.stApp {
    background-color: #10131d;
    color: white;
}
h1, h2, h3 {
    color: #ffc078 !important;
}
section[data-testid="stSidebar"] {
    background-color: #171b27;
}
</style>
""", unsafe_allow_html=True)

# Session storage
if "text" not in st.session_state:
    st.session_state.text = ""

if "chunks" not in st.session_state:
    st.session_state.chunks = []

if "filename" not in st.session_state:
    st.session_state.filename = ""

# Sidebar
st.sidebar.title("🧠 DocuMind AI")
st.sidebar.caption("INTELLIGENT DOCUMENT ASSISTANT")

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Documents", "AI Assistant"]
)

if st.sidebar.button("Clear Session"):
    st.session_state.text = ""
    st.session_state.chunks = []
    st.session_state.filename = ""
    st.rerun()


# PDF text extraction
def extract_pdf(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text, len(reader.pages)


# Text chunking
def split_text(text, size=900):
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) <= size:
            current += " " + sentence
        else:
            if current.strip():
                chunks.append(current.strip())
            current = sentence

    if current.strip():
        chunks.append(current.strip())

    return chunks


# Find relevant information
def find_answer(question, chunks):
    if not chunks:
        return []

    documents = chunks + [question]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        matrix[-1],
        matrix[:-1]
    ).flatten()

    best = similarity.argsort()[::-1][:3]

    return [
        (chunks[i], similarity[i])
        for i in best
        if similarity[i] > 0
    ]


# HOME PAGE
if page == "Home":

    st.title("🧠 DocuMind AI")
    st.subheader("Intelligent Document Question Answering System")

    col1, col2, col3 = st.columns(3)

    col1.info("📄 Upload PDF")
    col2.info("🔍 Explore Documents")
    col3.info("💬 Ask Questions")

    st.divider()

    st.header("Upload Your Document")

    file = st.file_uploader(
        "Choose PDF file",
        type=["pdf"]
    )

    if file is not None:

        if st.button("Process PDF"):

            with st.spinner("Processing document..."):

                text, pages = extract_pdf(file)

                if text.strip():

                    st.session_state.text = text
                    st.session_state.chunks = split_text(text)
                    st.session_state.filename = file.name

                    st.success("PDF uploaded successfully!")

                    st.write("File:", file.name)
                    st.write("Total Pages:", pages)
                    st.write(
                        "Text Sections:",
                        len(st.session_state.chunks)
                    )

                else:
                    st.error(
                        "No readable text found in PDF."
                    )

    if st.session_state.filename:
        st.success(
            f"Current Document: {st.session_state.filename}"
        )


# DOCUMENT PAGE
elif page == "Documents":

    st.title("📚 Explore Documents")

    if st.session_state.text:

        st.subheader(st.session_state.filename)

        st.write(
            "Total Characters:",
            len(st.session_state.text)
        )

        st.write(
            "Total Text Sections:",
            len(st.session_state.chunks)
        )

        st.text_area(
            "Extracted PDF Text",
            st.session_state.text[:12000],
            height=400
        )

    else:
        st.warning(
            "Please upload a PDF document first."
        )


# AI ASSISTANT PAGE
elif page == "AI Assistant":

    st.title("💬 AI Document Assistant")

    if st.session_state.text:

        st.write(
            f"Ask questions about {st.session_state.filename}"
        )

        question = st.text_input(
            "Enter your question",
            placeholder="What is the main objective?"
        )

        if st.button("Find Answer"):

            if question.strip():

                results = find_answer(
                    question,
                    st.session_state.chunks
                )

                if results:

                    st.subheader("Relevant Information")

                    for i, (answer, score) in enumerate(
                        results, 1
                    ):

                        with st.expander(
                            f"Result {i} | Score: {score:.3f}"
                        ):
                            st.write(answer)

                else:
                    st.warning(
                        "No relevant information found."
                    )

            else:
                st.warning("Please enter a question.")

    else:
        st.warning(
            "Upload and process a PDF first."
        )

st.sidebar.markdown("---")
st.sidebar.caption("Powered by Python and Streamlit")
