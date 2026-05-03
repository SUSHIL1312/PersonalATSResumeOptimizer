import customtkinter as ctk
import threading
import os
import json
from datetime import datetime
import time
import sys
import subprocess
import tkinter as tk
from PIL import Image, ImageTk
import fitz  # PyMuPDF

from ai_engine import optimize_resume_with_gemini, optimize_resume_with_chatgpt
from ats_engine import calculate_ats_score
from pdf_engine import generate_pdf
from pdf_parser import extract_text_from_pdf

# ---------------- CONFIG ---------------- #
CONFIG_FILE = "config.json"

def load_config(model="Gemini"):
    key_name = "gemini_key" if model == "Gemini" else "openai_key"
    model_name_key = "gemini_model" if model == "Gemini" else "openai_model"
    default_model = "gemini-1.5-flash" if model == "Gemini" else "gpt-4o-mini"
    
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return data.get(key_name), data.get(model_name_key, default_model)
    return None, default_model

def save_config(model, key, model_name):
    data = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            
    key_name = "gemini_key" if model == "Gemini" else "openai_key"
    model_name_key = "gemini_model" if model == "Gemini" else "openai_model"
    
    data[key_name] = key
    data[model_name_key] = model_name
    
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

# ---------------- SETTINGS POPUP ---------------- #
def set_api_key_popup():
    model = ai_model_var.get()
    
    def save():
        key = key_entry.get().strip()
        model_name = model_entry.get().strip()
        if key and model_name:
            save_config(model, key, model_name)
            popup.destroy()
            update_api_button()

    popup = ctk.CTkToplevel(root)
    popup.title(f"Change {model} Settings")
    popup.geometry("400x250")

    ctk.CTkLabel(popup, text="API Key:").pack(pady=(20, 0))
    key_entry = ctk.CTkEntry(popup, width=300)
    key_entry.pack(pady=5)
    
    ctk.CTkLabel(popup, text="Model Name:").pack(pady=(10, 0))
    model_entry = ctk.CTkEntry(popup, width=300)
    model_entry.pack(pady=5)
    
    current_key, current_model = load_config(model)
    if current_key:
        key_entry.insert(0, current_key)
    if current_model:
        model_entry.insert(0, current_model)

    ctk.CTkButton(popup, text="Save Settings", command=save).pack(pady=20)

# ---------------- UPDATE BUTTON ---------------- #
def update_api_button(*args):
    try:
        model = ai_model_var.get()
    except NameError:
        model = "Gemini"
    key, _ = load_config(model)
    if key:
        api_btn.configure(text=f"Change {model} Settings")
    else:
        api_btn.configure(text=f"Set {model} Settings")

