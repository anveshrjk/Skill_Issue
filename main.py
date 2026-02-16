from fastapi import FastAPI

# 1. Create the API Instance
# This 'app' variable represents your entire web server.
app = FastAPI(
    title="SkillIssue API",
    description="Fix your skill issues by trading knowledge with other students.",
    version="1.0.0"
)

# 2. Define a "Route"
# @app.get("/") tells FastAPI: "When someone visits the URL '/', run the function below."
# GET is the HTTP method used for fetching data (like loading a webpage).
@app.get("/")
def home():
    # We return a Python dictionary. FastAPI automatically converts this to JSON.
    return {"message": "SkillIssue API is running!", "status": "Active"}