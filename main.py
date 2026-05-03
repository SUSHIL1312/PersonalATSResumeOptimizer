import customtkinter as ctk
import threading
import os
import json
from datetime import datetime
import time
from PIL import Image

from ai_engine import optimize_resume_with_gemini, optimize_resume_with_chatgpt
from ats_engine import calculate_ats_score
from pdf_engine import generate_pdf
from pdf_parser import extract_text_from_pdf

# ---------------- CONFIG ---------------- #
CONFIG_FILE = "config.json"

def load_api_key(model="Gemini"):
    key_name = "gemini_key" if model == "Gemini" else "openai_key"
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f).get(key_name)
    return None

def save_api_key(model, key):
    data = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            
    key_name = "gemini_key" if model == "Gemini" else "openai_key"
    data[key_name] = key
    
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

# ---------------- API KEY POPUP ---------------- #
def set_api_key_popup():
    model = ai_model_var.get()
    
    def save():
        key = entry.get()
        if key:
            save_api_key(model, key)
            popup.destroy()
            update_api_button()

    popup = ctk.CTkToplevel(root)
    popup.title(f"Set {model} API Key")
    popup.geometry("400x150")

    entry = ctk.CTkEntry(popup, width=300, placeholder_text=f"Enter {model} API Key")
    
    current_key = load_api_key(model)
    if current_key:
        entry.insert(0, current_key)
        
    entry.pack(pady=20)

    ctk.CTkButton(popup, text="Save", command=save).pack()

# ---------------- UPDATE BUTTON ---------------- #
def update_api_button(*args):
    try:
        model = ai_model_var.get()
    except NameError:
        model = "Gemini"
    if load_api_key(model):
        api_btn.configure(text=f"Change {model} Key")
    else:
        api_btn.configure(text=f"Set {model} Key")

# ---------------- LOGGING ---------------- #
def log_msg(msg):
    def update():
        result_console.configure(state="normal")
        result_console.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        result_console.configure(state="disabled")
        result_console.see("end")
    root.after(0, update)

# ---------------- DEFAULT ATS ---------------- #
def check_default_ats():
    jd = jd_text.get("1.0", "end").strip()

    if not jd or jd == "Enter Job Description here...":
        log_msg("⚠️ Enter JD first")
        return

    def task():
        try:
            log_msg("⏳ Building and checking Default ATS...")
            default_tex = "input/defaultResume.tex"
            generate_pdf(default_tex)
            default_pdf = "input/defaultResume.pdf"
            text = extract_text_from_pdf(default_pdf)

            if not text:
                log_msg("❌ PDF parsing failed")
                return

            score = calculate_ats_score(jd, text)
            log_msg(f"✅ Default ATS Score: {score}%")

        except Exception as e:
            log_msg(f"❌ Error: {str(e)}")

    threading.Thread(target=task, daemon=True).start()

