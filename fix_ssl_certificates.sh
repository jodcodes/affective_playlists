#!/bin/bash
# Fix SSL Certificate Verification on macOS
# This script fixes the "SSL: CERTIFICATE_VERIFY_FAILED" error in Python

echo "========================================================================"
echo "Fixing SSL Certificate Verification"
echo "========================================================================"
echo ""

# Check which Python is being used
PYTHON_CMD=$(which python3)
echo "Python: $PYTHON_CMD"
echo "Version: $(python3 --version)"
echo ""

# Try the official installer first
echo "Attempting to install certificates using official method..."
if [ -f "/Applications/Python 3.11/Install Certificates.command" ]; then
    echo "Found Python 3.11 installer..."
    "/Applications/Python 3.11/Install Certificates.command"
    echo "✓ Certificates installed for Python 3.11"
elif [ -f "/Applications/Python 3.10/Install Certificates.command" ]; then
    echo "Found Python 3.10 installer..."
    "/Applications/Python 3.10/Install Certificates.command"
    echo "✓ Certificates installed for Python 3.10"
elif [ -f "/Applications/Python 3.9/Install Certificates.command" ]; then
    echo "Found Python 3.9 installer..."
    "/Applications/Python 3.9/Install Certificates.command"
    echo "✓ Certificates installed for Python 3.9"
else
    echo "Python installer not found, trying pip method..."
    echo ""
    echo "Upgrading certifi (SSL certificates package)..."
    python3 -m pip install --upgrade certifi
    
    # Also try macOS-specific fix
    echo ""
    echo "Attempting macOS SSL fix..."
    /Applications/Python\ 3.*/Install\ Certificates.command 2>/dev/null || \
    python3 -m certifi || \
    echo "Note: You may need to manually run the Python certificate installer"
fi

echo ""
echo "========================================================================"
echo "Verifying SSL Certificate Fix"
echo "========================================================================"
echo ""

# Test SSL connection
python3 << 'EOF'
import ssl
import urllib.request

print("Testing SSL connection to MusicBrainz...")
try:
    url = "https://musicbrainz.org/ws/2/recording?query=artist%3A%22Test%22&limit=1&fmt=json"
    headers = {'User-Agent': 'metad-fill/1.0 (testing)'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=5) as response:
        print("✓ SSL connection successful!")
        print(f"  Response status: {response.status}")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")
except Exception as e:
    print(f"✗ SSL connection failed: {e}")
    print("")
    print("Try these additional fixes:")
    print("  1. python3 -m pip install --upgrade certifi")
    print("  2. Find your Python installation: which python3")
    print("  3. Run: /path/to/python/Install\\ Certificates.command")
    print("  4. Or try: python3 -m pip install certifi")

print("")
print("Testing Python SSL module...")
try:
    import certifi
    print(f"✓ certifi installed at: {certifi.where()}")
    print(f"  Certificate bundle: {certifi.where()}")
except ImportError:
    print("✗ certifi not installed")
    print("  Run: python3 -m pip install certifi")

EOF

echo ""
echo "========================================================================"
echo "SSL Certificate Fix Complete"
echo "========================================================================"
echo ""
echo "If tests passed, your metadata enrichment should now work!"
echo "Try running: python main.py"
echo ""
