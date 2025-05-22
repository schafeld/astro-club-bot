import streamlit as st
from openai import OpenAI
import file_utils

# Language-dependent UI labels and placeholders
ui_texts = {
    "English": {
        "title": "⭐️🤖💬 Astro Club Bot",
        "intro": (
            "This is a research assistant chatbot for astronomy class teachers, powered by OpenAI's GPT-4o model. "
            "You can select the output language and specify the desired output format. "
            "To use this app, provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys)."
        ),
        "select_language": "Select output language",
        "output_format_label": "Specify the desired output format",
        "api_key_label": "Enter your OpenAI API Key",
        "api_key_info": "Please provide your OpenAI API key to continue.",
        "chat_input": "What would you like to research or prepare for your astronomy class?",
        "file_uploader_label": "Upload a document for additional context (.pdf, .doc, .docx, .txt, .md)",
        "file_processing": "Processing your file...",
        "file_success": "File processed successfully! The AI will consider this information.",
        "file_preview": "Document Content Preview",
        "file_error": "Error processing file",
        "client_success": "OpenAI client initialized successfully!",
        "file_context_intro": "The following document was provided as additional context:",
        "full_prompt_header": "Full Prompt (Messages):"
    },
    "German": {
        "title": "⭐️🤖💬 Astro Club Bot",
        "intro": (
            "Dies ist ein Recherche-Chatbot für Lehrkräfte im Astronomieunterricht, betrieben mit OpenAI's GPT-4o Modell. "
            "Sie können die Ausgabesprache wählen und das gewünschte Ausgabeformat angeben. "
            "Um diese App zu nutzen, geben Sie einen OpenAI API-Schlüssel ein, den Sie [hier](https://platform.openai.com/account/api-keys) erhalten."
        ),
        "select_language": "Ausgabesprache auswählen",
        "output_format_label": "Gewünschtes Ausgabeformat angeben",
        "api_key_label": "OpenAI API-Schlüssel eingeben",
        "api_key_info": "Bitte geben Sie Ihren OpenAI API-Schlüssel ein, um fortzufahren.",
        "chat_input": "Worüber möchten Sie recherchieren oder etwas für den Astronomieunterricht vorbereiten?",
        "file_uploader_label": "Dokument für zusätzlichen Kontext hochladen (.pdf, .doc, .docx, .txt, .md)",
        "file_processing": "Datei wird verarbeitet...",
        "file_success": "Datei erfolgreich verarbeitet! Die KI wird diese Informationen berücksichtigen.",
        "file_preview": "Vorschau des Dokumentinhalts",
        "file_error": "Fehler bei der Verarbeitung der Datei",
        "client_success": "OpenAI-Client wurde erfolgreich initialisiert!",
        "file_context_intro": "Das folgende Dokument wurde als zusätzlicher Kontext bereitgestellt:",
        "full_prompt_header": "Vollständiger Prompt (Nachrichten):"
    }
}

# Language selection
# Define a mapping for display names
language_display_names = {
    "English": "English",
    "German": "Deutsch"
}

# Language selection with display name mapping
selected_language = st.selectbox(
    ui_texts["English"]["select_language"] + " / " + ui_texts["German"]["select_language"],
    options=["English", "German"],
    format_func=lambda x: language_display_names[x],
    index=0
)

# Map the selected language to its proper name for the system prompt
language_mapping = {
    "English": "English",
    "German": "Deutsch"
}
language_for_prompt = language_mapping[selected_language]

# Fetch the correct labels based on the selected language
labels = ui_texts[selected_language]

st.title(labels["title"])
st.write(labels["intro"])

# Output format specification
output_format_options = {
    "English": "Generate one page of text in English suitable for fourth graders. Attach structured sources for further information, relevant YouTube clips, and Wikipedia images.",
    "German": "Generiere eine Seite Text in Deutsch(!), der vom Verständnis her für Viertklässler geeignet ist. Hänge strukturierte Quellen für tiefergehende Informationen, fachlich passende Youtube-Clips und Bilder bei Wikipedia an."
}
output_format = st.text_area(
    labels["output_format_label"],
    value=output_format_options[selected_language],
    height=80
)

# Try to get the API key from Streamlit secrets
api_key = st.secrets.get("OPENAI_API_KEY", None)

# If not found, ask the user for their API key
if not api_key:
    api_key = st.text_input(labels["api_key_label"], type="password")
    if not api_key:
        st.info(labels["api_key_info"], icon="🗝️")
        st.stop()

try:
    client = OpenAI(api_key=api_key)
    st.success(labels["client_success"])

    # Add file uploader for additional context
    uploaded_file = st.file_uploader(
        labels["file_uploader_label"],
        type=["pdf", "doc", "docx", "txt", "md"]  # Added "md"
    )
    
    # Process uploaded file
    file_content = None
    if uploaded_file is not None:
        with st.spinner(labels["file_processing"]):
            file_content = file_utils.extract_text_from_file(uploaded_file)
            if file_content and not file_content.startswith("Error:"):
                st.success(labels["file_success"])
                # Show content preview
                with st.expander(labels["file_preview"]):
                    st.text(file_content[:1000] + "..." if len(file_content) > 1000 else file_content)
            else:
                st.error(f"{labels['file_error']}: {file_content}")
                file_content = None

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Language-specific system prompts
    system_prompts = {
        "English": (
            f"You are a helpful research assistant for an astronomy class teacher. "
            f"All your answers MUST be in English and never in any other language. "
            f"Strictly follow this instruction, even if the user asks in another language. "
            f"Output format: {output_format}"
        ),
        "German": (
            f"Du bist ein hilfreicher Recherche-Assistent für Astronomielehrkräfte. "
            f"Alle deine Antworten MÜSSEN auf Deutsch sein und niemals in einer anderen Sprache. "
            f"Befolge diese Anweisung strikt, auch wenn der Benutzer in einer anderen Sprache fragt. "
            f"Ausgabeformat: {output_format}"
        )
    }

    # Select the appropriate system prompt based on the selected language
    system_prompt = system_prompts[selected_language]
    
    # Add file content to system prompt if available
    if file_content:
        file_context = f"\n\n{labels['file_context_intro']}\n\n{file_content}"
        system_prompt += file_context

    # Ensure system prompt is always the first message
    if not st.session_state.messages or st.session_state.messages[0].get("role") != "system":
        st.session_state.messages = [{"role": "system", "content": system_prompt}]
    else:
        # Update the system prompt if language changed or file uploaded
        st.session_state.messages[0] = {"role": "system", "content": system_prompt}

    for message in st.session_state.messages[1:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input(labels["chat_input"]):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Log the full prompt header message in the chat response section
        with st.chat_message("assistant"):
            st.markdown(f"**{labels['full_prompt_header']}**")
            for message in st.session_state.messages:
                st.markdown(f"- **{message['role'].capitalize()}**: {message['content']}")

            # Stream the answer
            response = st.write_stream(
                client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                )
            )
        st.session_state.messages.append({"role": "assistant", "content": response})

except Exception as e:
    st.error(f"Error initializing OpenAI client: {e}")
    st.warning("Please ensure your `OPENAI_API_KEY` is set in `.streamlit/secrets.toml`, Streamlit Cloud secrets, or enter it above.")
