import time
import uuid

from objects.ConversationContentObject import ConversationContentObject


class ConversationObject:
    def __init__(self, title: str, content: [(str, str)], timestamp):
        self.title: str = title
        self.content: [ConversationContentObject] = content
        self.timestamp = timestamp
        self.id = uuid.uuid1().int

    @staticmethod
    def init_new():
        return ConversationObject("New chat", [ConversationContentObject(None, "How cat I help you?")], time.time())

    def add_question_answer_pair(self, conversation_content_object: ConversationContentObject):
        self.content.append(conversation_content_object)

    def change_title(self, new_title: str):
        self.title = new_title

    def add_answer_to_last_content_pair(self, answer: str):
        self.content[-1].add_answer(answer)
