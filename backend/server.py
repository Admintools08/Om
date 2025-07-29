from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime
import requests
import json
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Gemini API configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class GenerateRequest(BaseModel):
    employeeName: str
    learning: str
    difficulty: str

class GenerateResponse(BaseModel):
    badgeUrl: str
    linkedinPost: str

# Badge generation function
def generate_badge_svg(employee_name: str, badge_text: str) -> str:
    """Generate SVG badge with Branding Pioneers branding"""
    svg_content = f"""
    <svg width="400" height="400" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="badgeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#FF416C;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#FF4B2B;stop-opacity:1" />
            </linearGradient>
            <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="rgba(0,0,0,0.2)"/>
            </filter>
        </defs>
        
        <!-- Background circle -->
        <circle cx="200" cy="200" r="180" fill="url(#badgeGradient)" filter="url(#shadow)"/>
        
        <!-- Inner circle -->
        <circle cx="200" cy="200" r="150" fill="rgba(255,255,255,0.1)" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
        
        <!-- Logo placeholder (we'll use text for now) -->
        <text x="200" y="120" font-family="Inter, sans-serif" font-size="24" font-weight="bold" fill="white" text-anchor="middle">
            BRANDING
        </text>
        <text x="200" y="145" font-family="Inter, sans-serif" font-size="24" font-weight="bold" fill="white" text-anchor="middle">
            PIONEERS
        </text>
        
        <!-- Badge text -->
        <text x="200" y="180" font-family="Inter, sans-serif" font-size="14" fill="white" text-anchor="middle">
            {badge_text}
        </text>
        
        <!-- Employee name -->
        <text x="200" y="220" font-family="Inter, sans-serif" font-size="18" font-weight="600" fill="white" text-anchor="middle">
            {employee_name}
        </text>
        
        <!-- Achievement text -->
        <text x="200" y="260" font-family="Inter, sans-serif" font-size="12" fill="rgba(255,255,255,0.9)" text-anchor="middle">
            Learning Champion
        </text>
        
        <!-- Decorative elements -->
        <circle cx="200" cy="300" r="3" fill="white" opacity="0.8"/>
        <circle cx="180" cy="300" r="2" fill="white" opacity="0.6"/>
        <circle cx="220" cy="300" r="2" fill="white" opacity="0.6"/>
    </svg>
    """
    return svg_content

@api_router.post("/generate", response_model=GenerateResponse)
async def generate_badge_and_post(request: GenerateRequest):
    try:
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
        # Prepare the prompt for Gemini API
        prompt = f"""You are an expert AI copywriter and branding strategist. You will receive three inputs: {request.employeeName}, {request.learning}, and {request.difficulty}.

### Task:
Generate TWO outputs clearly separated:

1. **Badge Description**: A short, creative, and celebratory text that can be used to design a digital badge image. It should include the employee's name, what they learned, and the difficulty level. Keep it under 15 words. Tone: motivational and professional.

2. **LinkedIn Post**: A fully optimized LinkedIn post (150-200 words) that:
   - Highlights the employee's achievement naturally.
   - Mentions what they learned in a proud, growth-oriented way.
   - Subtly mentions Branding Pioneers as a culture of continuous learning.
   - Uses an engaging tone, with small storytelling elements.
   - Includes a soft call-to-action (e.g., 'connect', 'let's share learnings', or 'celebrate together').
   - Uses 3-4 relevant hashtags at the end (#LearningJourney #BrandingPioneers #GrowthMindset etc.).

### Format Your Output Exactly As:
BADGE: <badge text here>
LINKEDIN_POST: <linkedin post text here>

### Inputs:
Employee Name: {request.employeeName}
Learning: {request.learning}
Difficulty: {request.difficulty}"""

        # Prepare request payload for Gemini API
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Make request to Gemini API
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Gemini API error: {response.text}")
        
        response_data = response.json()
        
        # Extract the generated text
        if not response_data.get('candidates') or not response_data['candidates'][0].get('content'):
            raise HTTPException(status_code=500, detail="Invalid response from Gemini API")
        
        generated_text = response_data['candidates'][0]['content']['parts'][0]['text']
        
        # Parse the response to extract badge text and LinkedIn post
        lines = generated_text.strip().split('\n')
        badge_text = ""
        linkedin_post = ""
        
        for line in lines:
            if line.startswith('BADGE:'):
                badge_text = line.replace('BADGE:', '').strip()
            elif line.startswith('LINKEDIN_POST:'):
                linkedin_post = line.replace('LINKEDIN_POST:', '').strip()
        
        if not badge_text or not linkedin_post:
            # Fallback parsing - try to find the content differently
            if 'BADGE:' in generated_text and 'LINKEDIN_POST:' in generated_text:
                parts = generated_text.split('LINKEDIN_POST:')
                badge_part = parts[0].replace('BADGE:', '').strip()
                linkedin_part = parts[1].strip()
                badge_text = badge_part
                linkedin_post = linkedin_part
            else:
                raise HTTPException(status_code=500, detail="Could not parse Gemini response")
        
        # Generate the badge SVG
        badge_svg = generate_badge_svg(request.employeeName, badge_text)
        
        # Convert SVG to base64 data URL
        badge_base64 = base64.b64encode(badge_svg.encode('utf-8')).decode('utf-8')
        badge_url = f"data:image/svg+xml;base64,{badge_base64}"
        
        return GenerateResponse(
            badgeUrl=badge_url,
            linkedinPost=linkedin_post
        )
        
    except Exception as e:
        logger.error(f"Error generating badge and post: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Branding Pioneers Badge Generator API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()