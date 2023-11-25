import os
import openai
import streamlit as st
from objects.ConversationObject import ConversationObject
from dotenv import load_dotenv
import time

load_dotenv()

conversations_list = [
    ConversationObject("Title 1", [("Question 1", "Answer 1"), ("Question 2", "Answer 2")], time.time()),
    ConversationObject("Title 2", [("Question 1", "Answer 1"),], time.time()),
    ConversationObject("Title 3", [("Question 1", "Answer 1"), ("Question 2", "Answer 2"), ("Question 3", "Answer 3"), ("Question 4", "Answer 4")], time.time()),
]

actual_conversation: ConversationObject = conversations_list[0]


def set_actual_conversation(obj: ConversationObject):
    global actual_conversation
    actual_conversation = obj


def main():
    with st.sidebar:
        for i, obj in enumerate(conversations_list):
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
