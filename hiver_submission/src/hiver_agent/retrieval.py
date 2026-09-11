
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Retriever:
    def __init__(self, max_features=150000):
        self.vectorizer=TfidfVectorizer(ngram_range=(1,2), min_df=2, max_features=max_features, sublinear_tf=True)
        self.texts=[]
        self.responses=[]
        self.matrix=None

    def fit(self, texts, responses):
        self.texts=list(map(str,texts)); self.responses=list(map(str,responses))
        self.matrix=self.vectorizer.fit_transform(self.texts)
        return self

    def retrieve(self, query, k=5):
        q=self.vectorizer.transform([str(query)])
        sims=cosine_similarity(q,self.matrix)[0]
        idx=sims.argsort()[::-1][:k]
        return [{"customer":self.texts[i],"response":self.responses[i],"similarity":float(sims[i])} for i in idx]
