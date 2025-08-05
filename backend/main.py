from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
import os
import uuid
from typing import AsyncGenerator
import asyncio
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

from models import User, Listing, UserLike, UserMatch, ListingLike
from schemas import (
    UserCreate, UserUpdate, UserResponse,
    ListingResponse, UserProfileResponse,
    LikeUserRequest, MatchResponse
)
from database import get_database, init_database, close_database
from auth import verify_telegram_auth, get_current_user
from services import UserService, ListingService, MatchingService

# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application...")
    try:
        await init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    yield
    # Shutdown - cleanup if needed
    logger.info("Shutting down application...")
    try:
        await close_database()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")

app = FastAPI(
    title="Social Rent API",
    description="API for Telegram housing social network",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Routes

@app.get("/")
async def root():
    return {"message": "Social Rent API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# User endpoints
@app.post("/api/users/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(verify_telegram_auth),
    db: AsyncSession = Depends(get_database)
):
    """Create or update user profile"""
    user_service = UserService(db)
    user = await user_service.create_or_update_user(current_user['id'], user_data)
    return user

@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Get current user profile"""
    return current_user

@app.put("/api/users/me", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Update current user profile"""
    user_service = UserService(db)
    user = await user_service.update_user(current_user.id, user_data)
    return user

@app.get("/api/users/potential-matches", response_model=list[UserProfileResponse])
async def get_potential_matches(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Get potential matches based on overlapping search areas"""
    matching_service = MatchingService(db)
    matches = await matching_service.get_potential_matches(current_user.id, limit)
    return matches

@app.post("/api/users/{user_id}/like")
async def like_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Like another user"""
    try:
        # Convert string UUID to UUID object
        liked_user_id = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    matching_service = MatchingService(db)
    result = await matching_service.like_user(current_user.id, liked_user_id)
    return result

@app.get("/api/users/matches", response_model=list[MatchResponse])
async def get_user_matches(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Get user's matches (mutual likes)"""
    matching_service = MatchingService(db)
    matches = await matching_service.get_user_matches(current_user.id)
    return matches

# Listing endpoints
@app.get("/api/listings/", response_model=list[ListingResponse])
async def get_listings(
    lat: float = None,
    lon: float = None,
    radius: int = 1000,  # meters
    price_min: int = None,
    price_max: int = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_database)
):
    """Get listings based on location and filters"""
    listing_service = ListingService(db)
    listings = await listing_service.search_listings(
        lat=lat, lon=lon, radius=radius,
        price_min=price_min, price_max=price_max,
        limit=limit
    )
    return listings

@app.get("/api/listings/search", response_model=list[ListingResponse])
async def search_listings_for_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Get listings based on current user's search criteria"""
    listing_service = ListingService(db)
    listings = await listing_service.get_listings_for_user(current_user)
    return listings

@app.post("/api/listings/{listing_id}/like")
async def like_listing(
    listing_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Like a listing"""
    try:
        # Convert string UUID to UUID object
        listing_uuid = uuid.UUID(listing_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid listing ID format"
        )
    
    listing_service = ListingService(db)
    result = await listing_service.like_listing(current_user.id, listing_uuid)
    return result

@app.get("/api/listings/liked", response_model=list[ListingResponse])
async def get_liked_listings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Get current user's liked listings"""
    listing_service = ListingService(db)
    listings = await listing_service.get_user_liked_listings(current_user.id)
    return listings

@app.get("/api/users/{user_id}/liked-listings", response_model=list[ListingResponse])
async def get_user_liked_listings(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Get liked listings of a matched user"""
    try:
        # Convert string UUID to UUID object
        target_user_id = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    matching_service = MatchingService(db)
    # Verify users are matched
    is_matched = await matching_service.are_users_matched(current_user.id, target_user_id)
    if not is_matched:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view liked listings of matched users"
        )
    
    listing_service = ListingService(db)
    listings = await listing_service.get_user_liked_listings(target_user_id)
    return listings

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)