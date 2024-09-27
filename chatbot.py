import streamlit as st
from groq import Groq
import fitz  # PyMuPDF

# Hardcoded credentials
GROQ_API_KEY = "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"

# Function to initialize the Groq client
def initialize_groq_client(api_key):
    try:
        return Groq(api_key=api_key)
    except Exception as e:
        st.error(f"Error initializing Groq client: {e}")
        return None

def assistant_response(client, input_text, context=None):
    system_prompt = "You are a helpful assistant to solve user query on an education platform. Give concise answers to provide solutions to the user."

    conversation = f"{context}\nUser: {input_text}\nAssistant:" if context else f"User: {input_text}\nAssistant:"

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": conversation}
            ],
            model="llama3-70b-8192",
            temperature=0.5
        )
        response = chat_completion.choices[0].message.content
        return response
    except Exception as e:
        st.error(f"Error generating chat completion: {e}")
        return "An error occurred while generating the response."

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_file):
    text = ""
    # Use PyMuPDF to read the PDF file from the uploaded file object
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# Streamlit app
def main():
    st.set_page_config(page_title="Educational Assistant Chatbot", page_icon=":books:")

    st.title("📚 Educational Assistant Chatbot")

    # Initialize Groq client
    client_groq = initialize_groq_client(GROQ_API_KEY)
    if client_groq is None:
        st.error("Failed to initialize the Groq client. Please check your API key.")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I assist you today?"}]
        st.session_state["pdf_text"] = ""  # Initialize pdf_text in session state

    # Sidebar for PDF upload
    st.sidebar.header("Upload PDF")
    pdf_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")

    if pdf_file is not None:
        try:
            # Extract text from the uploaded PDF
            pdf_text = extract_text_from_pdf(pdf_file)
            # Store the extracted text in session state without displaying it
            st.session_state.pdf_text = pdf_text
            st.sidebar.success("PDF text extracted successfully!")
        except Exception as e:
            st.sidebar.error(f"Error extracting text from PDF: {e}")

    # Handle user input
    user_input = st.chat_input("Enter your question:")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Prepare context including the extracted PDF text
        context = st.session_state.pdf_text + "\n" + "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages])

        # Generate assistant response
        try:
            full_response = assistant_response(client_groq, user_input, context=context)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"An error occurred while generating the response: {e}")

    # Display chat messages
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            st.chat_message("assistant").write(msg["content"])
        elif msg["role"] == "user":
            st.chat_message("user").write(msg["content"])

if __name__ == "__main__":
    main()
