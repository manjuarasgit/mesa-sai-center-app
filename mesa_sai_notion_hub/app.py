import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(APP_DIR)

app = FastAPI(title="Mesa Sai Center Notion Hub Preview (Option 3)", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sai_dir = os.path.join(ROOT_DIR, "Sai")
if os.path.exists(sai_dir):
    app.mount("/Sai", StaticFiles(directory=sai_dir), name="sai_slides")

@app.get("/")
def read_root():
    index_path = os.path.join(APP_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Option 3 Notion Hub is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8002, reload=False)
