# Fake News Detection and News Sentiment Analysis System
### Natural Language Processing (NLP) Major Project – Topic #4
**Faculty Coordinator:** Prof. Sagar Jain | **Team:** Group of 5 Students

---

## 🌟 Overview
This project implements **Project 4: Fake News Detection and News Sentiment Analysis System** from the official syllabus list.

It fulfills all mandatory academic components:
1. ✅ **Project Development:** Fully implemented NLP pipeline: Tokenization, Stopword removal, TF-IDF Vectorization, Word2Vec embeddings, Multinomial Naïve Bayes, Logistic Regression, Ensemble voting, and Sentiment Analysis.
2. ✅ **Working Website/Web Application:** Modern, responsive Flask web application featuring instant 1-click test samples (ISRO, WHO, Miracle Cure, 5G Conspiracy), model toggle selector, glowing Real/Fake verdict cards, sentiment polarity meter, subjectivity bar, and clickbait phrase tags.
3. ✅ **Project Report (PDF & Markdown):** Complete formal academic report (`Fake_News_Project_Report.pdf` and `PROJECT_REPORT.md`) containing all 14 required sections.
4. ✅ **PowerPoint Presentation (PPTX & Script):** Complete 13-slide 16:9 widescreen presentation deck (`Fake_News_Presentation.pptx` and `PRESENTATION_SLIDES.md`) structured with speaker notes for 5 students.

---

## 📂 Directory Structure

```
fake_news_detector/
├── app.py                          # Flask Web Server & API endpoints
├── nlp_model.py                    # NLP preprocessing, TF-IDF, Naive Bayes, Logistic Regression & Sentiment
├── dataset.py                      # Verified real news and viral fake news test samples
├── generate_report_pdf.py          # Script compiling the academic PDF report
├── generate_presentation_pptx.py   # Script compiling the 16:9 widescreen PPTX deck
├── Fake_News_Project_Report.pdf    # Compiled formal PDF Project Report
├── Fake_News_Presentation.pptx     # Compiled PowerPoint Presentation Deck
├── PROJECT_REPORT.md               # Complete Project Report in Markdown
├── PRESENTATION_SLIDES.md          # Complete Presentation Slides & Speaker Script
├── requirements.txt                # Python project dependencies
├── templates/
│   └── index.html                  # Web application UI template
└── static/
    ├── css/
    │   └── style.css               # Modern dark glassmorphic styling
    └── js/
        └── script.js               # Dynamic client-side interactions
```

---

## 🚀 How to Run the Web Application

### Step 1: Open Terminal / PowerShell in Project Directory
```powershell
cd C:\Users\Admin\.gemini\antigravity\scratch\fake_news_detector
```

### Step 2: Install Dependencies (if not already installed)
```powershell
pip install -r requirements.txt
```

### Step 3: Run the Flask Application
```powershell
python app.py
```

### Step 4: Open in Web Browser
Navigate to:
```
http://127.0.0.1:5000
```

### Step 5: Test in 1-Click
- Click any sample button (e.g., **"Real: ISRO Space"** or **"Fake: Miracle Cure"**).
- Choose the classifier: **Logistic Regression**, **Multinomial Naïve Bayes**, or **Ensemble Hybrid**.
- Click **"Analyze Veracity & Sentiment"**.
- View the real-time verdict, confidence score, sentiment polarity meter, and clickbait triggers!

---

## 👥 Group of 5 Students – Roles & Presentation Distribution

| Member | Assigned Project Role | Specific Presentation Slides |
| :--- | :--- | :--- |
| **Student 1** (Team Lead) | System Architecture & Backend | **Slides 1–2:** Title, Overview & Problem Statement |
| **Student 2** | Preprocessing & Literature Review | **Slides 3–4:** Motivation & Literature Review |
| **Student 3** | Feature Engineering & Math | **Slides 5–6:** Technologies & Mathematical Formulations |
| **Student 4** | Machine Learning & Classifiers | **Slides 7–9:** System Architecture, Classifiers & Stylometrics |
| **Student 5** | Web App, UI & Testing | **Slides 10–13:** Live Web Demo, Results, Conclusion & Q&A |

