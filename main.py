import os
import uuid
import shutil
from fastapi import FastAPI, UploadFile, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from video_engine import build_product_video

app = FastAPI()

# Mount static files and outputs so the frontend can access them
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# In-memory status tracker (for MVP only)
tasks_db = {}

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")

@app.get("/generator")
def serve_generator():
    return FileResponse("static/generator.html")

@app.post("/api/generate")
async def generate_video(
    background_tasks: BackgroundTasks,
    company_name: str = Form(...),
    product_name: str = Form(...),
    application_area: str = Form(...),
    selling_points: str = Form(...),
    bg_img: UploadFile = Form(...),
    product_img: UploadFile = Form(...),
    logo_img: UploadFile = Form(...)
):
    task_id = str(uuid.uuid4())
    tasks_db[task_id] = "processing"
    
    # Save uploaded files locally
    files_data = {"bg_img": bg_img, "product_img": product_img, "logo_img": logo_img}
    saved_paths = {}
    
    for key, file_obj in files_data.items():
        file_path = f"./uploads/{task_id}_{file_obj.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_obj.file, buffer)
        saved_paths[key] = file_path

    # Prepare data for the engine
    video_data = {
        "company_name": company_name,
        "product_name": product_name,
        "application_area": application_area,
        "selling_points": selling_points,
        "bg_img": saved_paths["bg_img"],
        "product_img": saved_paths["product_img"],
        "logo_img": saved_paths["logo_img"]
    }

    # Run the heavy video rendering in the background!
    def background_process(t_id, data):
        try:
            build_product_video(t_id, data)
            tasks_db[t_id] = "completed"
        except Exception as e:
            print(f"Error generating video: {e}")
            tasks_db[t_id] = "failed"

    background_tasks.add_task(background_process, task_id, video_data)
    
    return {"task_id": task_id, "status": "processing"}

@app.get("/api/status/{task_id}")
def get_status(task_id: str):
    status = tasks_db.get(task_id, "not_found")
    if status == "completed":
        return {"status": status, "video_url": f"/outputs/output_{task_id}.mp4"}
    return {"status": status}
