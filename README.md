# AI-Powered Job Readiness Platform

This project demonstrates a minimal implementation of an AI-powered platform for evaluating job readiness.  
It supports skill extraction, mapping, and readiness scoring through a simple Streamlit interface.

## Features

- Extraction of skills from job descriptions
- Role-based skill mapping
- Union merge of role skills and job description skills for evaluation
- Readiness scoring with improvement recommendations
- Streamlit web interface with CSV export support

## Quick Start

Clone the repository and set up the environment:

```bash
git clone https://github.com/AarishIrfan/ai-job-readiness.git
cd ai-job-readiness
python -m venv venv
# Activate venv
#   Windows: venv\Scripts\activate
#   Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
````

## Project Structure

```
ai-job-readiness/
│── app.py               # Streamlit application entry point
│── requirements.txt     # Python dependencies
│── utils/               # Helper functions (skill extraction, scoring, parsing)
│── data/                # Sample roles and job descriptions
│── README.md            # Documentation
```

Do you also want me to include a **"Deployment on Streamlit Cloud"** section (with steps and `requirements.txt` handling), so that anyone can run it online without local setup?
```
