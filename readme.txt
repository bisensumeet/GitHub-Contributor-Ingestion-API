GitHub Contributor Ingestion API
Overview:
The GitHub Contributor Ingestion API is a FastAPI-based web application designed to ingest contributors' data from GitHub repositories into a MongoDB database. It provides endpoints to fetch contributors' data from GitHub and retrieve contributor information from the MongoDB collection.

Prerequisites:
Before running the application, ensure you have the following:

Python 3.x installed on your system.
MongoDB server accessible with appropriate credentials and ssl certificate.
GitHub API token to access GitHub data.

Setup:
1. Install the required Python dependencies:
pip install -r requirements.txt

2. Create a .env file in the project directory and add the following environment variables:
MONGODB_URL=<mongodb_connection_url>
GITHUB_API_URL=https://api.github.com
GITHUB_API_TOKEN=<github_api_token>

Running the Application
To run the application, execute the following command:
uvicorn main:app --reload

The API will start running on http://127.0.0.1:8000/.

Endpoints
1. /ingest-contributors (POST)
This endpoint fetches contributors' data from the specified GitHub repository and ingests it into the MongoDB database.

Request Body: JSON object containing owner and repo fields specifying the GitHub repository.
{
    "owner": "facebook",
    "repo": "react"
}

Response: JSON object with a success message indicating the number of contributors ingested.
{
    "message": "Successfully ingested 50 contributors into Github_Data.Contributors collection"
}

2. /contributors (POST)
This endpoint retrieves contributor information from the MongoDB collection based on the provided parameters.

Request Body: JSON object containing owner, repo, username, and type fields.

{
    "owner": "facebook",
    "repo": "react",
    "username": "zpao",
    "type": "User"
}

Response: JSON object containing contributor information.

{
    "username": "zpao",
    "avatar_url": "https://avatars.githubusercontent.com/u/8445?v=4",
    "site_admin": false,
    "contributions": 1778
}

Logging:
The application logs events and errors using the Python logging module.

