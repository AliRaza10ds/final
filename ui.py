import os
import uuid
import json
import re
from flask import Flask, render_template, request, jsonify, make_response
from markupsafe import Markup
from dotenv import load_dotenv

from booking import ask_question, deals_history, hotel_history, supervisor_history,deals_memory,hotel_memory

load_dotenv()

app = Flask(__name__)

conversation_history_sessions = {}
MAX_HISTORY = 5

def reset_all_memory():
    global deals_history, deals_memory, last_searched_deal_id
    global hotel_history, hotel_memory, last_searched_hotel_id
    global supervisor_history

    deals_history = []
    deals_memory.clear()
    last_searched_deal_id = None

    hotel_history = []
    hotel_memory.clear()
    last_searched_hotel_id = None

    supervisor_history = []

EXIT_WORDS = ["bye", "exit", "quit", "ok bye", "clear"]

def check_exit(user_question: str) -> bool:
    return any(word in user_question.lower() for word in EXIT_WORDS)


@app.route('/')
def index():
    session_id = request.cookies.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())

    if session_id not in conversation_history_sessions:
        conversation_history_sessions[session_id] = []

    res = make_response(render_template('index.html', session_id=session_id))
    res.set_cookie('session_id', session_id)
    return res

@app.route('/start_session', methods=['POST'])
def start_session():
    data = request.get_json()
    session_id = data.get('session_id')

    deals_history.clear()
    hotel_history.clear()
    supervisor_history.clear()

    if session_id:
        conversation_history_sessions[session_id] = []

    return jsonify({"status": "ok"})
'''
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_question = data.get('message')
    session_id = data.get('session_id')

    if not user_question or not session_id:
        return jsonify({"error": "Missing message or session ID"}), 400

    if session_id not in conversation_history_sessions:
        conversation_history_sessions[session_id] = []

    user_question_lower = user_question.lower()

    #if any(word in user_question_lower for word in ["bye", "exit", "quit", "clear"]):
        #deals_history.clear()
       # hotel_history.clear()
       # supervisor_history.clear()
        #conversation_history_sessions[session_id] = []
       # return jsonify({"type": "text", "response": "Session cleared! Thankyou"})
    if check_exit(user_question_lower):
        reset_all_memory()
        return "Thank you! All previous chat history cleared. How can I help you today?"

    response_text = ask_question(user_question)

    if ("payNowBtn_" in response_text and 
    "Razorpay" in response_text and 
    "<button" in response_text):
     return jsonify({"type": "html", "response": response_text})

    history = conversation_history_sessions[session_id]
    history.append({"user": user_question, "bot": response_text})
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
    conversation_history_sessions[session_id] = history

    return jsonify({"type": "text", "response": response_text})
'''
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_question = data.get('message')
    session_id = data.get('session_id')

    if not user_question or not session_id:
        return jsonify({"error": "Missing message or session ID"}), 400

    if session_id not in conversation_history_sessions:
        conversation_history_sessions[session_id] = []

    if check_exit(user_question):
        reset_all_memory()
        return jsonify({
            "response": "Thank you! All previous chat history cleared. How can I help you today?"
        })

    response_text = ask_question(user_question)

    
    history = conversation_history_sessions[session_id]
    history.append({"user": user_question, "bot": response_text})
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
    conversation_history_sessions[session_id] = history

    if ("payNowBtn_" in response_text and 
        "Razorpay" in response_text and 
        "<button" in response_text):
        return jsonify({
            "type": "html", 
            "response": response_text
        })

    return jsonify({
        "response": response_text
    })


if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        print(" ERROR: GOOGLE_API_KEY is not set in .env file")
    else:
        print("🌍 Ghumloo Assistant running on http://127.0.0.1:5000")
        app.run(debug=True, port=5000)
