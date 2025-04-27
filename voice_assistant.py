import os
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import tempfile
import openai
from dotenv import load_dotenv

# Load environment variables from the correct path
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Debug print with more information
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"API Key found in voice_assistant.py: {api_key[:7]}...")
    if not api_key.startswith("sk-"):
        print("Warning: API key format appears incorrect!")
else:
    print("No API key found in environment variables!")
    # Try to load from launch.json if environment variable fails
    try:
        with open(os.path.join(os.path.dirname(__file__), '..', '.vscode', 'launch.json')) as f:
            import json
            launch_config = json.load(f)
            api_key = launch_config['configurations'][0]['env']['OPENAI_API_KEY']
            print(f"Found API key in launch.json: {api_key[:7]}...")
    except Exception as e:
        print(f"Could not load from launch.json: {e}")

# Set OpenAI API Key
openai.api_key = api_key

def check_api_key():
    """Check if API key is set and valid"""
    if not openai.api_key:
        st.error("❌ OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        return False
    return True

def create_recognizer():
    """Create and return a speech recognizer"""
    return sr.Recognizer()

def text_to_speech(text):
    """Convert text to speech and return the audio file path"""
    try:
        tts = gTTS(text=text, lang='en')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            temp_file = fp.name
            tts.save(temp_file)
            return temp_file
    except Exception as e:
        st.error(f"Error in text-to-speech conversion: {str(e)}")
        return None

def generate_ai_response(prompt):
    """Generate an AI response from OpenAI's API"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful and friendly AI voice assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,  # Limit response length
            temperature=0.7  # Control response creativity
        )
        return response['choices'][0]['message']['content']
    except openai.error.RateLimitError:
        return "I'm sorry, but I've reached my rate limit. Please try again later."
    except openai.error.AuthenticationError:
        return "Authentication error. Please check the API key."
    except Exception as e:
        st.error(f"Error generating AI response: {str(e)}")
        return "I'm sorry, I couldn't process that request."

def main():
    st.title("🎙️ AI Voice Assistant")
    st.write("Click the button and speak into your microphone!")

    # Check API key before proceeding
    if not check_api_key():
        return

    # Initialize recognizer
    recognizer = create_recognizer()

    # Session state for conversation history
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []

    # Create a button to start recording
    if st.button("🎤 Start Speaking"):
        try:
            # Use microphone as source
            with sr.Microphone() as source:
                st.info("🎙️ Listening... Speak now!")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                st.info("🎯 Processing your speech...")

            try:
                # Convert speech to text
                user_text = recognizer.recognize_google(audio)
                st.write("👤 You said:", user_text)

                # Generate AI response
                ai_response = generate_ai_response(user_text)
                st.write("🤖 Assistant:", ai_response)

                # Store in conversation history
                st.session_state.conversation.append({"user": user_text, "assistant": ai_response})

                # Convert AI response to speech
                audio_file = text_to_speech(ai_response)
                if audio_file:
                    # Play the audio
                    st.audio(audio_file, format='audio/mp3')
                    # Clean up the temporary file
                    os.unlink(audio_file)

            except sr.UnknownValueError:
                st.error("❌ Sorry, I couldn't understand what you said.")
            except sr.RequestError as e:
                st.error(f"❌ Could not request results; {str(e)}")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    # Display conversation history
    if st.session_state.conversation:
        st.markdown("### Conversation History")
        for entry in st.session_state.conversation:
            st.markdown(f"**You:** {entry['user']}")
            st.markdown(f"**Assistant:** {entry['assistant']}")
            st.markdown("---")

    st.markdown("### Instructions:")
    st.markdown("1. Click the 'Start Speaking' button")
    st.markdown("2. Ask any question clearly")
    st.markdown("3. Wait for the AI's spoken response")
    st.markdown("4. Enjoy your conversation!")

if __name__ == "__main__":
    main()
