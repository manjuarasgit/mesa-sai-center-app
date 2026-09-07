import os
import json
import uuid
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_DIR, "data", "app_data.json")
ROOT_DIR = os.path.dirname(APP_DIR)

app = FastAPI(title="Mesa Sathya Sai Center Hub", version="2.0.0")

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

# Serve slides from the workspace root Sai folder if available
sai_dir = os.path.join(ROOT_DIR, "Sai")
if os.path.exists(sai_dir):
    app.mount("/Sai", StaticFiles(directory=sai_dir), name="sai_slides")

# Serve static assets
static_dir = os.path.join(APP_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Mesa Sathya Sai Center API is running"}

@app.get("/api/data")
def get_all_data():
    return load_data()

@app.post("/api/events/rsvp")
def rsvp_special_event(payload: Dict[str, Any] = Body(...)):
    data = load_data()
    rsvps = data.get("special_event_rsvps", [])
    
    event_id = payload.get("event_id", "").strip()
    family_name = payload.get("family_name", "").strip()
    if not event_id or not family_name:
        raise HTTPException(status_code=400, detail="Event ID and Family/Volunteer name are required.")
        
    new_rsvp = {
        "id": f"rsvp-{uuid.uuid4().hex[:8]}",
        "event_id": event_id,
        "family_name": family_name,
        "adults": int(payload.get("adults", 1)),
        "kids": int(payload.get("kids", 0)),
        "contact_phone": payload.get("contact_phone", "").strip(),
        "notes": payload.get("notes", "").strip()
    }
    
    rsvps.insert(0, new_rsvp)
    data["special_event_rsvps"] = rsvps
    save_data(data)
    
    return {"success": True, "rsvp": new_rsvp, "message": "Thank you! Your interest / RSVP has been saved."}

@app.post("/api/seva/fmsc/register")
def register_fmsc(payload: Dict[str, Any] = Body(...)):
    data = load_data()
    fmsc = data.get("seva_fmsc", {})
    registrations = fmsc.get("registrations", [])
    
    family_name = payload.get("family_name", "").strip()
    if not family_name:
        raise HTTPException(status_code=400, detail="Family / Volunteer name is required.")
    
    new_reg = {
        "id": f"fmsc-{uuid.uuid4().hex[:8]}",
        "family_name": family_name,
        "contact_phone": payload.get("contact_phone", "").strip(),
        "adults_count": int(payload.get("adults_count", 1)),
        "kids_count": int(payload.get("kids_count", 0)),
        "kids_ages": payload.get("kids_ages", "").strip(),
        "notes": payload.get("notes", "").strip(),
        "fmsc_site_registered": bool(payload.get("fmsc_site_registered", False))
    }
    
    registrations.insert(0, new_reg)
    fmsc["registrations"] = registrations
    data["seva_fmsc"] = fmsc
    save_data(data)
    
    return {"success": True, "registration": new_reg, "message": "Successfully registered for FMSC Seva!"}

@app.delete("/api/seva/fmsc/register/{reg_id}")
def cancel_fmsc_registration(reg_id: str):
    data = load_data()
    fmsc = data.get("seva_fmsc", {})
    registrations = fmsc.get("registrations", [])
    
    filtered = [r for r in registrations if r.get("id") != reg_id]
    if len(filtered) == len(registrations):
        raise HTTPException(status_code=404, detail="Registration not found")
        
    fmsc["registrations"] = filtered
    data["seva_fmsc"] = fmsc
    save_data(data)
    return {"success": True, "message": "Registration removed"}

@app.post("/api/seva/breakfast/signup")
def signup_breakfast_item(payload: Dict[str, Any] = Body(...)):
    data = load_data()
    breakfast = data.get("seva_breakfast", {})
    items = breakfast.get("items", [])
    
    item_id = payload.get("item_id")
    volunteer = payload.get("volunteer", "").strip()
    phone = payload.get("phone", "").strip()
    qty = int(payload.get("qty", 1))
    
    if not item_id or not volunteer:
        raise HTTPException(status_code=400, detail="Item ID and Volunteer Name are required.")
        
    found = False
    for item in items:
        if item.get("id") == item_id:
            signed_up = item.get("signed_up", [])
            signed_up.append({
                "volunteer": volunteer,
                "phone": phone,
                "qty": qty
            })
            item["signed_up"] = signed_up
            found = True
            break
            
    if not found:
        raise HTTPException(status_code=404, detail="Item not found")
        
    breakfast["items"] = items
    data["seva_breakfast"] = breakfast
    save_data(data)
    
    return {"success": True, "message": f"Thank you {volunteer}! Your signup for {item['name']} has been saved."}

@app.post("/api/seva/breakfast/volunteer")
def signup_breakfast_volunteer(payload: Dict[str, Any] = Body(...)):
    data = load_data()
    breakfast = data.get("seva_breakfast", {})
    vols = breakfast.get("distribution_volunteers", [])
    
    name = payload.get("name", "").strip()
    role = payload.get("role", "General Volunteer").strip()
    phone = payload.get("phone", "").strip()
    
    if not name:
        raise HTTPException(status_code=400, detail="Volunteer Name is required.")
        
    vols.append({"name": name, "role": role, "phone": phone})
    breakfast["distribution_volunteers"] = vols
    data["seva_breakfast"] = breakfast
    save_data(data)
    
    return {"success": True, "message": f"Added {name} to distribution team!"}

@app.post("/api/announcements")
def add_announcement(payload: Dict[str, Any] = Body(...)):
    data = load_data()
    announcements = data.get("announcements", [])
    
    new_ann = {
        "id": f"ann-{uuid.uuid4().hex[:6]}",
        "title": payload.get("title", "").strip(),
        "date": payload.get("date", "").strip(),
        "category": payload.get("category", "General").strip(),
        "content": payload.get("content", "").strip(),
        "is_pinned": bool(payload.get("is_pinned", False))
    }
    
    announcements.insert(0, new_ann)
    data["announcements"] = announcements
    save_data(data)
    return {"success": True, "announcement": new_ann}

@app.post("/api/recaps")
def add_recap(payload: Dict[str, Any] = Body(...)):
    data = load_data()
    recaps = data.get("missed_session_recaps", [])
    
    new_recap = {
        "id": f"recap-{uuid.uuid4().hex[:6]}",
        "date": payload.get("date", "").strip(),
        "title": payload.get("title", "").strip(),
        "balvikas_summary": payload.get("balvikas_summary", "").strip(),
        "study_circle_summary": payload.get("study_circle_summary", "").strip(),
        "bhajan_summary": payload.get("bhajan_summary", "").strip(),
        "audio_link": payload.get("audio_link", "").strip(),
        "slides_link": payload.get("slides_link", "").strip()
    }
    
    recaps.insert(0, new_recap)
    data["missed_session_recaps"] = recaps
    save_data(data)
    return {"success": True, "recap": new_recap}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
