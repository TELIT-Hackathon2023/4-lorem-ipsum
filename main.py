import os
import random

import openai
import streamlit as st
from objects.ConversationObject import ConversationObject
from dotenv import load_dotenv
import time
from streamlit_ws_localstorage import injectWebsocketCode, getOrCreateUID
import pickle


load_dotenv()

if 'conversation_list' not in st.session_state:
    try:
        st.session_state['conversation_list'] = pickle.load(open("local_storage", "rb"))
    except:
        st.session_state['conversation_list'] = []

if 'actual_conversation' not in st.session_state:
    st.session_state['actual_conversation'] = ConversationObject.init_new()


def get_actual_conversation() -> ConversationObject:
    return st.session_state['actual_conversation']


def set_actual_conversation(obj: ConversationObject):
    st.session_state['actual_conversation'] = obj


def show_conversation_context():
    for pair in get_actual_conversation().content:
        question = pair[0]
        if question is not None:
            st.chat_message("user").write(pair[0])

        answer = pair[1]
        if answer is not None:
            st.chat_message("assistant").write(pair[1])


def start_new_conversation():
    if len(st.session_state['conversation_list']) == 0:
        return

    last: ConversationObject = st.session_state['conversation_list'][len(st.session_state['conversation_list']) - 1]
    if last.title != "New chat":
        set_actual_conversation(ConversationObject.init_new())

def process_user_input():
    prompt = st.session_state.user_input.strip()
    if len(prompt) == 0:
        return

    print(prompt)

    actual = get_actual_conversation()
    if len(actual.content) == 1:
        actual.change_title(prompt)
        set_actual_conversation(actual)
        st.session_state['conversation_list'].insert(0, actual)

    actual.add_question_answer_pair(question=prompt, answer="Placeholder")
    pickle.dump(st.session_state['conversation_list'], open("local_storage", "wb"))


def main():
    with st.sidebar:
        st.sidebar.button("Start a new conversation", type="primary", on_click=start_new_conversation)

        for conversation in st.session_state['conversation_list']:
            st.button(conversation.title, on_click=set_actual_conversation, args=[conversation])

    st.title(get_actual_conversation().title)
    show_conversation_context()
    st.chat_input(on_submit=process_user_input, key="user_input")


if __name__ == "__main__":
    main()
