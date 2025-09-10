# Advanced Resume Screening Assistant

An AI-powered Streamlit web application that automates resume screening by comparing resumes against a job description (JD). It extracts text, contact information, and skills from resumes and ranks candidates based on semantic similarity with the JD.

---

## Features

- Upload or paste **Job Description** (PDF/DOCX or text).  
- Upload multiple **Resumes** (PDF/DOCX).  
- **Automatic parsing** of resumes to extract text, sections, and contact info.  
- **Semantic similarity scoring** between JD and resumes using NLP embeddings.  
- **Skill extraction** from resumes and JD for detailed matching.  
- **Interactive results dashboard** with metrics, charts, and tables.  
- **Export results** as CSV or Excel.

---

## Tech Stack

- **Python 3.10+**  
- **Streamlit** – Web interface  
- **PyMuPDF (fitz)** – PDF parsing  
- **python-docx** – DOCX parsing  
- **Sentence Transformers** – NLP embeddings for semantic similarity  
- **Pandas & Plotly** – Data processing & visualization
