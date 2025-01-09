import openai
import os
from typing import Optional

class GrowthMapGenerator:
    def __init__(self, api_key: str):
        """Initialize the growth map generator with OpenAI API key."""
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self.api_key = api_key
        openai.api_key = self.api_key

    def generate_map(self, resume_text: str) -> str:
        """
        Generate a career growth map based on resume text.
        """
        try:
            prompt = f"""
            Create a detailed career growth map based on this resume:

            {resume_text}

            The map should include:
            1. Current position and skills
            2. Short-term growth opportunities (1-2 years)
            3. Mid-term career paths (3-5 years)
            4. Long-term career goals (5+ years)
            5. Required skills and certifications for each stage
            6. Potential roles and responsibilities

            Format the response as a clear, structured markdown document with sections and bullet points.
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You are a career path mapping expert who creates detailed, actionable growth plans."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error generating growth map: {str(e)}"
