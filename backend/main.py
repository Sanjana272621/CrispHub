from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from github_api import get_user_repos, get_repo_details, get_user_stats

app = FastAPI(
    title="CrispHub GitHub Analytics API",
    description="Backend API for GitHub Analytics Dashboard",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to CrispHub GitHub Analytics API"}

@app.get("/api/user/{username}")
async def get_user_repositories(username: str, sort_by: str = Query("updated", description="Sort repositories by")):
    """Get all public repositories for a GitHub username"""
    try:
        repos = await get_user_repos(username, sort_by)
        return {"username": username, "repositories": repos}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/repo/{username}/{repo}")
async def get_repository_details(username: str, repo: str):
    """Get detailed information for a specific repository"""
    try:
        details = await get_repo_details(username, repo)
        return details
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/stats/{username}")
async def get_analytics(username: str):
    """Get aggregated statistics for all user repositories"""
    try:
        stats = await get_user_stats(username)
        return stats
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)