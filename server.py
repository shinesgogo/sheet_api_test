from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.oauth2 import service_account
from googleapiclient.discovery import build
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
load_dotenv() 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this according to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load credentials from the JSON file
credentials = service_account.Credentials.from_service_account_file(
    './credentials.json',  # Update with the path to your credentials file
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

# Create the Google Sheets API service
service = build('sheets', 'v4', credentials=credentials)

class Feedback(BaseModel):
    url: str
    category: str
    score: str
    feedback: str

@app.post("/addFeedback")
async def add_feedback(feedback: Feedback):
    spreadsheet_id = os.getenv("SPREADSHEET_ID")  # Replace with your Google Sheets ID
    range_name = 'Sheet1!A:D'  # Adjust the range as needed

    values = [[feedback.url, feedback.category, feedback.score, feedback.feedback]]
    body = {
        'values': values
    }

    try:
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
