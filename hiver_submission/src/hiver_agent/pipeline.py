
import pandas as pd
from .intents import heuristic_intent
from .classifier import IntentClassifier
from .retrieval import Retriever
from .agent import SupportAgent

def load_pairs(path):
    df=pd.read_csv(path)
    # Accept either pre-paired data or TWCS-style rows.
    if {"text_customer","text_apple"}.issubset(df.columns):
        return df[["text_customer","text_apple"]].dropna()
    if {"text","response_tweet_id"}.issubset(df.columns):
        # For a prepared pair file, response text must already be joined.
        raise ValueError("Provide a paired CSV with text_customer,text_apple.")
    raise ValueError("Expected text_customer,text_apple columns.")

def train(pair_csv):
    df=load_pairs(pair_csv)
    labels=[heuristic_intent(x) for x in df.text_customer]
    clf=IntentClassifier().fit(df.text_customer, labels)
    ret=Retriever().fit(df.text_customer, df.text_apple)
    return SupportAgent(clf,ret)

def run_csv(agent, input_csv, output_csv):
    df=pd.read_csv(input_csv)
    text_col="customer_text" if "customer_text" in df.columns else "text"
    rows=[]
    for _,r in df.iterrows():
        out=agent.run(r[text_col])
        rows.append({**({ "example_id": r["example_id"] } if "example_id" in r else {}),
                     "customer_text":r[text_col], **out,
                     "top_similarity":out["evidence"][0]["similarity"] if out["evidence"] else 0,
                     "evidence_customer":out["evidence"][0]["customer"] if out["evidence"] else "",
                     "evidence_response":out["evidence"][0]["response"] if out["evidence"] else ""})
    pd.DataFrame(rows).to_csv(output_csv,index=False)
