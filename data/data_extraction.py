from langchain.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import json
from typing import Iterable
def save_docs_to_jsonl(array:Iterable[Document], file_path:str)->None:
    with open(file_path, 'a') as jsonl_file:
        for doc in array:
            jsonl_file.write(doc.json() + '\n')

def load_docs_from_jsonl(file_path)->Iterable[Document]:
    array = []
    with open(file_path, 'r') as jsonl_file:
        for line in jsonl_file:
            data = json.loads(line)
            obj = Document(**data)
            array.append(obj)
    return array


with open("./docs/links.json", 'r', encoding="utf-8") as file:
    js = json.load(file)[:2400]

last_i = 0
for i in range(0, len(js), 50):
    loader = UnstructuredURLLoader(urls=js[i:i+50], strategy="fast", continue_on_failure=True, show_progress_bar=True)
    data = loader.load()
    save_docs_to_jsonl(data, 'data_web.json')
    last_i = i+50

print(last_i)
loader = UnstructuredURLLoader(urls=js[last_i:len(js)], strategy="fast", continue_on_failure=True, show_progress_bar=True)
data = loader.load()
save_docs_to_jsonl(data, 'data_web.json')

print(data)

