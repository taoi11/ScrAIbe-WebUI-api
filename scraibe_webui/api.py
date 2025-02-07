from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Union
from .utils.wrapper import ScraibeWrapper

app = FastAPI()

class TranscriptionRequest(BaseModel):
    task: str
    num_speakers: int = 0
    translate: bool = False
    language: str = "Unspecified"

@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...), task: str = Form(...), num_speakers: int = Form(0), translate: bool = Form(False), language: str = Form("Unspecified")):
    scraibe_params = {
        "whisper_model": "base",
        "whisper_type": "whisper",
        "dia_model": None,
        "use_auth_token": None,
        "device": "cpu",
        "num_threads": 4
    }
    scraibe = ScraibeWrapper.load_from_dict(scraibe_params)
    audio_path = f"/tmp/{file.filename}"
    with open(audio_path, "wb") as audio_file:
        audio_file.write(await file.read())
    
    if task == "Auto Transcribe":
        result, out_str, out_json = scraibe.autotranscribe(audio_path, num_speakers, translate, language)
        return JSONResponse(content={"transcription": out_str, "json": out_json})
    elif task == "Transcribe":
        result = scraibe.transcribe(audio_path, translate, language)
        return JSONResponse(content={"transcription": result})
    elif task == "Diarisation":
        result = scraibe.diarisation(audio_path, num_speakers)
        return JSONResponse(content={"json": result})
    else:
        return JSONResponse(content={"error": "Invalid task"}, status_code=400)
