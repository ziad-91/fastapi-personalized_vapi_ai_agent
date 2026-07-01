import os
import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pyairtable import Api
from dotenv import load_dotenv

# Load environment variables, overriding any existing system ones to ensure fresh reads
load_dotenv(override=True)

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")
VAPI_PUBLIC_KEY = os.getenv("VAPI_PUBLIC_KEY")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")

app = FastAPI(title="Vapi B2B Token Vendor")

# Configure CORS so the frontend can successfully make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to specific domains in production for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/generate-token")
def generate_token(company: str = Query(..., description="The company name to look up")):
    """
    Endpoint to look up a company in Airtable and generate a secure WebRTC token from Vapi.
    """
    if not all([AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, VAPI_PUBLIC_KEY, VAPI_ASSISTANT_ID]):
        raise HTTPException(status_code=500, detail="Missing server configuration.")

    try:
        # 1. Query Airtable
        api = Api(AIRTABLE_API_KEY)
        table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
        
        # Searching by Output field (which contains the full hostname)
        # Note: Using formula matching exact string. Escape single quotes if necessary.
        safe_company = company.replace("'", "\\'")
        formula = f"{{Output}} = '{safe_company}'"
        records = table.all(formula=formula)

        if not records:
            raise HTTPException(status_code=404, detail="Company not found in Airtable.")

        # Extract the first matching record
        record_fields = records[0].get("fields", {})
        fetched_company_name = record_fields.get("companyName", company)
        job_title = record_fields.get("jobTitle", "Professional")
        
        # Extract first name
        full_name = record_fields.get("Name", "Guest")
        first_name = full_name.split()[0] if full_name and full_name.strip() else "Guest"

        # We no longer need to call Vapi from the backend since we are dynamically sending
        # the Public Key to the frontend. This keeps the frontend source code "dumb"
        # and free of hardcoded API keys while ensuring we don't get 401 Unauthorized errors.
        
        return {
            "companyName": fetched_company_name,
            "jobTitle": job_title,
            "firstName": first_name,
            "vapi_public_key": VAPI_PUBLIC_KEY,
            "assistant_id": VAPI_ASSISTANT_ID
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
