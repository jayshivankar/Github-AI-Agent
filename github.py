import os 
import requests
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

github_token = os.getenv("GITHUB_TOKEN")

import requests

def fetch_github_info(owner, repo, endpoint):
    """
    Fetches data from a specific GitHub repository endpoint.
    Example endpoints: 'pulls', 'issues', or 'commits'.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"  
    }

    try:
        response = requests.get(url, headers=headers)
        
        response.raise_for_status() 
        
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []



def fetch_issues(owner,repo):
    data = fetch_github_info(owner,repo,"issues")
    return load_issues(data)


def load_issues(issues):
    docs = []
    for issue in issues:
        metadata = {
            "author": issue["user"]["login"],
            "comments": issue["comments"],
            "body": issue["body"],
            "labels":issue["labels"],
            "created_at": issue["created_at"]
        }
        data = issue['title']
        if issue['body']:
            data += issue['body']
        doc = Document(page_content=data, metadata=metadata)
        docs.append(doc)
    return docs


# info = fetch_github_info(owner="techwithtim", repo="Flask-Web-App-Tutorial", endpoint="issues")
# print(info)