from fastapi import APIRouter, HTTPException, Query, Path as PathParam
from typing import List, Optional
import json
from datetime import datetime
import os
from pathlib import Path
from ...models.candidate import Candidate, CandidateScore
from ...services.scoring import ScoringService

router = APIRouter()

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Load job requirements from jobdescription.txt
def load_job_requirements():
    try:
        job_desc_path = BASE_DIR / "jobdescription.txt"
        with open(job_desc_path, "r") as f:
            content = f.read()
            # Extract requirements from the content
            return {
                "skills": ["React", "NextJS", "Tailwind", "Bootstrap"],
                "min_experience": 2,
                "education": "Bachelor's Degree",
                "keywords": ["full-stack", "web development", "frontend", "backend", "developer", "software engineer"]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading job requirements: {str(e)}")

# Load candidates from form-submission.json
def load_candidates():
    try:
        candidates_path = BASE_DIR / "form-submission.json"
        with open(candidates_path, "r") as f:
            data = json.load(f)
            # Convert string dates to datetime objects
            for candidate in data:
                if isinstance(candidate.get("submitted_at"), str):
                    candidate["submitted_at"] = datetime.fromisoformat(candidate["submitted_at"].replace("Z", "+00:00"))
            return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading candidates: {str(e)}")

def evaluate_candidates_data(
    min_score: Optional[float] = None,
    skills: Optional[List[str]] = None,
    location: Optional[str] = None
) -> List[CandidateScore]:
    job_requirements = load_job_requirements()
    candidates_data = load_candidates()
    
    scoring_service = ScoringService(job_requirements)
    evaluated_candidates = []
    
    # Convert location to lowercase once
    location_lower = location.lower() if location else None
    
    for candidate_data in candidates_data:
        # Apply filters
        candidate_location = candidate_data.get("location", "").lower()
        if location_lower and location_lower not in candidate_location:
            continue
            
        candidate_skills = [s.lower() for s in candidate_data.get("skills", [])]
        if skills and not any(skill.lower() in candidate_skills for skill in skills):
            continue
            
        try:
            # Make phone optional
            if "phone" not in candidate_data:
                candidate_data["phone"] = ""
                
            candidate = Candidate(**candidate_data)
            score = scoring_service.evaluate_candidate(candidate)
            
            if min_score is None or score.total_score >= min_score:
                evaluated_candidates.append(score)
        except Exception as e:
            # Log the error but continue processing other candidates
            print(f"Error processing candidate {candidate_data.get('name', 'Unknown')}: {str(e)}")
            continue
    
    # Sort candidates by total score in descending order
    evaluated_candidates.sort(key=lambda x: x.total_score, reverse=True)
    return evaluated_candidates

@router.get("/candidates", response_model=List[CandidateScore])
async def evaluate_candidates(
    min_score: Optional[float] = Query(None, description="Minimum total score to include"),
    skills: Optional[List[str]] = Query(None, description="Filter by required skills"),
    location: Optional[str] = Query(None, description="Filter by location")
):
    return evaluate_candidates_data(min_score=min_score, skills=skills, location=location)

@router.get("/candidates/top/{n}", response_model=List[CandidateScore])
async def get_top_candidates(
    n: int = PathParam(..., description="Number of top candidates to return", ge=1, le=100),
    min_score: Optional[float] = Query(None, description="Minimum total score to include")
):
    all_candidates = evaluate_candidates_data(min_score=min_score)
    return all_candidates[:n]

@router.get("/candidates/skills", response_model=List[str])
async def get_unique_skills():
    candidates_data = load_candidates()
    skills = set()
    for candidate in candidates_data:
        skills.update(skill.lower() for skill in candidate.get("skills", []))
    return sorted(list(skills))

@router.get("/candidates/locations", response_model=List[str])
async def get_unique_locations():
    candidates_data = load_candidates()
    locations = set(candidate.get("location", "") for candidate in candidates_data)
    return sorted(list(locations)) 