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