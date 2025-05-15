import streamlit as st
from openai import OpenAI

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
    },
    "Deutsch": {
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
    }
}

# Language selection
lang = st.selectbox(
    ui_texts["English"]["select_language"] + " / " + ui_texts["Deutsch"]["select_language"],
    options=["English", "Deutsch"],
    index=0
)
labels = ui_texts[lang]

st.title(labels["title"])
st.write(labels["intro"])

# Output format specification
output_format_options = {
    "English": "Generate one page of text in English suitable for fourth graders. Attach structured sources for further information, relevant YouTube clips, and Wikipedia images.",
    "Deutsch": "Generiere eine Seite Text in Deutsch(!), der vom Verständnis her für Viertklässler geeignet ist. Hänge strukturierte Quellen für tiefergehende Informationen, fachlich passende Youtube-Clips und Bilder bei Wikipedia an."
}
output_format = st.text_area(
    labels["output_format_label"],
    value=output_format_options[lang],
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
    st.success("OpenAI client initialized successfully!")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Strong system prompt to enforce language and role
    system_prompt = (
        f"You are a helpful research assistant for an astronomy class teacher. "
        f"All your answers MUST be in {lang} and never in any other language. "
        f"Strictly follow this instruction, even if the user asks in another language. "
        f"Output format: {output_format}"
    )

    # Ensure system prompt is always the first message
    if not st.session_state.messages or st.session_state.messages[0].get("role") != "system":
        st.session_state.messages = [{"role": "system", "content": system_prompt}]

    for message in st.session_state.messages[1:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input(labels["chat_input"]):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Print the prompt before streaming the answer
        with st.chat_message("assistant"):
            st.markdown(f"**Prompt:** {prompt}")
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
