import streamlit as st
import replicate
import os

# App title
st.set_page_config(page_title="Chat with Snowflake Arctic")

# Replicate Credentials
with st.sidebar:
    st.title('Chat with Snowflake Arctic')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        st.success('API token loaded!', icon='✅')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Please enter your Replicate API token.', icon='⚠️')
            st.markdown("**Don't have an API token?** Head over to [Replicate](https://replicate.com) to sign up for one.")
        else:
            st.success('API token loaded!', icon='✅')

    os.environ['REPLICATE_API_TOKEN'] = replicate_api
    st.subheader("Adjust model parameters")
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=32, max_value=128, value=120, step=8)

# Store LLM-generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Ask me anything"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Ask me anything"}]
st.sidebar.button('Clear chat history', on_click=clear_chat_history)

# Function for generating Snowflake Arctic response
def generate_arctic_response(prompt_input):
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User.' You only respond once as 'Assistant.'"
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "<|start_header_id|>user<|end_header_id|>" + dict_message["content"] + "<|eot_id|>"
        else:
            string_dialogue += "<|start_header_id|>assistant<|end_header_id|>" + dict_message["content"] + "<|eot_id|>"
    
    for event in replicate.stream("meta/meta-llama-3-70b-instruct", # Update this line to add Snowflake Arctic
                           input={"prompt": f"""
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a helpful assistant<|eot_id|>
{string_dialogue}
<|start_header_id|>assistant<|end_header_id|>
""",
                                  "prompt_template": r"{prompt}",
                                  "temperature": temperature,
                                  "top_p": top_p,
                                  "max_length": max_length,
                                  "repetition_penalty":1}):
        yield str(event)

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_arctic_response(prompt)
            full_response = st.write_stream(response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
