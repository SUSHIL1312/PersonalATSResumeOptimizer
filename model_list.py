import google.generativeai as genai
import json
import os

api_key = None
if os.path.exists("config.json"):
    with open("config.json", "r") as f:
        api_key = json.load(f).get("gemini_key")

if not api_key:
    print("Error: No gemini_key found in config.json")
    exit(1)

genai.configure(api_key=api_key)

models = genai.list_models()

for m in models:
    print(m.name, m.supported_generation_methods)