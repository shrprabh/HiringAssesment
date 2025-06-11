from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class WorkExperience(BaseModel):
    company: str
    roleName: str

class Degree(BaseModel):
    degree: str
    subject: str
    school: str
    gpa: str
    startDate: str
    endDate: str
    originalSchool: str
    isTop50: bool
    isTop25: Optional[bool] = None

class Education(BaseModel):
    highest_level: str
    degrees: List[Degree]

class SalaryExpectation(BaseModel):
    full_time: Optional[str] = None

class Candidate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = ""
    location: str
    submitted_at: datetime
    work_availability: List[str]
    annual_salary_expectation: Dict[str, str]
    work_experiences: List[WorkExperience]
    education: Education
    skills: List[str]

class CandidateScore(BaseModel):
    candidate: Candidate
    skills_score: float
    experience_score: float
    education_score: float
    total_score: float
    matching_skills: List[str]
    missing_skills: List[str]
    
    class Config:
        from_attributes = True 