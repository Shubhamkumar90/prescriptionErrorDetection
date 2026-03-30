# Prescription Error Detection System

<p align="center">
AI-powered system to detect and analyze errors in handwritten medical prescriptions using OCR and intelligent drug validation.
</p>

---

## Overview

This project aims to assist in reducing medication errors by automatically extracting and validating prescription data. It combines **OCR (Optical Character Recognition)** with **drug analysis logic** to identify potential issues in prescriptions.

---

## Features

- Extracts text from handwritten prescriptions using TrOCR
- Identifies and analyzes prescribed drugs
- Detects possible errors (dosage, spelling, unknown drugs)
- Provides user-friendly explanations of detected issues
- Web interface for easy image upload and results visualization
- Fast API-based processing using FastAPI backend

---

## Tech Stack

**Frontend:**
- React.js

**Backend:**
- FastAPI (Python)

**Machine Learning:**
- PyTorch
- HuggingFace Transformers (TrOCR)


**Other Tools & Platforms:**
- HuggingFace
- Kaggle

**Deployment:** 
- <a href='https://huggingface.co/spaces/shubham879/trocrApi'>Hugging Face Spaces</a> 
- <a href='https://prescription-error-detection.vercel.app/'>Vercel</a>

---

## How It Works

1. User uploads a prescription image
2. Image is processed using **TrOCR model**
3. Extracted text is analyzed
4. Drug names are validated
5. Errors are detected
6. System generates explanation
7. Results are returned via FastAPI and displayed on UI

---

## API Endpoint

### POST `/process-image`

**Request:**
- Form-data → image file

**Response:**
```json
{
  "ocr_text": "Extracted prescription text",
  "drug_analysis": [
    {
      "drug": "Paracetamol",
      "status": "Valid",
      "issue": null
    }
  ],
  "user_explanation": "No major issues detected. Prescription looks safe.",
  "success": true
}
```
---
## Model Details

- **Model:** TrOCR (Transformer-based OCR)  
- **Fine-tuned on:** Doctor’s Handwritten Prescription BD Dataset
- **CER (Character Error Rate):** ~9%  
- **Accuracy:** ~73%  

---

## UI Features

- Image preview before upload  
- Side-by-side display:
  - OCR Text  
  - Explanation  
- Structured drug analysis table  

---
## Error Detection Capabilities

- Unknown drugs  
- Misspelled medications  
- Unsafe prescriptions  
- Missing information  
- Drug validation using DrugBank database  
- Dosage validation system  

---  

## Visuals
### Upload Interface
<p align="center"><img width="944" height="421" alt="image" src="https://github.com/user-attachments/assets/7a8fca38-bba2-4e83-84fb-102eddf92046" /></p>

### Results View
<p align="center"><img width="900" height="500" alt="image" src="https://github.com/user-attachments/assets/684ee5a7-0894-47e2-8e9a-ab3309ad694f" /></p>

---
## Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/Shubhamkumar90/prescriptionErrorDetection.git
cd prescription-error-detection
```
### 2. Setup Environment Variables
Create a `.env` file inside the `backend/` folder:

```bash
cd backend
touch .env
```
Add the following:
```env
GEMINI_API_KEY=your_google_gemini_api_key
```
### 3. Setup Backend
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
Backend will run at:
```
http://127.0.0.1:8000
```
### 4. Setup Frontend
```bash
cd ../frontend
npm install
npm run dev
```
---
## Acknowledgements

- Hugging Face for TrOCR and deployment via Spaces  
- Google Gemini API for explanation generation  
- Doctor’s Handwritten Prescription Dataset for OCR training  
- DrugBank database for drug validation and analysis (access obtained via official request)  
- Open-source community for PyTorch, FastAPI, React, and other tools  
