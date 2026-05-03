import re
from collections import Counter

STOP_WORDS = {"and", "the", "to", "of", "in", "for", "with", "on", "a", "an", "is", "as", "at", "by", "this", "that", "it", "from", "or", "your", "you", "we", "our", "are", "be", "will", "can", "have", "has", "had", "do", "does"}

SKILL_SYNONYMS = {
    "cpp": "c++",
    "c plus plus": "c++",
    "js": "javascript",
    "ts": "typescript",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "nlp": "natural language processing",
    "k8s": "kubernetes",
    "aws": "amazon web services",
    "gcp": "google cloud",
    "react.js": "react",
    "reactjs": "react",
    "node.js": "node",
    "nodejs": "node",
    "golang": "go"
}

COMMON_SKILLS = {
    "Languages": [
        "python", "java", "c++", "c#", "javascript", "typescript", "sql", "nosql", "go", "ruby", "php", "rust"
    ],
    "Frameworks & Libraries": [
        "react", "angular", "vue", "node", "express", "django", "flask", "spring"
    ],
    "Cloud & DevOps": [
        "amazon web services", "azure", "google cloud", "docker", "kubernetes", "git", "ci/cd", "linux", "unix"
    ],
    "Data & AI": [
        "machine learning", "artificial intelligence", "natural language processing", "excel", "tableau", "power bi", "powerbi"
    ],
    "Soft Skills & Business": [
        "analytics", "communication", "leadership", "marketing", "sales", "management", "strategy", "agile", "scrum"
    ]
}

# ---------------- CLEAN TEXT ---------------- #
def preprocess(text):
    text = text.lower()
    # Normalize synonyms before standard keyword extraction if needed
    for k, v in SKILL_SYNONYMS.items():
        text = re.sub(r'(?<!\w)' + re.escape(k) + r'(?!\w)', v, text)
        
    words = re.findall(r'[a-z0-9\+#\.]+', text)
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]

# ---------------- KEYWORD MATCH ---------------- #
def keyword_score(jd, resume):
    jd_words = set(preprocess(jd))
    res_words = set(preprocess(resume))

    if not jd_words: return 1.0

    match = jd_words.intersection(res_words)
    return len(match) / max(len(jd_words), 1)

# ---------------- SKILL MATCH ---------------- #
def skill_score(jd, resume):
    jd_skills = extract_skills(jd)
    res_skills = extract_skills(resume)

    if not jd_skills: return 1.0

    match = jd_skills.intersection(res_skills)
    return len(match) / max(len(jd_skills), 1)

def extract_skills(text):
    text_lower = text.lower()
    
    # Normalize synonyms (e.g., 'cpp' -> 'c++')
    for k, v in SKILL_SYNONYMS.items():
        text_lower = re.sub(r'(?<!\w)' + re.escape(k) + r'(?!\w)', v, text_lower)
        
    found_skills = set()
    for category, skills in COMMON_SKILLS.items():
        for skill in skills:
            # Use negative lookbehind/lookahead instead of \b to properly match symbols like + and #
            if re.search(r'(?<!\w)' + re.escape(skill) + r'(?!\w)', text_lower):
                found_skills.add(skill)
            
    return found_skills

# ---------------- EXPERIENCE MATCH ---------------- #
def experience_score(jd, resume):
    jd_years = extract_years(jd)
    res_years = extract_years(resume)

    if jd_years == 0:
        return 1

    return min(res_years / jd_years, 1)

def extract_years(text):
    matches = re.findall(r'(\d+)\+?\s*(?:years|yrs)', text.lower())
    return max([int(m) for m in matches], default=0)

# ---------------- CONTENT QUALITY ---------------- #
def content_score(resume):
    words = preprocess(resume)
    if not words: return 0

    word_freq = Counter(words)
    repetition_penalty = sum([count for count in word_freq.values() if count > 5])
    unique_ratio = len(set(words)) / len(words)

    return max(unique_ratio - (repetition_penalty * 0.001), 0)

# ---------------- STRUCTURE SCORE ---------------- #
def structure_score(resume):
    sections = ["experience", "skills", "projects", "education"]
    score = 0
    for sec in sections:
        if sec in resume.lower():
            score += 1
    return score / len(sections)

# ---------------- FINAL ATS SCORE ---------------- #
def calculate_ats_score(jd, resume):
    k = keyword_score(jd, resume)
    s = skill_score(jd, resume)
    e = experience_score(jd, resume)
    c = content_score(resume)
    st = structure_score(resume)

    final_score = (
        0.30 * k +
        0.25 * s +
        0.20 * e +
        0.15 * c +
        0.10 * st
    ) * 100

    return round(final_score, 2)