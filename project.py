import streamlit as st
from PIL import Image
import pytesseract
import pyttsx3
import google.generativeai as genai
import io
import base64
import threading

# Set path for Tesseract-OCR (ensure Tesseract is installed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'




# Initialize Google Generative AI with API Key
genai.configure(api_key="GOOGLE_API_KEY")  # Replace with your actual API key

# Initialize Text-to-Speech engine
engine = pyttsx3.init()

# Set up Streamlit page
st.set_page_config(page_title="VisionAid", layout="wide")
st.title("AI Powered Solution for Assisting Visually Impaired Individuals")
st.sidebar.title(" Available Features")
st.sidebar.markdown("""
- Scene Interpretation
- Speech Conversion
- Object & Obstacle Recognition
""")

def extract_text_from_image(image):
    """Extracts text from the given image using OCR."""
    text = pytesseract.image_to_string(image)
    return text



def text_to_speech(text):
    """Converts the given text to speech using a separate thread."""
    def speak():
        engine.say(text)
        engine.runAndWait()

    tts_thread = threading.Thread(target=speak)
    tts_thread.start()


def generate_scene_description(image_data):
    """Generates a scene description using Google Generative AI."""
    model = genai.GenerativeModel('gemini-1.5-flash')  # Use your specific model here
    
    # Convert image to base64 for API usage
    image_base64 = encode_image_to_base64(image_data)
    
    input_prompt = "Describe the image content and identify any potential obstacles or details for helping the visually impaired."
    
    # Sending the base64-encoded image and the prompt to the model
    response = model.generate_content([input_prompt, image_base64])
    return response.text

def encode_image_to_base64(image_data):
    """Encodes image to base64."""
    buffered = io.BytesIO()
    image_data.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def input_image_setup(uploaded_file):
    """Prepares the uploaded image for processing."""
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        return image
    else:
        raise FileNotFoundError("No file uploaded.")

# Main app functionality
uploaded_file = st.file_uploader("📤 Upload an image...", type=["jpg", "jpeg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Process based on user interaction
    col1, col2, col3 = st.columns(3)
    scene_button = col1.button("🔍 Describe Scene")
    ocr_button = col2.button("📝 Extract Text")
    tts_button = col3.button("🔊 Text-to-Speech")

    # Prepare image data for scene description generation
    image_data = input_image_setup(uploaded_file)

    if scene_button:
        with st.spinner("Generating scene description..."):
            response = generate_scene_description(image_data)
            st.subheader("Scene Description")
            st.write(response)
            text_to_speech(response)  # Read out the description

    if ocr_button:
        with st.spinner("Extracting text from image..."):
            text = extract_text_from_image(image)
            st.subheader("Extracted Text")
            st.write(text)
            text_to_speech(text)  # Read out the extracted text

    if tts_button:
        with st.spinner("Converting text to speech..."):
            text = extract_text_from_image(image)
            if text.strip():
                text_to_speech(text)
                st.success("Text-to-Speech Conversion Completed!")
            else:
                st.warning("No text found in the image.")
