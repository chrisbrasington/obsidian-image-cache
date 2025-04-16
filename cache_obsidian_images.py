import os
import yaml
import requests
from pathlib import Path
from urllib.parse import urlparse, unquote

# --- Configuration ---
VAULT_PATH = os.path.expanduser("~/obsidian")
CACHE_PATH = os.path.join(VAULT_PATH, "cache")
IMAGE_FIELDS = ["coverUrlPortrait", "coverUrl", "image"]

# --- Ensure .img directory exists ---
os.makedirs(CACHE_PATH, exist_ok=True)

def extract_frontmatter(md_content):
    """Extract YAML frontmatter from markdown content"""
    if md_content.startswith("---"):
        end = md_content.find("\n---", 3)
        if end != -1:
            frontmatter = md_content[3:end].strip()
            return yaml.safe_load(frontmatter)
    return {}

def sanitize_url(url):
    """Ensure the image URL is safe and upgraded to zoom=2/https"""
    if not url: return None
    return url.replace("zoom=1", "zoom=2").replace("http:", "https:")

def get_safe_filename(url):
    """Turn a full URL into a safe unique filename"""
    parsed = urlparse(url)
    base = os.path.basename(parsed.path)
    if parsed.query:
        query_safe = parsed.query.replace("=", "-").replace("&", "__")
        base += f"___{query_safe}"
    return unquote(base)

def download_image(url, dest_path):
    """Download image if it doesn't already exist"""
    if os.path.exists(dest_path):
        print(f"[SKIP] Already cached: {os.path.basename(dest_path)}")
        return

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        with open(dest_path, "wb") as f:
            f.write(response.content)
        print(f"[DOWNLOADED] {url} → {dest_path}")
    except Exception as e:
        print(f"[ERROR] Failed to download {url} - {e}")

# --- Walk the Obsidian vault ---
for root, dirs, files in os.walk(VAULT_PATH):
    for file in files:
        if file.endswith(".md"):
            full_path = os.path.join(root, file)
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                frontmatter = extract_frontmatter(content)

                if not isinstance(frontmatter, dict):
                    continue

                for field in IMAGE_FIELDS:
                    url = sanitize_url(frontmatter.get(field))
                    if url:
                        filename = get_safe_filename(url)
                        dest_path = os.path.join(CACHE_PATH, filename)
                        print(f"[FOUND] {field} in {full_path}")
                        download_image(url, dest_path)
                        break  # only use the first matching image
            except Exception as e:
                print(f"[ERROR] Reading {full_path} - {e}")

