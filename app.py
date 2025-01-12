from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import google.generativeai as genai

# Configure the API Key for Google Generative AI
genai.configure(api_key="AIzaSyDgxQNnsxs35NorPl78EM-jlRy-QRmDJeo")  # Replace with your actual API key

# Create the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://chat_app_aozx_user:qwQ4ZOjIpUpM9nFhIK2noR4MSsHrachw@dpg-cu1uj33tq21c73ble8eg-a/chat_app_aozx'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the model for storing chat responses
class ChatResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    response = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Create all tables in the database
with app.app_context():
    db.create_all()

# Enable Cross-Origin Resource Sharing (CORS)
CORS(app)

# Function to store a new chat response
def store_chat_response(question, response):
    try:
        new_entry = ChatResponse(question=question, response=response)
        db.session.add(new_entry)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print("Error storing chat response:", e)
        return False

# Function to retrieve the latest chat interaction
def get_last_interaction():
    """
    Retrieve the most recent question-response pair.
    :return: Dictionary with the last question and response, or None if no interactions exist.
    """
    try:
        last_entry = ChatResponse.query.order_by(ChatResponse.created_at.desc()).first()
        if last_entry:
            return {'question': last_entry.question, 'response': last_entry.response}
        return None
    except Exception as e:
        print("Error retrieving last interaction:", e)
        return None

# Endpoint for receiving user input
@app.route('/api/question', methods=['POST'])
def receive_question():
    """
    Endpoint to receive a user question, generate a response using the AI model,
    and store the question-response pair in the database.
    """
    if 'question' not in request.form:
        return jsonify({'error': 'No question provided'}), 400

    user_question = request.form.get('question')

    if not user_question:
        return jsonify({'error': 'No question provided'}), 400

    # Retrieve the last question-response pair
    last_interaction = get_last_interaction()
    context_lines = []

    if last_interaction:
        # Add the previous interaction to the context
        context_lines.append(f"Q: {last_interaction['question']}")
        context_lines.append(f"A: {last_interaction['response']}")

    # Add the current question to the context
    context_lines.append(f"Q: {user_question}")
    context_lines.append("A:")

    # Join lines to create the full context
    context = "\n".join(context_lines)

    # Generate response from the AI model
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(context)
    except Exception as e:
        return jsonify({'error': 'Error generating response', 'details': str(e)}), 500

    # Store the new question-response pair in the database
    if store_chat_response(user_question, response.text.strip()):
        print("Response stored successfully.")

    return jsonify({
        'response': response.text.strip(),
        'last_interaction': last_interaction,
        'current_question': user_question
    })

if __name__ == '__main__':
    app.run(debug=True)
