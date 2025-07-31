// Application state
let currentStep = 1;
let conversationHistory = [];

// API Configuration - Replace with your deployment URL
const API_BASE_URL = 'https://growth-mindset.onrender.com'; // Change this to your Render URL

// Progress tracking
function updateProgress() {
    const progress = (currentStep / 3) * 100;
    document.getElementById('progressFill').style.width = progress + '%';
}

// Step management
function activateStep(stepNumber) {
    // Deactivate all steps
    document.querySelectorAll('.step-card').forEach(card => {
        card.classList.remove('active');
    });
    
    // Activate current step
    document.getElementById(`step${stepNumber}`).classList.add('active');
    currentStep = stepNumber;
    updateProgress();
}

// API call to backend
async function callClaudeAPI(messages, endpoint = '/chat') {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                messages: messages
            })
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }

        const data = await response.json();
        return data.response;
    } catch (error) {
        console.error('Error calling Claude API:', error);
        return "I apologize, but I'm having trouble connecting right now. Please check your internet connection and try again, or contact your instructor if the problem persists.";
    }
}

// Step 1: Analyze Challenge
async function analyzeChallenge() {
    const challenge = document.getElementById('challenge').value.trim();
    
    if (!challenge) {
        alert('Please describe your learning challenge first.');
        return;
    }

    // Show loading state
    document.getElementById('analyzeText').textContent = 'Analyzing...';
    document.getElementById('analyzeSpinner').style.display = 'block';
    
    const messages = [
        {
            role: "system",
            content: `You are a distinguished faculty professor at Ivey Business School, specializing in case-based learning and growth mindset development. Your role is to help students learn from their challenges using Ivey's pedagogical approach, which emphasizes:

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

Be supportive, insightful, and professorial in tone. Encourage students to see challenges as opportunities for growth.`
        },
        {
            role: "user",
            content: `A student at Ivey Business School is sharing a learning challenge they encountered. Please analyze this challenge and provide insights on:

1. What specific misconceptions or knowledge gaps might have contributed to their struggle
2. How this challenge relates to broader business concepts or case analysis skills
3. What they can learn from this experience using a growth mindset approach
4. Specific areas they should focus on for improvement

Student's challenge: "${challenge}"

Please provide a thoughtful, professorial response that helps them understand their learning process and sets them up for effective reflection.`
        }
    ];

    try {
        const response = await callClaudeAPI(messages);
        
        // Store in conversation history
        conversationHistory.push(
            { role: "user", content: `Student challenge: ${challenge}` },
            { role: "assistant", content: response }
        );

        // Display response
        document.getElementById('analysisContent').innerHTML = formatResponse(response);
        document.getElementById('analysisResponse').classList.add('show');
        
        // Activate next step
        setTimeout(() => {
            activateStep(2);
            document.querySelector('#step2 button').disabled = false;
        }, 1000);

    } catch (error) {
        alert('There was an error analyzing your challenge. Please try again.');
    } finally {
        // Reset button state
        document.getElementById('analyzeText').textContent = 'Get AI Analysis';
        document.getElementById('analyzeSpinner').style.display = 'none';
    }
}

// Step 2: Assess Reflection
async function assessReflection() {
    const reflection = document.getElementById('reflection').value.trim();
    
    if (!reflection) {
        alert('Please write your reflection first.');
        return;
    }

    // Show loading state
    document.getElementById('assessText').textContent = 'Assessing...';
    document.getElementById('assessSpinner').style.display = 'block';
    
    const messages = [
        ...conversationHistory,
        {
            role: "user",
            content: `The student has written a reflection based on our previous analysis. Please assess their reflection and provide feedback on:

1. How well they've understood the learning insights from the analysis
2. The depth of their self-awareness about their learning process
3. Whether they're demonstrating growth mindset thinking
4. Areas where their reflection could be strengthened
5. Specific suggestions for how they can apply these insights going forward

Student's reflection: "${reflection}"

Please provide constructive, encouraging feedback that helps them deepen their understanding and prepare for action planning.`
        }
    ];

    try {
        const response = await callClaudeAPI(messages);
        
        // Store in conversation history
        conversationHistory.push(
            { role: "user", content: `Student reflection: ${reflection}` },
            { role: "assistant", content: response }
        );

        // Display response
        document.getElementById('assessmentContent').innerHTML = formatResponse(response);
        document.getElementById('assessmentResponse').classList.add('show');
        
        // Activate next step
        setTimeout(() => {
            activateStep(3);
            document.querySelector('#step3 button').disabled = false;
        }, 1000);

    } catch (error) {
        alert('There was an error assessing your reflection. Please try again.');
    } finally {
        // Reset button state
        document.getElementById('assessText').textContent = 'Get Reflection Assessment';
        document.getElementById('assessSpinner').style.display = 'none';
    }
}

// Step 3: Finalize Session
async function finalizeSession() {
    const actionPlan = document.getElementById('actionPlan').value.trim();
    
    if (!actionPlan) {
        alert('Please create your action plan first.');
        return;
    }

    // Show loading state
    document.getElementById('finalizeText').textContent = 'Finalizing...';
    document.getElementById('finalizeSpinner').style.display = 'block';
    
    const messages = [
        ...conversationHistory,
        {
            role: "user",
            content: `The student has completed their learning session with their action plan. Please provide a summary that:

1. Acknowledges their growth throughout this session
2. Highlights key insights they've gained
3. Validates their action plan and suggests any enhancements
4. Encourages them to apply this growth mindset approach to future challenges
5. Provides a motivating conclusion about their learning journey

Student's action plan: "${actionPlan}"

Please provide an inspiring, professional summary that reinforces their learning and growth mindset development.`
        }
    ];

    try {
        const response = await callClaudeAPI(messages);
        
        // Display response
        document.getElementById('finalContent').innerHTML = formatResponse(response);
        document.getElementById('finalResponse').classList.add('show');
        
        // Complete progress
        updateProgress();

    } catch (error) {
        alert('There was an error finalizing your session. Please try again.');
    } finally {
        // Reset button state
        document.getElementById('finalizeText').textContent = 'Complete Learning Session';
        document.getElementById('finalizeSpinner').style.display = 'none';
    }
}

// Format response text for better display
function formatResponse(text) {
    // Convert line breaks to HTML
    return text.replace(/\n/g, '<br>');
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    updateProgress();
    
    // Enable textarea auto-resize
    document.querySelectorAll('.form-textarea').forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });
});