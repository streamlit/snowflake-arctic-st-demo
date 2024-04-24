# 🤖❄️ Snowflake Arctic Chatbot
This Streamlit app is not just any chatbot; it's your starter kit to play with Snowflake's brand new foundation model: Snowflake Arctic! Arctic was released on April 24, 2024 and is completely open-source 😍

Get the full lowdown on Arctic in Adrien Treuille's [blog post](tbd.com). Snowflake Arctic is also available via [Hugging Face](https://huggingface.co/Snowflake/snowflake-arctic-instruct) 🤗 and all your favorite model gardens soon! 🔜

Built a cool Streamlit app using Arctic? Share it on social media with #SnowflakeArctic! We'll repost you 🫡

![Streamlit app chatbot for Snowflake Arctic](Streamlit-Arctic-Screenshot.png)

## Getting your own Replicate API token

To use this app, you'll need to get your own [Replicate](https://replicate.com/) API token.

After creating a Replicate account, you can access your API token from [this page](https://replicate.com/account/api-tokens).

## Setup Instructions

### Prerequisites
- Python 3.8 or later 🐍
- pip3 📦

### Installation
1. **Clone this repository**
   ```bash
   git clone https://github.com/yourusername/snowflake-arctic-chatbot.git
   cd snowflake-arctic-chatbot
   ```

2. **Install requirements**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your API token to your secrets file**\
Create a `.streamlit` folder with a `secrets.toml` file inside.
   ```bash
   mkdir .streamlit
   cd .streamlit
   touch secrets.toml
   ```
   
   Use your text editor or IDE of choice to add the following to `secrets.toml`:
      ```toml
      REPLICATE_API_TOKEN = "your API token here"
      ```
   Learn more about Streamlit secrets management in [our docs](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).
   
   Alternatively, you can enter your Replicate API token via the `st.text_input` widget in the app itself (once you're running the app).

4. **Run the Streamlit app**
   ```bash
   cd ..
   streamlit run streamlit_app.py
   ```

### Support
Need help? Got a burning question or a spark of genius to share? Just open an issue in this repository.
