import os
import random
import uuid

import requests
import openai
import streamlit as st
from objects.ConversationObject import ConversationObject
from dotenv import load_dotenv
import time
import pickle
from objects.ConversationContentObject import ConversationContentObject

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
    for conversation_content_object in get_actual_conversation().content:
        question = conversation_content_object.question
        if question is not None:
            st.chat_message("user").write(question)

        answer = conversation_content_object.answer
        if answer is not None:
            st.chat_message("assistant").write(answer)


def start_new_conversation():
    if len(st.session_state['conversation_list']) == 0:
        return

    last: ConversationObject = st.session_state['conversation_list'][len(st.session_state['conversation_list']) - 1]
    if last.title != "New chat":
        set_actual_conversation(ConversationObject.init_new())


def process_user_input():
    st.session_state['is_input_blocked'] = True
    prompt = st.session_state.user_input.strip()
    if len(prompt) == 0:
        return

    actual = get_actual_conversation()
    if len(actual.content) == 1:
        API_ENDPOINT = "http://147.232.156.113:5000/get_title"

        body = {
            "query": prompt,
        }
        r = requests.post(API_ENDPOINT, json=body).json()
        print(r)

        actual.change_title(r['content'])
        set_actual_conversation(actual)
        st.session_state['conversation_list'].insert(0, actual)

    actual.add_question_answer_pair(ConversationContentObject(question=prompt, answer=None))

    API_ENDPOINT = "http://147.232.156.113:5000/query_request"

    body = {
        "query": prompt,
        "thread_id": actual.id
    }

    r = requests.post(API_ENDPOINT, json=body).json()

    actual.add_answer_to_last_content_pair(r['content'])
    metadata: [str] = r['metadata']
    fixed = []
    for link in metadata:
        fixed.append(link.replace(" ", "_"))
    print(fixed)

    if len(fixed) == 0:
        actual.add_answer_to_last_content_pair(r['content'])
    else:
        actual.add_answer_to_last_content_pair(r['content'] + "     " + fixed[0])

    pickle.dump(st.session_state['conversation_list'], open("local_storage", "wb"))


def main():
    with st.sidebar:
        st.sidebar.button("Start a new conversation", type="primary", on_click=start_new_conversation)

        st.markdown(
            """
            <div><br /></div>
            """,
            unsafe_allow_html=True
        )

        for conversation in st.session_state['conversation_list']:
            st.button(conversation.title, on_click=set_actual_conversation, args=[conversation], key=uuid.uuid1().int)

    st.title(get_actual_conversation().title)
    show_conversation_context()

    st.session_state['is_input_blocked'] = False
    st.chat_input(on_submit=process_user_input, key="user_input", disabled=st.session_state['is_input_blocked'])


if __name__ == "__main__":
    main()
