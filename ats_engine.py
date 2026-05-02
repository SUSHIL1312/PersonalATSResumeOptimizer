import re

def extract_words(text):
    return set(re.findall(r'\b\w+\b', text.lower()))

def calculate_ats_score(jd, resume):
    jd_words = extract_words(jd)
    res_words = extract_words(resume)

    keyword_score = len(jd_words & res_words) / max(len(jd_words), 1)

    section_score = 0
    for sec in ["experience", "skills", "projects"]:
        if sec in resume.lower():
            section_score += 1

    section_score /= 3

    score = (0.7 * keyword_score + 0.3 * section_score) * 100
    return round(score, 2)