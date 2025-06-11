from typing import List, Dict
from ..models.candidate import Candidate, CandidateScore, WorkExperience

class ScoringService:
    def __init__(self, job_requirements: Dict):
        self.job_requirements = job_requirements
        self.skill_weight = 0.4
        self.experience_weight = 0.3
        self.education_weight = 0.3

    def calculate_skills_match_score(self, candidate_skills: List[str]) -> float:
        if not self.job_requirements["skills"]:
            return 1.0
        
        candidate_skills_set = set(skill.lower() for skill in candidate_skills)
        required_skills_set = set(skill.lower() for skill in self.job_requirements["skills"])
        matching_skills = len(candidate_skills_set.intersection(required_skills_set))
        return matching_skills / len(required_skills_set)

    def calculate_experience_score(self, work_experiences: List[WorkExperience]) -> float:
        if not work_experiences:
            return 0.0
            
        # Count relevant roles (Full Stack Developer, Software Engineer, etc.)
        relevant_roles = ["full stack", "software engineer", "developer", "engineer"]
        relevant_experience = sum(
            1 for exp in work_experiences
            if any(role in exp.roleName.lower() for role in relevant_roles)
        )
        
        # Normalize score based on number of experiences
        return min(relevant_experience / 3, 1.0)  # Cap at 1.0 for 3+ relevant experiences

    def calculate_education_score(self, education: Dict) -> float:
        if not education or not education.get("degrees"):
            return 0.0
            
        score = 0.0
        for degree in education["degrees"]:
            # Check if degree is relevant to tech
            is_tech_degree = any(subject in degree["subject"].lower() 
                               for subject in ["computer", "software", "engineering", "science"])
            
            # Calculate base score
            if is_tech_degree:
                score += 0.4
                
            # Add bonus for top schools
            if degree.get("isTop50"):
                score += 0.3
            if degree.get("isTop25"):
                score += 0.2
                
            # Add bonus for high GPA
            if "3.5" in degree["gpa"]:
                score += 0.1
                
        return min(score, 1.0)  # Cap at 1.0

    def calculate_ats_score(self, candidate: Candidate) -> float:
        # Combine all text fields for keyword matching
        text = " ".join([
            candidate.name,
            candidate.location,
            " ".join(exp.roleName for exp in candidate.work_experiences),
            " ".join(degree["subject"] for degree in candidate.education.degrees),
            " ".join(candidate.skills)
        ]).lower()
        
        if not self.job_requirements["keywords"]:
            return 1.0
            
        matches = sum(1 for keyword in self.job_requirements["keywords"] if keyword.lower() in text)
        return matches / len(self.job_requirements["keywords"])

    def evaluate_candidate(self, candidate: Candidate) -> CandidateScore:
        # Calculate skills score
        matching_skills = [skill for skill in candidate.skills 
                         if skill.lower() in [s.lower() for s in self.job_requirements["skills"]]]
        missing_skills = [skill for skill in self.job_requirements["skills"] 
                         if skill.lower() not in [s.lower() for s in candidate.skills]]
        
        skills_score = len(matching_skills) / len(self.job_requirements["skills"]) * 100

        # Calculate experience score
        experience_score = self.calculate_experience_score(candidate.work_experiences) * 100

        # Calculate education score
        education_score = self.calculate_education_score(candidate.education.dict()) * 100

        # Calculate total score
        total_score = (
            skills_score * self.skill_weight +
            experience_score * self.experience_weight +
            education_score * self.education_weight
        )

        return CandidateScore(
            candidate=candidate,
            skills_score=skills_score,
            experience_score=experience_score,
            education_score=education_score,
            total_score=total_score,
            matching_skills=matching_skills,
            missing_skills=missing_skills
        ) 