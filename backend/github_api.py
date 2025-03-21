import aiohttp
import asyncio
import os
from datetime import datetime
from typing import Dict, List, Any
from collections import Counter

# Get GitHub token from environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
BASE_URL = "https://api.github.com"

async def fetch_data(url: str) -> Dict[str, Any]:
    """Generic function to fetch data from GitHub API"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as response:
            if response.status != 200:
                response_text = await response.text()
                raise Exception(f"GitHub API error: {response.status} - {response_text}")
            return await response.json()

async def get_user_repos(username: str, sort_by: str = "updated") -> List[Dict[str, Any]]:
    """Get all public repositories for a user"""
    url = f"{BASE_URL}/users/{username}/repos?sort={sort_by}&per_page=100"
    
    repos = await fetch_data(url)
    
    # Extract relevant information
    simplified_repos = []
    for repo in repos:
        # Skip forked repositories
        if repo.get("fork", False):
            continue
            
        simplified_repos.append({
            "name": repo["name"],
            "description": repo["description"],
            "stars": repo["stargazers_count"],
            "forks": repo["forks_count"],
            "language": repo["language"],
            "created_at": repo["created_at"],
            "updated_at": repo["updated_at"],
            "url": repo["html_url"],
            "size": repo["size"],
            "open_issues": repo["open_issues_count"],
            "topics": repo.get("topics", []),
            "has_wiki": repo["has_wiki"],
            "has_pages": repo["has_pages"],
            "watchers": repo["watchers_count"]
        })
    
    return simplified_repos

async def get_repo_details(username: str, repo: str) -> Dict[str, Any]:
    """Get detailed information for a specific repository"""
    # Get base repo information
    repo_url = f"{BASE_URL}/repos/{username}/{repo}"
    repo_data = await fetch_data(repo_url)
    
    # Get commits (last 30)
    commits_url = f"{repo_url}/commits?per_page=30"
    commits_data = await fetch_data(commits_url)
    
    # Get contributors
    contributors_url = f"{repo_url}/contributors?per_page=10"
    contributors_data = await fetch_data(contributors_url)
    
    # Get languages
    languages_url = f"{repo_url}/languages"
    languages_data = await fetch_data(languages_url)
    
    # Get weekly commit activity
    weekly_commit_url = f"{repo_url}/stats/commit_activity"
    weekly_commit_data = await fetch_data(weekly_commit_url)
    
    # Process commit data to get commit frequency by day
    commit_days = [commit["commit"]["author"]["date"].split("T")[0] for commit in commits_data]
    commit_day_counter = Counter(commit_days)
    
    return {
        "name": repo_data["name"],
        "full_name": repo_data["full_name"],
        "description": repo_data["description"],
        "created_at": repo_data["created_at"],
        "updated_at": repo_data["updated_at"],
        "stars": repo_data["stargazers_count"],
        "forks": repo_data["forks_count"],
        "open_issues": repo_data["open_issues_count"],
        "language": repo_data["language"],
        "languages": languages_data,
        "topics": repo_data.get("topics", []),
        "contributors": [
            {
                "login": contributor["login"],
                "avatar_url": contributor["avatar_url"],
                "contributions": contributor["contributions"]
            }
            for contributor in contributors_data
        ],
        "recent_commits": [
            {
                "sha": commit["sha"],
                "message": commit["commit"]["message"],
                "date": commit["commit"]["author"]["date"],
                "author": commit["commit"]["author"]["name"],
                "author_avatar": commit.get("author", {}).get("avatar_url", "")
            }
            for commit in commits_data
        ],
        "commit_frequency": dict(commit_day_counter),
        "weekly_commits": weekly_commit_data
    }

async def get_user_stats(username: str) -> Dict[str, Any]:
    """Generate aggregated statistics for all user repositories"""
    repos = await get_user_repos(username)
    
    # Calculate aggregated statistics
    total_stars = sum(repo["stars"] for repo in repos)
    total_forks = sum(repo["forks"] for repo in repos)
    languages = [repo["language"] for repo in repos if repo["language"]]
    language_counts = Counter(languages)
    
    # Get creation dates and calculate repository creation timeline
    creation_dates = [datetime.fromisoformat(repo["created_at"].replace("Z", "+00:00")) for repo in repos]
    creation_dates.sort()
    
    # Create timeline data
    timeline = []
    for date in creation_dates:
        timeline.append({
            "date": date.strftime("%Y-%m-%d"),
            "repos": len([d for d in creation_dates if d <= date])
        })
    
    # Get topics distribution
    all_topics = []
    for repo in repos:
        all_topics.extend(repo["topics"])
    topic_counts = Counter(all_topics)
    
    # Calculate average metrics
    avg_stars = total_stars / len(repos) if repos else 0
    avg_forks = total_forks / len(repos) if repos else 0
    
    return {
        "username": username,
        "repo_count": len(repos),
        "total_stars": total_stars,
        "total_forks": total_forks,
        "avg_stars": avg_stars,
        "avg_forks": avg_forks,
        "language_distribution": dict(language_counts),
        "timeline": timeline,
        "top_topics": dict(topic_counts.most_common(10)),
        "repos_by_stars": sorted(
            [{"name": repo["name"], "stars": repo["stars"]} for repo in repos], 
            key=lambda x: x["stars"], 
            reverse=True
        )[:5]
    }