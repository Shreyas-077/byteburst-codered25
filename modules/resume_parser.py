import pdfplumber
import re

def extract_text_from_pdf(file_path):
    """
    Extracts and processes relevant details from a PDF resume.
    :param file_path: Path to the PDF file.
    :return: Dictionary with extracted details.
    """
    with pdfplumber.open(file_path) as pdf:
        full_text = " ".join(page.extract_text() for page in pdf.pages if page.extract_text())

    # Extract specific details
    details = {
        "Name": extract_name(full_text),
        "Email": extract_email(full_text),
        "Phone": extract_phone(full_text),
        "Year of Passing (YOP)": extract_yop(full_text),
        "Skills": extract_skills(full_text),
        "Experience": extract_experience(full_text),
        "Certifications": extract_certifications(full_text)
    }

    return details

def extract_name(text):
    """
    Extracts name from the resume text (assuming the first line contains the name).
    :param text: Full resume text.
    :return: Name as a string.
    """
    lines = text.split("\n")
    return lines[0].strip() if lines else "Not Found"

def extract_email(text):
    """
    Extracts email address from the resume text.
    :param text: Full resume text.
    :return: Email as a string.
    """
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    match = re.search(email_pattern, text)
    return match.group(0) if match else "Not Found"

def extract_phone(text):
    """
    Extracts phone number from the resume text.
    :param text: Full resume text.
    :return: Phone number as a string.
    """
    phone_pattern = r"\b\d{10}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"
    match = re.search(phone_pattern, text)
    return match.group(0) if match else "Not Found"

def extract_yop(text):
    """
    Extracts the year of passing (YOP) from the resume text.
    :param text: Full resume text.
    :return: Year of Passing as a string.
    """
    yop_pattern = r"\b(19|20)\d{2}\b"
    matches = re.findall(yop_pattern, text)
    return ", ".join(set(matches)) if matches else "Not Found"

def extract_skills(text):
    """
    Extracts skills from the resume text based on a predefined list.
    :param text: Full resume text.
    :return: List of skills found.
    """
    predefined_skills = ["Python", "Machine Learning", "Data Analysis", "AI", "NLP", "Leadership", "Cloud Computing", "Big Data", "Java", "SQL"]
    skills_found = [skill for skill in predefined_skills if skill.lower() in text.lower()]
    return skills_found if skills_found else ["Not Found"]

def extract_experience(text):
    """
    Extracts work experience from the resume text.
    :param text: Full resume text.
    :return: List of experiences (years of experience or job descriptions).
    """
    experience_pattern = r"\b(\d+)\s+(years?|months?)\b"
    experience = re.findall(experience_pattern, text)
    return ", ".join([f"{exp[0]} {exp[1]}" for exp in experience]) if experience else "Not Found"

def extract_certifications(text):
    """
    Extracts certifications from the resume text.
    :param text: Full resume text.
    :return: List of certifications.
    """
    certifications = ["AWS Certified", "Google Cloud Certified", "PMP", "Scrum Master", "Machine Learning Specialization"]
    cert_found = [cert for cert in certifications if cert.lower() in text.lower()]
    return cert_found if cert_found else ["Not Found"]
