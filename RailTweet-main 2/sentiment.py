from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


#text = "I request for India govt think plz railway students future  .3year ago form fill up by railway exam"
#text = "The service was too bad, the agent was arogant"
text = "Very good, I liked it so much"

tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

tokens = tokenizer.encode(text, return_tensors='pt')
result = model(tokens)

print(int(torch.argmax(result.logits))+1)
