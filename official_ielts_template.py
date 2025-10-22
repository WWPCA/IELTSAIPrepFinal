"""
Official IELTS Template - Clean Implementation
Matches the official IELTS layout with proper navigation and task structure
"""

def create_official_ielts_template(assessment_type, user_email, session_id, current_task_data, question_text, chart_svg, chart_data, tasks):
    """Create template that matches official IELTS layout"""
    
    template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{assessment_type.replace('_', ' ').title()} Assessment</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            color: #333;
        }}
        
        .header {{
            background-color: #fff;
            padding: 15px 20px;
            border-bottom: 1px solid #ddd;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .logo-section {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .logo {{
            background-color: #e31e24;
            color: white;
            padding: 8px 12px;
            font-weight: bold;
            font-size: 18px;
            border-radius: 3px;
        }}
        
        .test-info {{
            font-size: 14px;
            color: #666;
        }}
        
        .header-right {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .timer {{
            background-color: #333;
            color: white;
            padding: 8px 15px;
            border-radius: 4px;
            font-weight: bold;
        }}
        
        .main-content {{
            display: flex;
            height: calc(100vh - 120px);
            background-color: #fff;
        }}
        
        .question-panel {{
            width: 50%;
            padding: 20px;
            border-right: 1px solid #ddd;
            overflow-y: auto;
        }}
        
        .answer-panel {{
            width: 50%;
            padding: 20px;
            display: flex;
            flex-direction: column;
        }}
        
        .part-header {{
            background-color: #f8f8f8;
            padding: 10px 15px;
            margin-bottom: 20px;
            border-left: 4px solid #e31e24;
        }}
        
        .part-title {{
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .part-instructions {{
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
        }}
        
        .task-content {{
            line-height: 1.6;
            margin-bottom: 20px;
        }}
        
        .chart-container {{
            margin: 20px 0;
            padding: 20px;
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            text-align: center;
        }}
        
        .chart-title {{
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }}
        
        .answer-area {{
            flex: 1;
            display: flex;
            flex-direction: column;
        }}
        
        .answer-textarea {{
            flex: 1;
            width: 100%;
            padding: 15px;
            border: 1px solid #ddd;
            font-family: Arial, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            resize: none;
            outline: none;
        }}
        
        .word-count {{
            text-align: right;
            padding: 10px;
            font-size: 12px;
            color: #666;
            border: 1px solid #ddd;
            border-top: none;
            background-color: #f9f9f9;
        }}
        
        .footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            background-color: #f8f8f8;
            border-top: 1px solid #ddd;
        }}
        
        .task-progress {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .task-indicator {{
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
        }}
        
        .task-indicator.active {{
            background-color: #e31e24;
            color: white;
        }}
        
        .task-indicator.completed {{
            background-color: #28a745;
            color: white;
        }}
        
        .task-indicator.inactive {{
            background-color: #e9ecef;
            color: #6c757d;
        }}
        
        .navigation-buttons {{
            display: flex;
            gap: 10px;
        }}
        
        .btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        
        .btn-back {{
            background-color: #6c757d;
            color: white;
        }}
        
        .btn-next {{
            background-color: #007bff;
            color: white;
        }}
        
        .btn-submit {{
            background-color: #28a745;
            color: white;
        }}
        
        .btn:disabled {{
            background-color: #e9ecef;
            color: #6c757d;
            cursor: not-allowed;
        }}
        
        .btn:hover:not(:disabled) {{
            opacity: 0.9;
        }}
        
        @media (max-width: 768px) {{
            .main-content {{
                flex-direction: column;
                height: auto;
            }}
            
            .question-panel,
            .answer-panel {{
                width: 100%;
            }}
            
            .question-panel {{
                border-right: none;
                border-bottom: 1px solid #ddd;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-section">
            <div class="logo">IELTS GenAI</div>
            <div class="test-info">Test taker ID: {user_email}</div>
        </div>
        <div class="header-right">
            <div class="timer" id="timer">60:00</div>
        </div>
    </div>
    
    <div class="main-content">
        <div class="question-panel">
            <div class="part-header">
                <div class="part-title">Part {current_task_data['task_number']}</div>
                <div class="part-instructions">
                    You should spend about {current_task_data['time_minutes']} minutes on this task. Write at least {current_task_data['word_count']} words.
                </div>
            </div>
            
            <div class="task-content" id="taskPrompt">
                {question_text if current_task_data['task_number'] == 1 else f"<strong>Write about the following topic:</strong><br><br>{current_task_data.get('instructions', 'Essay prompt')}<br><br>Give reasons for your answer and include any relevant examples from your own knowledge or experience."}
            </div>
            
            {f'<div class="chart-container"><div class="chart-title">{chart_data.get("title", "")}</div>{chart_svg}</div>' if current_task_data['task_number'] == 1 and chart_svg else ''}
        </div>
        
        <div class="answer-panel">
            <div class="answer-area">
                <textarea 
                    id="essayText" 
                    class="answer-textarea" 
                    placeholder="Type your answer here..."
                    maxlength="5000"
                ></textarea>
                <div class="word-count">
                    Words: <span id="wordCount">0</span>
                </div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <div class="task-progress">
            <span class="task-indicator {'active' if current_task_data['task_number'] == 1 else 'completed' if len(tasks) > 1 else 'inactive'}">Part 1</span>
            {f'<span class="task-indicator {"active" if current_task_data["task_number"] == 2 else "inactive"}">Part 2</span>' if len(tasks) > 1 else ''}
            <span style="margin-left: 10px; font-size: 12px; color: #666;">
                {current_task_data['task_number']} of {len(tasks) if len(tasks) > 1 else 1}
            </span>
        </div>
        
        <div class="navigation-buttons">
            <button class="btn btn-back" onclick="history.back()">Back</button>
            <button class="btn btn-submit" id="submitBtn" disabled>Submit</button>
            <button class="btn btn-next" id="nextBtn" style="display: none;">Next</button>
        </div>
    </div>
    
    <script>
        // Initialize functionality
        const essayText = document.getElementById('essayText');
        const wordCount = document.getElementById('wordCount');
        const submitBtn = document.getElementById('submitBtn');
        const nextBtn = document.getElementById('nextBtn');
        const timer = document.getElementById('timer');
        
        let timeRemaining = 60 * 60; // 60 minutes
        let timerInterval = null;
        let currentTask = {current_task_data['task_number']};
        let totalTasks = {len(tasks) if len(tasks) > 1 else 1};
        let task1Completed = false;
        
        // Word count functionality
        function updateWordCount() {{
            const text = essayText.value.trim();
            const words = text ? text.split(/\s+/).length : 0;
            wordCount.textContent = words;
            
            const minWords = {current_task_data['word_count']};
            if (words >= minWords) {{
                submitBtn.disabled = false;
                submitBtn.style.backgroundColor = '#28a745';
            }} else {{
                submitBtn.disabled = true;
                submitBtn.style.backgroundColor = '#e9ecef';
            }}
        }}
        
        // Timer functionality
        function updateTimer() {{
            const minutes = Math.floor(timeRemaining / 60);
            const seconds = timeRemaining % 60;
            timer.textContent = `${{minutes}}:${{seconds.toString().padStart(2, '0')}}`;
            
            if (timeRemaining <= 0) {{
                clearInterval(timerInterval);
                alert('Time is up! Your essay will be submitted automatically.');
                submitAssessment();
            }}
            
            timeRemaining--;
        }}
        
        // Submit functionality
        function submitAssessment() {{
            const essayContent = essayText.value.trim();
            if (!essayContent) {{
                alert('Please write your essay before submitting.');
                return;
            }}
            
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';
            
            // Simulate submission
            setTimeout(() => {{
                if (currentTask === 1 && totalTasks > 1) {{
                    // Task 1 completed, show next button
                    task1Completed = true;
                    submitBtn.style.display = 'none';
                    nextBtn.style.display = 'inline-block';
                    nextBtn.disabled = false;
                    alert('Task 1 completed! Click "Next" to continue to Task 2.');
                }} else {{
                    // Final task completed
                    alert('Assessment completed! Your results are being processed.');
                    // In real implementation, redirect to results page
                }}
            }}, 1000);
        }}
        
        // Next button functionality
        function goToNextTask() {{
            if (currentTask === 1 && task1Completed) {{
                window.location.href = '/assessment/{assessment_type}?task=2&session_id={session_id}&user_email={user_email}';
            }}
        }}
        
        // Event listeners
        essayText.addEventListener('input', updateWordCount);
        submitBtn.addEventListener('click', submitAssessment);
        nextBtn.addEventListener('click', goToNextTask);
        
        // Initialize timer
        timerInterval = setInterval(updateTimer, 1000);
        updateTimer();
        
        // Load saved draft
        const savedDraft = localStorage.getItem('ielts_essay_draft_{session_id}');
        if (savedDraft) {{
            essayText.value = savedDraft;
            updateWordCount();
        }}
        
        // Auto-save every 30 seconds
        setInterval(() => {{
            if (essayText.value.trim()) {{
                localStorage.setItem('ielts_essay_draft_{session_id}', essayText.value);
            }}
        }}, 30000);
    </script>
</body>
</html>
"""
    
    return template

if __name__ == "__main__":
    # Test the template
    test_data = {
        'task_number': 1,
        'time_minutes': 20,
        'word_count': 150,
        'instructions': 'Test instructions'
    }
    
    template = create_official_ielts_template(
        "academic_writing", 
        "test@example.com", 
        "test_session", 
        test_data, 
        "Test question", 
        "<svg>test chart</svg>", 
        {"title": "Test Chart"}, 
        [test_data]
    )
    
    print("Template created successfully!")