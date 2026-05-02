import google.generativeai as genai


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
- DO NOT add new skills
- DO NOT modify core technical skills
- DO NOT add new technologies
- DO NOT reorder projects or experience
- DO NOT fabricate metrics
- Keep resume in 1 Page and two row should not overlap after compiling in pdf take care of this.

ALLOWED:
- Improve wording
- Improve impact
- Remove redundancy
- Add realistic minor metrics if obvious

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
- You CAN modify Skills section heavily to match JD
- You CAN add relevant soft skills and business keywords
- You CAN align profile summary strongly with JD
- You CAN improve wording across resume
- Keep resume in 1 Page and two row should not overlap after compiling in pdf take care of this.

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


# ---------------- MAIN FUNCTION ---------------- #
def optimize_resume_with_gemini(resume, jd, profile, exp, remarks, api_key):
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-flash-latest")

    prompt = build_prompt(resume, jd, profile, exp, remarks)

    response = model.generate_content(prompt)

    return clean_latex(response.text)