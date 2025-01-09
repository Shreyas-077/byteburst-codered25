import openai
import os
from typing import Dict, List, Optional

class CareerGrowthPredictor:
    def __init__(self, api_key: str):
        """Initialize the career growth predictor with OpenAI API key."""
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self.api_key = api_key
        openai.api_key = self.api_key

    def predict_growth(self, resume_text: str) -> str:
        """
        Predict career growth based on resume text.
        """
        try:
            prompt = f"""
            Based on the following resume, predict the career growth trajectory and provide actionable insights:

            Resume:
            {resume_text}

            Please analyze:
            1. Current career stage
            2. Potential growth opportunities
            3. Skills to develop
            4. Timeline for progression
            5. Possible career paths

            Format the response in a clear, structured way with bullet points and sections.
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You are a career growth expert with deep knowledge of industry trends and professional development paths."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error predicting career growth: {str(e)}"

    def get_skill_recommendations(self, resume_text: str) -> List[str]:
        """
        Get skill recommendations based on resume text.
        """
        try:
            prompt = f"""
            Based on the following resume, recommend key skills to develop:

            Resume:
            {resume_text}

            Please provide:
            1. Technical skills to learn
            2. Soft skills to develop
            3. Industry-specific knowledge to acquire
            4. Certifications to pursue

            Return a list of specific, actionable recommendations.
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You are a career development expert who specializes in skill gap analysis and professional growth planning."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )

            # Parse the response into a list of recommendations
            recommendations = response.choices[0].message.content.split('\n')
            return [rec.strip() for rec in recommendations if rec.strip()]

        except Exception as e:
            return [f"Error getting skill recommendations: {str(e)}"]

    def analyze_career_risks(self, resume_text: str) -> Dict:
        """
        Analyze potential career risks and opportunities.
        """
        try:
            prompt = f"""
            Analyze the career risks and opportunities based on this resume:

            Resume:
            {resume_text}

            Please provide:
            1. Potential risks in current career path
            2. Market opportunities to explore
            3. Industry trends affecting this career
            4. Mitigation strategies

            Format the response as a structured analysis.
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You are a career risk analyst with expertise in industry trends and market analysis."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )

            return {
                "analysis": response.choices[0].message.content,
                "risk_level": self._calculate_risk_level(response.choices[0].message.content)
            }

        except Exception as e:
            return {"error": f"Error analyzing career risks: {str(e)}"}

    def _calculate_risk_level(self, analysis: str) -> str:
        """Calculate risk level based on analysis text."""
        risk_keywords = {
            "high": ["risky", "unstable", "declining", "obsolete", "challenging"],
            "medium": ["changing", "evolving", "competitive", "dynamic"],
            "low": ["stable", "growing", "promising", "secure", "established"]
        }

        analysis = analysis.lower()
        scores = {level: sum(1 for word in words if word in analysis)
                 for level, words in risk_keywords.items()}

        return max(scores.items(), key=lambda x: x[1])[0]
