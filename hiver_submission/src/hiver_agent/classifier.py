
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

class IntentClassifier:
    def __init__(self):
        self.vectorizer=TfidfVectorizer(ngram_range=(1,2), min_df=2, max_features=100000, sublinear_tf=True)
        self.model=LogisticRegression(max_iter=1000, class_weight="balanced")

    def fit(self, texts, labels):
        X=self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)
        return self

    def predict_one(self, text):
        X=self.vectorizer.transform([str(text)])
        p=self.model.predict_proba(X)[0]
        i=p.argmax()
        return self.model.classes_[i], float(p[i])

    def save(self,path):
        with open(path,"wb") as f: pickle.dump(self,f)

    @staticmethod
    def load(path):
        with open(path,"rb") as f: return pickle.load(f)
