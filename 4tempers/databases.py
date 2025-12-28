"""
Music Database Connections and Configuration

Provides centralized configuration for music metadata providers and database connections.
Supports Spotify, MusicBrainz, and other music information services.
"""

import logging
import os

logger = logging.getLogger(__name__)

# ==================== DATABASE PROVIDER CONFIGURATION ====================

DATABASES = {
    "spotify": {
        "name": "Spotify",
        "description": "Spotify Web API - Rich audio features and popularity metrics",
        "requires_auth": True,
        "required_env_vars": ["SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET"],
        "features": [
            "Energy level (0-1)",
            "Danceability (0-1)",
            "Popularity score",
            "Explicit content flag",
            "Preview URL",
            "Audio features (valence, tempo, loudness)"
        ],
        "rate_limit": "100 requests per 15 seconds",
        "cost": "Free (with limitations)"
    },
    "musicbrainz": {
        "name": "MusicBrainz",
        "description": "Open music database - Track metadata and release information",
        "requires_auth": False,
        "required_env_vars": [],
        "features": [
            "Track information",
            "Artist details",
            "Album/Release info",
            "Release year",
            "Recording metadata"
        ],
        "rate_limit": "Reasonable for personal use",
        "cost": "Free and Open Source"
    },
    "mock": {
        "name": "Mock Database",
        "description": "Test provider - No external API calls",
        "requires_auth": False,
        "required_env_vars": [],
        "features": [
            "Track name",
            "Artist name",
            "Album name",
            "Mock energy and danceability"
        ],
        "rate_limit": "Unlimited",
        "cost": "Free"
    }
}

# ==================== SETUP INSTRUCTIONS ====================

SETUP_INSTRUCTIONS = {
    "spotify": """
Spotify Setup Instructions:
1. Visit https://developer.spotify.com/dashboard
2. Create a new application
3. Copy your Client ID and Client Secret
4. Add to .env file:
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
5. Restart the application

Benefits: Best audio features and popularity data
Limitations: Requires API key, rate limited
""",
    "musicbrainz": """
MusicBrainz Setup Instructions:
1. No setup required!
2. MusicBrainz is free and open-source
3. API rate limits are generous for personal use

Benefits: No authentication needed, comprehensive metadata
Limitations: Slower than Spotify, limited audio features
""",
    "mock": """
Mock Database Setup:
1. No setup required
2. Useful for testing without API calls

Benefits: Fast, no external dependencies
Limitations: Returns dummy data
"""
}

# ==================== CONNECTION MANAGEMENT ====================

def log_database_info():
    """Log available database providers and setup info"""
    logger.info("=" * 70)
    logger.info("AVAILABLE MUSIC DATABASES")
    logger.info("=" * 70)
    
    for db_key, db_info in DATABASES.items():
        logger.info(f"\n📀 {db_info['name'].upper()}")
        logger.info(f"   Description: {db_info['description']}")
        logger.info(f"   Authentication: {'Required' if db_info['requires_auth'] else 'Not required'}")
        logger.info(f"   Cost: {db_info['cost']}")
        logger.info(f"   Rate Limit: {db_info['rate_limit']}")
        logger.info(f"   Features:")
        for feature in db_info['features']:
            logger.info(f"     ✓ {feature}")
    
    logger.info("\n" + "=" * 70)


def get_available_providers() -> list:
    """Get list of database providers with available credentials"""
    available = []
    
    logger.info("Checking available database providers...")
    
    # Check Spotify
    if os.getenv('SPOTIFY_CLIENT_ID') and os.getenv('SPOTIFY_CLIENT_SECRET'):
        available.append('spotify')
        logger.info("✓ Spotify credentials found")
    else:
        logger.debug("✗ Spotify credentials not found")
    
    # MusicBrainz is always available (no auth required)
    available.append('musicbrainz')
    logger.info("✓ MusicBrainz available (no auth required)")
    
    # Mock is always available for testing
    available.append('mock')
    logger.info("✓ Mock provider available")
    
    return available


def get_recommended_provider() -> str:
    """Get the best available database provider based on credentials"""
    available = get_available_providers()
    
    # Priority: Spotify > MusicBrainz > Mock
    if 'spotify' in available:
        logger.info("Using Spotify as primary metadata provider (best audio features)")
        return 'spotify'
    elif 'musicbrainz' in available:
        logger.info("Using MusicBrainz as primary metadata provider (free, comprehensive)")
        return 'musicbrainz'
    else:
        logger.info("Using Mock provider (testing mode)")
        return 'mock'


def log_setup_instructions(provider: str):
    """Log setup instructions for a specific provider"""
    if provider in SETUP_INSTRUCTIONS:
        logger.info(SETUP_INSTRUCTIONS[provider])
    else:
        logger.warning(f"No setup instructions found for provider: {provider}")


# ==================== MUSIC API ENDPOINTS ====================

API_ENDPOINTS = {
    "spotify": {
        "auth": "https://accounts.spotify.com/api/token",
        "search": "https://api.spotify.com/v1/search",
        "audio_features": "https://api.spotify.com/v1/audio-features/{track_id}",
        "artist": "https://api.spotify.com/v1/artists/{artist_id}"
    },
    "musicbrainz": {
        "search": "https://musicbrainz.org/ws/2",
        "recording": "https://musicbrainz.org/ws/2/recording",
        "artist": "https://musicbrainz.org/ws/2/artist",
        "release": "https://musicbrainz.org/ws/2/release"
    }
}

# ==================== LOGGING ====================

def log_database_selection(provider: str):
    """Log which database provider is being used"""
    logger.info("=" * 60)
    logger.info(f"METADATA PROVIDER: {DATABASES[provider]['name'].upper()}")
    logger.info("=" * 60)
    logger.info(f"Description: {DATABASES[provider]['description']}")
    logger.info(f"Features: {', '.join(DATABASES[provider]['features'][:3])}...")
    logger.info("=" * 60)
