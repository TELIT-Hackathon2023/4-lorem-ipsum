import time


class ConversationObject:
    def __init__(self, title: str, content: [(str, str)], timestamp):
        self.title: str = title
        self.content: [(str, str)] = content
        self.timestamp = timestamp

    @staticmethod
    def init_new():
        return ConversationObject("New chat", [], time.time())

    def add_question_answer_pair(self, question: str, answer: str):
        self.content.append((question, answer))
