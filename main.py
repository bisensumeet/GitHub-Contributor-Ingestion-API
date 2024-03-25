import logging
from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel
import motor.motor_asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
mongodb_url = os.getenv("MONGODB_URL")
github_api_url = os.getenv("GITHUB_API_URL")
github_api_token = os.getenv("GITHUB_API_TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Define Pydantic model for input data
class InputData(BaseModel):
    owner: str
    repo: str

# Define Pydantic model for contributor data
class ContributorData(BaseModel):
    owner: str
    repo: str
    username: str
    avatar_url: str
    site_admin: bool
    contributions: int

class ContributorInfoInput(BaseModel):
    owner: str
    repo: str
    username: str
    type: str  # Assuming type can be either "User" or "Bot"

class ContributorInfoResponse(BaseModel):
    username: str
    avatar_url: str
    site_admin: bool
    contributions: int

# MongoDB connection
client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)
db = client.Github_Data
collection = db.get_collection('Contributors')

@app.get("/")
async def root():
    return {"message": "Welcome to my web application"}

@app.post("/ingest-contributors")
async def fetch_contributors(data: InputData):
    try:
        owner = data.owner
        repo = data.repo
        logger.info(f"Fetching contributors for repository: {owner}/{repo}")
        
        # Construct URL for GitHub API request
        url = f"{github_api_url}/repos/{owner}/{repo}/contributors"
        headers = {
            "Authorization": github_api_token
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for non-2xx status codes
        contributors = response.json()
        total_contributions = 0
        # Insert contributors into MongoDB
        for idx, contributor in enumerate(contributors):
            contributor_data = ContributorData(
                owner=owner,
                repo=repo,
                username=contributor["login"],
                avatar_url=contributor["avatar_url"],
                site_admin=contributor["site_admin"],
                contributions=contributor["contributions"]
            )
            total_contributions += contributor_data.contributions
            logger.debug(f"Inserting contributor {idx}: {contributor_data}")
            result = await collection.insert_one(contributor_data.dict())
        
        return { "message": f"Successfully ingested {total_contributions} contributors into Github_Data.Contributors collection" }
    except requests.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch contributors")
    except Exception as e:
        logger.exception("An error occurred while fetching contributors")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/contributors")
async def get_contributor_info(data: ContributorInfoInput):
    try:
        # Validate input data
        if data.type not in ["User", "Bot"]:
            raise HTTPException(status_code=400, detail="Invalid contributor type. Must be 'User' or 'Bot'.")

        # Query MongoDB collection based on provided parameters
        query = {
            "owner": data.owner,
            "repo": data.repo,
            "username": data.username
        }
        logger.info(f"Querying contributor info: {query}")
        contributor_data = await collection.find_one(query)
        
        # If contributor not found, raise HTTPException with 404 status code
        if contributor_data is None:
            raise HTTPException(status_code=404, detail="Contributor not found.")

        # Construct response data
        response_data = ContributorInfoResponse(
            username=contributor_data["username"],
            avatar_url=contributor_data["avatar_url"],
            site_admin=contributor_data["site_admin"],
            contributions=contributor_data["contributions"]
        )
        return response_data
    except HTTPException as e:
        raise e  # Re-raise HTTPException to return response with appropriate status code and detail message
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error.") from e
