
import streamlit as st
import io
from pypdf import PdfReader
from google import genai

# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="DocuGenius AI",
    page_icon="📚",
    layout="wide"
)

# =====================================
# PURPLE & DARK BLUE DESIGN
# =====================================

st.markdown("""
<style>

/* Main background */
.stApp {
    background: linear-gradient(135deg, #10172F, #172554, #241447);
    color: #FFFFFF;
}

/* Main text */
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp p,
.stApp label,
.stApp li {
    color: #FFFFFF !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #3B0764, #172554);
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

/* Main title */
.title {
    text-align: center;
    color: #C4B5FD !important;
    font-size: 44px;
    font-weight: 800;
}

/* Subtitle */
.subtitle {
    text-align: center;
    color: #BFDBFE !important;
    font-size: 19px;
}

/* Cards */
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
    color: #FFFFFF !important;
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(90deg, #7C3AED, #2563EB);
    color: #FFFFFF !important;
    border: none;
    border-radius: 10px;
    padding: 8px 20px;
    font-weight: bold;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: linear-gradient(90deg, #9333EA, #3B82F6);
    color: white !important;
    border: 1px solid #C4B5FD;
}

/* Text input */
.stTextInput input,
.stTextArea textarea {
    background-color: #FFFFFF !important;
    color: #111827 !important;
    border: 2px solid #8B5CF6 !important;
    border-radius: 8px;
}

/* Input placeholder */
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #6B7280 !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #26345C;
    border: 1px solid #8064D6;
    border-radius: 12px;
    padding: 12px;
    color: white !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #292653;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #8064D6;
}

[data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {
    color: #FFFFFF !important;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 10px;
}

/* Radio buttons */
.stRadio label {
    color: white !important;
}

/* Select boxes */
.stSelectbox div[data-baseweb="select"] {
    background-color: white;
    color: #111827;
}

/* Horizontal line */
hr {
    border-color: #6D5BA6;
}

/* Spinner */
.stSpinner {
    color: #C4B5FD !important;
}

/* Links */
.stApp a {
    color: #A5B4FC !important;
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
# GEMINI AI FUNCTION
# =====================================

def call_gemini(prompt, api_key):

    if not api_key.strip():
        raise ValueError("Please enter your Gemini API Key.")

    client = genai.Client(api_key=api_key.strip())

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    if not response.text:
        raise Exception("AI did not return an answer.")

    return response.text.strip()


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
# QUESTION ANSWERING FUNCTION
# =====================================

def ask_question(question, document_text, api_key):

    prompt = f"""
You are DocuGenius AI, an intelligent PDF assistant.

Answer the user's question using ONLY the uploaded document.

Instructions:
1. Give only ONE complete and direct answer.
2. Use simple and easy English.
3. Do not show multiple results or scores.
4. Do not repeat the question.
5. Give a short paragraph unless more detail is necessary.
6. Do not invent information.
7. If the answer is not available in the document,
clearly say:
"The answer is not available in the uploaded document."

UPLOADED DOCUMENT:
{document_text[:30000]}

USER QUESTION:
{question}

Now provide one final answer:
"""

    return call_gemini(prompt, api_key)


# =====================================
# SUMMARY FUNCTION
# =====================================

def generate_summary(document_text, api_key):

    prompt = f"""
Summarize the uploaded document in simple English.

Include:
1. Introduction
2. Main Purpose
3. Important Points
4. Conclusion

Use clear headings and short explanations.

DOCUMENT:
{document_text[:30000]}
"""

    return call_gemini(prompt, api_key)


# =====================================
# SIDEBAR
# =====================================

st.sidebar.markdown(
    """
    <h1 style='text-align:center; color:#C4B5FD;'>
    📚 DocuGenius AI
    </h1>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

st.sidebar.subheader("🔐 Gemini API Key")

api_key = st.sidebar.text_input(
    "Enter Gemini API Key",
    type="password",
    placeholder="Paste your API key"
)

st.sidebar.markdown("---")

st.sidebar.subheader("📂 Upload PDF")

uploaded_file = st.sidebar.file_uploader(
    "Choose PDF",
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
        "Gemini AI will help you understand your document."
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
        <h3>🤖 AI Answers</h3>
        <p>Ask questions and receive one complete answer.</p>
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

        st.info(
            "Upload a PDF from the sidebar to get started."
        )


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

            submit = st.form_submit_button("🚀 Ask AI")

        if submit:

            if not question.strip():

                st.warning("Please enter a question.")

            elif not api_key.strip():

                st.error("Please enter your Gemini API Key.")

            else:

                try:

                    with st.spinner("🤖 Generating your answer..."):

                        answer = ask_question(
                            question,
                            st.session_state.document_text,
                            api_key
                        )

                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": answer
                    })

                except Exception as error:

                    st.error(str(error))

        st.markdown("---")

        st.subheader("🤖 AI Answer")

        if st.session_state.chat_history:

            latest = st.session_state.chat_history[-1]

            st.markdown(
                f"**Question:** {latest['question']}"
            )

            st.success(latest["answer"])

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

            if not api_key.strip():

                st.error("Please enter your Gemini API Key.")

            else:

                try:

                    with st.spinner("Generating summary..."):

                        summary = generate_summary(
                            st.session_state.document_text,
                            api_key
                        )

                    st.session_state.summary = summary

                except Exception as error:

                    st.error(str(error))

        if st.session_state.summary:

            st.markdown("---")

            st.subheader("📌 AI Summary")

            st.markdown(st.session_state.summary)


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

    DocuGenius AI is an AI-powered application
    that helps users understand PDF documents.

    ### ✨ Main Features

    - 📄 PDF Upload
    - 📖 PDF Text Extraction
    - 🤖 AI Question Answering
    - 💬 One Complete Answer
    - 📝 Automatic PDF Summary
    - 📚 Document Reader
    - 🗂️ Answer History

    ### 💻 Technologies

    - Python
    - Streamlit
    - Google Gemini API
    - PyPDF

    ### 🎓 Project Category

    Generative Artificial Intelligence
    """)


# =====================================
# FOOTER
# =====================================

st.sidebar.markdown("---")

st.sidebar.caption(
    "Made with ❤️ using Python and Gemini AI"
)
