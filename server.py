from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)

# Anthropic Claude API configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

# Store conversation histories by session
conversation_histories = {}

def call_claude_api(messages, max_tokens=1000):
    """
    Call the Anthropic Claude API with conversation messages
    """
    if not ANTHROPIC_API_KEY:
        raise Exception("ANTHROPIC_API_KEY environment variable not set")
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01"
    }
    
    # Convert OpenAI-style messages to Claude format
    claude_messages = []
    system_message = None
    
    for message in messages:
        if message["role"] == "system":
            system_message = message["content"]
        else:
            claude_messages.append({
                "role": message["role"],
                "content": message["content"]
            })
    
    payload = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": max_tokens,
        "messages": claude_messages
    }
    
    if system_message:
        payload["system"] = system_message
    
    try:
        response = requests.post(ANTHROPIC_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        return data["content"][0]["text"]
        
    except requests.exceptions.RequestException as e:
        print(f"Error calling Claude API: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        raise Exception(f"Claude API error: {str(e)}")

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "healthy",
        "service": "Ivey Growth Mindset Learning API",
        "message": "AI Faculty Professor ready to help students develop growth mindset",
        "version": "1.0",
        "anthropic_configured": bool(ANTHROPIC_API_KEY)
    })

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Ivey Growth Mindset Learning API",
        "anthropic_configured": bool(ANTHROPIC_API_KEY),
        "active_sessions": len(conversation_histories),
        "timestamp": datetime.now().isoformat()
    })

@app.route("/chat", methods=["POST"])
def chat():
    """
    Main chat endpoint for Claude API interactions
    """
    try:
        data = request.json
        messages = data.get("messages", [])
        session_id = data.get("session_id", "default")
        
        if not messages:
            return jsonify({"error": "No messages provided"}), 400
        
        # Call Claude API
        response_text = call_claude_api(messages)
        
        # Store conversation history for this session
        if session_id not in conversation_histories:
            conversation_histories[session_id] = []
        
        # Store the user's message and Claude's response
        conversation_histories[session_id].extend([
            {"role": "user", "content": messages[-1]["content"], "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": response_text, "timestamp": datetime.now().isoformat()}
        ])
        
        return jsonify({
            "response": response_text,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": "I apologize, but I'm having technical difficulties right now. Please try again in a moment.",
            "details": str(e) if app.debug else None
        }), 500

