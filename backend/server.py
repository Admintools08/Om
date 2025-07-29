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
def generate_badge_svg(employee_name: str, badge_text: str, difficulty: str) -> str:
    """Generate SVG badge with Branding Pioneers branding - different designs for each difficulty"""
    
    # Define color schemes for each difficulty
    difficulty_colors = {
        "Easy": {
            "primary": "#00FF88",
            "secondary": "#00CC66", 
            "accent": "#1C1C1C",
            "glow": "#00FFAA",
            "wing": "#90EE90"
        },
        "Moderate": {
            "primary": "#FFAA00",
            "secondary": "#FF8800",
            "accent": "#222222", 
            "glow": "#FFDD55",
            "wing": "#FFD700"
        },
        "Hard": {
            "primary": "#FF3366",
            "secondary": "#FF1144",
            "accent": "#2A2A2A",
            "glow": "#FF6688", 
            "wing": "#FF69B4"
        }
    }
    
    colors = difficulty_colors.get(difficulty, difficulty_colors["Easy"])
    
    # Difficulty symbols
    difficulty_symbols = {
        "Easy": "★",
        "Moderate": "★★", 
        "Hard": "★★★"
    }
    
    symbol = difficulty_symbols.get(difficulty, "★")
    
    svg_content = f"""
    <svg width="400" height="400" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <!-- Dark atmospheric background gradient -->
            <radialGradient id="backgroundGradient" cx="50%" cy="30%" r="80%">
                <stop offset="0%" style="stop-color:#2a2a2a;stop-opacity:1" />
                <stop offset="70%" style="stop-color:#1a1a1a;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#0f0f0f;stop-opacity:1" />
            </radialGradient>
            
            <!-- Hexagon gradient for difficulty -->
            <linearGradient id="hexGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{colors['primary']};stop-opacity:1" />
                <stop offset="100%" style="stop-color:{colors['secondary']};stop-opacity:1" />
            </linearGradient>
            
            <!-- Metallic wing gradient -->
            <linearGradient id="wingGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{colors['wing']};stop-opacity:0.8" />
                <stop offset="50%" style="stop-color:#c0c0c0;stop-opacity:0.6" />
                <stop offset="100%" style="stop-color:#a0a0a0;stop-opacity:0.4" />
            </linearGradient>
            
            <!-- Inner hexagon gradient -->
            <linearGradient id="innerHexGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{colors['accent']};stop-opacity:1" />
                <stop offset="100%" style="stop-color:#1a1a1a;stop-opacity:1" />
            </linearGradient>
            
            <!-- Glow filter -->
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                <feMerge> 
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
            
            <!-- Shadow filter -->
            <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                <feDropShadow dx="0" dy="8" stdDeviation="8" flood-color="rgba(0,0,0,0.4)"/>
            </filter>
            
            <!-- Difficulty glow -->
            <filter id="difficultyGlow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                <feFlood flood-color="{colors['glow']}" result="glowColor"/>
                <feComposite in="glowColor" in2="coloredBlur" operator="in" result="softGlow"/>
                <feMerge> 
                    <feMergeNode in="softGlow"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        
        <!-- Dark atmospheric background -->
        <rect width="400" height="400" fill="url(#backgroundGradient)"/>
        
        <!-- Atmospheric mist effect -->
        <circle cx="100" cy="100" r="80" fill="rgba(255,255,255,0.03)"/>
        <circle cx="300" cy="150" r="60" fill="rgba(255,255,255,0.02)"/>
        <circle cx="150" cy="320" r="70" fill="rgba(255,255,255,0.03)"/>
        
        <!-- Left wing -->
        <path d="M 120 200 L 90 180 L 85 190 L 90 200 L 85 210 L 90 220 L 120 200 Z" fill="url(#wingGradient)" filter="url(#shadow)"/>
        <path d="M 140 190 L 110 170 L 105 180 L 110 190 L 105 200 L 110 210 L 140 190 Z" fill="url(#wingGradient)" filter="url(#shadow)"/>
        <path d="M 140 210 L 110 230 L 105 220 L 110 210 L 105 200 L 110 190 L 140 210 Z" fill="url(#wingGradient)" filter="url(#shadow)"/>
        
        <!-- Right wing -->
        <path d="M 280 200 L 310 180 L 315 190 L 310 200 L 315 210 L 310 220 L 280 200 Z" fill="url(#wingGradient)" filter="url(#shadow)"/>
        <path d="M 260 190 L 290 170 L 295 180 L 290 190 L 295 200 L 290 210 L 260 190 Z" fill="url(#wingGradient)" filter="url(#shadow)"/>
        <path d="M 260 210 L 290 230 L 295 220 L 290 210 L 295 200 L 290 190 L 260 210 Z" fill="url(#wingGradient)" filter="url(#shadow)"/>
        
        <!-- Main hexagonal badge -->
        <path d="M 200 120 L 250 150 L 250 210 L 200 240 L 150 210 L 150 150 Z" fill="url(#hexGradient)" filter="url(#shadow)"/>
        
        <!-- Inner hexagon -->
        <path d="M 200 140 L 230 160 L 230 200 L 200 220 L 170 200 L 170 160 Z" fill="url(#innerHexGradient)" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
        
        <!-- Difficulty stars -->
        <text x="200" y="190" font-family="Arial, sans-serif" font-size="32" font-weight="bold" fill="white" text-anchor="middle" filter="url(#difficultyGlow)">
            {symbol}
        </text>
        
        <!-- Branding Pioneers logo at top -->
        <text x="200" y="50" font-family="Inter, sans-serif" font-size="16" font-weight="bold" fill="white" text-anchor="middle">
            BRANDING PIONEERS
        </text>
        
        <!-- Employee name -->
        <text x="200" y="280" font-family="Inter, sans-serif" font-size="24" font-weight="bold" fill="white" text-anchor="middle">
            {employee_name}
        </text>
        
        <!-- Achievement subtitle with difficulty -->
        <text x="200" y="305" font-family="Inter, sans-serif" font-size="14" fill="rgba(255,255,255,0.9)" text-anchor="middle">
            Learning Champion - {difficulty} Achievement
        </text>
        
        <!-- Difficulty indicator at bottom -->
        <rect x="160" y="340" width="80" height="20" rx="10" fill="url(#hexGradient)" opacity="0.8"/>
        <text x="200" y="354" font-family="Inter, sans-serif" font-size="12" font-weight="bold" fill="white" text-anchor="middle">
            {difficulty.upper()}
        </text>
        
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

1. **Badge Description**: A short, creative, and celebratory text that can be used to design a digital badge image. It should include what they learned and be motivational. Keep it under 10 words. Tone: motivational and professional.

2. **LinkedIn Post**: A fully optimized LinkedIn post (200-300 words) that follows this EXACT format and structure:

🎉 Super proud to share that I've just unlocked Level 1 in [Learning Topic] by Branding Pioneers! 🔥

This isn't just learning, it's a transformative journey that's preparing professionals like me to master {request.learning} and apply it in real-world scenarios.

I've made a commitment to:
Learn in Public and document everything I'm discovering not just for myself, but to inspire others to start their learning journey too. 🌱

Here are my key takeaways from this {request.difficulty.lower()} level challenge:
🧠 [Key insight 1 related to what they learned]
🔍 [Key insight 2 related to what they learned]  
⚙️ [Key insight 3 related to what they learned]

The learnings from this level have completely transformed my understanding of {request.learning} in real-world applications.

➡️ I'll be sharing updates of my journey and what I achieve in future levels

🧭 Follow my journey and feel free to DM if you are curious, let's grow together.

💬 What's one thing you're curious about when it comes to {request.learning}? Let's chat in the comments.

#LearningInPublic #BrandingPioneers #GrowthMindset #ProfessionalDevelopment

### Important Guidelines:
- Use EXACTLY the structure above with the same emojis and format
- Replace [Learning Topic] with a relevant topic name based on what they learned
- Replace the bracketed sections with specific, relevant content
- Keep the tone enthusiastic and engaging
- Make the key takeaways specific to what they actually learned
- End with the exact hashtags shown

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