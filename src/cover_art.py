"""
Cover art downloading and embedding module for metadata enrichment.

LAYER: Data Layer - Cover Art Management
ROLE: Download and embed cover art for tracks
ARCHITECTURE: See src/README.md for full architecture

Sources for cover art:
1. MusicBrainz (via CoverArtArchive API)
2. Spotify (via album artwork)
3. Last.fm (via album images)
4. Discogs (via album covers)

Features:
- Download cover art from multiple sources
- Cache downloaded images to avoid re-downloads
- Embed artwork in audio files (MP4, MP3)
- Validate image format and size
- Handle fallback sources gracefully
"""

import hashlib
import json
import logging
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional, Tuple

from src.metadata_enrichment import DatabaseSource, TrackIdentifier


# SSL context setup
def _setup_ssl_context():
    """Setup SSL context with proper certificate handling."""
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        try:
            return ssl.create_default_context()
        except:
            return ssl._create_unverified_context()


_SSL_CONTEXT = _setup_ssl_context()


class CoverArtDownloader:
    """Download cover art from multiple sources."""

    def __init__(
        self, cache_dir: str = "data/cache/cover_art", logger: Optional[logging.Logger] = None
    ):
        """
        Initialize CoverArtDownloader.

        Args:
            cache_dir: Directory to cache downloaded images
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.cache_dir = cache_dir
        self._ensure_cache_dir()

        # Config
        self.max_image_size = 5_000_000  # 5MB max
        self.timeout = 10  # seconds
        self.valid_formats = {".jpg", ".jpeg", ".png", ".gif"}

    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        os.makedirs(self.cache_dir, exist_ok=True)

    def _fetch_url(self, url: str) -> Optional[bytes]:
        """Fetch binary content from URL."""
        try:
            headers = {"User-Agent": "metad-fill/1.0"}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(
                req, timeout=self.timeout, context=_SSL_CONTEXT
            ) as response:
                data: bytes = response.read()
                if len(data) > self.max_image_size:
                    self.logger.warning(
                        f"Image too large: {len(data)} bytes, max {self.max_image_size}"
                    )
                    return None
                return data
        except Exception as e:
            self.logger.debug(f"Failed to fetch {url}: {e}")
            return None

    def _get_cache_path(self, url: str) -> str:
        """Generate cache file path from URL hash."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{url_hash}.jpg")

    def _cache_exists(self, url: str) -> bool:
        """Check if cover art is cached."""
        return os.path.exists(self._get_cache_path(url))

    def _get_cached_image(self, url: str) -> Optional[bytes]:
        """Get cached image bytes."""
        cache_path = self._get_cache_path(url)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "rb") as f:
                    return f.read()
            except Exception as e:
                self.logger.debug(f"Failed to read cache: {e}")
        return None

    def _save_to_cache(self, url: str, data: bytes) -> bool:
        """Save image to cache."""
        try:
            cache_path = self._get_cache_path(url)
            with open(cache_path, "wb") as f:
                f.write(data)
            return True
        except Exception as e:
            self.logger.debug(f"Failed to save to cache: {e}")
            return False

    def download_from_musicbrainz(self, mbid: str) -> Optional[bytes]:
        """
        Download cover art from CoverArtArchive (MusicBrainz).

        Args:
            mbid: MusicBrainz release ID

        Returns:
            Image bytes or None if not found
        """
        if not mbid:
            return None

        url = f"https://coverartarchive.org/release/{mbid}/front-500"

        # Check cache
        if self._cache_exists(url):
            return self._get_cached_image(url)

        # Download
        self.logger.debug(f"Downloading cover art from MusicBrainz: {mbid}")
        data = self._fetch_url(url)

        if data:
            self._save_to_cache(url, data)
            return data

        return None

    def download_from_spotify(self, album_id: str) -> Optional[bytes]:
        """
        Download cover art from Spotify.

        Args:
            album_id: Spotify album ID

        Returns:
            Image bytes or None if not found
        """
        if not album_id:
            return None

        # Note: Spotify API requires authentication, so we use a direct URL approach
        # This would require SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET from .env
        # For now, we return None as this requires more complex setup
        self.logger.debug("Spotify cover art requires API authentication - skipping")
        return None

    def download_from_lastfm(self, artist: str, album: str) -> Optional[bytes]:
        """
        Download cover art from Last.fm.

        Args:
            artist: Artist name
            album: Album name

        Returns:
            Image bytes or None if not found
        """
        if not artist or not album:
            return None

        # Last.fm provides image URLs in their API responses
        # This would require LASTFM_API_KEY from .env
        self.logger.debug("Last.fm cover art download requires API key - skipping")
        return None

    def download_from_discogs(self, discogs_id: str) -> Optional[bytes]:
        """
        Download cover art from Discogs.

        Args:
            discogs_id: Discogs release ID

        Returns:
            Image bytes or None if not found
        """
        if not discogs_id:
            return None

        # Discogs API requires authentication token
        self.logger.debug("Discogs cover art requires API token - skipping")
        return None

    def download(
        self, mbid: Optional[str] = None, artist: Optional[str] = None, album: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Download cover art using priority order.

        Priority:
        1. MusicBrainz (CoverArtArchive) - Most reliable
        2. Spotify - Better quality
        3. Last.fm - User community
        4. Discogs - Vinyl database

        Args:
            mbid: MusicBrainz release ID (best option)
            artist: Artist name
            album: Album name

        Returns:
            Image bytes or None
        """
        # Try MusicBrainz first (most reliable)
        if mbid:
            data = self.download_from_musicbrainz(mbid)
            if data:
                return data

        # Other sources would require API authentication
        # Spotify, Last.fm, Discogs all need credentials

        return None


class CoverArtEmbedder:
    """Embed cover art in audio files."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize CoverArtEmbedder."""
        self.logger = logger or logging.getLogger(__name__)

    def embed_mp4(self, filepath: str, image_data: bytes) -> bool:
        """
        Embed cover art in MP4/M4A file.

        Args:
            filepath: Path to audio file
            image_data: Image bytes to embed

        Returns:
            True if successful
        """
        # Check if file exists
        if not os.path.exists(filepath):
            self.logger.warning(f"File does not exist: {filepath}")
            return False

        try:
            from mutagen.mp4 import MP4

            audio = MP4(filepath)

            # Import needed for MP4 cover art
            from mutagen.mp4 import MP4Cover

            # Determine format
            if image_data.startswith(b"\xff\xd8\xff"):  # JPEG
                cover_format = MP4Cover.FORMAT_JPEG
            elif image_data.startswith(b"\x89PNG"):  # PNG
                cover_format = MP4Cover.FORMAT_PNG
            else:
                self.logger.warning(f"Unknown image format for {filepath}")
                return False

            # Set cover art
            audio["covr"] = [MP4Cover(image_data, cover_format)]
            audio.save()

            self.logger.debug(f"Embedded cover art in MP4: {filepath}")
            return True

        except ImportError:
            self.logger.warning("mutagen not installed - cannot embed MP4 cover art")
            return False
        except Exception as e:
            self.logger.error(f"Failed to embed cover art in MP4: {e}")
            return False

    def embed_mp3(self, filepath: str, image_data: bytes) -> bool:
        """
        Embed cover art in MP3 file.

        Args:
            filepath: Path to audio file
            image_data: Image bytes to embed

        Returns:
            True if successful
        """
        # Check if file exists
        if not os.path.exists(filepath):
            self.logger.warning(f"File does not exist: {filepath}")
            return False

        try:
            from mutagen.id3 import APIC, ID3

            # Load or create ID3 tags
            try:
                audio = ID3(filepath)
            except:
                audio = ID3()

            # Determine format
            if image_data.startswith(b"\xff\xd8\xff"):  # JPEG
                mime_type = "image/jpeg"
            elif image_data.startswith(b"\x89PNG"):  # PNG
                mime_type = "image/png"
            else:
                self.logger.warning(f"Unknown image format for {filepath}")
                return False

            # Add picture frame
            audio["APIC"] = APIC(
                encoding=3, mime=mime_type, type=3, desc="Cover", data=image_data  # Cover (front)
            )

            audio.save(filepath)
            self.logger.debug(f"Embedded cover art in MP3: {filepath}")
            return True

        except ImportError:
            self.logger.warning("mutagen not installed - cannot embed MP3 cover art")
            return False
        except Exception as e:
            self.logger.error(f"Failed to embed cover art in MP3: {e}")
            return False

    def embed(self, filepath: str, image_data: bytes) -> bool:
        """
        Embed cover art in audio file.

        Args:
            filepath: Path to audio file
            image_data: Image bytes

        Returns:
            True if successful
        """
        ext = os.path.splitext(filepath)[1].lower()

        if ext in {".m4a", ".mp4"}:
            return self.embed_mp4(filepath, image_data)
        elif ext in {".mp3"}:
            return self.embed_mp3(filepath, image_data)
        else:
            self.logger.warning(f"Unsupported audio format: {ext}")
            return False


class CoverArtManager:
    """High-level cover art management."""

    def __init__(
        self, cache_dir: str = "data/cache/cover_art", logger: Optional[logging.Logger] = None
    ):
        """Initialize CoverArtManager."""
        self.logger = logger or logging.getLogger(__name__)
        self.downloader = CoverArtDownloader(cache_dir, logger)
        self.embedder = CoverArtEmbedder(logger)

    def enrich_with_cover_art(
        self,
        filepath: str,
        mbid: Optional[str] = None,
        artist: Optional[str] = None,
        album: Optional[str] = None,
    ) -> bool:
        """
        Download and embed cover art.

        Args:
            filepath: Path to audio file
            mbid: MusicBrainz release ID
            artist: Artist name (for fallback)
            album: Album name (for fallback)

        Returns:
            True if cover art was successfully embedded
        """
        if not os.path.exists(filepath):
            self.logger.warning(f"File not found: {filepath}")
            return False

        # Download cover art
        image_data = self.downloader.download(mbid, artist, album)
        if not image_data:
            self.logger.debug(f"No cover art found for {filepath}")
            return False

        # Embed in audio file
        success = self.embedder.embed(filepath, image_data)
        if success:
            self.logger.debug(f"Cover art enriched for {filepath}")

        return success
