import os
import secrets
from typing import Optional
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery, APIKeyCookie
import hashlib
import hmac

# Security schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)
bearer_security = HTTPBearer(auto_error=False)

# Configuration
class AuthConfig:
    """Authentication configuration."""
    
    def __init__(self):
        # Master API keys (in production, store these securely)
        self.master_keys = os.getenv("API_KEYS", "").split(",")
        self.master_keys = [key.strip() for key in self.master_keys if key.strip()]
        
        # If no keys provided, generate a default one for development
        if not self.master_keys:
            default_key = os.getenv("DEFAULT_API_KEY", "wanderwise-dev-key-2024")
            self.master_keys = [default_key]
            print(f"⚠️  Using development API key: {default_key}")
            print("   Set API_KEYS environment variable for production")
        
        # Rate limiting settings max 100 requests per hour
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
        
        # Premium features
        self.premium_keys = os.getenv("PREMIUM_API_KEYS", "").split(",")
        self.premium_keys = [key.strip() for key in self.premium_keys if key.strip()]

auth_config = AuthConfig()

def verify_api_key(api_key: str) -> dict:
    """Verify an API key and return user info."""
    if not api_key:
        return None
    
    # Check if it's a valid master key
    if api_key in auth_config.master_keys:
        return {
            "valid": True,
            "user_id": "master",
            "tier": "premium" if api_key in auth_config.premium_keys else "standard",
            "rate_limit": auth_config.rate_limit_requests
        }
    
    # To be extended to check database, JWT tokens, etc.
    return None

def get_api_key_from_header(api_key_header: Optional[str] = Security(api_key_header)) -> Optional[str]:
    """Extract API key from header."""
    return api_key_header

def get_api_key_from_query(api_key_query: Optional[str] = Security(api_key_query)) -> Optional[str]:
    """Extract API key from query parameter."""
    return api_key_query

def get_api_key_from_bearer(credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_security)) -> Optional[str]:
    """Extract API key from Bearer token."""
    if credentials:
        return credentials.credentials
    return None

async def get_current_user(
    api_key_header: Optional[str] = Depends(get_api_key_from_header),
    api_key_query: Optional[str] = Depends(get_api_key_from_query),
    api_key_bearer: Optional[str] = Depends(get_api_key_from_bearer)
) -> dict:
    """
    Get current authenticated user from various API key sources.
    Checks header, query parameter, and bearer token in that order.
    """
    
    # Try different sources for API key
    api_key = api_key_header or api_key_query or api_key_bearer
    
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Provide via X-API-Key header, api_key query parameter, or Authorization Bearer token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = verify_api_key(api_key)
    if not user:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    
    return user

async def get_optional_user(
    api_key_header: Optional[str] = Depends(get_api_key_from_header),
    api_key_query: Optional[str] = Depends(get_api_key_from_query),
    api_key_bearer: Optional[str] = Depends(get_api_key_from_bearer)
) -> Optional[dict]:
    """Get user if API key is provided, but don't require it."""
    api_key = api_key_header or api_key_query or api_key_bearer
    if api_key:
        return verify_api_key(api_key)
    return None

# Rate limiting (simple in-memory implementation)
import time
from collections import defaultdict

class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests = defaultdict(list)
    
    def is_allowed(self, user_id: str, limit: int, window: int = 3600) -> bool:
        """Check if user is within rate limit."""
        now = time.time()
        user_requests = self.requests[user_id]
        
        # Remove old requests outside the window
        user_requests[:] = [req_time for req_time in user_requests if now - req_time < window]
        
        if len(user_requests) >= limit:
            return False
        
        # Add current request
        user_requests.append(now)
        return True
    
    def get_remaining(self, user_id: str, limit: int, window: int = 3600) -> int:
        """Get remaining requests for user."""
        now = time.time()
        user_requests = self.requests[user_id]
        user_requests[:] = [req_time for req_time in user_requests if now - req_time < window]
        return max(0, limit - len(user_requests))

rate_limiter = RateLimiter()

async def check_rate_limit(user: dict = Depends(get_current_user)) -> dict:
    """Check rate limit for authenticated user."""
    user_id = user["user_id"]
    limit = user["rate_limit"]
    
    if not rate_limiter.is_allowed(user_id, limit):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {limit} requests per hour.",
            headers={
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time() + 3600))
            }
        )
    
    remaining = rate_limiter.get_remaining(user_id, limit)
    user["rate_limit_remaining"] = remaining
    
    return user

def generate_api_key() -> str:
    """Generate a new API key."""
    return f"wanderwise_{''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(32))}"

def hash_api_key(api_key: str) -> str:
    """Hash an API key for secure storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()