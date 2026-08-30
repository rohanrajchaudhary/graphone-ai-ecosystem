import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    print("❌ GITHUB_TOKEN not found")
    raise SystemExit(1)

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
}

response = requests.get(
    "https://api.github.com/user",
    headers=headers,
    timeout=15
)

print("Status:", response.status_code)

if response.status_code == 200:
    data = response.json()
    print("✅ GitHub token is working")
    print("Authenticated user:", data.get("login"))

    remaining = response.headers.get("X-RateLimit-Remaining")
    limit = response.headers.get("X-RateLimit-Limit")

    print("Rate limit:", remaining, "/", limit)

else:
    print("❌ Token test failed")
    print("Response:", response.text[:500])