# ---------------- EDIT TEMPLATE POPUP ---------------- #
def edit_template_popup():
    template_path = "input/defaultResume.tex"
    
    def save():
        with open(template_path, "w") as f:
            f.write(text_box.get("1.0", "end"))
        popup.destroy()
        log_msg("✅ Default template updated.")

    popup = ctk.CTkToplevel(root)
    popup.title("📝 Edit Base Template")
    popup.geometry("800x600")

    text_box = ctk.CTkTextbox(popup, font=("Courier", 12))
    text_box.pack(fill="both", expand=True, padx=10, pady=10)
    
    if os.path.exists(template_path):
        with open(template_path, "r") as f:
            text_box.insert("1.0", f.read())

    ctk.CTkButton(popup, text="💾 Save Template", command=save, fg_color="#4CAF50", hover_color="#45A049", height=40).pack(pady=10)

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
    api_key, model_name = load_config(selected_model)
    if not api_key:
        root.after(0, lambda: [log_msg(f"⚠️ Set {selected_model} API Key first"), reenable_btn()])
        return

    try:
        log_msg(f"⏳ Calling {selected_model} ({model_name}) for optimization...")
        with open("input/defaultResume.tex") as f:
            resume = f.read()

        # -------- AI OPTIMIZATION -------- #
        if selected_model == "Gemini":
            optimized = optimize_resume_with_gemini(
                resume, jd, profile, exp, remarks, api_key, model_name
            )
        else:
            optimized = optimize_resume_with_chatgpt(
                resume, jd, profile, exp, remarks, api_key, model_name
            )
        
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
        root.after(0, lambda: [log_msg("⏳ Building PDF in background..."), update_editor()])

        # -------- GENERATE PDF IN BACKGROUND -------- #
        def build_pdf_task():
            try:
                generate_pdf(tex_path)
                pdf_path = tex_path.replace(".tex", ".pdf")
                pdf_text = extract_text_from_pdf(pdf_path)
                
                if pdf_text and jd and jd != "Enter Job Description here...":
                    score = calculate_ats_score(jd, pdf_text)
                    root.after(0, lambda s=score: log_msg(f"✅ Build Complete! Final ATS Score: {s}%"))
                else:
                    root.after(0, lambda: log_msg(f"🎉 Saved: {filename}.pdf"))
                
                root.after(0, lambda: update_pdf_preview(pdf_path))
            except Exception as e:
                root.after(0, lambda err=str(e): log_msg(f"❌ PDF Error: {err}"))
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
paned_window = tk.PanedWindow(root, orient="horizontal", sashwidth=8, bg="#555555", borderwidth=0, sashrelief="raised")
paned_window.pack(fill="both", expand=True, padx=10, pady=10)

left_pane = ctk.CTkFrame(paned_window, width=500)
paned_window.add(left_pane, minsize=450)

right_pane = ctk.CTkFrame(paned_window)
paned_window.add(right_pane, minsize=450)

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

edit_template_btn = ctk.CTkButton(
    btn_frame,
    text="📝 Edit Base Template",
    font=("Arial", 14, "bold"),
    fg_color="#8E44AD",
    hover_color="#732D91",
    height=40,
    command=edit_template_popup
)
edit_template_btn.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew", padx=5)

# Result Console
result_console = ctk.CTkTextbox(left_pane, height=120, font=("Courier", 14), state="disabled")
result_console.pack(padx=20, pady=10, fill="both", expand=True)

# ================= RIGHT PANE ================= #
current_tex_path = None
current_pdf_zoom = 900

def zoom_in():
    global current_pdf_zoom
    current_pdf_zoom += 100
    if current_tex_path:
        update_pdf_preview(current_tex_path.replace(".tex", ".pdf"))

def zoom_out():
    global current_pdf_zoom
    current_pdf_zoom = max(400, current_pdf_zoom - 100)
    if current_tex_path:
        update_pdf_preview(current_tex_path.replace(".tex", ".pdf"))

preview_label = ctk.CTkLabel(right_pane, text="📄 Resume Studio", font=("Arial", 20, "bold"))
preview_label.pack(pady=10)

tabview = ctk.CTkTabview(right_pane)
tabview.pack(fill="both", expand=True, padx=10, pady=5)

tabview.add("LaTeX Source")
tabview.add("PDF Preview")

editor = ctk.CTkTextbox(tabview.tab("LaTeX Source"), font=("Courier", 12))
editor.pack(fill="both", expand=True, padx=5, pady=5)

zoom_frame = ctk.CTkFrame(tabview.tab("PDF Preview"), fg_color="transparent")
zoom_frame.pack(fill="x", pady=(0, 5))

zoom_out_btn = ctk.CTkButton(zoom_frame, text="➖ Zoom Out", width=80, command=zoom_out)
zoom_out_btn.pack(side="left", padx=5)

zoom_in_btn = ctk.CTkButton(zoom_frame, text="➕ Zoom In", width=80, command=zoom_in)
zoom_in_btn.pack(side="left", padx=5)

pdf_frame = ctk.CTkFrame(tabview.tab("PDF Preview"))
pdf_frame.pack(fill="both", expand=True, padx=5, pady=5)

