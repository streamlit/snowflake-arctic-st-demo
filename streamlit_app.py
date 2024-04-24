import streamlit as st
import replicate
import os
from pathlib import Path

# App title
st.set_page_config(page_title="Snowflake Arctic")


def get_token() -> str:
    # Lookup token in Streamlit secrets first
    if Path(".streamlit/secrets.toml").exists():
        if "REPLICATE_API_TOKEN" in st.secrets:
            return st.secrets["REPLICATE_API_TOKEN"]

    # Otherwise, show a text input to get the token
    return st.text_input(
        "Enter your Replicate API token (or [create one](https://replicate.com)):",
        type="password",
    )


# Replicate Token
with st.sidebar:
    st.title("Snowflake Arctic")

    replicate_api_token = get_token()
    token_is_valid = replicate_api_token.startswith("r8_") and len(replicate_api_token) == 40

    if replicate_api_token:
        if not token_is_valid:
            st.warning(
                "Token is not valid! It should start with `r8_` and be 40 characters long.",
                icon="⚠️",
            )

    os.environ["REPLICATE_API_TOKEN"] = replicate_api_token


    with st.sidebar.container(border=True):

        temperature = st.slider(
            "Temperature",
            min_value=0.01,
            max_value=1.0,
            value=0.6,
            step=0.01,
            help="Controls the randomness of the generated text. A lower value makes the output more deterministic, while a higher value introduces more randomness.",
            disabled=not token_is_valid,
        )

        top_p = st.slider(
            "Top p",
            min_value=0.01,
            max_value=1.0,
            value=0.9,
            step=0.01,
            help="Controls the variety of responses. Lower values focus on fewer options, while higher values explore more diverse options.",
            disabled=not token_is_valid,
        )

# Store LLM-generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi. I'm Arctic, a new, efficient, intelligent, and truly open language model created by Snowflake AI Research. Ask me anything.",
        }
    ]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


def clear_chat_history():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi. I'm Arctic, a new, efficient, intelligent, and truly open language model created by Snowflake AI Research. Ask me anything.",
        }
    ]


st.sidebar.button(
    "Clear chat history", on_click=clear_chat_history, disabled=not token_is_valid
)

st.sidebar.caption(
    "Built by [Snowflake](https://snowflake.com/) to demonstrate [Snowflake Arctic](https://www.snowflake.com/blog/arctic-open-and-efficient-foundation-language-models-snowflake). App hosted on [Streamlit Community Cloud](https://streamlit.io/cloud). Model hosted by [Replicate](https://replicate.com/snowflake/snowflake-arctic-instruct)."
)


# Function for generating Snowflake Arctic response
def generate_arctic_response():
    prompt = []
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            prompt.append("<|im_start|>user\n" + dict_message["content"] + "<|im_end|>")
        else:
            prompt.append(
                "<|im_start|>assistant\n" + dict_message["content"] + "<|im_end|>"
            )

    prompt.append("<|im_start|>assistant")
    prompt.append("")

    for event in replicate.stream(
        "snowflake/snowflake-arctic-instruct",
        input={
            "prompt": "\n".join(prompt),
            "prompt_template": r"{prompt}",
            "temperature": temperature,
            "top_p": top_p,
        },
    ):
        yield str(event)


# User-provided prompt
if prompt := st.chat_input(disabled=not token_is_valid):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        response = generate_arctic_response()
        full_response = st.write_stream(response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
