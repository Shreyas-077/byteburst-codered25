import openai
import datetime
from typing import Dict, List, Optional
import json
import os

class CareerCoach:
    def __init__(self, api_key: str):
        """Initialize the career coach with OpenAI API key."""
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self.api_key = api_key
        openai.api_key = self.api_key
        
    def generate_daily_motivation(self, user_profile: Dict) -> Dict:
        """Generate personalized daily motivation message."""
        try:
            prompt = f"""
            Create a motivational message for a {user_profile['job_role']} professional.
            Consider their goals: {user_profile['goals']}
            Recent achievements: {user_profile['achievements']}
            Areas of improvement: {user_profile['improvement_areas']}
            
            Return the response in this JSON format:
            {{
                "message": "The motivational message",
                "focus_area": "Today's focus area",
                "quick_tip": "A practical tip for today",
                "quote": "An inspiring quote",
                "action_item": "One specific action to take today"
            }}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You are an experienced career coach who provides personalized, actionable advice."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error generating motivation: {str(e)}")
            return None
    
    def generate_weekly_challenge(self, user_profile: Dict) -> Dict:
        """Generate personalized weekly skill challenge."""
        try:
            prompt = f"""
            Create a weekly skill challenge for a {user_profile['job_role']} professional.
            Current skill level: {user_profile['skill_level']}
            Available time: {user_profile['available_time']} hours per week
            Goals: {user_profile['goals']}
            Current skills: {user_profile['skills']}
            
            Return the response in this JSON format:
            {{
                "challenge_name": "Name of the challenge",
                "description": "Description of the challenge",
                "daily_tasks": [
                    {{
                        "day": "Day of the week",
                        "task": "Task description",
                        "time_required": "Estimated time",
                        "resources": "Helpful resources"
                    }}
                ],
                "success_criteria": "How to measure success",
                "bonus_challenge": "Additional optional challenge",
                "expected_outcome": "What to expect after completion"
            }}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You are an experienced career coach who creates engaging learning challenges."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error generating weekly challenge: {str(e)}")
            return None
    
    def generate_monthly_review(self, user_profile: Dict, monthly_data: Dict) -> Dict:
        """Generate monthly progress review."""
        try:
            prompt = f"""
            Create a monthly progress review for a {user_profile['job_role']} professional.
            
            Monthly Data:
            Completed challenges: {monthly_data['completed_challenges']}
            Achievements: {monthly_data['achievements']}
            Skills improved: {monthly_data['skills_improved']}
            Time invested: {monthly_data['time_invested']} hours
            
            Return the response in this JSON format:
            {{
                "summary": "Overall progress summary",
                "key_achievements": ["List of key achievements"],
                "areas_of_growth": [
                    {{
                        "skill": "Skill name",
                        "progress": "Progress made",
                        "next_steps": "Recommended next steps"
                    }}
                ],
                "insights": ["List of insights"],
                "next_month_focus": {{
                    "primary_goal": "Main goal for next month",
                    "action_items": ["List of action items"]
                }}
            }}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You are an experienced career coach who provides insightful progress reviews."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error generating monthly review: {str(e)}")
            return None
    
    def generate_action_plan(self, user_profile: Dict, goals: List[str]) -> Dict:
        """Generate personalized action plan."""
        try:
            prompt = f"""
            Create an action plan for a {user_profile['job_role']} professional.
            Goals: {goals}
            Current skills: {user_profile['skills']}
            Available time: {user_profile['available_time']} hours per week
            
            Return the response in this JSON format:
            {{
                "plan_name": "Name of the action plan",
                "overview": "Plan overview",
                "milestones": [
                    {{
                        "name": "Milestone name",
                        "timeframe": "Expected duration",
                        "tasks": [
                            {{
                                "task": "Task description",
                                "priority": "High/Medium/Low",
                                "resources": "Helpful resources",
                                "success_criteria": "How to measure completion"
                            }}
                        ]
                    }}
                ],
                "success_metrics": ["List of success metrics"],
                "potential_challenges": [
                    {{
                        "challenge": "Potential challenge",
                        "solution": "Proposed solution"
                    }}
                ]
            }}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You are an experienced career coach who creates detailed action plans."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error generating action plan: {str(e)}")
            return None
    
    def generate_progress_feedback(self, user_profile: Dict, progress_data: Dict) -> Dict:
        """Generate progress feedback."""
        try:
            prompt = f"""
            Provide progress feedback for a {user_profile['job_role']} professional.
            
            Progress Data:
            Recent progress: {progress_data['recent_progress']}
            Completed tasks: {progress_data['completed_tasks']}
            Challenges faced: {progress_data['challenges']}
            Time spent: {progress_data['time_spent']} hours
            
            Return the response in this JSON format:
            {{
                "overall_assessment": "Overall progress assessment",
                "key_observations": [
                    {{
                        "observation": "Key observation",
                        "impact": "Impact on progress",
                        "recommendation": "Recommendation"
                    }}
                ],
                "strengths": [
                    {{
                        "strength": "Identified strength",
                        "how_to_leverage": "How to leverage this strength"
                    }}
                ],
                "improvement_areas": [
                    {{
                        "area": "Area for improvement",
                        "why_important": "Why this matters",
                        "how_to_improve": "How to improve"
                    }}
                ],
                "next_steps": ["List of next steps"],
                "motivation": "Motivational message"
            }}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You are an experienced career coach who provides constructive feedback."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error generating progress feedback: {str(e)}")
            return None
