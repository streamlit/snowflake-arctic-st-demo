import streamlit as st
import replicate
import os
from transformers import AutoTokenizer

if 'token_count' not in st.session_state:
    st.session_state.token_count = 0

# Set assistant icon to Snowflake logo
icons = {"assistant": "./Snowflake_Logomark_blue.svg", "user": "⛷️"}

# App title
st.set_page_config(page_title="Snowflake Arctic")

def main():
    """Execution starts here."""
    get_replicate_api_token()
    display_sidebar_ui()
    init_chat_history()
    display_chat_messages()
    get_and_process_prompt()

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hi. I'm Arctic, a new, efficient, intelligent, and truly open language model created by Snowflake AI Research. Ask me anything."}]

def get_replicate_api_token():
    # Disabling the UI-based token input for now

    # if 'REPLICATE_API_TOKEN' in st.secret:
    #     replicate_api = 
    # else:
    #     replicate_api = st.text_input('Enter Replicate API token:', type='password')
    #     if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
    #         st.warning('Please enter your Replicate API token.', icon='⚠️')
    #         st.markdown("**Don't have an API token?** Head over to [Replicate](https://replicate.com) to sign up for one.")
    os.environ['REPLICATE_API_TOKEN'] = st.secrets['REPLICATE_API_TOKEN']

def display_sidebar_ui():
    with st.sidebar:
        st.title('Snowflake Arctic')
        st.subheader("Adjust model parameters")
        st.slider('temperature', min_value=0.01, max_value=5.0, value=0.3,
                                step=0.01, key="temperature")
        st.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01,
                          key="top_p")

        st.button('Clear chat history', on_click=clear_chat_history)

        st.subheader("New!")
        st.sidebar.caption('Build your own app powered by Arctic and [enter to win](https://arctic-streamlit-hackathon.devpost.com/) $10k in prizes.')

        st.subheader("About")
        st.caption('Built by [Snowflake](https://snowflake.com/) to demonstrate [Snowflake Arctic](https://www.snowflake.com/blog/arctic-open-and-efficient-foundation-language-models-snowflake). App hosted on [Streamlit Community Cloud](https://streamlit.io/cloud). Model hosted by [Replicate](https://replicate.com/snowflake/snowflake-arctic-instruct).')


def init_chat_history():
    """Create a st.session_state.messages list to store chat messages"""
    if "messages" not in st.session_state:
        clear_chat_history()
        with st.spinner("Loading guardrails..."):
            check_safety()

def display_chat_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.write(message["content"])


@st.cache_resource(show_spinner=False)
def get_tokenizer():
    """Get a tokenizer to make sure we're not sending too much text
    text to the Model. Eventually we will replace this with ArcticTokenizer
    """
    return AutoTokenizer.from_pretrained("huggyllama/llama-7b")

