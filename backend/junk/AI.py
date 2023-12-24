import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import json

#model_path = 'psmathur/orca_mini_3b'
model_id = 'hongyin/mistral-0.5b-40k'

with open("sample.json", "r") as read_file:
    data = json.load(read_file)


tokenizer = AutoTokenizer.from_pretrained(model_id)

model = AutoModelForCausalLM.from_pretrained(model_id)

text = "What is the most entertaining and fun to listen couple of sentences of this dialogue: " + "Artificial intelligence algorithms are designed to make decisions, often using real-time data. They are unlike passive machines that are capable only of mechanical or predetermined responses. Using sensors, digital data, or remote inputs, they combine information from a variety of different sources, analyze the material instantly, and act on the insights derived from those data. With massive improvements in storage systems, processing speeds, and analytic techniques, they are capable of tremendous sophistication in analysis and decisionmaking. AI systems have the ability to learn and adapt as they make decisions. In the transportation area, for example, semi-autonomous vehicles have tools that let drivers and vehicles know about upcoming congestion, potholes, highway construction, or other possible traffic impediments. Vehicles can take advantage of the experience of other vehicles on the road, without human involvement, and the entire corpus of their achieved “experience” is immediately and fully transferable to other similarly configured vehicles. Their advanced algorithms, sensors, and cameras incorporate experience in current operations, and use dashboards and visual displays to present information in real time so human drivers are able to make sense of ongoing traffic and vehicular conditions. And in the case of fully autonomous vehicles, advanced systems can completely control the car or truck, and make all the navigational decisions. AI generally is undertaken in conjunction with machine learning and data analytics.5 Machine learning takes data and looks for underlying trends. If it spots something that is relevant for a practical problem, software designers can take that knowledge and use it to analyze specific issues. All that is required are data that are sufficiently robust that algorithms can discern useful patterns. Data can come in the form of digital information, satellite imagery, visual information, text, or unstructured data."
inputs = tokenizer(text, return_tensors="pt")

outputs = model.generate(**inputs, max_new_tokens=120)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))

#print(data["text"])
