from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import subprocess
import os
import json
import glob
from dotenv import load_dotenv
from openai import OpenAI
import tempfile

load_dotenv()

app = FastAPI()
client = OpenAI()
VAULT_PATH = os.getenv("VAULT_PATH")
HISTORY_FILE = os.path.expanduser("~/voice-ai-server/chat_history.json")

app.mount("/static", StaticFiles(directory="static"), name="static")

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-10:], f)

def get_tts_text(response_text: str) -> str:
    """응답 분석해서 TTS 내용 결정"""
    if "저장" in response_text or "생성" in response_text or "작성" in response_text or "추가" in response_text:
        return "노트를 저장했습니다. 노트 탭에서 확인해보세요."
    elif len(response_text) > 500:
        return response_text[:300] + "... 자세한 내용은 노트를 확인하세요."
    else:
        return response_text

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
async def chat(message: str, tts: bool = False):
    history = load_history()
    context = "\n".join([f"User: {h['user']}\nAssistant: {h['assistant']}" for h in history[-5:]])
    
    # 시스템 프롬프트 (YAML 규칙 포함)
    system_prompt = """[중요: Obsidian 노트 작성 규칙]
노트를 생성하거나 수정할 때 YAML frontmatter가 필요하면:
1. 파일 맨 위에 --- 로 시작하고 --- 로 끝냄
2. 콜론(:) 뒤에 반드시 공백 추가
3. 특수문자가 있는 값은 따옴표로 감싸기
4. 날짜 형식: YYYY-MM-DD
예시:
---
title: "제목"
date: 2026-01-11
tags: [태그1, 태그2]
---
"""
    
    if context:
        full_prompt = f"{system_prompt}\n\n이전 대화:\n{context}\n\n새 질문: {message}"
    else:
        full_prompt = f"{system_prompt}\n\n{message}"
    
    result = subprocess.run(
        ["claude", "--dangerously-skip-permissions", "-p", full_prompt],
        cwd=VAULT_PATH,
        capture_output=True,
        text=True,
        timeout=180
    )
    
    response_text = result.stdout.strip()
    history.append({"user": message, "assistant": response_text[:500]})
    save_history(history)
    
    if tts and response_text:
        tts_text = get_tts_text(response_text)
        audio_path = await generate_tts(tts_text)
        return FileResponse(audio_path, media_type="audio/mpeg")
    
    return {"response": response_text}

@app.post("/voice")
async def voice(audio: UploadFile = File(...), tts: bool = True):
    """음성 → STT → Claude → TTS 응답"""
    audio_path = f"/tmp/{audio.filename}"
    with open(audio_path, "wb") as f:
        content = await audio.read()
        f.write(content)
    
    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    
    user_message = transcript.text
    
    history = load_history()
    context = "\n".join([f"User: {h['user']}\nAssistant: {h['assistant']}" for h in history[-5:]])
    
    # 시스템 프롬프트 (YAML 규칙 포함)
    system_prompt = """[중요: Obsidian 노트 작성 규칙]
노트를 생성하거나 수정할 때 YAML frontmatter가 필요하면:
1. 파일 맨 위에 --- 로 시작하고 --- 로 끝냄
2. 콜론(:) 뒤에 반드시 공백 추가
3. 특수문자가 있는 값은 따옴표로 감싸기
4. 날짜 형식: YYYY-MM-DD
"""
    
    if context:
        full_prompt = f"{system_prompt}\n\n이전 대화:\n{context}\n\n새 질문: {user_message}"
    else:
        full_prompt = f"{system_prompt}\n\n{user_message}"
    
    result = subprocess.run(
        ["claude", "--dangerously-skip-permissions", "-p", full_prompt],
        cwd=VAULT_PATH,
        capture_output=True,
        text=True,
        timeout=180
    )
    
    response_text = result.stdout.strip()
    history.append({"user": user_message, "assistant": response_text[:500]})
    save_history(history)
    
    if tts and response_text:
        tts_text = get_tts_text(response_text)
        audio_response_path = await generate_tts(tts_text)
        return FileResponse(audio_response_path, media_type="audio/mpeg")
    
    return {"transcript": user_message, "response": response_text}

@app.post("/clear")
async def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    return {"status": "cleared"}

@app.get("/history")
async def get_history():
    """대화 기록 조회"""
    return load_history()

@app.get("/notes")
async def list_notes():
    """최근 노트 목록"""
    notes = []
    for f in glob.glob(f"{VAULT_PATH}/**/*.md", recursive=True):
        try:
            stat = os.stat(f)
            notes.append({
                "path": f.replace(VAULT_PATH, ""),
                "name": os.path.basename(f),
                "modified": stat.st_mtime
            })
        except:
            pass
    notes.sort(key=lambda x: x["modified"], reverse=True)
    return notes[:20]

@app.get("/note")
async def get_note(path: str):
    """노트 내용 조회"""
    full_path = VAULT_PATH + path
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return {"content": f.read()}
    return {"error": "not found"}

async def generate_tts(text: str) -> str:
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )
    audio_path = tempfile.mktemp(suffix=".mp3")
    with open(audio_path, "wb") as f:
        for chunk in response.iter_bytes():
            f.write(chunk)
    return audio_path

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
