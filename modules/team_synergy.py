import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import random

def generate_team_profile(num_features=5, num_teams=3):
    """
    Generates random team profiles with the same number of features as candidate skills.
    :param num_features: Number of features (skills + personality traits) for each team profile.
    :param num_teams: Number of team profiles to generate.
    :return: List of team profile vectors with consistent dimensions.
    """
    # Each team profile now includes both skills and personality traits (adaptability, leadership, etc.)
    team_profiles = [
        [random.randint(0, 5) for _ in range(num_features)] for _ in range(num_teams)
    ]
    return team_profiles

def extract_candidate_skills(resume_text):
    """
    Extracts relevant skills and traits from the candidate's resume.
    :param resume_text: Text extracted from the resume.
    :return: List of skill and personality trait values (e.g., [2, 1, 3, 4, 5]).
    """
    skills = ["Python", "Data Science", "Management", "Machine Learning", "Leadership"]
    personality_traits = ["adaptability", "communication", "initiative", "teamwork"]

    # Count the skills in the resume
    skill_counts = [resume_text.lower().count(skill.lower()) for skill in skills]

    # Simulating personality traits based on words present in the resume (simplified example)
    trait_counts = [
        resume_text.lower().count(trait.lower()) for trait in personality_traits
    ]

    # Combining skills and personality traits into a single vector
    return skill_counts + trait_counts

def calculate_synergy_score(candidate_skills, team_profiles):
    """
    Compares candidate skills and personality traits with team profiles and calculates the synergy score.
    :param candidate_skills: List of candidate's skills and personality traits.
    :param team_profiles: List of team profiles.
    :return: Synergy score for each team.
    """
    candidate_vector = np.array(candidate_skills).reshape(1, -1)
    team_vectors = np.array(team_profiles)

    # Check dimensions before calculating cosine similarity
    if candidate_vector.shape[1] != team_vectors.shape[1]:
        raise ValueError(
            f"Incompatible dimensions: Candidate vector has {candidate_vector.shape[1]} features, "
            f"but team vectors have {team_vectors.shape[1]} features."
        )

    synergy_scores = cosine_similarity(candidate_vector, team_vectors)
    return synergy_scores[0]  # Return synergy scores for all teams

def team_synergy_analysis(candidate_skills, team_profiles):
    """
    Returns a detailed analysis of how well a candidate fits within a team.
    :param candidate_skills: List of candidate's skills and traits.
    :param team_profiles: List of team profiles.
    :return: Detailed synergy analysis.
    """
    synergy_scores = calculate_synergy_score(candidate_skills, team_profiles)
    analysis = []

    for i, score in enumerate(synergy_scores):
        if score > 0.8:
            analysis.append(f"Team {i+1}: Excellent fit. High synergy score of {score:.2f}.")
        elif score > 0.5:
            analysis.append(f"Team {i+1}: Good fit. Moderate synergy score of {score:.2f}.")
        else:
            analysis.append(f"Team {i+1}: Low synergy score of {score:.2f}. Training or adjustments may be needed.")
    
    return analysis
