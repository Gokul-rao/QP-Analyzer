# Global variables to store preloaded models
import os
import pickle

import spacy
from gensim.models import KeyedVectors

word_vector = None
svm_model = None
nlp_model = None

def load_models():
    global word_vector, svm_model, nlp_model
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if not word_vector or not svm_model or not nlp_model:
        models_path = os.path.join(base_dir, "prediction_models")
        vector_model_path = os.path.join(models_path, "word2vec-google-news-300.model")
        svm_model_path = os.path.join(models_path, "svm_model.pkl")

        # Loading models
        print("Loading models globally...")

        print("Loading Word Vector Model...")
        word_vector = KeyedVectors.load(vector_model_path)
        print("Word Vector Loaded!")

        print("Loading SVM Model...")
        svm_model = pickle.load(open(svm_model_path, 'rb'))
        print("SVM model loaded!")

        print("Loading NLP model")
        nlp_model = spacy.load('en_core_web_md')

        print("Models loaded successfully.")    