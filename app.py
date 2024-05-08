from flask import Flask, jsonify, request, send_from_directory
import openai
import numpy as np
import faiss
import json
import os
import re
from flask_cors import CORS
from utils import scrape_site, generate_embeddings, save_data, load_data

# initialize Flask app
app = Flask(__name__, static_folder='static')
CORS(app)  #  Cross-Origin Resource Sharing for all origins

# OpenAI API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

# load or initialize embedding data
embeddings_data = load_data('vc_embeddings.json') if os.path.exists('vc_embeddings.json') else []
urls = [entry['url'] for entry in embeddings_data]
embeddings = np.array([entry['embedding'] for entry in embeddings_data if 'embedding' in entry])

#  FAISS index for fast nearest neighbor search
dimension = 1536
index = faiss.IndexFlatL2(dimension)
if embeddings.size > 0:
    index.add(embeddings)

@app.route('/')
def index_page():
    """  main index page. """
    return send_from_directory('static', 'index.html')

@app.route('/search', methods=['POST'])
def search_similar():
    """ search for similar venture capitals based on the given URL or text. """
    global embeddings, urls, index  # Reference global variables
    content = request.json
    query_text = content.get('text', '')
    logs = []

    if re.match(r'^https?://', query_text):
        if query_text in urls:
            idx = urls.index(query_text)
            query_embedding = embeddings[idx]
            logs.append("Using cached embedding.")
        else:
            scraped_content = scrape_site(query_text)
            if scraped_content:
                logs.append(f"Scraped content (for debugging): {scraped_content[:500]}")
                embedding = generate_embeddings(scraped_content)
                if embedding:
                    embeddings_data.append({'url': query_text, 'embedding': embedding})
                    save_data(embeddings_data, 'vc_embeddings.json')
                    urls.append(query_text)
                    embeddings = np.vstack([embeddings, embedding])
                    index.add(np.array([embedding]))
                    query_embedding = embedding
                    logs.append("New embedding saved and indexed.")
                else:
                    return jsonify({'error': 'Failed to generate embedding.', 'logs': logs}), 400
            else:
                return jsonify({'error': 'No content could be scraped.', 'logs': logs}), 400
    else:
        embedding = generate_embeddings(query_text)
        if embedding:
            query_embedding = embedding
            logs.append("Embedding generated for non-URL text.")
        else:
            return jsonify({'error': 'Failed to generate embedding from text.', 'logs': logs}), 400

    #  eliminate the query itself from the results
    distances, indices = index.search(np.array([query_embedding]), 4)
    similar_vcs = [{'url': urls[idx]} for i, idx in enumerate(indices[0]) if urls[idx] != query_text][:3]
    logs.append("Similar VCs found.")
    return jsonify(similar_vcs=similar_vcs, logs=logs)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
