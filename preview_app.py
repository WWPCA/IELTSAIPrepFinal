#!/usr/bin/env python3
"""
Simple Flask app to preview the updated working_template.html
"""

from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    """Serve the updated working template for preview"""
    with open('working_template.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    return template_content

@app.route('/login')
def login():
    """Serve login page"""
    with open('login.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    return template_content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)