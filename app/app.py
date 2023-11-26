from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import StrOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.prompts.prompt import PromptTemplate
from langchain.schema import format_document
from openai import OpenAI

from langchain.schema import HumanMessage, SystemMessage
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough
from flask import Flask, request, Response, render_template
from dotenv import load_dotenv
from operator import itemgetter
from typing import List, Tuple
import os

load_dotenv("params.env")
app = Flask(__name__)
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
# print(os.environ["OPENAI_API_KEY"])

embeddings = OpenAIEmbeddings()
db = Chroma(persist_directory="./chroma_db_extended", embedding_function=embeddings)
retriever = db.as_retriever(search_type="mmr",
    search_kwargs={'k': 10, 'fetch_k': 50})
memory_list = {}

_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question

Chat History:
{chat_history}
Follow Up Input: {question} in LOTR

Answer in the following language: {language}
Standalone question:"""

_template_de = """Angesichts des folgenden Gesprächs und einer Folgefrage formulieren Sie die Folgefrage so um, dass sie eine eigenständige Frage ist

Chatverlauf:
{chat_history}
Follow-up-Eingabe: {question} in LOTR

Antworten Sie in der folgenden Sprache: {language}
Eigenständige Frage:"""

_template_sk = """Vzhľadom na nasledujúcu konverzáciu a doplňujúcu otázku preformulujte doplňujúcu otázku na samostatnú otázku

História rozhovoru:
{chat_history}
Následný vstup: {question} v LOTR

Odpoveď v nasledujúcom jazyku: {language}
Samostatná otázka:"""

template = """Answer the question based only on the following context:
{context}

Question: {question} in LOTR

Answer in the following language: {language}
"""

template_de = """Beantworten Sie die Frage nur basierend auf dem folgenden Kontext:
{context}

Frage: {question} in LOTR

Antworten Sie in der folgenden Sprache: {language}
"""

template_sk = """Odpovedzte na otázku len na základe nasledujúceho kontextu:
{context}

Otázka: {question} v LOTR

Odpoveď v nasledujúcom jazyku: {language}
"""

CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)
CONDENSE_QUESTION_PROMPT_DE = PromptTemplate.from_template(_template_de)
CONDENSE_QUESTION_PROMPT_SK = PromptTemplate.from_template(_template_sk)

DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

model = ChatOpenAI(
    model_name="gpt-4",
    temperature=0)



ANSWER_PROMPT = ChatPromptTemplate.from_template(template)
ANSWER_PROMPT_SK = ChatPromptTemplate.from_template(template_sk)
ANSWER_PROMPT_DE = ChatPromptTemplate.from_template(template_de)


def get_language(text):
    content = f"""What is the laguage of this text:{text}? Answer strictly from this options: 1. English 2. German, 3. Slovak"""
    client = OpenAI()

    cl = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=content,
        temperature=0
    )

    params_list = cl.choices
    print(params_list[0].text)
    if "slovak" in params_list[0].text.lower():
        return "slovak"
    elif "english" in params_list[0].text.lower():
        return "english"
    else:
        return "german"


def _format_chat_history(chat_history: List[Tuple]) -> str:
    print(chat_history)
    buffer = ""
    # for dialogue_turn in chat_history:
    if len(chat_history) > 0:
        human = "Human: " + chat_history[0].content
        ai = "Assistant: " + chat_history[1].content
        buffer += "\n" + "\n".join([human, ai])
    return buffer


def _combine_documents(docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)


def create_memory(thread_id):
    memory = ConversationBufferMemory(
        return_messages=True, output_key="answer", input_key="question"
    )
    memory_list[thread_id] = memory


def create_memory_request(query, thread_id, promt1, promt2):

    loaded_memory = RunnablePassthrough.assign(
        chat_history=RunnableLambda(memory_list[thread_id].load_memory_variables) | itemgetter("history"),
    )
    # Now we calculate the standalone question
    standalone_question = {
        "standalone_question": {
                                   "question": lambda x: x["question"],
                                   "chat_history": lambda x: _format_chat_history(x["chat_history"]),
                                   "language": lambda x: x["language"]
                               }
                               | CONDENSE_QUESTION_PROMPT
                               | ChatOpenAI(model_name="gpt-4", temperature=0)
                               | StrOutputParser(),
    }
    # Now we retrieve the documents
    retrieved_documents = {
        "docs": itemgetter("standalone_question") | retriever,
        "question": lambda x: x["standalone_question"],
        "language":lambda x: x["standalone_question"]
    }
    # Now we construct the inputs for the final prompt
    final_inputs = {
        "context": lambda x: _combine_documents(x["docs"]),
        "question": itemgetter("question"),
        "language": itemgetter("language")
    }
    # And finally, we do the part that returns the answers
    answer = {
        "answer": final_inputs | ANSWER_PROMPT | ChatOpenAI(),
        "docs": itemgetter("docs"),
    }
    # And now we put it all together!
    final_chain = loaded_memory | standalone_question | retrieved_documents | answer


    result = final_chain.invoke(query)
    memory_list[thread_id].save_context(query, {"answer": result["answer"].content})
    print(memory_list[thread_id].load_memory_variables({}))
    return result


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)



def create_title_request(msg):
    chat = ChatOpenAI(temperature=0)
    messages = [
        SystemMessage(
            content="You are a helpful assistant that creates short title from message"
        ),
        HumanMessage(
            content=msg
        ),
    ]
    return chat(messages)


@app.route('/health-check')
def health_check():
    return {"status": "Up and running!"}


@app.route('/get_title', methods=['POST'])
def get_title():
    req = request.json["query"]
    response = create_title_request(req)
    print(response)
    return {"content": response.content}


@app.route('/query_request', methods=['POST'])
def query_request():
    req = request.json["query"]
    id = request.json["thread_id"]
    # lang = request.json["language"]
    lang = get_language(req)
    if id not in memory_list:
        create_memory(id)
    if lang == 'slovak':
        res = create_memory_request({"question": req, "language": lang}, id, CONDENSE_QUESTION_PROMPT_SK, ANSWER_PROMPT_SK)
    if lang == 'german':
        res = create_memory_request({"question": req, "language": lang}, id, CONDENSE_QUESTION_PROMPT_DE, ANSWER_PROMPT_DE)
    else:
        res = create_memory_request({"question": req, "language": lang}, id, CONDENSE_QUESTION_PROMPT, ANSWER_PROMPT)

    links = [x.replace(' ', '_', x.count(' ')) for x in list(set([doc.metadata["source"] for doc in res["docs"]]))]

    return {"content": res["answer"].content,
            "metadata": links}

# Uncommit if you want to deploy locally without docker
port = int(os.environ.get('PORT', 5000))
app.run(debug=True, host='0.0.0.0', port=port)
