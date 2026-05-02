
# 🚀 ATS Resume Optimizer (Python + Gemini + LaTeX)

A desktop application that helps you **optimize your resume based on a Job Description (JD)** and evaluate it using a realistic **ATS (Applicant Tracking System) score**.

---

## ✨ Features

- 🤖 AI-powered Resume Optimization (Gemini)
- 📊 ATS Score based on **parsed PDF (realistic approach)**
- 🎯 Profile-based behavior:
  - **IT** → strict (no fake skills added)
  - **MBA** → flexible (JD-aligned optimization)
- 📁 Organized output 
- 🖥️ Modern GUI (CustomTkinter)
- 🔐 One-time Gemini API key setup

---

## ⚙️ Setup Instructions

### 🧪 1. Create Virtual Environment

```bash
python -m venv atsOptimize
````

---

### ▶️ 2. Activate Environment

#### 💻 Mac / Linux

```bash
source atsOptimize/bin/activate
```

#### 🪟 Windows

```bash
atsOptimize\Scripts\activate
```

---

### 📦 3. Install Dependencies

```bash
pip install customtkinter google-generativeai pymupdf
```

---

### 📄 4. Install LaTeX (Required)

Install one of the following:

* **Mac** → MacTeX
* **Windows** → MiKTeX
* **Linux** → TeX Live

Verify installation:

```bash
pdflatex --version
```

---

## 🔑 Gemini API Setup

1. Go to:
   👉 [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

2. Generate an API key

3. Run the app and click:

```
Set API Key
```

4. Paste your key (stored locally in `config.json`)

---

## 📂 Project Structure

```
ats_resume_optimizer/
│
├── main.py
├── ai_engine.py
├── ats_engine.py
├── pdf_engine.py
├── pdf_parser.py
├── config.json
│
├── input/
│   └── defaultResume.tex
│
├── output/
│   └── YYYY-MM-DD/
```

---

## 📄 Input Resume Format

Place your resume in:

```
input/defaultResume.tex
```

### Example:

```latex
\documentclass{article}
\begin{document}

\section*{Experience}
...

\section*{Projects}
...

\section*{Skills}
C++, Java, Python

\end{document}
```

---

### ⚠️ Important

* Maintain **valid LaTeX syntax**
* Use proper environments (`itemize`, `enumerate`)
* Avoid broken commands like:

  ```
  \resumeItem (outside itemize)
  ```

---

## ▶️ Run the Application

```bash
python main.py
```

---

## 🧑‍💻 How to Use

1. Launch the app
2. Paste Job Description
3. Select:

   * Profile (IT / MBA)
   * Experience
4. Enter Company Name
5. (Optional) Add Remarks

---

### 🔘 Optimize Resume

* Generates optimized resume
* Converts to PDF
* Calculates ATS score

---

### 🔘 Check Default ATS

* Calculates ATS score of your original resume

---

## 📦 Output

Generated files are stored in:

```
output/YYYY-MM-DD/
```

Example:

```
output/2026-05-02/Google_IT_1714647382.pdf
```

---

## 📊 ATS Scoring Logic

* Extracts text from PDF
* Matches keywords with JD
* Checks presence of sections:

  * Skills
  * Experience
  * Projects

---

## ⚠️ Notes

* ATS score depends on PDF parsing (real-world behavior)
* Complex layouts may reduce parsing accuracy
* Ensure LaTeX compiles successfully

---

## 🚀 Future Improvements

* Resume diff viewer (before vs after)
* Keyword highlighting
* ATS improvement explanation
* Web-based SaaS version

---

## 🤝 Contributing

Feel free to fork and improve this project.



