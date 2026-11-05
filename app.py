elif page == "💬 Document Q&A":

    st.title("💬 Ask Your Document")

    if not st.session_state.document_text:
        st.warning("Please upload a PDF first.")

    else:
        question = st.text_input(
            "Enter your question",
            placeholder="What is Artificial Intelligence?"
        )

        if st.button("🚀 Ask AI"):

            if not question.strip():
                st.warning("Please enter a question.")

            elif not api_key.strip():
                st.error("Please enter your Gemini API Key.")

            else:
                try:
                    with st.spinner("Generating answer..."):

                        answer = ask_question(
                            question,
                            st.session_state.document_text,
                            api_key
                        )

                    st.markdown("---")
                    st.subheader("🤖 AI Answer")

                    # Display only one complete answer
                    st.write(answer)

                except Exception as error:
                    st.error(str(error))
