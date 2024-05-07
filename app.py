from flask import Flask, jsonify, request, send_from_directory
import openai
import numpy as np
import faiss
import json
from flask_cors import CORS
import os
app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all origins

# Load API Key securely
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Load embeddings
with open('vc_embeddings.json', 'r') as f:
    embeddings_data = json.load(f)
urls = [entry['url'] for entry in embeddings_data]
embeddings = np.array([entry['embedding'] for entry in embeddings_data])

# Initialize FAISS index globally
dimension = 1536
index = faiss.IndexFlatL2(dimension)  # Ensure this is correct
index.add(embeddings)  # Adding embeddings to the FAISS index

@app.route('/')
def index_page():
    return send_from_directory('static', 'index.html')

@app.route('/search', methods=['POST'])
def search_similar():
    content = request.json
    query_text = content['text']
    print(f"Received text: {query_text}")
    
    try:
        response = openai.Embedding.create(input=query_text, model="text-embedding-ada-002")
        print(f"OpenAI API Response: {response}")
        
        if 'data' in response and 'embedding' in response['data'][0]:
            query_embedding = np.array(response['data'][0]['embedding']).reshape(1, -1)
            print(f"Query Embedding: {query_embedding}")
            
            print(f"Index type: {type(index)}")  # Debugging the type of index
            print(f"Index attributes: {dir(index)}")  # Debugging the attributes of index

            distances, indices = index.search(query_embedding, 3)
            similar_vcs = [{'url': urls[idx], 'distance': float(distances[0][i])} for i, idx in enumerate(indices[0])]
            return jsonify(similar_vcs), 200
        else:
            return jsonify({'error': 'Embedding not found in response'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
