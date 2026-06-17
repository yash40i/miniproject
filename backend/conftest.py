"""
Pytest configuration for Resume-Insight AI backend.
Excludes integration/script tests that require a running server.
"""
collect_ignore = [
    "tests/test_results.py",    # Requires running API server
    "tests/test_api_flow.py",   # Requires running API server
    "tests/test_e2e.py",        # Requires running API server
    "tests/test_db.py",         # Standalone script, not a pytest suite
]
