import google.generativeai as genai

genai.configure(api_key="AIzaSyDfm8poXWInS30HGCaf9i5WV9iIil67yYw")

models = genai.list_models()

for m in models:
    print(m.name, m.supported_generation_methods)