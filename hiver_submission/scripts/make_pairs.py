
"""Convert a TWCS-style CSV into paired customer/AppleSupport rows.
This expects response_tweet_id/in_response_to_tweet_id to be present and
AppleSupport to be the selected brand. For the assignment, run this on a
documented subsample of the raw dataset."""
import argparse, pandas as pd

p=argparse.ArgumentParser()
p.add_argument("--input",required=True)
p.add_argument("--output",required=True)
args=p.parse_args()

df=pd.read_csv(args.input)
df["text"]=df["text"].fillna("").astype(str)
by_id=df.set_index("tweet_id")["text"].to_dict()
rows=[]
for _,r in df[df["in_response_to_tweet_id"].notna()].iterrows():
    parent=by_id.get(r["in_response_to_tweet_id"])
    if parent and str(r["author_id"]) != str(r.get("author_id")):
        rows.append({"text_customer":parent,"text_apple":r["text"]})
pd.DataFrame(rows).drop_duplicates().to_csv(args.output,index=False)
print("Wrote",len(rows),"pairs")
