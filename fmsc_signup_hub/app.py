import os
import json
import uuid
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_DIR, "data", "events.json")
STATIC_DIR = os.path.join(APP_DIR, "static")

app = FastAPI(
    title="Sai Seva FMSC Group Portal",
    description="Sign-up portal and WhatsApp invite generator for Saibaba Group Phoenix SSSGC FMSC seva",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_data() -> Dict[str, Any]:
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=500, detail="Data file not found.")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data: Dict[str, Any]):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def extract_join_code(input_str: str) -> str:
    """Extracts joincode from full URL or returns code directly."""
    input_str = input_str.strip()
    match = re.search(r"joincode=([A-Za-z0-9]+)", input_str, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    match_code = re.search(r"code=([A-Za-z0-9\-_]+)", input_str, re.IGNORECASE)
    if match_code:
        return match_code.group(1).upper()
    # If it's alphanumeric up to 16 chars
    clean = re.sub(r"[^A-Za-z0-9\-_]", "", input_str)
    return clean.upper()

# Mount static folder
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def read_root():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Sai Seva FMSC Hub API is active"}

@app.get("/api/data")
def get_all_data():
    return load_data()

@app.post("/api/rsvp")
def add_rsvp(payload: Dict[str, Any] = Body(...)):
    data = load_data()
    sessions = data.get("sessions", [])
    
    session_id = payload.get("session_id", "").strip()
    name = payload.get("name", "").strip()
    if not session_id or not name:
        raise HTTPException(status_code=400, detail="Session ID and Volunteer Name are required.")
    
    target_session = next((s for s in sessions if s.get("id") == session_id), None)
    if not target_session:
        raise HTTPException(status_code=404, detail="Session not found.")
        
    adults = int(payload.get("adults_count", 1))
    kids = int(payload.get("kids_count", 0))
    total_requested = adults + kids
    
    # Calculate current filled spots
    current_volunteers = target_session.get("volunteers", [])
    current_filled = sum(v.get("adults_count", 1) + v.get("kids_count", 0) for v in current_volunteers)
    total_spots = target_session.get("total_spots", 36)
    
    new_vol = {
        "id": f"vol-{uuid.uuid4().hex[:8]}",
        "name": name,
        "email": payload.get("email", "").strip(),
        "phone": payload.get("phone", "").strip(),
        "type": "Adult" if adults > 0 else "Youth",
        "adults_count": adults,
        "kids_count": kids,
        "kids_ages": payload.get("kids_ages", "").strip(),
        "registered_on_fmsc": bool(payload.get("registered_on_fmsc", False)),
        "carpool": payload.get("carpool", "Driving"),
        "notes": payload.get("notes", "").strip(),
        "created_at": datetime.now().isoformat()
    }
    
    current_volunteers.append(new_vol)
    target_session["volunteers"] = current_volunteers
    save_data(data)
    
    return {
        "success": True,
        "message": f"Om Sri Sai Ram! {name} successfully registered for {target_session.get('date_formatted')}.",
        "rsvp": new_vol,
        "session": target_session
    }

@app.delete("/api/rsvp/{session_id}/{volunteer_id}")
def delete_rsvp(session_id: str, volunteer_id: str):
    data = load_data()
    sessions = data.get("sessions", [])
    target_session = next((s for s in sessions if s.get("id") == session_id), None)
    if not target_session:
        raise HTTPException(status_code=404, detail="Session not found.")
        
    volunteers = target_session.get("volunteers", [])
    filtered = [v for v in volunteers if v.get("id") != volunteer_id]
    target_session["volunteers"] = filtered
    save_data(data)
    return {"success": True, "message": "Volunteer reservation removed."}

@app.post("/api/session")
def create_or_update_session(payload: Dict[str, Any] = Body(...)):
    data = load_data()
    sessions = data.get("sessions", [])
    
    raw_date = payload.get("date", "").strip()
    if not raw_date:
        raise HTTPException(status_code=400, detail="Date is required (YYYY-MM-DD).")
        
    raw_code = payload.get("join_code", "").strip()
    raw_url = payload.get("join_url", "").strip()
    
    extracted_code = ""
    if raw_url and not raw_code:
        extracted_code = extract_join_code(raw_url)
    elif raw_code:
        extracted_code = extract_join_code(raw_code)
        
    join_url = raw_url if raw_url.startswith("http") else (f"http://www.fmsc.org/join-group?joincode={extracted_code}" if extracted_code else "")
    
    try:
        dt = datetime.strptime(raw_date, "%Y-%m-%d")
        formatted_date = dt.strftime("%A, %B %d, %Y")
    except ValueError:
        formatted_date = raw_date
        
    session_id = payload.get("id") or f"session-{raw_date}"
    
    existing = next((s for s in sessions if s.get("id") == session_id), None)
    if existing:
        existing["date"] = raw_date
        existing["date_formatted"] = formatted_date
        existing["time"] = payload.get("time", existing.get("time", "2:30 PM - 4:00 PM"))
        existing["arrival_time"] = payload.get("arrival_time", existing.get("arrival_time", "2:15 PM"))
        existing["location_name"] = payload.get("location_name", existing.get("location_name", "FMSC Tempe Site"))
        existing["address"] = payload.get("address", existing.get("address", "1100 West Grove Parkway, Tempe, AZ 85283"))
        existing["total_spots"] = int(payload.get("total_spots", existing.get("total_spots", 36)))
        existing["join_code"] = extracted_code or existing.get("join_code", "")
        existing["join_url"] = join_url or existing.get("join_url", "")
        existing["is_active"] = payload.get("is_active", True)
        save_data(data)
        return {"success": True, "message": "Session updated successfully.", "session": existing}
    else:
        new_session = {
            "id": session_id,
            "date": raw_date,
            "date_formatted": formatted_date,
            "time": payload.get("time", "2:30 PM - 4:00 PM"),
            "arrival_time": payload.get("arrival_time", "2:15 PM"),
            "location_name": payload.get("location_name", "FMSC Tempe Site"),
            "address": payload.get("address", "1100 West Grove Parkway, Tempe, AZ 85283"),
            "total_spots": int(payload.get("total_spots", 36)),
            "join_code": extracted_code,
            "join_url": join_url,
            "is_active": True,
            "volunteers": []
        }
        sessions.append(new_session)
        # Sort sessions by date
        sessions.sort(key=lambda s: s.get("date", ""))
        data["sessions"] = sessions
        save_data(data)
        return {"success": True, "message": "New FMSC session added.", "session": new_session}

@app.delete("/api/session/{session_id}")
def delete_session(session_id: str):
    data = load_data()
    sessions = data.get("sessions", [])
    filtered = [s for s in sessions if s.get("id") != session_id]
    if len(filtered) == len(sessions):
        raise HTTPException(status_code=404, detail="Session not found.")
    data["sessions"] = filtered
    save_data(data)
    return {"success": True, "message": "Session deleted."}

@app.post("/api/settings")
def update_settings(payload: Dict[str, Any] = Body(...)):
    data = load_data()
    group_info = data.get("group_info", {})
    for key in ["group_name", "organization", "leader_name", "leader_email", "leader_phone", "default_location_name", "default_address", "site_contact", "google_maps_url", "portal_public_url"]:
        if key in payload:
            group_info[key] = payload[key]
    data["group_info"] = group_info
    save_data(data)
    return {"success": True, "message": "Settings updated.", "group_info": group_info}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8005, reload=False)
