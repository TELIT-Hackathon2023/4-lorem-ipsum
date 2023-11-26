from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import StrOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.prompts.prompt import PromptTemplate
from langchain.schema import format_document

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
db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = db.as_retriever()
memory_list = {}

_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)
DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

model = ChatOpenAI(
    model_name="gpt-4",
    temperature=0)


template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
ANSWER_PROMPT = ChatPromptTemplate.from_template(template)

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



def create_memory_request(query, thread_id):
    # memory = ConversationBufferMemory(
    #     return_messages=True, output_key="answer", input_key="question"
    # )
    #
    # # First we add a step to load memory
    # # This adds a "memory" key to the input object
    # loaded_memory = RunnablePassthrough.assign(
    #     chat_history=RunnableLambda(memory.load_memory_variables) | itemgetter("history"),
    # )

    loaded_memory = RunnablePassthrough.assign(
        chat_history=RunnableLambda(memory_list[thread_id].load_memory_variables) | itemgetter("history"),
    )
    # Now we calculate the standalone question
    standalone_question = {
        "standalone_question": {
                                   "question": lambda x: x["question"],
                                   "chat_history": lambda x: _format_chat_history(x["chat_history"]),
                               }
                               | CONDENSE_QUESTION_PROMPT
                               | ChatOpenAI(model_name="gpt-4", temperature=0)
                               | StrOutputParser(),
    }
    # Now we retrieve the documents
    retrieved_documents = {
        "docs": itemgetter("standalone_question") | retriever,
        "question": lambda x: x["standalone_question"],
    }
    # Now we construct the inputs for the final prompt
    final_inputs = {
        "context": lambda x: _combine_documents(x["docs"]),
        "question": itemgetter("question"),
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


@app.route('/health-check')
def health_check():
    return {"status": "Up and running!"}


@app.route('/query_request', methods=['POST'])
def query_request():
    req = request.json["query"]
    id = request.json["thread_id"]
    if id not in memory_list:
        create_memory(id)
    res = create_memory_request({"question": req}, id)
    # res = chain.invoke({"question": res, "language": "italian"})
    print(res)
    return {"content": res["answer"].content, "metadata": list(set([doc.metadata["source"] for doc in res["docs"]]))}

# Uncommit if you want to deploy locally without docker
port = int(os.environ.get('PORT', 5000))
app.run(debug=True, host='0.0.0.0', port=port)
