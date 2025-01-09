import re

def calculate_pq_with_growth(resume_text, skills_matched, years_of_experience):
    """
    Calculates PQ based on skills, experience, and growth indicators, normalized to 100.
    """
    # Growth indicators
    advanced_skills = ["Python", "Machine Learning", "AI", "Cloud Computing", "Big Data"]
    certifications = ["certified", "certificate", "certification", "AWS", "Google Cloud", "PMP", "Scrum Master", "Azure", "Machine Learning Specialization"]
    projects = ["side project", "volunteer", "freelance", "hackathon", "open source", "mentoring"]

    # Count matches for growth indicators
    learning_speed = len([skill for skill in advanced_skills if skill.lower() in resume_text.lower()])
    adaptability = len([keyword for keyword in ["cloud", "big data", "multi-disciplinary", "collaboration", "flexibility", "cross-functional", "open source", "hackathon", "teamwork"] if keyword.lower() in resume_text.lower()])
    passion_for_improvement = len([project for project in projects if project.lower() in resume_text.lower()])
    years_of_experience = len(re.findall(r"\b\d+\s+(years?|months?)\b|\b(one|two|three|four|five|six|seven|eight|nine|ten)\s+(years?|months?)\b", resume_text, re.IGNORECASE))
    cert_count = len(re.findall(r"(AWS|Google Cloud|certified|certificate|certification|Machine Learning Specialization|PMP|Scrum Master|Azure)", resume_text, re.IGNORECASE))

    # Ensure that years of experience is never zero (set to 1 if not found)
    # if years_of_experience == 0:
    #     years_of_experience = 1  # Assume a minimum of 1 year

    # Raw PQ Score calculation
    pq_score = (skills_matched * 5) + (years_of_experience * 5) + (learning_speed * 4) + (adaptability * 2) + (passion_for_improvement * 3) + (cert_count * 2)


    # Normalize PQ Score to 100
    # max_score = (5 * 5) + (10 * 5) + (5 * 4) + (5 * 2) + (5 * 3) + (5 * 2)  # Adjust based on the max possible for each factor
    normalized_pq_score = (pq_score / 100) * 100  # Normalize to 100

    return {
        "PQ Score": normalized_pq_score,
        "Skills Matched": skills_matched,
        "Certifications": cert_count,
        "Learning Speed": learning_speed,
        "Adaptability": adaptability,
        "Passion for Improvement": passion_for_improvement,
        "Years of Experience": years_of_experience,
    }


def calculate_risk_reward(pq_score, skills_matched, years_of_experience):
    """
    Determines if the candidate is a "safe" candidate or "high-risk, high-reward".
    :param pq_score: The PQ score calculated earlier.
    :param skills_matched: The number of matched skills.
    :param years_of_experience: Years of experience mentioned in the resume.
    :return: A dictionary with risk-reward analysis.
    """
    # Risk-Reward logic based on PQ Score and skills
    if pq_score >= 75 and skills_matched >= 4:
        assessment = "Safe Candidate: Well-matched, but with low growth potential."
        risk_level = "Low"
        reward_level = "Moderate"
        recommendations = [
            "Focus on leadership and mentoring opportunities",
            "Explore advanced certifications",
            "Consider cross-functional projects"
        ]
    elif pq_score < 50 or years_of_experience < 2:
        assessment = f"High-Risk, High-Reward: {100 - pq_score}% match now but has the potential to exceed expectations with training."
        risk_level = "High"
        reward_level = "High"
        recommendations = [
            "Invest in intensive training programs",
            "Pair with experienced mentors",
            "Set clear performance milestones"
        ]
    else:
        assessment = f"Balanced Candidate: {pq_score}% match with a {100 - pq_score}% chance of exceeding expectations within a year."
        risk_level = "Moderate"
        reward_level = "Moderate"
        recommendations = [
            "Focus on skill gap training",
            "Take on challenging projects",
            "Build domain expertise"
        ]

    return {
        "assessment": assessment,
        "risk_level": risk_level,
        "reward_level": reward_level,
        "recommendations": recommendations
    }
