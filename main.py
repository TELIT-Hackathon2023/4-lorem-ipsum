import os

import openai
import streamlit as st
from objects.ConversationObject import ConversationObject

object_list = [
    ConversationObject("Object 1", "test content 1"),
    ConversationObject("Object 2", "test content 2"),
    ConversationObject("Object 3", "test content 3"),
]

actual_conversation: ConversationObject = object_list[0]


def set_actual_conversation(obj: ConversationObject):
    global actual_conversation
    actual_conversation = obj


def main():
    with st.sidebar:
        # openai_api_key = st.title("How can I help you today?")

        for i, obj in enumerate(object_list):
            if st.button(obj.title):
                set_actual_conversation(obj)

    st.title(actual_conversation.title)
    st.write(actual_conversation.content)
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        openai.api_key = os.getenv("OPENAI_API_KEY")
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                st.session_state.messages[-1]
            ],
        )
        msg = response.choices[0].message
        st.session_state.messages.append(msg)
        st.chat_message("assistant").write(msg.content)


if __name__ == "__main__":
    main()
