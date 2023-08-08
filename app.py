import nltk
import requests
import openai
import os
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

nltk.download('punkt')

# Set up Flask app and OpenAI API key
app = Flask(__name__)
openai.api_key = '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'

# Define function to scrap the websites related to user's input.
def google_search(query):
    url = 'https://www.google.com/search'
    params = {'q': query}
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, params=params, headers=header)

    soup = BeautifulSoup(response.text, 'html.parser')
    search_results = soup.find_all('div', {'class': 'MjjYud'})
    return search_results

# Define route to render HTML template
@app.route("/")
def home():
    return render_template("index.html")

# Define function to embed scrapping data.
def summarize(text, num_sentences=3):
    parser = PlaintextParser(text, Tokenizer('english'))
    summarizer = LexRankSummarizer()
    summary = summarizer(parser.document, num_sentences)
    return ' '.join([str(s) for s in summary])


# Define route for API endpoint
@app.route("/api", methods=["POST"])
def api():
    # Get question from form data
    question = request.json["question"]

    results = google_search(question)
    
    print(results)

    summarizes = []
    for text in results:
        summary = summarize(text)
        summarizes.append(summary)

    summarizes = ''
    for text in results:
        summary = summarize(text)
        summarizes + ' ' + summary
    
    # Use OpenAI to generate answer
    response = openai.Completion.create(
        engine="text-davinci-003", prompt=f"I will give you text content, you will explain it and output an explanation with website urls related to text content. I want you to pretend to explain the text to a middle school student who has no background knowledge or professional knowledge about the text I give you. Your task is to write the highest quality explanation possible, including examples and analogies certainly. You have to give me website urls certainly. Now, using the concepts above, explain the following text. {question}", max_tokens=1024, n=1, stop=None, temperature=0.7,
    )
    print(response)
    answer = response.choices[0].text.strip()
    
    return jsonify({"answer": answer})

# Run app
if __name__ == "__main__":
    app.run()