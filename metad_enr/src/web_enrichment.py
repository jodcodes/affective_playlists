"""
Web-based data enrichment module.
Fetches genre/artist data from external sources and caches locally.
Supports Discogs, MusicBrainz, Last.fm, and RateYourMusic.
"""

import json
import os
import time
from typing import Dict, List, Optional, Set
from datetime import datetime
import urllib.request
import urllib.error


class WebDataFetcher:
    """Fetch and cache genre/artist data from web sources."""

    def __init__(self, cache_dir: str = "data/cache", cache_ttl: int = 604800):  # 7 days
        self.cache_dir = cache_dir
        self.cache_ttl = cache_ttl
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_path(self, source: str, query: str) -> str:
        """Get cache file path for a query."""
        safe_query = "".join(c if c.isalnum() else "_" for c in query)
        return os.path.join(self.cache_dir, f"{source}_{safe_query}.json")

    def _is_cache_valid(self, filepath: str) -> bool:
        """Check if cache file is still valid."""
        if not os.path.exists(filepath):
            return False
        
        mtime = os.path.getmtime(filepath)
        age = time.time() - mtime
        return age < self.cache_ttl

    def _get_cached(self, source: str, query: str) -> Optional[dict]:
        """Get cached data if available and valid."""
        cache_path = self._get_cache_path(source, query)
        
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not read cache {cache_path}: {e}")
        
        return None

    def _cache_result(self, source: str, query: str, data: dict) -> None:
        """Cache fetched data."""
        cache_path = self._get_cache_path(source, query)
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Warning: Could not write cache {cache_path}: {e}")

    def _fetch_url(self, url: str, timeout: int = 5) -> Optional[str]:
        """Fetch content from URL."""
        try:
            headers = {'User-Agent': 'metad-fill/1.0'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read().decode('utf-8')
        except urllib.error.URLError as e:
            print(f"Warning: Could not fetch {url}: {e}")
            return None
        except Exception as e:
            print(f"Warning: Error fetching {url}: {e}")
            return None

    def fetch_discogs_artist_genres(self, artist_name: str) -> Optional[List[str]]:
        """
        Fetch artist genres from Discogs API.
        Returns: List of genre tags or None if not found.
        """
        cached = self._get_cached("discogs_artist", artist_name)
        if cached is not None:
            return cached.get('genres')

        # Note: Discogs requires a token, which we'll mock here
        # In production, use: https://api.discogs.com/artists/{name}
        # For now, return None to indicate web fetching not implemented without API key
        return None

    def fetch_musicbrainz_artist_tags(self, artist_name: str) -> Optional[List[str]]:
        """
        Fetch artist tags from MusicBrainz API.
        Returns: List of genre tags or None if not found.
        """
        cached = self._get_cached("musicbrainz_artist", artist_name)
        if cached is not None:
            return cached.get('tags')

        # MusicBrainz free API endpoint
        url = f"https://musicbrainz.org/ws/2/artist/?query=artist:{artist_name}&fmt=json"
        
        content = self._fetch_url(url)
        if not content:
            return None

        try:
            data = json.loads(content)
            
            # Extract tags from first result
            if 'artists' in data and data['artists']:
                artist = data['artists'][0]
                tags = [tag['name'] for tag in artist.get('tags', [])]
                
                result = {'tags': tags, 'source': 'musicbrainz', 'timestamp': datetime.now().isoformat()}
                self._cache_result("musicbrainz_artist", artist_name, result)
                
                return tags
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON from MusicBrainz for {artist_name}")

        return None

    def fetch_lastfm_artist_tags(self, artist_name: str, api_key: Optional[str] = None) -> Optional[List[str]]:
        """
        Fetch artist tags from Last.fm API.
        Requires API key: https://www.last.fm/api/account/create
        Returns: List of genre tags or None if not found.
        """
        if not api_key:
            # Check environment variable
            api_key = os.environ.get('LASTFM_API_KEY')
        
        if not api_key:
            return None

        cached = self._get_cached("lastfm_artist", artist_name)
        if cached is not None:
            return cached.get('tags')

        url = f"http://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&artist={artist_name}&api_key={api_key}&format=json"
        
        content = self._fetch_url(url)
        if not content:
            return None

        try:
            data = json.loads(content)
            
            if 'toptags' in data and 'tag' in data['toptags']:
                tags = [tag['name'] for tag in data['toptags']['tag'][:10]]  # Top 10 tags
                
                result = {'tags': tags, 'source': 'lastfm', 'timestamp': datetime.now().isoformat()}
                self._cache_result("lastfm_artist", artist_name, result)
                
                return tags
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON from Last.fm for {artist_name}")

        return None

    def fetch_rym_artist_genres(self, artist_name: str) -> Optional[List[str]]:
        """
        Fetch artist genres from RateYourMusic (web scraping fallback).
        Note: RateYourMusic doesn't provide a public API, so this returns None.
        """
        # RateYourMusic doesn't have a public API
        # This is a placeholder for potential future web scraping implementation
        return None

    def fetch_all_sources(self, artist_name: str, 
                         sources: List[str] = None,
                         lastfm_api_key: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Fetch artist data from all available sources.
        Returns: {source: [genres, ...], ...}
        """
        if sources is None:
            sources = ['musicbrainz', 'lastfm']

        results = {}

        if 'musicbrainz' in sources:
            tags = self.fetch_musicbrainz_artist_tags(artist_name)
            if tags:
                results['musicbrainz'] = tags

        if 'lastfm' in sources:
            tags = self.fetch_lastfm_artist_tags(artist_name, lastfm_api_key)
            if tags:
                results['lastfm'] = tags

        if 'discogs' in sources:
            tags = self.fetch_discogs_artist_genres(artist_name)
            if tags:
                results['discogs'] = tags

        if 'rym' in sources:
            tags = self.fetch_rym_artist_genres(artist_name)
            if tags:
                results['rym'] = tags

        return results

    def merge_artist_lists(self, local_artists: Set[str], web_artists: List[str]) -> Set[str]:
        """
        Merge local and web-fetched artist lists, deduplicating.
        """
        merged = local_artists.copy()
        for artist in web_artists:
            merged.add(artist)
        
        return merged

    def enrich_genre_mappings(self, genre_mapping: dict, 
                              fetcher_results: Dict[str, Dict[str, List[str]]]) -> dict:
        """
        Enrich genre mapping with fetched keywords.
        fetcher_results: {artist: {source: [tags, ...], ...}, ...}
        """
        enriched = json.loads(json.dumps(genre_mapping))  # Deep copy
        
        for artist, sources in fetcher_results.items():
            # Collect all tags for this artist
            all_tags = set()
            for source, tags in sources.items():
                all_tags.update(tags)
            
            # This would require additional logic to map tags to genre clusters
            # For now, just log the results
            print(f"Enriched data for {artist}: {all_tags}")

        return enriched