# ---------------- LOAD PDF ATS ---------------- #
def load_and_check_pdf():
    jd = jd_text.get("1.0", "end").strip()
    if not jd or jd == "Enter Job Description here...":
        log_msg("⚠️ Enter Job Description first")
        return

    file_path = ctk.filedialog.askopenfilename(
        title="Select Resume PDF",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if not file_path:
        return

    def task():
        try:
            log_msg(f"⏳ Analyzing {os.path.basename(file_path)}...")
            text = extract_text_from_pdf(file_path)
            if not text:
                log_msg("❌ PDF parsing failed or file is empty")
                return
                
            score = calculate_ats_score(jd, text)
            log_msg(f"✅ Loaded PDF ATS Score: {score}%")
        except Exception as e:
            log_msg(f"❌ Error reading PDF: {str(e)}")

    threading.Thread(target=task, daemon=True).start()

# ---------------- OPTIMIZATION ---------------- #
def run_optimizer():
    def reenable_btn():
        optimize_btn.configure(state="normal", text="🚀 Optimize Resume")

    jd = jd_text.get("1.0", "end").strip()
    profile = profile_var.get()
    exp = exp_entry.get()
    remarks = remarks_text.get("1.0", "end").strip()
    company = company_entry.get()

    if not jd or jd == "Enter Job Description here...":
        root.after(0, lambda: [log_msg("⚠️ Enter Job Description"), reenable_btn()])
        return
        
    if remarks == "Enter Remarks here...":
        remarks = ""

    selected_model = ai_model_var.get()
    api_key = load_api_key(selected_model)
    if not api_key:
        root.after(0, lambda: [log_msg(f"⚠️ Set {selected_model} API Key first"), reenable_btn()])
        return

    try:
        log_msg(f"⏳ Calling {selected_model} for optimization...")
        with open("input/defaultResume.tex") as f:
            resume = f.read()

        # -------- AI OPTIMIZATION -------- #
        if selected_model == "Gemini":
            optimized = optimize_resume_with_gemini(
                resume, jd, profile, exp, remarks, api_key
            )
        else:
            optimized = optimize_resume_with_chatgpt(
                resume, jd, profile, exp, remarks, api_key
            )
        
        # -------- INSTANT ATS -------- #
        score = calculate_ats_score(jd, optimized)

        # -------- SAVE FILE -------- #
        timestamp = datetime.now().strftime("%y%m%d_%H%M")
        comp_name = company.strip() if company.strip() else "UnknownCompany"
        output_dir = f"output/{profile}/{comp_name}"
        os.makedirs(output_dir, exist_ok=True)

        filename = f"{timestamp}_{profile}"
        tex_path = f"{output_dir}/{filename}.tex"
        
        global current_tex_path
        current_tex_path = tex_path

        with open(tex_path, "w") as f:
            f.write(optimized)
            
        def update_editor():
            editor.delete("1.0", "end")
            editor.insert("1.0", optimized)

        # Update UI instantly before generating PDF
        root.after(0, lambda: [log_msg(f"✅ Optimized ATS Score: {score}%\n⏳ Building PDF in background..."), update_editor()])

        # -------- GENERATE PDF IN BACKGROUND -------- #
        def build_pdf_task():
            try:
                generate_pdf(tex_path)
                root.after(0, lambda: log_msg(f"🎉 Saved: {filename}.pdf"))
            except Exception as e:
                root.after(0, lambda: log_msg(f"❌ PDF Error: {str(e)}"))
            finally:
                root.after(0, reenable_btn)

        pdf_thread = threading.Thread(target=build_pdf_task)
        pdf_thread.daemon = True
        pdf_thread.start()

    except Exception as e:
        err_msg = str(e)
        root.after(0, lambda m=err_msg: [log_msg(f"❌ Error: {m}"), reenable_btn()])

# ---------------- THREAD WRAPPER ---------------- #
def run_thread():
    optimize_btn.configure(state="disabled", text="⏳ Working...")
    thread = threading.Thread(target=run_optimizer)
    thread.daemon = True
    thread.start()

# ---------------- UI ---------------- #
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("ATS Resume Optimizer Pro")
root.geometry("1300x800")

# Create Main Frames
left_pane = ctk.CTkFrame(root, width=500)
left_pane.pack(side="left", fill="y", padx=10, pady=10)

right_pane = ctk.CTkFrame(root)
right_pane.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# ================= LEFT PANE ================= #
# Logo
try:
    logo_img = ctk.CTkImage(Image.open("assets/logo.png"), size=(80, 80))
    logo_label = ctk.CTkLabel(left_pane, image=logo_img, text="")
    logo_label.pack(pady=(10, 0))
except Exception as e:
    print("Logo load error:", e)

# Title
title = ctk.CTkLabel(left_pane, text="ATS Resume Optimizer Pro", font=("Arial", 28, "bold"))
title.pack(pady=5)

ctk.CTkLabel(left_pane, text="Job Description", font=("Arial", 16, "bold")).pack(pady=(10, 0))

# JD Input
jd_text = ctk.CTkTextbox(left_pane, height=150)
jd_text.pack(padx=20, pady=5, fill="x")
jd_text.insert("1.0", "Enter Job Description here...")
jd_text.bind("<FocusIn>", lambda e: jd_text.delete("1.0", "end") if jd_text.get("1.0", "end-1c") == "Enter Job Description here..." else None)
jd_text.bind("<FocusOut>", lambda e: jd_text.insert("1.0", "Enter Job Description here...") if not jd_text.get("1.0", "end-1c").strip() else None)

ctk.CTkLabel(left_pane, text="Candidate Details", font=("Arial", 16, "bold")).pack(pady=(10, 0))

# Input Frame
frame = ctk.CTkFrame(left_pane)
frame.pack(padx=20, pady=5, fill="x")

profile_var = ctk.StringVar(value="IT")
ai_model_var = ctk.StringVar(value="Gemini")

ctk.CTkOptionMenu(frame, variable=profile_var, values=["IT", "MBA"]).grid(row=0, column=0, padx=5)

ctk.CTkOptionMenu(frame, variable=ai_model_var, values=["Gemini", "ChatGPT"], command=update_api_button).grid(row=0, column=1, padx=5)

exp_entry = ctk.CTkEntry(frame, placeholder_text="Years of Experience", width=120)
exp_entry.grid(row=0, column=2, padx=5)

company_entry = ctk.CTkEntry(frame, placeholder_text="Company Name", width=120)
company_entry.grid(row=0, column=3, padx=5)

api_btn = ctk.CTkButton(frame, text="", command=set_api_key_popup, width=120)
api_btn.grid(row=0, column=4, padx=5)

ctk.CTkLabel(left_pane, text="Additional Remarks", font=("Arial", 16, "bold")).pack(pady=(10, 0))

# Remarks
remarks_text = ctk.CTkTextbox(left_pane, height=100)
remarks_text.pack(padx=20, pady=5, fill="x")
remarks_text.insert("1.0", "Enter Remarks here...")
remarks_text.bind("<FocusIn>", lambda e: remarks_text.delete("1.0", "end") if remarks_text.get("1.0", "end-1c") == "Enter Remarks here..." else None)
remarks_text.bind("<FocusOut>", lambda e: remarks_text.insert("1.0", "Enter Remarks here...") if not remarks_text.get("1.0", "end-1c").strip() else None)

# Buttons Frame
btn_frame = ctk.CTkFrame(left_pane)
btn_frame.pack(pady=15)

optimize_btn = ctk.CTkButton(
    btn_frame,
    text="🚀 Optimize Resume",
    fg_color="#4CAF50",
    hover_color="#45A049",
    font=("Arial", 14, "bold"),
    height=40,
    command=run_thread
)
optimize_btn.grid(row=0, column=0, padx=5)

ctk.CTkButton(
    btn_frame,
    text="Check Default ATS",
    font=("Arial", 14, "bold"),
    height=40,
    command=check_default_ats
).grid(row=0, column=1, padx=5)

ctk.CTkButton(
    btn_frame,
    text="Load PDF ATS",
    font=("Arial", 14, "bold"),
    height=40,
    command=load_and_check_pdf
).grid(row=0, column=2, padx=5)

# Result Console
result_console = ctk.CTkTextbox(left_pane, height=120, font=("Courier", 14), state="disabled")
result_console.pack(padx=20, pady=10, fill="both", expand=True)

# ================= RIGHT PANE ================= #
current_tex_path = None

preview_label = ctk.CTkLabel(right_pane, text="📄 LaTeX Editor & Preview", font=("Arial", 20, "bold"))
preview_label.pack(pady=10)

editor = ctk.CTkTextbox(right_pane, font=("Courier", 12))
editor.pack(fill="both", expand=True, padx=10, pady=5)

def rebuild_edited_pdf():
    if not current_tex_path:
        log_msg("⚠️ No resume generated to rebuild!")
        return
        
    text = editor.get("1.0", "end").strip()
    if not text:
        return
        
    def task():
        try:
            log_msg("⏳ Saving and Rebuilding PDF...")
            with open(current_tex_path, "w") as f:
                f.write(text)
            
            generate_pdf(current_tex_path)
            
            # Recalculate ATS
            jd = jd_text.get("1.0", "end").strip()
            pdf_path = current_tex_path.replace(".tex", ".pdf")
            pdf_text = extract_text_from_pdf(pdf_path)
            if pdf_text and jd and jd != "Enter Job Description here...":
                score = calculate_ats_score(jd, pdf_text)
                log_msg(f"✅ Rebuilt! New ATS Score: {score}%")
            else:
                log_msg(f"🎉 Rebuilt successfully!")
                
        except Exception as e:
            log_msg(f"❌ Rebuild Error: {str(e)}")
            
    threading.Thread(target=task, daemon=True).start()

rebuild_btn = ctk.CTkButton(
    right_pane, 
    text="⚙️ Save & Rebuild PDF", 
    fg_color="#008CBA",
    hover_color="#007399",
    font=("Arial", 16, "bold"),
    height=40,
    command=rebuild_edited_pdf
)
rebuild_btn.pack(pady=10)

# Initialize API button state
update_api_button()

# Run App
root.mainloop()