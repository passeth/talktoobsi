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
from google.cloud import texttospeech
from urllib.parse import quote

load_dotenv()

# Google Cloud TTS 인증
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.expanduser("~/voice-ai-server/google-tts-credentials.json")
tts_client = texttospeech.TextToSpeechClient()

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
        json.dump(history[-20:], f)  # 20개로 확장

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
    
    # 시스템 프롬프트
    system_prompt = """[역할]
당신은 Obsidian Vault 관리 AI입니다. 사용자의 요청에 따라 실제로 파일을 생성, 수정, 검색합니다.

[중요 규칙]
1. 노트 생성/수정 요청 시 반드시 실제 파일을 생성하거나 수정하세요
2. 텍스트로만 응답하지 말고, 실제 파일 작업을 수행하세요
3. 작업 완료 후 간단히 뭘 했는지 알려주세요

[파일 경로 규칙]
- Daily Notes: 001_Growth Calendar/2026/YYYY-MM-DD.md
- 프로젝트: Projects/프로젝트명/파일명.md
- 인박스: 001_Growth Calendar/Inbox.md

[YAML frontmatter 규칙]
노트 생성 시:
---
title: "제목"
date: 2026-01-11
tags: [태그1, 태그2]
---

[응답 패턴]
- 노트 생성: "네, [파일명]에 기록했습니다" (실제 파일 작업 후)
- 검색: 검색 결과 요약
- 질문: 간단히 답변
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
    history.append({"user": message, "assistant": response_text[:1000]})  # 더 많이 저장
    save_history(history)
    
    if tts and response_text:
        tts_text = get_tts_text(response_text)
        audio_path = await generate_tts(tts_text)
        
        # 오디오를 base64로 인코딩
        import base64
        with open(audio_path, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode()
        
        # 전체 응답 텍스트와 오디오를 함께 반환
        return {
            "response": response_text,
            "audio": audio_base64,
            "tts_text": tts_text
        }
    
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
    
    # 시스템 프롬프트
    system_prompt = """[역할]
당신은 Obsidian Vault 관리 AI입니다. 사용자의 요청에 따라 실제로 파일을 생성, 수정, 검색합니다.

[중요 규칙]
1. 노트 생성/수정 요청 시 반드시 실제 파일을 생성하거나 수정하세요
2. 텍스트로만 응답하지 말고, 실제 파일 작업을 수행하세요
3. 작업 완료 후 간단히 뭘 했는지 알려주세요

[파일 경로 규칙]
- Daily Notes: 001_Growth Calendar/2026/YYYY-MM-DD.md
- 프로젝트: Projects/프로젝트명/파일명.md
- 인박스: 001_Growth Calendar/Inbox.md

[YAML frontmatter 규칙]
노트 생성 시:
---
title: "제목"
date: 2026-01-11
tags: [태그1, 태그2]
---

[응답 패턴]
- 노트 생성: "네, [파일명]에 기록했습니다" (실제 파일 작업 후)
- 검색: 검색 결과 요약
- 질문: 간단히 답변
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
    history.append({"user": user_message, "assistant": response_text[:1000]})  # 더 많이 저장
    save_history(history)
    
    if tts and response_text:
        tts_text = get_tts_text(response_text)
        audio_response_path = await generate_tts(tts_text)
        
        # 오디오를 base64로 인코딩
        import base64
        with open(audio_response_path, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode()
        
        # 전체 응답 텍스트와 오디오를 함께 반환
        return {
            "transcript": user_message,
            "response": response_text,
            "audio": audio_base64,
            "tts_text": tts_text
        }
    
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
    """Google Cloud TTS로 음성 생성"""
    synthesis_input = texttospeech.SynthesisInput(text=text)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code="ko-KR",
        name="ko-KR-Wavenet-A",  # 고품질 한국어 여성 음성
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.1  # 약간 빠르게
    )
    
    response = tts_client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    
    audio_path = tempfile.mktemp(suffix=".mp3")
    with open(audio_path, "wb") as f:
        f.write(response.audio_content)
    return audio_path

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
