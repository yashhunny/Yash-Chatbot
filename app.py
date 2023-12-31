import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from html_chatbot_template import css, bot_template, user_template


def extract_text(pdf_files):
    """
    Function to extract the text from a PDF file

    Args:
        pdf_file (file): The PDF files to extract the text from

    Returns:
        text (str): The extracted text from the PDF file
    """

    # Initialize the raw text variable
    text = ""

    # Iterate over the documents
    for pdf_file in pdf_files:
        #print("[INFO] Extracting text from {}".format(pdf_file.name))

        # Read the PDF file
        pdf_reader = PdfReader(pdf_file)

        # Extract the text from the PDF pages and add it to the raw text variable
        for page in pdf_reader.pages:
            text += page.extract_text()
    
    return text

def get_chunks(text):
    """
    Function to get the chunks of text from the raw text

    Args:
        text (str): The raw text from the PDF file

    Returns:
        chunks (list): The list of chunks of text
    """

    # Initialize the text splitter
    splitter = CharacterTextSplitter(
        separator="\n", # Split the text by new line
        chunk_size=1000, # Split the text into chunks of 1000 characters
        chunk_overlap=200, # Overlap the chunks by 200 characters
        length_function=len # Use the length function to get the length of the text
    )

    # Get the chunks of text
    chunks = splitter.split_text(text)

    return chunks

def get_vectorstore(chunks):
    """
    Function to create avector store for the chunks of text to store the embeddings

    Args:
        chunks (list): The list of chunks of text

    Returns:
        vector_store (FAISS): The vector store for the chunks of text
    """

    # Initialize the embeddings model to get the embeddings for the chunks of text
    embeddings = OpenAIEmbeddings()

    # Create a vector store for the chunks of text embeddings
    # Can use any other online vector store (Elasticsearch, PineCone, etc.)
    vector_store = FAISS.from_texts(texts=chunks, embedding=embeddings)

    return vector_store

def get_conversation_chain(vector_store):
    """
    Function to create a conversation chain for the chat model

    Args:
        vector_store (FAISS): The vector store for the chunks of text
    
    Returns:
        conversation_chain (ConversationRetrievalChain): The conversation chain for the chat model
    """
    
    # Initialize the chat model using Langchain OpenAi API
    # Set the temperature and select the model to use
    # Can replace this with any other chat model (Llama, Falcom, etc.)
    llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.1)

    # Initialize the chat memory
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Create a conversation chain for the chat model
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, # Chat model
        retriever=vector_store.as_retriever(), # Vector store
        memory=memory, # Chat memory
    )

    return conversation_chain

def generate_response(question):
    """
    Function to generate a response for the user query using the chat model

    Args:
        question (str): The user query

    Returns:
        response (str): The response from the chat model
    """

    # Get the response from the chat model for the user query
    response = st.session_state.conversations({'question': question})

    # Update the chat history
    st.session_state.chat_history = response['chat_history']

    # Add the response to the UI
    for i, message in enumerate(st.session_state.chat_history):
        # Check if the message is from the user or the chatbot
        if i % 2 == 0:
            # User message
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            # Chatbot message
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)

def load_personal_info():
    st.sidebar.subheader("About Yash Malik")

    # Add your photo
    st.sidebar.image("assets/yash_photo.jpg")

    # Brief Description
    st.sidebar.markdown("""
        Hi, I'm Yash Malik, a passionate individual with a keen interest in Product Management and Business Analytics.
        Feel free to ask me about my past experiences, my accomplishments, skills, and some of my personal info!
    """)

## Landing page UI
def run_UI():
    """
    The main UI function to display the UI for the webapp

    Args:
        None

    Returns:
        None
    """

    # Set the page tab title
    st.set_page_config(page_title="Yash's Chatbot", page_icon="🤖", layout="wide")

    # Add the custom CSS to the UI
    st.write(css, unsafe_allow_html=True)

    # Sidebar menu
    with st.sidebar:
        st.subheader("Yash Malik")

        # Add your photo
        st.image("assets/yash_photo.jpg")

        # Brief Description
        st.markdown("Hi, I'm Yash Malik, a passionate individual with a keen interest in Product Management and Business Analytics. Feel free to ask me about my past experiences, my accomplishments, skills, and some of my personal info!")

        
      # Provide hardcoded download link for the resume
        st.subheader("Resume")
        st.markdown("You can download my resume below:")
        resume_path = "./assets/Yash_Malik_Resume.pdf"
        st.sidebar.markdown(f"[Download Resume]({resume_path})", unsafe_allow_html=True)
        #st.sidebar.download_button("Or click here", key="resume_download_button", label="Click here", file_path=resume_path)
   
    # Initialize the session state variables to store the conversations and chat history
    if "conversations" not in st.session_state:
        st.session_state.conversations = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    # Set the page title
    st.header("Hi there, you can call me Stevie 🤖")

    # Input text box for user query
    user_question = st.text_input("Ask me about Yash's resume and Personal Leadrship Brand!")

    # Check if the user has entered a query/prompt
    if user_question:
        # Call the function to generate the response
        generate_response(user_question)

    # Sidebar menu
    with st.sidebar:
        st.subheader("Yash Malik")


def setup():
    # Load the environment variables (API keys)
    load_dotenv()

    # Load default resume file
    pdf_files = ["./assets/Yash_Malik_Resume.pdf", "./assets/Personal_Leadership_Brand.pdf"]
    
    # Extract text
    raw_text = extract_text(pdf_files)
        
    # Get the chunks of text
    chunks = get_chunks(raw_text)
    
    # Create a vector store for the chunks of text
    vector_store = get_vectorstore(chunks)

    # Create a conversation chain for the chat model
    st.session_state.conversations = get_conversation_chain(vector_store)


# Application entry point
if __name__ == "__main__":
    # Load data & setup
    setup()
    # Run the UI
    run_UI()