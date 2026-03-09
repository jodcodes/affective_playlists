# Design: Platform Guards and API Validation

## Technical Approach

### 1. Platform Guard Function
```python
def require_macos(feature_name: str) -> bool:
    """Guard function that checks sys.platform == "darwin"."""
    if sys.platform == "darwin":
        return True
    # Print user-facing error and suggestion
    print(error(f"{feature_name} requires macOS and Music.app"))
    return False
```

Applied to:
- `run_temperament_analysis()` - guards LLM client init
- `run_metadata_enrichment()` - guards playlist branch (folder mode allowed)
- `run_playlist_organization()` - guards move operations

### 2. API Key Validation
```python
def validate_openai_api_key() -> bool:
    """Early validation before client init."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print(error("OPENAI_API_KEY not configured"))
        print(info("Setup: https://platform.openai.com/api-keys"))
        logger.error("OPENAI_API_KEY missing")
        return False
    return True
```

Called in `run_temperament_analysis()` after platform check but before client init.

### 3. Improved Logging
Replace generic `print()` with structured logging:
- `logger.warning()` for import warnings
- `logger.debug()` for flow tracking
- `logger.error(..., exc_info=True)` for exception context

### 4. Testing Strategy
- **Unit tests**: Verify `require_macos()` on multiple platforms (darwin, linux, win32)
- **Integration tests**: Verify CLI exits correctly when guards trigger
- **Validation tests**: Verify API key validation blocks and allows appropriately

## Error Handling
- All guards return boolean (True = OK, False = stop)
- Early returns prevent cascade failures
- User-facing messages include actionable next steps
- Structured logging aids debugging

## Backwards Compatibility
- No changes to CLI interface or arguments
- Folder-mode enrichment still works on all platforms (no macOS guard)
- Existing successful paths unchanged
