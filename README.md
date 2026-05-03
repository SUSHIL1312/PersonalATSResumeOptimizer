# 🚀 ATS Resume Optimizer Pro

A highly advanced, AI-powered desktop application built with Python and CustomTkinter that automatically tailors your LaTeX resume to any Job Description (JD) to maximize your ATS (Applicant Tracking System) score.

It supports dual AI engines (**Google Gemini** & **OpenAI ChatGPT**) and provides a production-ready, dual-pane environment to preview, edit, and rebuild your optimized resumes on the fly.

---

## ✨ Features

- **🤖 Dual AI Engines**: Switch seamlessly between Gemini and ChatGPT.
- **🎯 Intelligent Tailoring**: Aggressively aligns MBA resumes with the JD, while strictly locking hard tech skills for IT profiles to prevent hallucinations.
- **📈 Live ATS Scoring**: Uses advanced synonym matching, stop-word filtering, and n-gram analysis to accurately score your resume against the JD.
- **🖥️ Dual-Pane Workstation**: View your inputs on the left and a live LaTeX editor/preview on the right.
- **⚙️ Instant PDF Rebuilding**: Edit the AI-generated LaTeX directly in the app and click "Save & Rebuild PDF" to recompile and instantly rescore your resume.
- **📂 Automated Organization**: Automatically saves your optimized `.tex` and `.pdf` files into tidy folders structured by `Profile/Company/Date`.

---

## 🛠️ Prerequisites

Before installing the python packages, you **MUST** have a working LaTeX distribution installed on your system because the application uses `pdflatex` to compile the PDF files in the background.

- **Mac**: Install [BasicTeX](https://tug.org/mactex/morepackages.html) (or run `brew install --cask basictex` as it is much smaller than full MacTeX)
- **Windows**: Install [MiKTeX](https://miktex.org/download) or [TeX Live](https://tug.org/texlive/)
- **Linux**: Run `sudo apt-get install texlive-full`

---

## 💻 Setup & Installation

Follow these steps to set up the project on your local machine.

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd PersonalATSResumeOptimizer
```

### 2. Create a Virtual Environment
It is highly recommended to use a virtual environment to keep dependencies isolated.
```bash
# Create the virtual environment named "atsResumeEnv"
python3 -m venv atsResumeEnv
```

### 3. Activate the Virtual Environment
**On Mac / Linux:**
```bash
source atsResumeEnv/bin/activate
```
**On Windows:**
```cmd
atsResumeEnv\Scripts\activate
```
*(You will know it is activated when you see `(atsResumeEnv)` at the beginning of your terminal prompt).*

### 4. Install Dependencies
With the virtual environment activated, install all required packages:
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Application

Once your dependencies are installed, you can launch the app:

```bash
python main.py
```

### 🔑 Setting up API Keys
1. When the app opens, look for the **"Set Gemini Key"** (or **"Set ChatGPT Key"**) button in the left panel.
2. Click it, paste your API key, and click Save. 
3. The app securely stores this in a local `config.json` file. You can switch between AI models using the dropdown, and the app will remember both keys independently.

---

## 📁 Directory Structure
- `main.py`: The main GUI application.
- `ai_engine.py`: Handles all API communication and strict prompting logic for Gemini/ChatGPT.
- `ats_engine.py`: The algorithm that calculates the ATS score.
- `pdf_engine.py`: The bridge that talks to your system's `pdflatex` compiler.
- `pdf_parser.py`: Extracts and reads text from PDFs.
- `input/defaultResume.tex`: Your base, un-optimized resume template.
- `assets/`: Contains UI assets like the app logo.
- `output/`: Where all your neatly organized, company-specific tailored resumes are saved!