canvas = tk.Canvas(pdf_frame, bg="#2b2b2b", highlightthickness=0)
vbar = ctk.CTkScrollbar(pdf_frame, orientation="vertical", command=canvas.yview)
hbar = ctk.CTkScrollbar(pdf_frame, orientation="horizontal", command=canvas.xview)
canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)

vbar.pack(side="right", fill="y")
hbar.pack(side="bottom", fill="x")
canvas.pack(side="left", fill="both", expand=True)

pdf_image_label = tk.Label(canvas, bg="#2b2b2b", fg="white", text="No PDF generated yet.")
canvas.create_window((0, 0), window=pdf_image_label, anchor="nw")

def update_pdf_preview(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=200) # Increased DPI for sharpness
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Make the image scale dynamically with the zoom level
        basewidth = current_pdf_zoom
        if img.size[0] > 0:
            wpercent = (basewidth / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((basewidth, hsize), Image.Resampling.LANCZOS)
            
        photo = ImageTk.PhotoImage(img)
        pdf_image_label.configure(image=photo, text="")
        pdf_image_label.image = photo
        
        canvas.configure(scrollregion=(0, 0, basewidth, hsize))
        doc.close()
    except Exception as e:
        log_msg(f"❌ PDF Render Error: {str(e)}")

def locate_in_system():
    if current_tex_path:
        pdf_path = os.path.abspath(current_tex_path.replace(".tex", ".pdf"))
        if os.path.exists(pdf_path):
            if sys.platform == "win32":
                subprocess.run(['explorer', '/select,', os.path.normpath(pdf_path)])
            elif sys.platform == "darwin":
                subprocess.run(['open', '-R', pdf_path])
            else:
                subprocess.run(['xdg-open', os.path.dirname(pdf_path)])
        else:
            log_msg("⚠️ PDF not found yet.")

def open_in_system_viewer():
    if current_tex_path:
        pdf_path = current_tex_path.replace(".tex", ".pdf")
        if os.path.exists(pdf_path):
            if sys.platform == "win32":
                os.startfile(pdf_path)
            elif sys.platform == "darwin":
                os.system(f"open '{pdf_path}'")
            else:
                os.system(f"xdg-open '{pdf_path}'")
        else:
            log_msg("⚠️ PDF not found yet.")

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
            
            root.after(0, lambda: update_pdf_preview(pdf_path))
            
            if pdf_text and jd and jd != "Enter Job Description here...":
                score = calculate_ats_score(jd, pdf_text)
                log_msg(f"✅ Rebuilt! New ATS Score: {score}%")
            else:
                log_msg(f"🎉 Rebuilt successfully!")
                
        except Exception as e:
            log_msg(f"❌ Rebuild Error: {str(e)}")
            
    threading.Thread(target=task, daemon=True).start()

action_btn_frame = ctk.CTkFrame(right_pane)
action_btn_frame.pack(pady=10)

rebuild_btn = ctk.CTkButton(
    action_btn_frame, 
    text="⚙️ Save & Rebuild PDF", 
    fg_color="#008CBA",
    hover_color="#007399",
    font=("Arial", 16, "bold"),
    height=40,
    command=rebuild_edited_pdf
)
rebuild_btn.grid(row=0, column=0, padx=10)

open_btn = ctk.CTkButton(
    action_btn_frame, 
    text="🔗 Open External PDF", 
    fg_color="#555555",
    hover_color="#444444",
    font=("Arial", 16, "bold"),
    height=40,
    command=open_in_system_viewer
)
open_btn.grid(row=0, column=1, padx=10)

locate_btn = ctk.CTkButton(
    action_btn_frame, 
    text="📁 Locate File", 
    fg_color="#555555",
    hover_color="#444444",
    font=("Arial", 16, "bold"),
    height=40,
    command=locate_in_system
)
locate_btn.grid(row=0, column=2, padx=10)

# Initialize API button state
update_api_button()

# Run App
root.mainloop()