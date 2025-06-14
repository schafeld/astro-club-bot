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
            "To use this app, provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys) or enter the app password so you do not need an API key of your own."
        ),
        "select_language": "Select output language",
        "output_format_label": "Specify optional context, e.g. the desired output format.",
        "api_key_label": "...or enter your own OpenAI API Key",
        "api_key_info_box": "App password or your own API key?",
        "api_key_info": "Please provide your OpenAI API key to continue.",
        "role_input": "What's the role the AI should assume?",
        "chat_input": "What is your question?",
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
            "Um diese App zu nutzen, geben Sie einen OpenAI API-Schlüssel ein, den Sie [hier](https://platform.openai.com/account/api-keys) erhalten oder geben Sie das App-Passwort ein, dann brauchen Sie keinen eigenen Schlüssel."
        ),
        "select_language": "Ausgabesprache auswählen",
        "output_format_label": "Optionalen Kontext angeben, z.B. gewünschtes Ausgabeformat.",
        "api_key_label": "...oder eigenen OpenAI API-Schlüssel eingeben",
        "api_key_info_box": "App Passwort oder eigener OpenAI API-Schlüssel?",
        "api_key_info": "Bitte geben Sie Ihren OpenAI API-Schlüssel ein, um fortzufahren.",
        "role_input": "Welche Rolle soll die KI übernehmen?",
        "chat_input": "Was ist Ihre Frage?",
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

# Password protection
password_correct = False
password_label = "Enter app password..." if selected_language == "English" else "Bitte Passwort für diese Anwendung eingeben..."
if "PASSWORD_ASTRO_CLUB_BOT" in st.secrets:
    password = st.text_input(password_label, type="password")
    if password:
        if password == st.secrets["PASSWORD_ASTRO_CLUB_BOT"]:
            password_correct = True
        else:
            st.error("Incorrect password. Please try again." if selected_language == "English" else "Falsches Passwort. Bitte versuchen Sie es erneut.")
            st.stop()
else:
    password_correct = True  # No password set in secrets, allow access

# API key logic with bordered box and explanation
with st.container():
    st.markdown(
        f"""
        <div style="border: 2px solid #bbb; border-radius: 8px; padding: 1em; margin-bottom: 1em;">
            <b>{labels['api_key_info_box']}</b><br>
            <span>
                {"You can use the system's OpenAI API key by entering the app password above, or " if selected_language == "English" else "Sie können den OpenAI API-Schlüssel des Systems nutzen, indem Sie oben das App-Passwort eingeben, oder "}
                <span title="Get your own OpenAI API key at https://platform.openai.com/account/api-keys">
                    { "enter your own API key below" if selected_language == "English" else "geben Sie unten Ihren eigenen API-Schlüssel ein" }
                </span>.
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

api_key = None
if password_correct:
    api_key = st.secrets.get("OPENAI_API_KEY", None)
    if not api_key:
        api_key = st.text_input(labels["api_key_label"], type="password")
        if not api_key:
            st.info(labels["api_key_info"], icon="🗝️")
            st.stop()
else:
    api_key = st.text_input(
        labels["api_key_label"],
        type="password",
        help="Get your own OpenAI API key at https://platform.openai.com/account/api-keys" if selected_language == "English" else "Ihren eigenen OpenAI API-Schlüssel erhalten Sie unter https://platform.openai.com/account/api-keys"
    )
    if not api_key:
        st.info(labels["api_key_info"], icon="🗝️")
        st.stop()

try:
    client = OpenAI(api_key=api_key)
    st.success(labels["client_success"])

    # Output format specification / optional context input field
    output_format_options = {
        "English": "Generate text in English suitable for fourth graders. Provide quality links for core topics.",
        "German": "Generiere Text in Deutsch(!), der vom Verständnis her für Viertklässler geeignet ist. Belege alle Kernaussagen mit seriösen Links."
    }
    output_format = st.text_area(
        labels["output_format_label"],
        value=output_format_options[selected_language],
        height=80
    )

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

    # Language-specific default base roles
    default_base_roles = {
        "English": "You are a helpful research assistant for an astronomy class teacher.",
        "German": "Du bist ein hilfreicher Recherche-Assistent für Astronomielehrkräfte."
    }

    # User-editable base role input. This replaces the previous 'question' text_area.
    current_base_role = st.text_area(
        labels["role_input"],  # "What's the role the AI should assume?"
        value=default_base_roles[selected_language], 
        height=100
    )

    # Construct the full system prompt content
    system_prompt_parts = []
    if current_base_role and current_base_role.strip():
        system_prompt_parts.append(current_base_role.strip())
    
    if output_format and output_format.strip(): # Content from the "output_format_label" text area
        system_prompt_parts.append(output_format.strip())

    if file_content:
        # Ensure file_context_intro is only added if there's actual file_content
        file_context_string = f"{labels['file_context_intro']}\n\n{file_content}"
        system_prompt_parts.append(file_context_string)
    
    # Join parts with double newlines, filter out empty/None parts
    final_system_prompt_content = "\n\n".join(filter(None, system_prompt_parts))
    
    # Ensure system prompt is always the first message
    if not st.session_state.messages or st.session_state.messages[0].get("role") != "system":
        st.session_state.messages = [{"role": "system", "content": final_system_prompt_content}]
    else:
        # Only update if the content has actually changed
        if st.session_state.messages[0].get("content") != final_system_prompt_content:
            st.session_state.messages[0] = {"role": "system", "content": final_system_prompt_content}

    # Debug toggle
    debug = st.toggle("Debug", value=False)

    # Debugging prompt construction logic
    if debug:
        st.markdown(f"### {labels['full_prompt_header']} (System Prompt Content)")
        st.code(final_system_prompt_content, language="markdown")

    for message in st.session_state.messages[1:]: # Display messages after the system prompt
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input(labels["chat_input"]):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if debug:
                st.markdown(f"**{labels['full_prompt_header']}**")
                for message in st.session_state.messages:
                    st.markdown(f"- **{message['role'].capitalize()}**: {message['content']}")
            # Stream the answer (always)
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
