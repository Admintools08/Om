from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import requests
import json
import base64
from fastapi import Cookie, Response

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

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: str = "user"  # "user" or "admin"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    total_badges_generated: int = 0

class UserCreate(BaseModel):
    name: str

class UserLogin(BaseModel):
    name: str

class BadgeGeneration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_name: str
    employee_name: str
    learning: str
    difficulty: str
    badge_text: str
    linkedin_post: str
    badge_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AdminAction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    admin_id: str
    admin_name: str
    action: str
    details: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class GenerateRequest(BaseModel):
    employeeName: str
    learning: str
    difficulty: str

class GenerateResponse(BaseModel):
    badgeUrl: str
    linkedinPost: str

class AuthResponse(BaseModel):
    user: User
    session_token: str

class EmployeeProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    full_name: str
    position: str
    department: str
    date_of_joining: datetime
    existing_skills: List[str]
    learning_interests: List[str]
    profile_picture: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class EmployeeProfileCreate(BaseModel):
    full_name: str
    position: str
    department: str
    date_of_joining: datetime
    existing_skills: List[str]
    learning_interests: List[str]
    profile_picture: Optional[str] = None

class LearningGoal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: str
    target_completion_date: datetime
    status: str = "active"  # "active", "completed", "paused"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LearningGoalCreate(BaseModel):
    title: str
    description: str
    target_completion_date: datetime

