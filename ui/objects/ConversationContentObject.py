class ConversationContentObject:

    def __init__(self, question, answer):
        self.question = question
        self.answer = answer

    def add_answer(self, answer: str):
        self.answer = answer