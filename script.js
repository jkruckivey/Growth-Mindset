// Application state
let currentStep = 1;
let conversationHistory = [];

// API Configuration - Updated to point to your Render backend
const API_BASE_URL = 'https://growth-mindset.onrender.com';

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

// Step 1: Analyze Challenge - UPDATED TO USE SPECIALIZED ENDPOINT
async function analyzeChallenge() {
    const challenge = document.getElementById('challenge').value.trim();
    
    if (!challenge) {
        alert('Please describe your learning challenge first.');
        return;
    }

    // Show loading state
    document.getElementById('analyzeText').textContent = 'Analyzing...';
    document.getElementById('analyzeSpinner').style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE_URL}/analyze_challenge`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                challenge: challenge,
                session_id: 'default'
            })
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }

        const data = await response.json();
        
        // Store in conversation history
        conversationHistory.push(
            { role: "user", content: `Student challenge: ${challenge}` },
            { role: "assistant", content: data.response }
        );

        // Display response
        document.getElementById('analysisContent').innerHTML = formatResponse(data.response);
        document.getElementById('analysisResponse').classList.add('show');
        
        // Activate next step
        setTimeout(() => {
            activateStep(2);
            document.querySelector('#step2 button').disabled = false;
        }, 1000);

    } catch (error) {
        console.error('Error analyzing challenge:', error);
        alert('There was an error analyzing your challenge. Please try again.');
    } finally {
        // Reset button state
        document.getElementById('analyzeText').textContent = 'Get AI Analysis';
        document.getElementById('analyzeSpinner').style.display = 'none';
    }
}

// Step 2: Assess Reflection - UPDATED TO USE SPECIALIZED ENDPOINT
async function assessReflection() {
    const reflection = document.getElementById('reflection').value.trim();
    
    if (!reflection) {
        alert('Please write your reflection first.');
        return;
    }

    // Show loading state
    document.getElementById('assessText').textContent = 'Assessing...';
    document.getElementById('assessSpinner').style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE_URL}/assess_reflection`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                reflection: reflection,
                session_id: 'default'
            })
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }

        const data = await response.json();
        
        // Store in conversation history
        conversationHistory.push(
            { role: "user", content: `Student reflection: ${reflection}` },
            { role: "assistant", content: data.response }
        );

        // Display response
        document.getElementById('assessmentContent').innerHTML = formatResponse(data.response);
        document.getElementById('assessmentResponse').classList.add('show');
        
        // Activate next step
        setTimeout(() => {
            activateStep(3);
            document.querySelector('#step3 button').disabled = false;
        }, 1000);

    } catch (error) {
        console.error('Error assessing reflection:', error);
        alert('There was an error assessing your reflection. Please try again.');
    } finally {
        // Reset button state
        document.getElementById('assessText').textContent = 'Get Reflection Assessment';
        document.getElementById('assessSpinner').style.display = 'none';
    }
}

// Step 3: Finalize Session - UPDATED TO USE SPECIALIZED ENDPOINT
async function finalizeSession() {
    const actionPlan = document.getElementById('actionPlan').value.trim();
    
    if (!actionPlan) {
        alert('Please create your action plan first.');
        return;
    }

    // Show loading state
    document.getElementById('finalizeText').textContent = 'Finalizing...';
    document.getElementById('finalizeSpinner').style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE_URL}/finalize_session`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action_plan: actionPlan,
                session_id: 'default'
            })
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }

        const data = await response.json();
        
        // Store in conversation history
        conversationHistory.push(
            { role: "user", content: `Student action plan: ${actionPlan}` },
            { role: "assistant", content: data.response }
        );

        // Display response
        document.getElementById('finalContent').innerHTML = formatResponse(data.response);
        document.getElementById('finalResponse').classList.add('show');
        
        // Complete progress
        updateProgress();

    } catch (error) {
        console.error('Error finalizing session:', error);
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