class Milestone(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    goal_id: Optional[str] = None
    what_learned: str
    source: str  # From where learned
    can_teach: bool
    hours_invested: float
    project_certificate_link: Optional[str] = None
    month_year: str  # Format: "2024-01"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MilestoneCreate(BaseModel):
    goal_id: Optional[str] = None
    what_learned: str
    source: str
    can_teach: bool
    hours_invested: float
    project_certificate_link: Optional[str] = None

class Resource(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    url: str
    description: str
    category: str
    tags: List[str]
    added_by_user_id: str
    approved: bool = False
    approved_by_admin_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ResourceCreate(BaseModel):
    title: str
    url: str
    description: str
    category: str
    tags: List[str]

class Bookmark(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    bookmarked_user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AdminStats(BaseModel):
    total_users: int
    total_admins: int
    total_badges_generated: int
    recent_activities: List[dict]
    top_learners: List[dict]
    # Learning platform stats
    total_profiles: int
    total_goals: int
    total_milestones: int
    total_resources: int
    monthly_learning_hours: float
    employees_meeting_target: int
    top_learning_platforms: List[dict]
    skills_by_department: List[dict]

# Authentication endpoints
@api_router.post("/auth/login", response_model=AuthResponse)
async def login_user(user_data: UserLogin, response: Response):
    try:
        # Check if user exists
        existing_user = await db.users.find_one({"name": user_data.name})
        
        if existing_user:
            # Update last active
            await db.users.update_one(
                {"id": existing_user["id"]},
                {"$set": {"last_active": datetime.utcnow()}}
            )
            user = User(**existing_user)
        else:
            # Create new user
            role = "admin" if user_data.name == "Arush T." else "user"
            user = User(name=user_data.name, role=role)
            await db.users.insert_one(user.dict())
        
        # Generate session token (simple approach - in production use JWT)
        session_token = str(uuid.uuid4())
        await db.users.update_one(
            {"id": user.id},
            {"$set": {"session_token": session_token}}
        )
        
        # Set cookie
        response.set_cookie(
            key="session_token", 
            value=session_token, 
            max_age=86400 * 7,  # 7 days
            httponly=True,
            samesite="lax"
        )
        
        # Log admin action if admin
        if user.role == "admin":
            admin_action = AdminAction(
                admin_id=user.id,
                admin_name=user.name,
                action="login",
                details="Admin logged into the system"
            )
            await db.admin_actions.insert_one(admin_action.dict())
        
        return AuthResponse(user=user, session_token=session_token)
        
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/auth/logout")
async def logout_user(response: Response, session_token: str = Cookie(None)):
    try:
        if session_token:
            # Remove session token from user
            await db.users.update_one(
                {"session_token": session_token},
                {"$unset": {"session_token": ""}}
            )
        
        # Clear cookie
        response.delete_cookie(key="session_token")
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/auth/me")
async def get_current_user(session_token: str = Cookie(None)):
    try:
        if not session_token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        user = await db.users.find_one({"session_token": session_token})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        return User(**user)
        
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication required")

# Employee Profile endpoints
@api_router.post("/profile", response_model=EmployeeProfile)
async def create_employee_profile(profile_data: EmployeeProfileCreate, session_token: str = Cookie(None)):
    try:
        user = await verify_user_session(session_token)
        
        # Check if profile already exists
        existing_profile = await db.employee_profiles.find_one({"user_id": user["id"]})
        if existing_profile:
            raise HTTPException(status_code=400, detail="Profile already exists")
        
        profile = EmployeeProfile(user_id=user["id"], **profile_data.dict())
        await db.employee_profiles.insert_one(profile.dict())
        
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/profile")
async def get_employee_profile(session_token: str = Cookie(None)):
    try:
        user = await verify_user_session(session_token)
        
        profile = await db.employee_profiles.find_one({"user_id": user["id"]})
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return EmployeeProfile(**profile)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/profile")
async def update_employee_profile(profile_data: EmployeeProfileCreate, session_token: str = Cookie(None)):
    try:
        user = await verify_user_session(session_token)
        
        update_data = profile_data.dict()
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.employee_profiles.update_one(
            {"user_id": user["id"]},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        updated_profile = await db.employee_profiles.find_one({"user_id": user["id"]})
        return EmployeeProfile(**updated_profile)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Learning Goals endpoints
@api_router.post("/goals", response_model=LearningGoal)
async def create_learning_goal(goal_data: LearningGoalCreate, session_token: str = Cookie(None)):
    try:
        user = await verify_user_session(session_token)
        
        goal = LearningGoal(user_id=user["id"], **goal_data.dict())
        await db.learning_goals.insert_one(goal.dict())
        
        return goal
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/goals")
async def get_learning_goals(session_token: str = Cookie(None)):
    try:
        user = await verify_user_session(session_token)
        
        goals = []
        async for goal in db.learning_goals.find({"user_id": user["id"]}).sort("created_at", -1):
            goals.append(LearningGoal(**goal))
        
        return {"goals": goals}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/goals/{goal_id}")
async def update_learning_goal(goal_id: str, goal_data: LearningGoalCreate, session_token: str = Cookie(None)):
    try:
        user = await verify_user_session(session_token)
        
        update_data = goal_data.dict()
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.learning_goals.update_one(
            {"id": goal_id, "user_id": user["id"]},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        updated_goal = await db.learning_goals.find_one({"id": goal_id})
        return LearningGoal(**updated_goal)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Milestones endpoints
@api_router.post("/milestones", response_model=Milestone)
async def create_milestone(milestone_data: MilestoneCreate, session_token: str = Cookie(None)):
    try:
        user = await verify_user_session(session_token)
        
        # Set current month-year
        current_month = datetime.utcnow().strftime("%Y-%m")
        
        milestone = Milestone(
            user_id=user["id"],
            month_year=current_month,
            **milestone_data.dict()
        )
        await db.milestones.insert_one(milestone.dict())
        
        # Auto-add resource if it's a new source
        await auto_add_resource_from_milestone(milestone, user["id"])
        
        return milestone
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/milestones")
async def get_milestones(session_token: str = Cookie(None)):
    try:
        user = await verify_user_session(session_token)
        
        milestones = []
        async for milestone in db.milestones.find({"user_id": user["id"]}).sort("created_at", -1):
            milestones.append(Milestone(**milestone))
        
        return {"milestones": milestones}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Resources endpoints
@api_router.get("/resources")
async def get_approved_resources(category: str = None, session_token: str = Cookie(None)):
    try:
        await verify_user_session(session_token)
        
        query = {"approved": True}
        if category:
            query["category"] = category
        
        resources = []
        async for resource in db.resources.find(query).sort("created_at", -1):
            resources.append(Resource(**resource))
        
        return {"resources": resources}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Peer Learning endpoints
@api_router.get("/peers")
async def get_peer_profiles(session_token: str = Cookie(None)):
    try:
        user = await verify_user_session(session_token)
        
        # Get all profiles except current user
        profiles = []
        async for profile in db.employee_profiles.find({"user_id": {"$ne": user["id"]}}):
            # Remove sensitive data - only show learning-related info
            peer_profile = {
                "id": profile["id"],
                "full_name": profile["full_name"],
                "position": profile["position"],
                "department": profile["department"],
                "existing_skills": profile["existing_skills"],
                "learning_interests": profile["learning_interests"],
                "profile_picture": profile.get("profile_picture")
            }
            
            # Add recent milestones
            recent_milestones = []
            async for milestone in db.milestones.find({"user_id": profile["user_id"]}).sort("created_at", -1).limit(3):
                recent_milestones.append({
                    "what_learned": milestone["what_learned"],
                    "source": milestone["source"],
                    "can_teach": milestone["can_teach"],
                    "hours_invested": milestone["hours_invested"],
                    "created_at": milestone["created_at"]
                })
            
            peer_profile["recent_milestones"] = recent_milestones
            profiles.append(peer_profile)
        
        return {"peers": profiles}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/bookmarks/{user_id}")
async def bookmark_user(user_id: str, session_token: str = Cookie(None)):
    try:
        user = await verify_user_session(session_token)
        
        # Check if bookmark already exists
        existing = await db.bookmarks.find_one({"user_id": user["id"], "bookmarked_user_id": user_id})
        if existing:
            raise HTTPException(status_code=400, detail="Already bookmarked")
        
        bookmark = Bookmark(user_id=user["id"], bookmarked_user_id=user_id)
        await db.bookmarks.insert_one(bookmark.dict())
        
        return {"message": "User bookmarked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper function to verify user session
async def verify_user_session(session_token: str = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await db.users.find_one({"session_token": session_token})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    return user

# Helper function to auto-add resources from milestones
async def auto_add_resource_from_milestone(milestone: Milestone, user_id: str):
    try:
        # Extract domain/platform name from source
        source = milestone.source.lower()
        
        # Check if resource already exists
        existing = await db.resources.find_one({"url": milestone.source})
        if existing:
            return
        
        # Create resource entry (requires admin approval)
        resource = Resource(
            title=f"Learning Resource: {milestone.what_learned[:50]}...",
            url=milestone.source,
            description=f"Resource for learning: {milestone.what_learned}",
            category="General",
            tags=[milestone.what_learned.split()[0].lower()],
            added_by_user_id=user_id,
            approved=False
        )
        
        await db.resources.insert_one(resource.dict())
    except Exception as e:
        # Don't fail milestone creation if resource addition fails
        logger.error(f"Failed to auto-add resource: {str(e)}")

# Enhanced admin endpoints
async def verify_admin(session_token: str = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = await db.users.find_one({"session_token": session_token})
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user

# Admin endpoints
@api_router.get("/admin/stats", response_model=AdminStats)
async def get_admin_stats(session_token: str = Cookie(None)):
    try:
        admin_user = await verify_admin(session_token)
        
        # Get existing badge stats
        total_users = await db.users.count_documents({})
        total_admins = await db.users.count_documents({"role": "admin"})
        total_badges = await db.badge_generations.count_documents({})
        
        # Get recent activities (last 20 badge generations)
        recent_activities = []
        async for activity in db.badge_generations.find({}).sort("created_at", -1).limit(20):
            recent_activities.append({
                "user_name": activity["user_name"],
                "employee_name": activity["employee_name"],
                "learning": activity["learning"],
                "difficulty": activity["difficulty"],
                "created_at": activity["created_at"]
            })
        
        # Get top learners (badge count)
        pipeline = [
            {"$group": {"_id": "$user_name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        top_learners = []
        async for learner in db.badge_generations.aggregate(pipeline):
            top_learners.append({
                "name": learner["_id"],
                "badge_count": learner["count"]
            })
        
        # Get learning platform stats
        total_profiles = await db.employee_profiles.count_documents({})
        total_goals = await db.learning_goals.count_documents({})
        total_milestones = await db.milestones.count_documents({})
        total_resources = await db.resources.count_documents({})
        
        # Calculate monthly learning hours for current month
        current_month = datetime.utcnow().strftime("%Y-%m")
        monthly_hours_pipeline = [
            {"$match": {"month_year": current_month}},
            {"$group": {"_id": None, "total_hours": {"$sum": "$hours_invested"}}}
        ]
        monthly_hours_result = await db.milestones.aggregate(monthly_hours_pipeline).to_list(1)
        monthly_learning_hours = monthly_hours_result[0]["total_hours"] if monthly_hours_result else 0
        
        # Count employees meeting 6-hour target this month
        employees_meeting_target_pipeline = [
            {"$match": {"month_year": current_month}},
            {"$group": {"_id": "$user_id", "total_hours": {"$sum": "$hours_invested"}}},
            {"$match": {"total_hours": {"$gte": 6}}}
        ]
        meeting_target_result = await db.milestones.aggregate(employees_meeting_target_pipeline).to_list(1000)
        employees_meeting_target = len(meeting_target_result)
        
        # Get top learning platforms
        platforms_pipeline = [
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        top_platforms = []
        async for platform in db.milestones.aggregate(platforms_pipeline):
            top_platforms.append({
                "platform": platform["_id"],
                "usage_count": platform["count"]
            })
        
        # Get skills by department
        skills_by_dept = []
        async for profile in db.employee_profiles.find({}):
            for skill in profile.get("existing_skills", []):
                skills_by_dept.append({
                    "department": profile["department"],
                    "skill": skill
                })
        
        # Log admin action
        admin_action = AdminAction(
            admin_id=admin_user["id"],
            admin_name=admin_user["name"],
            action="view_enhanced_stats",
            details="Viewed enhanced admin dashboard with learning platform analytics"
        )
        await db.admin_actions.insert_one(admin_action.dict())
        
        return AdminStats(
            # Badge stats
            total_users=total_users,
            total_admins=total_admins,
            total_badges_generated=total_badges,
            recent_activities=recent_activities,
            top_learners=top_learners,
            # Learning platform stats
            total_profiles=total_profiles,
            total_goals=total_goals,
            total_milestones=total_milestones,
            total_resources=total_resources,
            monthly_learning_hours=monthly_learning_hours,
            employees_meeting_target=employees_meeting_target,
            top_learning_platforms=top_platforms,
            skills_by_department=skills_by_dept[:20]  # Limit for performance
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting enhanced admin stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/resources/pending")
async def get_pending_resources(session_token: str = Cookie(None)):
    try:
        admin_user = await verify_admin(session_token)
        
        resources = []
        async for resource in db.resources.find({"approved": False}).sort("created_at", -1):
            resources.append(Resource(**resource))
        
        # Log admin action
        admin_action = AdminAction(
            admin_id=admin_user["id"],
            admin_name=admin_user["name"],
            action="view_pending_resources",
            details="Viewed pending resources for approval"
        )
        await db.admin_actions.insert_one(admin_action.dict())
        
        return {"resources": resources}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/resources/{resource_id}/approve")
async def approve_resource(resource_id: str, session_token: str = Cookie(None)):
    try:
        admin_user = await verify_admin(session_token)
        
        result = await db.resources.update_one(
            {"id": resource_id},
            {
                "$set": {
                    "approved": True,
                    "approved_by_admin_id": admin_user["id"]
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        # Log admin action
        admin_action = AdminAction(
            admin_id=admin_user["id"],
            admin_name=admin_user["name"],
            action="approve_resource",
            details=f"Approved resource with ID: {resource_id}"
        )
        await db.admin_actions.insert_one(admin_action.dict())
        
        return {"message": "Resource approved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/learning-analytics")
async def get_learning_analytics(session_token: str = Cookie(None)):
    try:
        admin_user = await verify_admin(session_token)
        
        # Department-wise learning hours
        dept_hours_pipeline = [
            {"$lookup": {
                "from": "employee_profiles",
                "localField": "user_id",
                "foreignField": "user_id",
                "as": "profile"
            }},
            {"$unwind": "$profile"},
            {"$group": {
                "_id": "$profile.department",
                "total_hours": {"$sum": "$hours_invested"},
                "milestone_count": {"$sum": 1}
            }},
            {"$sort": {"total_hours": -1}}
        ]
        
        dept_analytics = []
        async for result in db.milestones.aggregate(dept_hours_pipeline):
            dept_analytics.append({
                "department": result["_id"],
                "total_hours": result["total_hours"],
                "milestone_count": result["milestone_count"]
            })
        
        # Skills trend analysis
        skills_pipeline = [
            {"$lookup": {
                "from": "employee_profiles",
                "localField": "user_id",
                "foreignField": "user_id",
                "as": "profile"
            }},
            {"$unwind": "$profile"},
            {"$group": {
                "_id": {
                    "skill": {"$toLower": {"$trim": {"input": "$what_learned"}}},
                    "month": "$month_year"
                },
                "count": {"$sum": 1}
            }},
            {"$group": {
                "_id": "$_id.skill",
                "monthly_data": {"$push": {
                    "month": "$_id.month",
                    "count": "$count"
                }},
                "total": {"$sum": "$count"}
            }},
            {"$sort": {"total": -1}},
            {"$limit": 20}
        ]
        
        skills_trends = []
        async for result in db.milestones.aggregate(skills_pipeline):
            skills_trends.append({
                "skill": result["_id"],
                "total_count": result["total"],
                "monthly_data": result["monthly_data"]
            })
        
        # Log admin action
        admin_action = AdminAction(
            admin_id=admin_user["id"],
            admin_name=admin_user["name"],
            action="view_learning_analytics",
            details="Viewed detailed learning analytics dashboard"
        )
        await db.admin_actions.insert_one(admin_action.dict())
        
        return {
            "department_analytics": dept_analytics,
            "skills_trends": skills_trends
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/users")
async def get_all_users(session_token: str = Cookie(None)):
    try:
        admin_user = await verify_admin(session_token)
        
        users = []
        async for user in db.users.find({}):
            users.append(User(**user))
        
        # Log admin action
        admin_action = AdminAction(
            admin_id=admin_user["id"],
            admin_name=admin_user["name"],
            action="view_users",
            details="Viewed all users list"
        )
        await db.admin_actions.insert_one(admin_action.dict())
        
        return {"users": users}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/badges")
async def get_all_badge_generations(session_token: str = Cookie(None)):
    try:
        admin_user = await verify_admin(session_token)
        
        badges = []
        async for badge in db.badge_generations.find({}).sort("created_at", -1):
            badges.append(BadgeGeneration(**badge))
        
        # Log admin action
        admin_action = AdminAction(
            admin_id=admin_user["id"],
            admin_name=admin_user["name"],
            action="view_badges",
            details="Viewed all badge generations"
        )
        await db.admin_actions.insert_one(admin_action.dict())
        
        return {"badges": badges}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting badge generations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/actions")
async def get_admin_actions(session_token: str = Cookie(None)):
    try:
        admin_user = await verify_admin(session_token)
        
        actions = []
        async for action in db.admin_actions.find({}).sort("timestamp", -1).limit(100):
            actions.append(AdminAction(**action))
        
        return {"actions": actions}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting admin actions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
async def generate_badge_and_post(request: GenerateRequest, session_token: str = Cookie(None)):
    try:
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
        # Verify user session
        if not session_token:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Find user by session token (simple approach - in production use JWT)
        user = await db.users.find_one({"session_token": session_token})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid session")

        # Prepare the prompt for Gemini API
        prompt = f"""You are an expert AI copywriter and branding strategist. You will receive three inputs: {request.employeeName}, {request.learning}, and {request.difficulty}.

### Task:
Generate TWO outputs clearly separated:

1. **Badge Description**: A short, creative, and celebratory text that can be used to design a digital badge image. It should include what they learned and be motivational. Keep it under 10 words. Tone: motivational and professional.

2. **LinkedIn Post**: A fully optimized LinkedIn post (200-300 words) that follows this EXACT format and structure:

🎉 Super proud to share that I've just achieved a {request.difficulty} learning milestone in [Learning Topic] by Branding Pioneers! 🔥

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
        badge_svg = generate_badge_svg(request.employeeName, badge_text, request.difficulty)
        
        # Convert SVG to base64 data URL
        badge_base64 = base64.b64encode(badge_svg.encode('utf-8')).decode('utf-8')
        badge_url = f"data:image/svg+xml;base64,{badge_base64}"
        
        # Store badge generation in database
        badge_generation = BadgeGeneration(
            user_id=user["id"],
            user_name=user["name"],
            employee_name=request.employeeName,
            learning=request.learning,
            difficulty=request.difficulty,
            badge_text=badge_text,
            linkedin_post=linkedin_post,
            badge_url=badge_url
        )
        await db.badge_generations.insert_one(badge_generation.dict())
        
        # Update user's badge count and last active
        await db.users.update_one(
            {"id": user["id"]},
            {
                "$inc": {"total_badges_generated": 1},
                "$set": {"last_active": datetime.utcnow()}
            }
        )
        
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