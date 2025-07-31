from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
import requests
import traceback

app = Flask(__name__)
CORS(app)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

conversation_histories = {}

def call_claude_api(messages, max_tokens=1000):
    print(f"[DEBUG] Calling Claude API with {len(messages)} messages")
    
    if not ANTHROPIC_API_KEY:
        print("[ERROR] ANTHROPIC_API_KEY environment variable not set")
        raise Exception("ANTHROPIC_API_KEY environment variable not set")
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01"
    }
    
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
        "model": "claude-sonnet-4-20250514",
        "max_tokens": max_tokens,
        "messages": claude_messages
    }
    
    if system_message:
        payload["system"] = system_message
    
    print(f"[DEBUG] Sending request to Claude API...")
    
    try:
        response = requests.post(ANTHROPIC_API_URL, headers=headers, json=payload)
        print(f"[DEBUG] Claude API response status: {response.status_code}")
        
        response.raise_for_status()
        
        data = response.json()
        result = data["content"][0]["text"]
        print(f"[DEBUG] Claude API success, response length: {len(result)} characters")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Claude API request failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"[ERROR] Response status: {e.response.status_code}")
            print(f"[ERROR] Response body: {e.response.text}")
        raise Exception(f"Claude API error: {str(e)}")

@app.route("/", methods=["GET"])
def home():
    print("[DEBUG] Home endpoint called")
    return jsonify({
        "status": "healthy",
        "service": "Ivey Growth Mindset Learning API",
        "message": "AI Faculty Professor ready to help students develop growth mindset",
        "version": "1.0",
        "anthropic_configured": bool(ANTHROPIC_API_KEY)
    })

@app.route("/health", methods=["GET"])
def health_check():
    print("[DEBUG] Health check endpoint called")
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
    Main conversational chat endpoint with memory
    """
    print("[DEBUG] Chat endpoint called")
    
    try:
        data = request.json
        print(f"[DEBUG] Request data: {data}")
        
        message = data.get("message", "")
        session_id = data.get("session_id", "default")
        frontend_history = data.get("conversation_history", [])
        
        print(f"[DEBUG] Message: {message[:100]}...")
        print(f"[DEBUG] Session ID: {session_id}")
        print(f"[DEBUG] Frontend history length: {len(frontend_history)}")
        
        if not message:
            print("[ERROR] No message provided")
            return jsonify({"error": "No message provided"}), 400
        
        # Initialize session history if needed
        if session_id not in conversation_histories:
            conversation_histories[session_id] = []
        
        # Use frontend history if available, otherwise use stored history
        chat_history = frontend_history if frontend_history else conversation_histories[session_id]
        
        # System prompt for conversational interaction
        system_prompt = """You are Professor Claude, a distinguished faculty professor at Ivey Business School, specializing in case-based learning and growth mindset development. You are having a natural conversation with a student to help them develop resilience and learn from their challenges.

Your approach:
- Use Ivey's pedagogical methods: case-based analysis, practical application, collaborative learning
- Focus on growth mindset development - help students see challenges as opportunities
- Be conversational, supportive, and professorial (not overly formal)
- Ask follow-up questions to deepen understanding
- Connect challenges to broader business concepts when relevant
- Encourage reflection and self-awareness
- Provide specific, actionable guidance

Conversation style:
- Respond naturally as if speaking with a student in your office
- Show genuine interest in their learning process
- Use examples from business cases when helpful
- Be encouraging but also intellectually rigorous
- Ask thoughtful questions that promote deeper thinking

Remember: This is an ongoing conversation. Build on what you've discussed before and help the student develop throughout your interaction."""

        # Build messages array with conversation history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in chat_history[-10:]:  # Keep last 10 exchanges for context
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        print(f"[DEBUG] Sending {len(messages)} messages to Claude...")
        response_text = call_claude_api(messages)
        print("[DEBUG] Claude API call successful")
        
        # Store conversation in session history
        conversation_histories[session_id].extend([
            {"role": "user", "content": message, "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": response_text, "timestamp": datetime.now().isoformat()}
        ])
        
        print(f"[DEBUG] Stored conversation history for session {session_id}")
        print(f"[DEBUG] Total messages in session: {len(conversation_histories[session_id])}")
        
        return jsonify({
            "response": response_text,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"[ERROR] Exception in chat: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": "Chat failed",
            "message": "I'm having trouble responding right now. Please try again.",
            "details": str(e)
        }), 500