def check_safety() -> bool: 
    conversation_history = st.session_state.messages
    input = {
        "prompt": f"[INST] Task: Check if there is unsafe content in 'Agent' messages in conversations according our safety policy with the below categories.\n\n<BEGIN UNSAFE CONTENT CATEGORIES>\nO1: Violence and Hate.\nShould not\n- Help people plan or engage in violence.\n- Encourage people to engage in violence.\n- Express hateful, derogatory, or demeaning sentiments against people based on sensitive personal characteristics like their race, color, religion, national origin, sexual orientation, gender, gender identity, or disability.\n- Encourage discrimination against people based on those characteristics and should not use slurs or create insults based on those characteristics.\nCan\n- Provide information on violence and discrimination.\n- Discuss the topics of hate and violence, and can discuss historical events involving violence.\nO2: Sexual Content.\nShould not\n- Engage in sexually explicit (i.e., erotic) conversations and should not encourage people to engage in sexual activities.\nCan\n- Discuss topics related to sexuality and sexual education.\n- Provide general information regarding sexual activities.\n- Provide guidance on topics related to sexual health.\nO3: Criminal Planning.\nShould not\n- Help people plan or engage in criminal activities like theft, kidnapping, or financial crimes, especially when the person indicates that they may act on the information provided to them.\n- Encourage people to engage in criminal activities or condone criminal behavior.\nCan\n- Help people understand how crimes are committed, provided that the response is not so detailed that it could be used to provide a roadmap for future crimes.\n- Help people understand how systems work that are used to prevent crimes, provided those descriptions do not provide detailed information on how to defeat those systems.\nO4: Guns and Illegal Weapons.\nShould not\n- Assist in the planning or execution of firearm or illegal weapons crimes, especially when the person indicates that they may act on the information provided to them.\n- Encourage people to engage in firearm or illegal weapons crimes or condone such behavior.\nCan\n- Discuss firearms and the arguments for and against firearm ownership.\nO5: Regulated or Controlled Substances.\nShould not\n- Encourage or assist people in the trafficking, consumption, or use of regulated or controlled substances, including but not limited to illegal drugs, tobacco, alcohol, and cannabis.\n- Assist or encourage people to create such substances when it is illegal to do so.\nCan\n- Discuss the use of regulated or controlled substances, and can provide general information on those substances (ex: what their chemical composition is and what their effects are).\n- Provide information on how those substances are manufactured, provided that the information is not so detailed as to provide step-by-step instructions for their creation.\nO6: Self-Harm.\nShould not\n- Encourage people to harm themselves.\n- Romanticize or condone self-harm or suicide.\n- Provide information regarding the methods of suicide or self-harm.\n- Provide any information or advice, other than information regarding appropriate health resources, to people who express or imply that they wish to harm themselves.\nCan\n- Provide general information regarding self-harm and suicide (ex: statistics, the mental health challenges faced by those who take these actions).\nShould\n- Provide information regarding appropriate health resources to people who imply or express the desire to harm themselves.\n<END UNSAFE CONTENT CATEGORIES>\n\n<BEGIN CONVERSATION>\n\n{conversation_history}\n\n<END CONVERSATION>\n\nProvide your safety assessment for Agent in the above conversation:\n- First line must read 'safe' or 'unsafe'.\n- If unsafe, a second line must include a comma-separated list of violated categories. [/INST]"
    }

    output = replicate.run(
        "tomasmcm/llamaguard-7b:86a2d8b79335b1557fc5709d237113aa34e3ae391ee46a68cc8440180151903d",
        input=input
    )
    if "unsafe" in output:
        st.warning("Your query violated our safety guidelines.",icon="⚠️")
        return False

    return True

def get_num_tokens(prompt):
    """Get the number of tokens in a given prompt"""
    tokenizer = get_tokenizer()
    tokens = tokenizer.tokenize(prompt)
    return len(tokens)

def fatal_error(error_message: str):
    """Display an error message requiring the chat to be cleared. This function
    also halts script execution."""
    st.error(error_message)
    st.button('Reset chat', on_click=clear_chat_history, key="clear_chat_history")
    st.stop()

def get_and_process_prompt():
    """Get the user prompt and process it"""
    # User-provided prompt
    if prompt := st.chat_input(disabled=False):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="⛷️"):
            st.write(prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant", avatar="./Snowflake_Logomark_blue.svg"):
            response = generate_arctic_response()
            full_response = st.write_stream(response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)

def generate_arctic_response():
    """String generator for the Snowflake Arctic response."""
    prompt = []
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            prompt.append("<|im_start|>user\n" + dict_message["content"] + "<|im_end|>")
        else:
            prompt.append("<|im_start|>assistant\n" + dict_message["content"] + "<|im_end|>")
    
    prompt.append("<|im_start|>assistant")
    prompt.append("")
    prompt_str = "\n".join(prompt)

    num_tokens = get_num_tokens(prompt_str)
    # if num_tokens - st.session_state.token_count > 50:
    #     st.success("Checking for safety...")
    #     if not check_safety():
    #         st.stop()

    st.session_state.token_count = num_tokens
    
    if num_tokens >= 3072:
        fatal_error("Conversation length too long. Please keep it under 3072 tokens.")
    
    for event_index, event in enumerate(replicate.stream("snowflake/snowflake-arctic-instruct",
                           input={"prompt": prompt_str,
                                  "prompt_template": r"{prompt}",
                                  "temperature": st.session_state.temperature,
                                  "top_p": st.session_state.top_p,
                                  })):
        if (event_index + 1) % 50 == 0:
            if not check_safety():
                fatal_error("I cannot reply to this question.")
        # st.warning(f"`{event_index}:` {event}")
        yield str(event)



if __name__ == "__main__":
    main()
