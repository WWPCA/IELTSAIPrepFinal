"""
IELTS Writing Assessment Routes
This module provides routes for assessing IELTS writing responses using OpenAI GPT-4o.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models import db, PracticeTest, UserTestAttempt, User, CompleteTestProgress
from openai_writing_assessment import assess_writing_task1, assess_writing_task2, assess_complete_writing_test
import json
import os

writing_assessment = Blueprint('writing_assessment', __name__)

@writing_assessment.route('/writing/submit_task/<int:test_id>', methods=['POST'])
@login_required
def submit_writing_task(test_id):
    """
    Submit a writing task for assessment
    """
    try:
        # Get the test
        test = PracticeTest.query.get_or_404(test_id)
        
        # Verify user has access to this test
        if not test.is_free and not current_user.is_subscribed():
            flash("You must be subscribed to submit this test.", "danger")
            return redirect(url_for('practice.test_details', test_type='writing', test_id=test_id))
        
        # Check if user has already taken this test
        if current_user.has_taken_test(test_id, 'writing'):
            flash("You have already taken this test. Premium users can take each test once to keep costs manageable.", "warning")
            
            # Find their previous attempt to display results
            previous_attempt = UserTestAttempt.query.filter_by(
                user_id=current_user.id,
                test_id=test_id
            ).order_by(UserTestAttempt.attempt_date.desc()).first()
            
            if previous_attempt:
                return redirect(url_for('writing_assessment.writing_assessment_results', attempt_id=previous_attempt.id))
            else:
                return redirect(url_for('practice.test_details', test_type='writing', test_id=test_id))
        
        # Get the essay text from the form
        essay_text = request.form.get('essay_text', '')
        
        if not essay_text or len(essay_text.strip()) < 50:
            flash("Your essay is too short. Please write a more substantial response.", "warning")
            return redirect(url_for('practice.take_test', test_type='writing', test_id=test_id))
        
        # Get the test data
        test_questions = test.questions
        
        # Determine if this is Task 1 or Task 2 based on the test section
        task_number = 1 if test.section == 1 else 2
        
        # Get the task prompt
        task_prompt = test_questions[0]['question'] if test_questions else ''
        
        # Process based on task type
        if task_number == 1:
            assessment = assess_writing_task1(essay_text, task_prompt, test.ielts_test_type)
        else:
            assessment = assess_writing_task2(essay_text, task_prompt, test.ielts_test_type)
        
        # Calculate the overall band score for this task
        overall_task_score = 0
        if "scores" in assessment:
            scores = assessment["scores"]
            task_score_key = "Task Achievement" if task_number == 1 else "Task Response"
            overall_task_score = (
                scores.get(task_score_key, 0) + 
                scores.get("Coherence and Cohesion", 0) + 
                scores.get("Lexical Resource", 0) + 
                scores.get("Grammatical Range and Accuracy", 0)
            ) / 4
        
        # Create a new attempt record
        attempt = UserTestAttempt(
            user_id=current_user.id,
            test_id=test_id,
            user_answers=json.dumps({'essay_text': essay_text}),
            score=overall_task_score,
            assessment=json.dumps(assessment)
        )
        
        # If this is part of a complete test, link it to the test progress
        complete_test_progress_id = session.get('complete_test_progress_id')
        if complete_test_progress_id:
            attempt.complete_test_progress_id = complete_test_progress_id
            test_progress = CompleteTestProgress.query.get(complete_test_progress_id)
            if test_progress:
                # Mark this section as completed
                test_progress.mark_section_completed('writing', overall_task_score)
                
                # Update progress current section
                if test_progress.is_test_completed():
                    test_progress.current_section = None
                else:
                    test_progress.current_section = test_progress.get_next_section()
                    
                db.session.add(test_progress)
        
        db.session.add(attempt)
        
        # Mark test as completed for this user
        current_user.mark_test_completed(test_id, 'writing')
        
        # Update the user's streak
        current_user.update_streak()
        
        db.session.commit()
        
        # Redirect to the results page
        return redirect(url_for('writing_assessment.writing_assessment_results', attempt_id=attempt.id))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error processing writing submission: {str(e)}")
        flash(f"An error occurred while processing your submission. Please try again.", "danger")
        return redirect(url_for('practice.take_test', test_type='writing', test_id=test_id))

@writing_assessment.route('/writing/results/<int:attempt_id>')
@login_required
def writing_assessment_results(attempt_id):
    """
    Display the results of a writing assessment
    """
    # Get the attempt
    attempt = UserTestAttempt.query.get_or_404(attempt_id)
    
    # Verify this attempt belongs to the current user
    if attempt.user_id != current_user.id:
        flash("You are not authorized to view these results.", "danger")
        return redirect(url_for('practice.index'))
    
    # Get the test
    test = PracticeTest.query.get_or_404(attempt.test_id)
    
    # Get the assessment data
    assessment = json.loads(attempt.assessment) if attempt.assessment else {}
    
    # Determine if this is part of a complete test
    is_part_of_complete_test = attempt.complete_test_progress_id is not None
    
    # Prepare data for the template
    data = {
        'attempt': attempt,
        'test': test,
        'assessment': assessment,
        'user_essay': json.loads(attempt.user_answers).get('essay_text', ''),
        'band_score': round(float(attempt.score or 0), 1),
        'task_number': 1 if test.section == 1 else 2,
        'is_part_of_complete_test': is_part_of_complete_test
    }
    
    # Render the results template
    return render_template('practice/writing_results.html', **data)

@writing_assessment.route('/api/writing/assess-task', methods=['POST'])
@login_required
def api_assess_writing_task():
    """
    API endpoint to assess a writing task
    """
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        essay_text = data.get('essay_text')
        task_prompt = data.get('task_prompt')
        task_number = int(data.get('task_number', 1))
        ielts_test_type = data.get('ielts_test_type', 'academic')
        
        if not essay_text or not task_prompt:
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Process based on task type
        if task_number == 1:
            assessment = assess_writing_task1(essay_text, task_prompt, ielts_test_type)
        else:
            assessment = assess_writing_task2(essay_text, task_prompt, ielts_test_type)
            
        return jsonify(assessment)
        
    except Exception as e:
        print(f"Error assessing writing task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@writing_assessment.route('/api/writing/assess-complete-test', methods=['POST'])
@login_required
def api_assess_complete_writing_test():
    """
    API endpoint to assess a complete writing test (Task 1 and Task 2)
    """
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        task1_essay = data.get('task1_essay')
        task1_prompt = data.get('task1_prompt')
        task2_essay = data.get('task2_essay')
        task2_prompt = data.get('task2_prompt')
        ielts_test_type = data.get('ielts_test_type', 'academic')
        
        if not task1_essay or not task1_prompt or not task2_essay or not task2_prompt:
            return jsonify({'error': 'Missing required parameters'}), 400
            
        assessment = assess_complete_writing_test(
            task1_essay, task1_prompt, 
            task2_essay, task2_prompt, 
            ielts_test_type
        )
            
        return jsonify(assessment)
        
    except Exception as e:
        print(f"Error assessing complete writing test: {str(e)}")
        return jsonify({'error': str(e)}), 500