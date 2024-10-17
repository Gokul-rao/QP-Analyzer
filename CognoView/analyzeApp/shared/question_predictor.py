from .models_loader import word_vector, svm_model, nlp_model
import numpy as np

def get_cognitive_level(category_index: int) -> str:
    levels = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']
    mapped_levels = {index: level for index, level in enumerate(levels)}

    cognitive_level = mapped_levels[category_index]
    return cognitive_level


class CognitiveLevelPredictor:
    def __init__(self) -> None:
        if word_vector is None or svm_model is None or nlp_model is None:
            raise Exception("Models not loaded. Ensure that models_loader.load_models() is called at startup.")
        self.word_vector = word_vector
        self.svm_model = svm_model
        self.nlp = nlp_model


    def tokenize_text(self, text):
        """ Tokenize the Given Sentences or Text using NLP """

        document = self.nlp(text)

        tokens = [word.lemma_.strip() for word in document] # Lemmatizing tokens
        return tokens

    def vectorize_sentence(self, tokens):
        """ Takes the Tokens and takes average of all word vectors """
        vector_size =  self.word_vector.vector_size

        sentence_vector = np.zeros(vector_size) # creates zero vectors

        # Calculate average of all vectors
        counter = 0
        for word in tokens:
            if word in self.word_vector:
                sentence_vector += self.word_vector[word]
                counter += 1

        if counter == 0:
            return None

        average_sentence_vector = sentence_vector / counter
        return average_sentence_vector

    def predict_blooms_category(self, user_question: str) -> str | None:
        try:
            tokenized_question = self.tokenize_text(user_question)
            vectorized_question = self.vectorize_sentence(tokenized_question)

            predicted_cognitive_level = self.svm_model.predict([vectorized_question])
            predicted_level_text = get_cognitive_level(predicted_cognitive_level[0])
            return predicted_level_text
        except Exception as e:
            print(f"Exception Occurred => {str(e)}")
            return None


if __name__ == "__main__":

    print('inside')
    predictor = CognitiveLevelPredictor()

    # question = "Develop an agile plan for the upcoming project"
    # question = "Demonstrate about implementing MVC with RequestDispatcher with example."
    # question = "List out any 5 PO types."
    question = "afd"

    level = predictor.predict_blooms_category(question)
    print(f"{question}\nCognitive level for the above question is {level}")