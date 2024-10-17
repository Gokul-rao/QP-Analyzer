import os
import re
import fitz
from .question_predictor import CognitiveLevelPredictor

class QuestionExtractor:
    def __init__(self, question_paper_path):
        self.question_paper_path = question_paper_path
        self.question_options = ('(a)', '(b)', '(c)', '(d)', '(e)')
        self.question_pattern = r'^\d+\.\s*|\([a-z]\)\s*'
        self.marks_pattern = r'(\d+\s*[×x]\s*\d+\s*=\s*\d+)'

        self.question_predictor = CognitiveLevelPredictor()

    def extract_text_from_pdf(self, question_pdf):
        question_file_path = os.path.join(self.question_paper_path, question_pdf)

        if os.path.exists(question_file_path):
            with fitz.open(question_file_path) as document:
                question_text = "".join([page.get_text() for page in document])
            return question_text
        else:
            print(f"{question_file_path} File path does not exist")
            return None

    def get_only_questions(self, question_text):
        sentences = question_text.split("\n")
        questions = []

        for sentence in sentences:
            sentence = sentence.strip()

            # Filter out any marks field using the marks pattern
            if re.search(self.marks_pattern, sentence):
                continue

            if sentence and (sentence[0].isdigit() or sentence.startswith(self.question_options)):
                cleaned_question = re.sub(self.question_pattern, '', sentence).strip()
                questions.append(cleaned_question)
            else:
                continue

        return questions

    def predict_cognitive_level(self, question):
        cleaned_question = re.sub(self.question_pattern, '', question).strip()
        cognitive_level = self.question_predictor.predict_blooms_category(cleaned_question)
        return cognitive_level if cognitive_level else 'NA'



if __name__ == "__main__":
    qp_path = "D:\\"
    question_extractor = QuestionExtractor(qp_path)

    question_text = question_extractor.extract_text_from_pdf("qp3.pdf")
    if question_text:
        questions = question_extractor.get_only_questions(question_text)
        print("\n".join(questions))