# backend/app/tools/github_tool.py
import requests
import base64
from typing import Dict, Any, List, Tuple
from app.config import settings


def extract_github_username(input_str: str) -> str:
    """Normalizes a GitHub URL or handle into a clean username."""
    clean = input_str.strip().rstrip("/")
    if "github.com/" in clean:
        parts = clean.split("github.com/")[-1].split("/")
        return parts[0]
    return clean.lstrip("@")


def fetch_github_dossier(github_input: str, max_repos: int = 6) -> Tuple[Dict[str, Any], List[str]]:
    """
    Queries the GitHub REST API using the Personal Access Token (Classic) to enrich the student's profile.
    Extracts bio, public repos, primary languages, and README summaries for top projects.
    """
    logs: List[str] = []
    if not github_input or not github_input.strip():
        logs.append("[WARN] No GitHub profile provided. Skipping GitHub enrichment.")
        return {}, logs

    username = extract_github_username(github_input)
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "ScholarSwarm-Agent"
    }
    if settings.GITHUB_TOKEN:
        # Classic PATs work with both 'token <PAT>' and 'Bearer <PAT>'
        headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

    base_url = "https://api.github.com"

    try:
        # 1. Fetch User Profile
        user_resp = requests.get(f"{base_url}/users/{username}", headers=headers, timeout=10)
        if user_resp.status_code == 404:
            logs.append(f"[WARN] GitHub user '{username}' not found (404). Continuing with resume data only.")
            return {}, logs
        elif user_resp.status_code == 401:
            logs.append("[WARN] GitHub Token unauthorized (401). Falling back to unauthenticated public request...")
            headers.pop("Authorization", None)
            user_resp = requests.get(f"{base_url}/users/{username}", headers=headers, timeout=10)

        user_resp.raise_for_status()
        user_data = user_resp.json()

        # 2. Fetch Public Repositories (sorted by recently pushed/updated)
        repos_resp = requests.get(
            f"{base_url}/users/{username}/repos?sort=updated&per_page=15&type=owner",
            headers=headers,
            timeout=10
        )
        repos_resp.raise_for_status()
        repos_data = repos_resp.json()

        # Filter out forks unless the user only has forks, and sort by stars + recent activity
        own_repos = [r for r in repos_data if not r.get("fork", False)] or repos_data
        own_repos.sort(key=lambda r: (r.get("stargazers_count", 0), r.get("updated_at", "")), reverse=True)
        top_repos = own_repos[:max_repos]

        enriched_projects = []
        all_languages = set()

        # 3. Inspect Top Repos & Fetch README Snippets
        for idx, repo in enumerate(top_repos):
            repo_name = repo.get("name", "")
            lang = repo.get("language")
            if lang:
                all_languages.add(lang)

            readme_excerpt = ""
            # Fetch README for the top 3 repositories to save latency while getting deep project context
            if idx < 3:
                readme_resp = requests.get(
                    f"{base_url}/repos/{username}/{repo_name}/readme",
                    headers=headers,
                    timeout=8
                )
                if readme_resp.status_code == 200:
                    content_b64 = readme_resp.json().get("content", "")
                    if content_b64:
                        decoded = base64.b64decode(content_b64).decode("utf-8", errors="ignore")
                        readme_excerpt = decoded[:1200].strip()  # First 1200 chars of README

            enriched_projects.append({
                "name": repo_name,
                "url": repo.get("html_url", ""),
                "description": repo.get("description") or "No description provided.",
                "primary_language": lang or "Unknown",
                "stars": repo.get("stargazers_count", 0),
                "topics": repo.get("topics", []),
                "readme_excerpt": readme_excerpt
            })

        dossier = {
            "username": username,
            "profile_url": user_data.get("html_url", f"https://github.com/{username}"),
            "name": user_data.get("name") or username,
            "bio": user_data.get("bio") or "",
            "public_repos_count": user_data.get("public_repos", 0),
            "detected_languages": list(all_languages),
            "top_projects": enriched_projects
        }

        logs.append(
            f"[SUCCESS] Enriched GitHub profile @{username}: analyzed {len(enriched_projects)} top repos "
            f"and detected languages: {', '.join(all_languages) if all_languages else 'N/A'}."
        )
        return dossier, logs

    except Exception as e:
        logs.append(f"[RECOVERY] GitHub API error for '{username}' ({str(e)}). Proceeding with Resume/Marksheet only.")
        return {}, logs