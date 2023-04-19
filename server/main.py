# Import the needed modules
from fastapi import FastAPI, Request
import uvicorn
import os
from dotenv import load_dotenv
from src.routes.chat import chat

# load variables from the .env file
load_dotenv()

# initialize FastAPI
api = FastAPI()
api.include_router(chat)

# create a simple test route to test the API
@api.get("/test")
async def root():
    return {"msg": "API is online"}

if __name__ == "__main__":
    # set up the development server. API will run on port 3500
    if os.environ.get('APP_ENV') == "development":
        uvicorn.run("main:api", host="0.0.0.0",
                    port=3500, workers=4, reload=True)
    else:
        pass