@app.route("/analyze_challenge", methods=["POST"])
def analyze_challenge():
    """
    Specialized endpoint for analyzing student challenges
    """
    try:
        data = request.json
        challenge = data.get("challenge", "")
        session_id = data.get("session_id", "default")
        
        if not challenge:
            return jsonify({"error": "No challenge provided"}), 400
        
        system_prompt = """You are a distinguished faculty professor at Ivey Business School, specializing in case-based learning and growth mindset development. Your role is to help students learn from their challenges using Ivey's pedagogical approach, which emphasizes:

1. Case-based analysis and critical thinking
2. Learning from failure and building resilience  
3. Practical application of business concepts
4. Collaborative learning and diverse perspectives
5. Action-oriented decision making

When analyzing student challenges:
- Focus on the learning process, not just the outcome
- Help identify specific misconceptions or knowledge gaps
- Connect challenges to broader business principles
- Encourage growth mindset thinking
- Provide constructive, supportive feedback
- Reference case analysis methodology when relevant

Be supportive, insightful, and professorial in tone. Encourage students to see challenges as opportunities for growth."""

        user_prompt = f"""A student at Ivey Business School is sharing a learning challenge they encountered. Please analyze this challenge and provide insights on:

1. What specific misconceptions or knowledge gaps might have contributed to their struggle
2. How this challenge relates to broader business concepts or case analysis skills
3. What they can learn from this experience using a growth mindset approach
4. Specific areas they should focus on for improvement

Student's challenge: "{challenge}"

Please provide a thoughtful, professorial response that helps them understand their learning process and sets them up for effective reflection."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response_text = call_claude_api(messages)
        
        # Store conversation history
        if session_id not in conversation_histories:
            conversation_histories[session_id] = []
        
        conversation_histories[session_id].extend([
            {"role": "user", "content": f"Challenge: {challenge}", "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": response_text, "timestamp": datetime.now().isoformat()}
        ])
        
        return jsonify({
            "response": response_text,
            "session_id": session_id,
            "step": "challenge_analysis",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error in analyze_challenge endpoint: {str(e)}")
        return jsonify({
            "error": "Analysis failed",
            "message": "I'm having trouble analyzing your challenge right now. Please try again.",
            "details": str(e) if app.debug else None
        }), 500

@app.route("/assess_reflection", methods=["POST"])
def assess_reflection():
    """
    Specialized endpoint for assessing student reflections
    """
    try:
        data = request.json
        reflection = data.get("reflection", "")
        session_id = data.get("session_id", "default")
        
        if not reflection:
            return jsonify({"error": "No reflection provided"}), 400
        
        # Get conversation history for context
        history = conversation_histories.get(session_id, [])
        
        system_prompt = """You are a distinguished faculty professor at Ivey Business School. You are now assessing a student's reflection on their learning challenge. Your role is to provide constructive feedback that helps them deepen their self-awareness and growth mindset development."""

        user_prompt = f"""The student has written a reflection based on our previous analysis. Please assess their reflection and provide feedback on:

1. How well they've understood the learning insights from the analysis
2. The depth of their self-awareness about their learning process
3. Whether they're demonstrating growth mindset thinking
4. Areas where their reflection could be strengthened
5. Specific suggestions for how they can apply these insights going forward

Student's reflection: "{reflection}"

Please provide constructive, encouraging feedback that helps them deepen their understanding and prepare for action planning."""

        # Build messages with conversation history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add relevant history
        for msg in history[-4:]:  # Last 4 messages for context
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": user_prompt})
        
        response_text = call_claude_api(messages)
        
        # Store in conversation history
        conversation_histories[session_id].extend([
            {"role": "user", "content": f"Reflection: {reflection}", "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": response_text, "timestamp": datetime.now().isoformat()}
        ])
        
        return jsonify({
            "response": response_text,
            "session_id": session_id,
            "step": "reflection_assessment",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error in assess_reflection endpoint: {str(e)}")
        return jsonify({
            "error": "Assessment failed",
            "message": "I'm having trouble assessing your reflection right now. Please try again.",
            "details": str(e) if app.debug else None
        }), 500

@app.route("/finalize_session", methods=["POST"])
def finalize_session():
    """
    Specialized endpoint for finalizing learning sessions
    """
    try:
        data = request.json
        action_plan = data.get("action_plan", "")
        session_id = data.get("session_id", "default")
        
        if not action_plan:
            return jsonify({"error": "No action plan provided"}), 400
        
        # Get conversation history for context
        history = conversation_histories.get(session_id, [])
        
        system_prompt = """You are a distinguished faculty professor at Ivey Business School. You are now providing a final summary for a student who has completed their growth mindset learning session. Your role is to acknowledge their growth, validate their learning, and inspire continued development."""

        user_prompt = f"""The student has completed their learning session with their action plan. Please provide a summary that:

1. Acknowledges their growth throughout this session
2. Highlights key insights they've gained
3. Validates their action plan and suggests any enhancements
4. Encourages them to apply this growth mindset approach to future challenges
5. Provides a motivating conclusion about their learning journey

Student's action plan: "{action_plan}"

Please provide an inspiring, professional summary that reinforces their learning and growth mindset development."""

        # Build messages with full conversation history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add relevant history
        for msg in history[-6:]:  # Last 6 messages for full context
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": user_prompt})
        
        response_text = call_claude_api(messages)
        
        # Store in conversation history
        conversation_histories[session_id].extend([
            {"role": "user", "content": f"Action Plan: {action_plan}", "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": response_text, "timestamp": datetime.now().isoformat()}
        ])
        
        return jsonify({
            "response": response_text,
            "session_id": session_id,
            "step": "session_complete",
            "timestamp": datetime.now().isoformat(),
            "session_summary": {
                "total_exchanges": len(conversation_histories[session_id]),
                "completed_steps": ["challenge_analysis", "reflection_assessment", "action_planning"]
            }
        })
        
    except Exception as e:
        print(f"Error in finalize_session endpoint: {str(e)}")
        return jsonify({
            "error": "Session finalization failed",
            "message": "I'm having trouble finalizing your session right now. Please try again.",
            "details": str(e) if app.debug else None
        }), 500

@app.route("/get_session_history", methods=["GET"])
def get_session_history():
    """
    Get conversation history for a session
    """
    session_id = request.args.get("session_id", "default")
    
    history = conversation_histories.get(session_id, [])
    
    return jsonify({
        "session_id": session_id,
        "history": history,
        "message_count": len(history),
        "timestamp": datetime.now().isoformat()
    })

@app.route("/reset_session", methods=["POST"])
def reset_session():
    """
    Reset a conversation session
    """
    data = request.json
    session_id = data.get("session_id", "default")
    
    if session_id in conversation_histories:
        del conversation_histories[session_id]
    
    return jsonify({
        "message": f"Session {session_id} reset successfully",
        "session_id": session_id,
        "timestamp": datetime.now().isoformat()
    })

@app.route("/test_claude", methods=["GET"])
def test_claude():
    """
    Test endpoint to verify Claude API connectivity
    """
    try:
        test_messages = [
            {
                "role": "system", 
                "content": "You are a helpful assistant. Respond with exactly: 'Claude API connection successful!'"
            },
            {
                "role": "user", 
                "content": "Test message"
            }
        ]
        
        response = call_claude_api(test_messages, max_tokens=50)
        
        return jsonify({
            "status": "success",
            "message": "Claude API is working correctly",
            "test_response": response,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Claude API test failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == "__main__":
    if not ANTHROPIC_API_KEY:
        print("WARNING: ANTHROPIC_API_KEY environment variable not set!")
        print("Please set your Anthropic API key before running the server.")
        print("You can get an API key from: https://console.anthropic.com/")
    else:
        print("✅ Anthropic API key configured")
    
    print("🚀 Starting Ivey Growth Mindset Learning API")
    print("🎓 AI Faculty Professor ready to help students develop resilience")
    print(f"🌐 Server will run on port {os.environ.get('PORT', 5000)}")
    
    app.run(
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("DEBUG", "False").lower() == "true"
    )