
import argparse
from .pipeline import train, run_csv

p=argparse.ArgumentParser()
p.add_argument("--pairs",required=True,help="Prepared CSV with text_customer,text_apple")
p.add_argument("--input",required=True,help="CSV containing customer_text (and optionally example_id)")
p.add_argument("--output",default="agent_predictions.csv")
args=p.parse_args()

agent=train(args.pairs)
run_csv(agent,args.input,args.output)
print(f"Wrote {args.output}")
