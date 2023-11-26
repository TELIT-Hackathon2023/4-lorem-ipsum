import time
import uuid


class ConversationObject:
    def __init__(self, title: str, content: [(str, str)], timestamp):
        self.title: str = title
        self.content: [(str, str)] = content
        self.timestamp = timestamp
        self.id = uuid.uuid1()

    @staticmethod
    def init_new():
        return ConversationObject("New chat", [(None, "How cat I help you?")], time.time())

    def add_question_answer_pair(self, question, answer):
        self.content.append((question, answer))

    def change_title(self, new_title: str):
        self.title = new_title

    # def get_last_content_pair(self):
    #     return self.content[self.]