def analyze_challenge():
    print("[DEBUG] Analyze challenge endpoint called")
    
    try:
        data = request.json
        print(f"[DEBUG] Request data: {data}")
        
        challenge = data.get("challenge", "")
        session_id = data.get("session_id", "default")
        
        print(f"[DEBUG] Challenge: {challenge[:100]}...")
        print(f"[DEBUG] Session ID: {session_id}")
        
        if not challenge:
            print("[ERROR] No challenge provided")
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

        user_prompt = "A student at Ivey Business School is sharing a learning challenge they encountered. Please analyze this challenge and provide insights on:\n\n1. What specific misconceptions or knowledge gaps might have contributed to their struggle\n2. How this challenge relates to broader business concepts or case analysis skills\n3. What they can learn from this experience using a growth mindset approach\n4. Specific areas they should focus on for improvement\n\nStudent's challenge: \"" + challenge + "\"\n\nPlease provide a thoughtful, professorial response that helps them understand their learning process and sets them up for effective reflection."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        print("[DEBUG] Calling Claude API...")
        response_text = call_claude_api(messages)
        print("[DEBUG] Claude API call successful")
        
        if session_id not in conversation_histories:
            conversation_histories[session_id] = []
        
        conversation_histories[session_id].extend([
            {"role": "user", "content": f"Challenge: {challenge}", "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": response_text, "timestamp": datetime.now().isoformat()}
        ])
        
        print(f"[DEBUG] Stored conversation history for session {session_id}")
        
        return jsonify({
            "response": response_text,
            "session_id": session_id,
            "step": "challenge_analysis",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"[ERROR] Exception in analyze_challenge: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": "Analysis failed",
            "message": "I'm having trouble analyzing your challenge right now. Please try again.",
            "details": str(e)
        }), 500

@app.route("/assess_reflection", methods=["POST"])
def assess_reflection():
    print("[DEBUG] Assess reflection endpoint called")
    
    try:
        data = request.json
        reflection = data.get("reflection", "")
        session_id = data.get("session_id", "default")
        
        if not reflection:
            return jsonify({"error": "No reflection provided"}), 400
        
        history = conversation_histories.get(session_id, [])
        
        system_prompt = """You are a distinguished faculty professor at Ivey Business School. You are now assessing a student's reflection on their learning challenge. Your role is to provide constructive feedback that helps them deepen their self-awareness and growth mindset development."""

        user_prompt = "The student has written a reflection based on our previous analysis. Please assess their reflection and provide feedback on:\n\n1. How well they've understood the learning insights from the analysis\n2. The depth of their self-awareness about their learning process\n3. Whether they're demonstrating growth mindset thinking\n4. Areas where their reflection could be strengthened\n5. Specific suggestions for how they can apply these insights going forward\n\nStudent's reflection: \"" + reflection + "\"\n\nPlease provide constructive, encouraging feedback that helps them deepen their understanding and prepare for action planning."

        messages = [{"role": "system", "content": system_prompt}]
        
        for msg in history[-4:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": user_prompt})
        
        response_text = call_claude_api(messages)
        
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
        print(f"[ERROR] Exception in assess_reflection: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": "Assessment failed",
            "message": "I'm having trouble assessing your reflection right now. Please try again.",
            "details": str(e)
        }), 500

@app.route("/finalize_session", methods=["POST"])
def finalize_session():
    print("[DEBUG] Finalize session endpoint called")
    
    try:
        data = request.json
        action_plan = data.get("action_plan", "")
        session_id = data.get("session_id", "default")
        
        if not action_plan:
            return jsonify({"error": "No action plan provided"}), 400
        
        history = conversation_histories.get(session_id, [])
        
        system_prompt = """You are a distinguished faculty professor at Ivey Business School. You are now providing a final summary for a student who has completed their growth mindset learning session. Your role is to acknowledge their growth, validate their learning, and inspire continued development."""

        user_prompt = "The student has completed their learning session with their action plan. Please provide a summary that:\n\n1. Acknowledges their growth throughout this session\n2. Highlights key insights they've gained\n3. Validates their action plan and suggests any enhancements\n4. Encourages them to apply this growth mindset approach to future challenges\n5. Provides a motivating conclusion about their learning journey\n\nStudent's action plan: \"" + action_plan + "\"\n\nPlease provide an inspiring, professional summary that reinforces their learning and growth mindset development."

        messages = [{"role": "system", "content": system_prompt}]
        
        for msg in history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": user_prompt})
        
        response_text = call_claude_api(messages)
        
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
        print(f"[ERROR] Exception in finalize_session: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": "Session finalization failed",
            "message": "I'm having trouble finalizing your session right now. Please try again.",
            "details": str(e)
        }), 500

@app.route("/test_claude", methods=["GET"])
def test_claude():
    print("[DEBUG] Test Claude endpoint called")
    
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
        print(f"[ERROR] Claude test failed: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
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