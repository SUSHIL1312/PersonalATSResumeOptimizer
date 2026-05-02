import customtkinter as ctk
import threading
import os
import json
from datetime import datetime
import time

from ai_engine import optimize_resume_with_gemini
from ats_engine import calculate_ats_score
from pdf_engine import generate_pdf
from pdf_parser import extract_text_from_pdf

# ---------------- CONFIG ---------------- #
CONFIG_FILE = "config.json"

def load_api_key():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f).get("gemini_key")
    return None

def save_api_key(key):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"gemini_key": key}, f)

# ---------------- API KEY POPUP ---------------- #
def set_api_key_popup():
    def save():
        key = entry.get()
        if key:
            save_api_key(key)
            popup.destroy()
            update_api_button()

    popup = ctk.CTkToplevel(root)
    popup.title("Set API Key")
    popup.geometry("400x150")

    entry = ctk.CTkEntry(popup, width=300, placeholder_text="Enter Gemini API Key")
    entry.pack(pady=20)

    ctk.CTkButton(popup, text="Save", command=save).pack()

# ---------------- UPDATE BUTTON ---------------- #
def update_api_button():
    if load_api_key():
        api_btn.configure(text="Change API Key")
    else:
        api_btn.configure(text="Set API Key")

# ---------------- DEFAULT ATS ---------------- #
def check_default_ats():
    jd = jd_text.get("1.0", "end")

    if not jd.strip():
        result_label.configure(text="Enter JD first")
        return

    try:
        default_tex = "input/defaultResume.tex"

        # Generate PDF in same folder
        generate_pdf(default_tex)

        default_pdf = "input/defaultResume.pdf"

        text = extract_text_from_pdf(default_pdf)

        if not text:
            result_label.configure(text="PDF parsing failed")
            return

        score = calculate_ats_score(jd, text)

        result_label.configure(text=f"Default ATS Score: {score}%")

    except Exception as e:
        result_label.configure(text=str(e))

# ---------------- OPTIMIZATION ---------------- #
def run_optimizer():
    jd = jd_text.get("1.0", "end")
    profile = profile_var.get()
    exp = exp_entry.get()
    remarks = remarks_text.get("1.0", "end")
    company = company_entry.get()

    if not jd.strip():
        result_label.configure(text="Enter Job Description")
        return

    api_key = load_api_key()
    if not api_key:
        result_label.configure(text="Set API Key first")
        return

    try:
        with open("input/defaultResume.tex") as f:
            resume = f.read()

        # -------- GEMINI -------- #
        optimized = optimize_resume_with_gemini(
            resume, jd, profile, exp, remarks, api_key
        )

        # -------- SAVE FILE -------- #
        date_folder = datetime.now().strftime("%Y-%m-%d")
        os.makedirs(f"output/{date_folder}", exist_ok=True)

        filename = f"{company}_{profile}_{int(time.time())}"

        tex_path = f"output/{date_folder}/{filename}.tex"

        with open(tex_path, "w") as f:
            f.write(optimized)

        # -------- GENERATE PDF -------- #
        generate_pdf(tex_path)

        pdf_path = tex_path.replace(".tex", ".pdf")

        # -------- ATS FROM PDF -------- #
        pdf_text = extract_text_from_pdf(pdf_path)

        if not pdf_text:
            result_label.configure(text="PDF parsing failed")
            return

        score = calculate_ats_score(jd, pdf_text)

        result_label.configure(
            text=f"Optimized ATS Score: {score}%\nSaved: {filename}.pdf"
        )

    except Exception as e:
        result_label.configure(text=str(e))

# ---------------- THREAD WRAPPER ---------------- #
def run_thread():
    threading.Thread(target=run_optimizer).start()

# ---------------- UI ---------------- #
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("ATS Resume Optimizer")
root.geometry("900x700")

# Title
title = ctk.CTkLabel(root, text="ATS Resume Optimizer", font=("Arial", 24))
title.pack(pady=10)

# JD Input
jd_text = ctk.CTkTextbox(root, height=150)
jd_text.pack(padx=20, pady=10, fill="x")

# Input Frame
frame = ctk.CTkFrame(root)
frame.pack(padx=20, pady=10, fill="x")

profile_var = ctk.StringVar(value="IT")

ctk.CTkOptionMenu(frame, variable=profile_var, values=["IT", "MBA"]).grid(row=0, column=0, padx=10)

exp_entry = ctk.CTkEntry(frame, placeholder_text="Years of Experience")
exp_entry.grid(row=0, column=1, padx=10)

company_entry = ctk.CTkEntry(frame, placeholder_text="Company Name")
company_entry.grid(row=0, column=2, padx=10)

api_btn = ctk.CTkButton(frame, text="", command=set_api_key_popup)
api_btn.grid(row=0, column=3, padx=10)

# Remarks
remarks_text = ctk.CTkTextbox(root, height=100)
remarks_text.pack(padx=20, pady=10, fill="x")

# Buttons Frame
btn_frame = ctk.CTkFrame(root)
btn_frame.pack(pady=10)

ctk.CTkButton(
    btn_frame,
    text="Optimize Resume",
    command=run_thread
).grid(row=0, column=0, padx=10)

ctk.CTkButton(
    btn_frame,
    text="Check Default ATS",
    command=check_default_ats
).grid(row=0, column=1, padx=10)

# Result
result_label = ctk.CTkLabel(root, text="", font=("Arial", 16))
result_label.pack(pady=20)

# Initialize API button state
update_api_button()

# Run App
root.mainloop()