
# ---------------- CLEAN LATEX ---------------- #
def clean_latex(text):
    text = text.replace("```latex", "")
    text = text.replace("```", "")
    text = text.replace("LATEX:", "")
    return text.strip()


# ---------------- PROMPT BUILDER ---------------- #
def build_prompt(resume, jd, profile, exp, remarks):
    
    if profile == "IT":
        return f"""
You are an ATS Resume Optimizer for SOFTWARE ENGINEERING roles.

STRICT RULES:
- DO NOT add or invent new hard skills, programming languages, or frameworks.
- DO NOT modify the "Tech Language skills" or "Databases" sections UNLESS explicitly requested in the Remarks.
- DO NOT reorder projects or experience.
- DO NOT fabricate metrics.
- Keep resume in 1 Page and two rows should not overlap after compiling in pdf.

ALLOWED:
- You CAN alter the "Soft Skills" section to align with the JD.
- Improve wording and impact of experience bullet points.
- Remove redundancy.
- Add realistic minor metrics if obvious.

Profile: {profile}
Experience: {exp} years

Job Description:
{jd}

Resume:
{resume}

Remarks:
{remarks}

IMPORTANT:
- Preserve LaTeX structure
- DO NOT break itemize environments

Return ONLY LaTeX.
"""

    else:  # MBA / Non-tech
        return f"""
You are an ATS Resume Optimizer for BUSINESS / MBA roles.

GOAL:
Maximize ATS score and shortlist chances.

RULES:
- You CAN modify the Skills section heavily to match JD.
- MBA profiles don't need strict tech language constraints. You CAN add relevant business tools, CRM, personality traits, and soft skills required by the JD.
- You CAN align profile summary strongly with JD.
- You CAN improve wording across resume focusing on personality, leadership, and management.
- Keep resume in 1 Page and two rows should not overlap after compiling in pdf.

STRICT LIMITS:
- DO NOT fabricate experience
- DO NOT change project meaning
- DO NOT add tools/skills that require deep expertise unless already implied
- DO NOT reorder projects or experience

FOCUS:
- Skills alignment with JD
- Business impact
- Communication, leadership, stakeholder management
- Marketing / Product / Strategy keywords (if relevant)

Profile: {profile}
Experience: {exp} years

Job Description:
{jd}

Resume:
{resume}

Remarks:
{remarks}

IMPORTANT:
- Keep LaTeX valid
- Maintain structure

Return ONLY LaTeX.
"""


# ---------------- MAIN FUNCTION (GEMINI) ---------------- #
def optimize_resume_with_gemini(resume, jd, profile, exp, remarks, api_key, model_name="gemini-1.5-flash"):
    import google.generativeai as genai
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(model_name)

    prompt = build_prompt(resume, jd, profile, exp, remarks)

    response = model.generate_content(prompt)

    return clean_latex(response.text)

# ---------------- MAIN FUNCTION (CHATGPT) ---------------- #
def optimize_resume_with_chatgpt(resume, jd, profile, exp, remarks, api_key, model_name="gpt-4o-mini"):
    import openai
    
    client = openai.OpenAI(api_key=api_key)
    prompt = build_prompt(resume, jd, profile, exp, remarks)
    
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are an expert ATS Resume Optimizer. Only return raw LaTeX code. Do not include markdown blocks or any other conversational text."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    return clean_latex(response.choices[0].message.content)