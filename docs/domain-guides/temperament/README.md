# Temperament Analysis Domain Guide

LLM-based classification of playlists into four emotional temperaments: Woe, Frolic, Dread, and Malice.

## Overview

Temperament analysis uses language models to interpret track metadata and playlist context, classifying each playlist into exactly one of four emotional categories. The system includes resilient processing, API credential validation, and platform-specific constraints.

### Core Features

- **Four-category classification**: Woe (sad), Frolic (happy), Dread (dark), Malice (aggressive)
- **LLM-based interpretation**: Uses OpenAI GPT to analyze playlist mood
- **Music.app authentication**: Requires valid Music.app access on macOS
- **Early credential validation**: Detects missing API keys before client initialization
- **Per-playlist error handling**: Graceful failure with clear logging on API timeouts
- **Platform constraints**: Requires macOS for Music.app access; skips on non-macOS with guidance

## Authoritative Specification

Complete specification: [openspec/specs/temperament/spec.md](../../../openspec/specs/temperament/spec.md)

### Four Temperaments

| Temperament | Mood Profile | Example Tracks |
|-------------|--------------|-----------------|
| **Woe** | Sad, melancholic, introspective | Ballads, acoustic, emotional vocals |
| **Frolic** | Happy, upbeat, energetic | Pop, dance, uplifting rhythms |
| **Dread** | Dark, ominous, intense | Industrial, metal, atmospheric tension |
| **Malice** | Aggressive, hostile, chaotic | Punk, noise, confrontational energy |

### Key Scenarios

**Successful classification**  
A valid playlist with accessible tracks returns exactly one temperament label without API errors.

**Missing API credentials**  
When the OPENAI_API_KEY is not configured, the system detects it BEFORE client initialization, prints the setup link, logs the error, and exits with code 1.

**Music.app access failure**  
If Music.app is unavailable, the system stops and returns an authentication error.

**Non-macOS execution**  
On Linux or Windows, the system exits with a platform-specific error message and suggests workarounds (e.g., folder enrichment).

**API timeout during analysis**  
When the LLM request times out and retry policy is exhausted, the system logs the failure context and returns a non-zero exit code.

## Implementation

Source files related to temperament analysis:

- [src/temperament_analyzer.py](../../../src/temperament_analyzer.py) - Core analysis orchestration
- [src/llm_client.py](../../../src/llm_client.py) - OpenAI API integration
- [src/prompts.py](../../../src/prompts.py) - LLM prompt templates
- [tests/test_temperament_analyzer_quick.py](../../../tests/test_temperament_analyzer_quick.py) - Test suite

## Configuration

Temperament analysis is configured via:

- Environment variable: `OPENAI_API_KEY` - Required for GPT integration
- [src/config.py](../../../src/config.py) - Core configuration handling

## API Integration

- **Provider**: OpenAI (GPT models)
- **Authentication**: API key via environment variable
- **Timeout**: Configurable with retry policy
- **Fallback**: Non-zero exit code on exhausted retries with detailed logging

## Deployment Constraints

- **macOS required**: Temperament analysis requires Music.app access via AppleScript
- **API credentials required**: OPENAI_API_KEY must be set in environment
- **Non-macOS**: System exits gracefully with platform guidance; alternative workflows still available

## Related Domains

- [Metadata Enrichment](../metadata/) - Provides enriched metadata as input context
- [Playlist Organization](../playlists/) - Alternative classification based on genre

## Legacy Reference

For historical context and requirements traceability:
- [docs/legacy-specs/SPEC_TEMPERAMENT_ANALYZER.md](../../legacy-specs/SPEC_TEMPERAMENT_ANALYZER.md)
