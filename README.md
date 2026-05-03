
# 🚀 ATS Resume Optimizer Pro

A highly advanced, AI-powered desktop application built with Python and CustomTkinter that automatically tailors your LaTeX resume to any Job Description (JD) to maximize your ATS (Applicant Tracking System) score.

It supports dual AI engines (**Google Gemini** & **OpenAI ChatGPT**) and provides a production-ready, dual-pane environment to preview, edit, and rebuild your optimized resumes on the fly.

---

## ✨ Features

- 🤖 **Dual AI Engines**: Switch seamlessly between Gemini and ChatGPT directly from the UI
- 🎯 **Intelligent Tailoring**:
  - IT → Strict (no fake skills)
  - MBA → JD-aligned optimization
- 📈 **Live ATS Scoring**:
  - Keyword + synonym matching
  - Skill alignment
  - Experience weighting
  - Content quality checks
- 🖥️ **Dual-Pane Workstation**:
  - Left → Inputs (JD, profile, remarks)
  - Right → Live LaTeX editor
- ✏️ **Edit Resume from UI**:
  - Modify `defaultResume.tex` directly inside the app
- 🔄 **Instant PDF Rebuild**:
  - Edit → Save → Rebuild → Recalculate ATS
- 📂 **Smart File Organization**:
  - Saved as: `Profile/Company/Date/`
- 🖱️ **Resizable UI Panels**:
  - Adjust window partitions using mouse
- ⚡ **Non-blocking UI**:
  - Smooth experience (no freezing)

---

## 🛠️ Prerequisites

You **MUST** have LaTeX installed (used for PDF generation).

---

### ✅ Check if LaTeX is already installed

```bash
pdflatex --version
````

✔ If it shows version → **No need to install again**
❌ If command not found → install LaTeX

---

### 📦 Install LaTeX (if not installed)

#### Mac (Recommended - lightweight)

```bash
brew install --cask basictex
```

Then:

```bash
echo 'export PATH="/Library/TeX/texbin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

---

#### Windows

* Install MiKTeX: [https://miktex.org/download](https://miktex.org/download)

---

#### Linux

```bash
sudo apt-get install texlive-full
```

---

## 💻 Setup & Installation

---

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd PersonalATSResumeOptimizer
```

---

### 2. Check Existing Environments (Optional)

```bash
ls
```

👉 If you already see something like:

```text
atsResumeEnv/
```

✔ You can reuse it
❌ Otherwise create new

---

### 3. Create Virtual Environment

```bash
python3 -m venv atsResumeEnv
```

---

### 4. Activate Environment

#### Mac / Linux

```bash
source atsResumeEnv/bin/activate
```

#### Windows

```bash
atsResumeEnv\Scripts\activate
```

---

### 5. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🚀 Running the Application

```bash
python main.py
```

---

## 🔑 API Key Setup (From UI)

No manual setup required in code.

### Steps:

1. Launch app
2. Click:

   * **Set Gemini Key**
   * OR **Set ChatGPT Key**
3. Paste your API key
4. Save

👉 Keys are stored locally in `config.json`

---

### 🔗 Get API Keys

* Gemini:
  👉 [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

* OpenAI:
  👉 [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

---

## 🧑‍💻 How to Use

1. Paste Job Description
2. Select:

   * Profile (IT / MBA)
   * Experience
3. Enter Company Name
4. (Optional) Add Remarks

---

### 🔘 Optimize Resume

* Generates optimized LaTeX
* Builds PDF
* Calculates ATS score

---

### 🔘 Check Default ATS

* Calculates ATS score for original resume

---

### ✏️ Edit Resume Inside App

* Modify LaTeX directly
* Click **Save & Rebuild PDF**

---

## 📂 Project Structure

```
PersonalATSResumeOptimizer/
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
├── assets/
│
├── output/
│   └── Profile/Company/Date/
```

---

## 📄 Resume Input Format

You can update the defaultResume form the UI too. 

Your base resume must be in:

```
input/defaultResume.tex
```

---

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

* Keep valid LaTeX syntax
* Use proper environments (`itemize`, etc.)
* Avoid broken commands

---

## 📊 ATS Scoring Logic

The scoring system considers:

* Keyword relevance
* Skill matching
* Experience alignment
* Content quality
* Resume structure


---

## 🤝 Contributing

Feel free to fork and improve this project.

---

## ⭐ Support

If you found this useful, consider giving it a ⭐ on GitHub!

