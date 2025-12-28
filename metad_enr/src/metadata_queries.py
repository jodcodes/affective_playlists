"""
Database query modules for metadata enrichment.

Queries external music databases in priority order:
1. MusicBrainz
2. AcousticBrainz
3. Discogs
4. Wikidata
5. Last.fm

All queries are read-only. No rate-limited API keys are required.
Implements caching to minimize requests.
"""

import json
import urllib.request
import urllib.error
import urllib.parse
from typing import Dict, List, Optional, Tuple
import logging
import time
from abc import ABC, abstractmethod
from .metadata_enrichment import MetadataField, DatabaseSource, MetadataEntry


class DatabaseQuery(ABC):
    """Abstract base class for database queries."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    @abstractmethod
    def query(self, artist: str, title: str, duration: Optional[int] = None) \
            -> Dict[MetadataField, Tuple[str, float]]:
        """
        Query database for metadata.
        
        Args:
            artist: Artist name
            title: Track title
            duration: Duration in seconds (optional, for matching)
            
        Returns:
            {MetadataField: (value, confidence), ...}
        """
        pass

    def _fetch_url(self, url: str, timeout: int = 5) -> Optional[str]:
        """
        Fetch content from URL.
        
        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            
        Returns:
            Response body or None if failed
        """
        try:
            headers = {'User-Agent': 'metad-fill/1.0 (metadata enrichment)'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read().decode('utf-8')
        except urllib.error.URLError as e:
            self.logger.debug(f"URL fetch failed: {e}")
            return None
        except Exception as e:
            self.logger.debug(f"Error fetching {url}: {e}")
            return None


class MusicBrainzQuery(DatabaseQuery):
    """Query MusicBrainz for metadata."""

    BASE_URL = "https://musicbrainz.org/ws/2"

    def query(self, artist: str, title: str, duration: Optional[int] = None) \
            -> Dict[MetadataField, Tuple[str, float]]:
        """
        Query MusicBrainz for track metadata.
        
        Returns: {field: (value, confidence), ...}
        """
        results = {}

        # Search for recording by artist and title
        recording = self._search_recording(artist, title)
        if not recording:
            return results

        self.logger.debug(f"Found MusicBrainz recording: {recording.get('id')}")

        # Extract metadata from recording
        if 'title' in recording:
            results[MetadataField.GENRE] = (recording['title'], 1.0)

        if 'first-release-date' in recording:
            year = recording['first-release-date'].split('-')[0]
            results[MetadataField.YEAR] = (year, 0.9)

        # Get genre from release if available
        if 'releases' in recording and recording['releases']:
            release = recording['releases'][0]
            genre = self._extract_genre_from_release(release)
            if genre:
                results[MetadataField.GENRE] = (genre, 0.7)

        return results

    def _search_recording(self, artist: str, title: str) -> Optional[dict]:
        """Search for recording in MusicBrainz."""
        query_str = f'artist:"{artist}" recording:"{title}"'
        params = urllib.parse.urlencode({
            'query': query_str,
            'limit': 5,
            'fmt': 'json'
        })

        url = f"{self.BASE_URL}/recording?{params}"
        response = self._fetch_url(url)

        if not response:
            return None

        try:
            data = json.loads(response)
            recordings = data.get('recordings', [])
            
            if recordings:
                return recordings[0]
        except json.JSONDecodeError:
            pass

        return None

    def _extract_genre_from_release(self, release: dict) -> Optional[str]:
        """Extract genre from MusicBrainz release."""
        # MusicBrainz doesn't have explicit genre field in older API
        # Check for tags or other genre indicators
        if 'tags' in release:
            tags = release['tags']
            if isinstance(tags, list) and tags:
                return tags[0].get('name')

        return None


class AcousticBrainzQuery(DatabaseQuery):
    """Query AcousticBrainz for BPM and audio features."""

    BASE_URL = "https://acousticbrainz.org/api/v1"

    def query(self, artist: str, title: str, duration: Optional[int] = None) \
            -> Dict[MetadataField, Tuple[str, float]]:
        """
        Query AcousticBrainz for audio features (primarily BPM).
        
        Returns: {field: (value, confidence), ...}
        """
        results = {}

        # AcousticBrainz requires MBID (MusicBrainz ID)
        # In production, would look up MBID first
        self.logger.debug(f"AcousticBrainz query not implemented (requires MBID lookup)")

        return results

    def query_by_mbid(self, mbid: str) -> Optional[Dict]:
        """
        Query AcousticBrainz by MusicBrainz ID.
        
        Args:
            mbid: MusicBrainz recording ID
            
        Returns:
            AcousticBrainz data or None
        """
        url = f"{self.BASE_URL}/{mbid}"
        response = self._fetch_url(url)

        if not response:
            return None

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return None

    def extract_bpm(self, acousticbrainz_data: dict) -> Optional[Tuple[str, float]]:
        """Extract BPM from AcousticBrainz data."""
        try:
            # BPM is in highlevel.rhythm section
            bpm = acousticbrainz_data.get('highlevel', {}).get('rhythm', {})
            if 'bpm' in bpm:
                return (str(int(bpm['bpm'])), 0.95)
        except (KeyError, ValueError, TypeError):
            pass

        return None


class DiscogsQuery(DatabaseQuery):
    """Query Discogs for metadata."""

    BASE_URL = "https://api.discogs.com"

    def query(self, artist: str, title: str, duration: Optional[int] = None) \
            -> Dict[MetadataField, Tuple[str, float]]:
        """
        Query Discogs for track metadata.
        
        Note: Discogs API requires token. This is simplified version.
        
        Returns: {field: (value, confidence), ...}
        """
        results = {}
        self.logger.debug(f"Discogs query (requires auth token)")

        return results


class WikidataQuery(DatabaseQuery):
    """Query Wikidata for metadata."""

    BASE_URL = "https://www.wikidata.org/w/api.php"

    def query(self, artist: str, title: str, duration: Optional[int] = None) \
            -> Dict[MetadataField, Tuple[str, float]]:
        """
        Query Wikidata for release date and genre.
        
        Returns: {field: (value, confidence), ...}
        """
        results = {}

        # Search for musical work/song
        entity = self._search_entity(title)
        if not entity:
            return results

        self.logger.debug(f"Found Wikidata entity: {entity}")

        # Query entity for metadata
        metadata = self._get_entity_metadata(entity)
        if not metadata:
            return results

        # Extract year
        if 'publication_date' in metadata:
            year = metadata['publication_date'].split('-')[0]
            results[MetadataField.YEAR] = (year, 0.8)

        # Extract genre
        if 'genre' in metadata:
            results[MetadataField.GENRE] = (metadata['genre'], 0.6)

        return results

    def _search_entity(self, title: str) -> Optional[str]:
        """Search for entity in Wikidata."""
        params = urllib.parse.urlencode({
            'action': 'query',
            'format': 'json',
            'search': title,
            'srsearch': f'haswbstatement:P31=Q7366'  # Instance of: musical work
        })

        url = f"{self.BASE_URL}?{params}"
        response = self._fetch_url(url, timeout=10)

        if not response:
            return None

        try:
            data = json.loads(response)
            search_results = data.get('query', {}).get('search', [])
            if search_results:
                return search_results[0]['title']
        except (json.JSONDecodeError, KeyError):
            pass

        return None

    def _get_entity_metadata(self, entity_title: str) -> Optional[dict]:
        """Get metadata for entity."""
        # Simplified - would query entity properties
        return None


class LastfmQuery(DatabaseQuery):
    """Query Last.fm for metadata (requires API key)."""

    BASE_URL = "http://ws.audioscrobbler.com/2.0"

    def __init__(self, api_key: Optional[str] = None, logger: Optional[logging.Logger] = None):
        super().__init__(logger)
        self.api_key = api_key

    def query(self, artist: str, title: str, duration: Optional[int] = None) \
            -> Dict[MetadataField, Tuple[str, float]]:
        """
        Query Last.fm for metadata.
        
        Note: Requires API key. Returns user-generated tags.
        
        Returns: {field: (value, confidence), ...}
        """
        if not self.api_key:
            self.logger.debug("Last.fm API key not provided")
            return {}

        results = {}

        # Query track info
        track_info = self._get_track_info(artist, title)
        if not track_info:
            return results

        # Extract tags (user-generated genre equivalents)
        if 'tags' in track_info:
            tags = track_info['tags']
            if isinstance(tags, list) and tags:
                genre = tags[0]  # Most popular tag
                results[MetadataField.GENRE] = (genre, 0.5)

        return results

    def _get_track_info(self, artist: str, title: str) -> Optional[dict]:
        """Get track info from Last.fm."""
        params = urllib.parse.urlencode({
            'method': 'track.getInfo',
            'artist': artist,
            'track': title,
            'api_key': self.api_key,
            'format': 'json'
        })

        url = f"{self.BASE_URL}?{params}"
        response = self._fetch_url(url, timeout=10)

        if not response:
            return None

        try:
            data = json.loads(response)
            return data.get('track')
        except json.JSONDecodeError:
            pass

        return None


class MetadataQueryOrchestrator:
    """Orchestrate queries across all databases in priority order."""

    # Priority order for queries
    QUERY_ORDER = [
        (DatabaseSource.MUSICBRAINZ, MusicBrainzQuery),
        (DatabaseSource.ACOUSTICBRAINZ, AcousticBrainzQuery),
        (DatabaseSource.DISCOGS, DiscogsQuery),
        (DatabaseSource.WIKIDATA, WikidataQuery),
        (DatabaseSource.LASTFM, LastfmQuery),
    ]

    def __init__(self, lastfm_api_key: Optional[str] = None,
                 logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.lastfm_api_key = lastfm_api_key
        self.query_cache: Dict[Tuple[str, str], List[MetadataEntry]] = {}

    def query_all_sources(self, artist: str, title: str,
                         duration: Optional[int] = None) -> List[MetadataEntry]:
        """
        Query all available sources for metadata.
        
        Queries are performed in deterministic priority order.
        Higher-confidence matches from earlier sources are preferred.
        
        Args:
            artist: Artist name
            title: Track title
            duration: Duration in seconds
            
        Returns:
            List of MetadataEntry objects with sources
        """
        # Check cache
        cache_key = (artist, title)
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]

        entries = []
        field_sources: Dict[MetadataField, float] = {}  # Track best confidence per field

        for source, query_class in self.QUERY_ORDER:
            if source == DatabaseSource.LASTFM:
                # LastFM requires API key
                if not self.lastfm_api_key:
                    continue
                querier = query_class(api_key=self.lastfm_api_key, logger=self.logger)
            else:
                querier = query_class(logger=self.logger)

            self.logger.debug(f"Querying {source.name} for {artist} - {title}")

            results = querier.query(artist, title, duration)

            for field, (value, confidence) in results.items():
                # Only accept if we don't have a higher-confidence match
                if field not in field_sources or confidence > field_sources[field]:
                    # Remove any previous entry for this field
                    entries = [e for e in entries if e.field != field]

                    entry = MetadataEntry(
                        field=field,
                        value=value,
                        source=source,
                        confidence=confidence
                    )
                    entries.append(entry)
                    field_sources[field] = confidence

            # Add rate limiting between queries
            time.sleep(0.5)

        # Cache results
        self.query_cache[cache_key] = entries

        return entries

    def clear_cache(self) -> None:
        """Clear query cache."""
        self.query_cache.clear()
        self.logger.debug("Cleared metadata query cache")
