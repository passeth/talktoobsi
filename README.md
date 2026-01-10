# 🎙️ Voice AI Companion

> **운전 중 음성으로 Obsidian Vault와 대화하기**

iPhone/Mac에서 음성으로 Obsidian 노트를 검색, 생성, 수정할 수 있는 AI 비서입니다.

## ✨ 주요 기능

- 🎤 **음성 대화**: Whisper STT + OpenAI TTS
- 🧠 **Claude Code 연동**: Obsidian Vault 내 파일 읽기/쓰기
- 📜 **대화 기록**: 세션 유지 및 이전 대화 참조
- 📄 **마크다운 뷰어**: YAML Frontmatter 지원
- 🌐 **HTTPS 터널**: iOS Safari 마이크 권한 지원

## 📋 사전 준비

- macOS (24시간 서버로 사용)
- Python 3.10+
- [OpenAI API Key](https://platform.openai.com/api-keys)
- [Claude Code](https://claude.ai) 설치 및 로그인
- Obsidian Vault

## 🚀 설치 방법

### 1. 저장소 클론

```bash
git clone https://github.com/YOUR_USERNAME/voice-ai-companion.git
cd voice-ai-companion
```

### 2. Python 가상환경 설정

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 환경변수 설정

```bash
cp .env.example .env
nano .env
```

`.env` 파일 수정:
```
OPENAI_API_KEY=sk-your-api-key-here
VAULT_PATH=/Users/YOUR_USERNAME/path/to/your/obsidian/vault
```

### 4. 서버 실행

```bash
python main.py
```

서버가 `http://localhost:8000`에서 시작됩니다.

### 5. HTTPS 터널 (iOS용)

iOS Safari에서 마이크 권한을 사용하려면 HTTPS가 필요합니다:

```bash
brew install cloudflared
cloudflared tunnel --url http://localhost:8000
```

출력되는 `https://xxx.trycloudflare.com` URL로 iPhone에서 접속하세요.

## 📱 사용 방법

### 웹 앱
1. 브라우저에서 `http://localhost:8000` 또는 HTTPS URL 접속
2. 💬 대화 탭: 음성으로 대화
3. 📜 기록 탭: 이전 대화 확인
4. 📄 노트 탭: Vault 노트 조회

### iPhone 홈 화면에 추가
1. Safari로 HTTPS URL 접속
2. 공유 버튼 → "홈 화면에 추가"
3. 앱처럼 사용!

## 🔧 API 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/` | GET | 웹 앱 |
| `/health` | GET | 서버 상태 |
| `/chat` | POST | 텍스트 대화 |
| `/voice` | POST | 음성 대화 |
| `/history` | GET | 대화 기록 |
| `/notes` | GET | 노트 목록 |
| `/note` | GET | 노트 내용 |
| `/clear` | POST | 대화 초기화 |

## 🔄 24시간 서버 운영

### 잠자기 방지
```bash
sudo pmset -c sleep 0
sudo pmset -c disksleep 0
```

### 자동 시작 (LaunchAgent)
```bash
cat > ~/Library/LaunchAgents/com.voice-ai.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.voice-ai</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd ~/voice-ai-companion && source venv/bin/activate && python main.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.voice-ai.plist
```

## 📁 프로젝트 구조

```
voice-ai-companion/
├── main.py              # FastAPI 서버
├── requirements.txt     # Python 의존성
├── .env.example         # 환경변수 템플릿
├── static/
│   ├── index.html       # PWA 메인 페이지
│   ├── style.css        # 스타일
│   ├── app.js           # 클라이언트 로직
│   └── manifest.json    # PWA 설정
└── README.md
```

## 🤝 기여

이슈와 PR을 환영합니다!

## 📄 라이선스

MIT License
