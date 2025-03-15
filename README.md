---
title: University Portal Assistant
emoji: 🎓
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.32.0
app_file: minimal_app.py
pinned: false
license: mit
---

# University Portal Assistant

A Streamlit-based chatbot application that helps university students and staff with portal-related queries.

## Features

- User-friendly chat interface built with Streamlit
- Answers frequently asked questions about the university portal
- Enhanced responses using OpenAI's GPT-4o model
- Fallback mechanism for unanswered questions
- Professional UI with custom styling

## Requirements

- Python 3.8+
- Streamlit
- OpenAI API key
- Agno framework

## Setup

1. Clone this repository
2. Install the required packages:

   ```bash
   pip install streamlit openai python-dotenv pandas agno
   ```

3. Create a `.env` file with your OpenAI API key:

   ```bash
   OPENAI_API_KEY=your_api_key_here
   ```

4. Run the application:

   ```bash
   streamlit run minimal_app.py
   ```

## Files

- `minimal_app.py`: Main Streamlit application
- `university_portal_faqs.csv`: CSV file containing frequently asked questions and answers
- `unanswered_questions.csv`: CSV file for storing unanswered questions for human follow-up

## How It Works

The application uses a keyword-based matching system to find the most relevant FAQ for a user query. It then enhances the response using OpenAI's GPT-4o model to provide a more professional and helpful answer. If no matching FAQ is found, the question is saved for human follow-up.
