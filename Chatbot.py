import requests
import json
import streamlit as st
from streamlit_chat import message
from components.Sidebar import sidebar
from shared import constants

api_key, selected_model = sidebar(constants.OPENROUTER_DEFAULT_CHAT_MODEL)

st.title("💬 Streamlit GPT")
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

with st.form("chat_input", clear_on_submit=True):
    a, b = st.columns([4, 1])
    user_input = a.text_input(
        label="Your message:",
        placeholder="What would you like to say?",
        label_visibility="collapsed",
    )
    b.form_submit_button("Send", use_container_width=True)

for i, msg in enumerate(st.session_state.messages):
    message(msg["content"], is_user=msg["role"] == "user", key=i)

if user_input and not api_key:
    st.info("Please click Connect OpenRouter to continue.")

if user_input and api_key:
    st.session_state.messages.append({"role": "user", "content": user_input})
    message(user_input, is_user=True)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": constants.OPENROUTER_REFERRER,
    }

    payload = {
        "model": selected_model,
        "messages": st.session_state.messages,
        "stream": True  # Enable streaming
    }

    response = requests.post(
        f"{constants.OPENROUTER_API_BASE}/chat/completions",
        headers=headers,
        json=payload,
        stream=True  # Request streaming
    )

    if response.status_code == 200:
        full_message = {"role": "assistant", "content": ""}
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    data_str = decoded_line[len("data: "):]
                    if data_str.strip() == "OPENROUTER PROCESSING":
                        continue  # Skip the processing comments
                    try:
                        event_data = json.loads(data_str)
                        if event_data.get("choices"):
                            delta = event_data["choices"][0]["delta"]
                            if delta.get("content"):
                                full_message["content"] += delta["content"]
                                # Update the UI with the streaming content
                                st.session_state.messages[-1] = full_message
                                
                    except json.JSONDecodeError:
                        pass  # Handle JSON decode error if needed

        st.session_state.messages.append(full_message)
        message(full_message["content"])
    else:
        st.error(f"Failed to get a response from the server. Status code: {response.status_code}")
        st.error(f"Response: {response.text}")
