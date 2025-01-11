from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

# Configure the API Key for Google Generative AI
genai.configure(api_key="AIzaSyDgxQNnsxs35NorPl78EM-jlRy-QRmDJeo")

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Endpoint for receiving user input
@app.route('/api/question', methods=['POST'])
def receive_question():
    # Check if the request contains form-data
    if 'question' not in request.form:
        return jsonify({'error': 'No question provided'}), 400

    # Get the question from form-data
    user_question = request.form.get('question')

    if not user_question:
        return jsonify({'error': 'No question provided'}), 400

    # Generate response from AI model
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(user_question)

    return jsonify({'response': response.text})

if __name__ == '__main__':
    app.run(debug=True)
