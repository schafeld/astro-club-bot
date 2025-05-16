# 💬 Astro Club Teaching Assistant

A helpful assistant for planning astronomy classes for elementary school classes. This is to become the virtual teaching assistant for "Olli's Astro Club".

Tasks to be included:

- brainsorming ideas on a topic
- suggesting topics
- gathering materials, e.g. info sources, images, art & crafts ideas,and video clips
- preparing the lesson's topic-specific "Astro News" page

## Initially started as Chatbot template

A simple Streamlit app that shows how to build a chatbot using OpenAI's GPT-3.5.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chatbot-template.streamlit.app/)

[Getting started with Streamlit](https://streamlit.io/#install) on your local machine.

### Prerequisites for running the app locally

Have an OpenAI API key. You can get one by signing up at [OpenAI](https://platform.openai.com/signup).
You can set the API key in your environment variables or create a `.env` file in the root directory of the project with the following content:

```bash
# Example for my Mac:
touch /Users/user001/.streamlit/secrets.toml
nano /Users/user001/.streamlit/secrets.toml
# Add the following line to the file:
OPENAI_API_KEY=your_openai_api_key
```

Now the app will run locally. For running the app on Streamlit Cloud, you can set the API key in the app settings.

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
