import asyncio
import aiohttp
import json
import sys

# Configuration
API_BASE_URL = "http://localhost:8000/api"
TEST_USERNAME = "octocat"  # A public GitHub user with many repos
TEST_REPO = "hello-world"  # A known repository from the test user

async def test_user_endpoint(session):
    """Test the user repositories endpoint"""
    print(f"\nTesting user endpoint for {TEST_USERNAME}...")
    
    url = f"{API_BASE_URL}/user/{TEST_USERNAME}"
    async with session.get(url) as response:
        if response.status != 200:
            print(f"Error: User endpoint failed with status {response.status}")
            print(await response.text())
            return False
        
        data = await response.json()
        
        # Verify data structure
        if "username" not in data or "repositories" not in data:
            print("Error: User endpoint response is missing required fields")
            return False
        
        if not isinstance(data["repositories"], list):
            print("Error: Repositories field is not a list")
            return False
        
        print(f"User endpoint working! Found {len(data['repositories'])} repositories")
        
        # Print a sample repository if available
        if data["repositories"]:
            sample_repo = data["repositories"][0]
            print("\nSample repository data:")
            print(json.dumps(sample_repo, indent=2))
        
        return True

async def test_repo_endpoint(session):
    """Test the repository details endpoint"""
    print(f"\nTesting repo endpoint for {TEST_USERNAME}/{TEST_REPO}...")
    
    url = f"{API_BASE_URL}/repo/{TEST_USERNAME}/{TEST_REPO}"
    async with session.get(url) as response:
        if response.status != 200:
            print(f"Error: Repo endpoint failed with status {response.status}")
            print(await response.text())
            return False
        
        data = await response.json()
        
        # Verify data structure
        required_fields = ["name", "description", "stars", "forks", "contributors", "recent_commits", "languages"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print(f"Error: Repo endpoint response is missing required fields: {missing_fields}")
            return False
        
        print(f"Repo endpoint working! Found details for {data['name']}")
        
        # Print some key data points
        print("\nRepository stats:")
        print(f"Stars: {data['stars']}")
        print(f"Forks: {data['forks']}")
        print(f"Contributors: {len(data['contributors'])}")
        print(f"Recent commits: {len(data['recent_commits'])}")
        print(f"Languages: {list(data['languages'].keys())}")
        
        return True

async def test_stats_endpoint(session):
    """Test the user stats endpoint"""
    print(f"\n🔍 Testing stats endpoint for {TEST_USERNAME}...")
    
    url = f"{API_BASE_URL}/stats/{TEST_USERNAME}"
    async with session.get(url) as response:
        if response.status != 200:
            print(f"Error: Stats endpoint failed with status {response.status}")
            print(await response.text())
            return False
        
        data = await response.json()
        
        # Verify data structure
        required_fields = ["repo_count", "total_stars", "total_forks", "language_distribution", "timeline"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print(f"Error: Stats endpoint response is missing required fields: {missing_fields}")
            return False
        
        print(f"Stats endpoint working! Generated analytics for {TEST_USERNAME}")
        
        # Print analytics summary
        print("\nAnalytics summary:")
        print(f"Total repositories: {data['repo_count']}")
        print(f"Total stars: {data['total_stars']}")
        print(f"Top languages: {list(data['language_distribution'].keys())[:3]}")
        print(f"Top repositories by stars: {[repo['name'] for repo in data['repos_by_stars']]}")
        
        return True

async def main():
    """Run all tests"""
    print("Starting CrispHub GitHub Analytics Backend Tests")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test root endpoint
            print("\nTesting root endpoint...")
            async with session.get("http://localhost:8000/") as response:
                if response.status != 200:
                    print(f"Error: API is not running or root endpoint failed")
                    return
                print("API is running!")
            
            # Run all endpoint tests
            user_test = await test_user_endpoint(session)
            repo_test = await test_repo_endpoint(session)
            stats_test = await test_stats_endpoint(session)
            
            # Summary
            print("\nTest Summary:")
            print(f"User endpoint: {'Passed' if user_test else 'Failed'}")
            print(f"Repo endpoint: {'Passed' if repo_test else 'Failed'}")
            print(f"Stats endpoint: {'Passed' if stats_test else 'Failed'}")
            
            if user_test and repo_test and stats_test:
                print("\nAll tests passed! Your backend is working correctly.")
            else:
                print("\n⚠Some tests failed. Check the logs above for details.")
                
    except aiohttp.ClientConnectorError:
        print("Error: Could not connect to the API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    asyncio.run(main())
