# 🎙️ Talk to Obsi

> **운전 중에도, 걸으면서도 — 음성으로 Obsidian과 대화하세요!**

iPhone이나 Mac에서 **말로** Obsidian 노트를 검색하고, 생성하고, 수정할 수 있는 AI 비서예요.

![Platform](https://img.shields.io/badge/Platform-macOS-blue) ![Python](https://img.shields.io/badge/Python-3.10+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 변경 로그

### v1.1.0 (2026-01-11)
- ✨ **TTS 모드 토글** - 짧게/전체/직접 모드 선택
- ✨ **실시간 음성 인식** - 말하는 동안 텍스트 표시
- ✨ **진행 상태 애니메이션** - Claude 응답 대기 중 표시
- ✨ **Google Cloud TTS** - 더 빠르고 자연스러운 한국어 음성
- ✨ **재생/중지 토글** - 오디오 재생 제어
- 🔧 5분 타임아웃 설정
- 🔧 대화 히스토리 20개로 확장

### v1.0.0
- 초기 릴리스

---

## ✨ 이런 게 됩니다!

- 🎤 **"오늘 회의 내용 정리해줘"** → 노트 자동 생성
- 📝 **"지난주에 쓴 일기 찾아줘"** → 검색해서 읽어줌
- 💡 **"이 아이디어 Daily Notes에 저장해줘"** → 바로 저장
- 📊 **"내 프로젝트 현황 요약해줘"** → 분석해서 답변

**손 안 쓰고 Obsidian을 쓸 수 있어요!** 🚗💬

---

## 🎯 이런 분께 추천해요

- ✅ 운전 중에 떠오르는 아이디어를 바로 기록하고 싶은 분
- ✅ 산책하면서 생각을 정리하고 싶은 분
- ✅ 타이핑 대신 말로 노트하고 싶은 분
- ✅ Obsidian을 더 자주 쓰고 싶은데 귀찮은 분

---

## 📋 필요한 것들

| 필수 항목 | 설명 |
|----------|------|
| 🖥️ **Mac** | 24시간 서버로 사용 (안 쓰는 맥북도 OK!) |
| 🔑 **OpenAI API Key** | [여기서 발급](https://platform.openai.com/api-keys) |
| 🔑 **Google Cloud TTS** | [서비스 계정 키](https://console.cloud.google.com/) (선택) |
| 🤖 **Claude Code** | [여기서 설치](https://claude.ai/code) (Pro 구독 필요) |
| 📁 **Obsidian Vault** | 이미 있으시죠? |
| 📱 **iPhone** | 선택사항 (Mac에서만 써도 돼요) |

---

## 🚀 설치해볼까요?

### Step 1: Mac 준비하기

터미널을 열고 따라하세요! (Spotlight → "터미널" 검색)

```bash
# Homebrew가 없다면 먼저 설치 (이미 있다면 건너뛰기)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

> 💡 `brew --version` 명령어로 설치 여부 확인 가능!

### Step 2: 필수 앱 설치

```bash
# Tailscale (외부 접속용)
brew install --cask tailscale

# Cloudflared (HTTPS 터널)
brew install cloudflared
```

Tailscale 앱 실행 → 로그인해주세요!

### Step 3: Claude Code 설치

```bash
curl -fsSL https://claude.ai/install.sh | sh
claude login
```

### Step 4: 프로젝트 다운로드

```bash
cd ~
git clone https://github.com/passeth/talktoobsi.git
cd talktoobsi
```

### Step 5: Python 설정

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 6: 환경변수 설정

```bash
cp .env.example .env
nano .env
```

이렇게 수정하세요:
```
OPENAI_API_KEY=여기에-API-키-붙여넣기
VAULT_PATH=/Users/내이름/Documents/Obsidian Vault
```

> 💡 **Vault 경로 찾기**: Finder에서 Vault 폴더를 터미널로 드래그하면 경로가 나와요!

### Step 7: 서버 시작!

```bash
python main.py
```

`http://localhost:8000` 에서 서버가 시작됐어요! 🎉

---

## 📱 iPhone에서 사용하기

### 1. HTTPS 터널 만들기

iOS Safari는 HTTPS에서만 마이크를 허용해요. 새 터미널 탭에서:

```bash
cloudflared tunnel --url http://localhost:8000
```

이런 URL이 나와요:
```
https://random-words-here.trycloudflare.com
```

### 2. iPhone 설정

1. **Tailscale 앱** 설치 (App Store)
2. Mac과 같은 계정으로 로그인
3. **Safari**에서 위 URL 접속
4. 마이크 권한 허용!

### 3. 홈화면에 추가 (앱처럼 쓰기)

1. Safari 하단 **공유 버튼** 탭
2. **"홈 화면에 추가"** 선택
3. 이제 앱처럼 쓸 수 있어요! 📲

---

## 💬 사용 방법

### UI 구성

```
[ 🔈 짧게 ] [ 🔊 전체 ] [ ⌨️ 직접 ]  ← TTS 모드 선택
[텍스트 입력...              ] [📤]  ← 텍스트 입력
[🎤 녹음    ] [🔊] [🗑️]              ← 음성 녹음/재생
```

### TTS 모드

| 모드 | 설명 |
|------|------|
| 🔈 **짧게** | 응답 요약만 읽어줌 (기본) |
| 🔊 **전체** | 전체 응답 읽어줌 |
| ⌨️ **직접** | Claude Code 명령어 직접 입력 |

### 탭 구성

| 탭 | 기능 |
|:--:|------|
| 💬 | 음성으로 대화 |
| 📜 | 이전 대화 기록 보기 |
| 📄 | Vault 노트 읽기 |

### 대화 예시

- 🗣️ "안녕, 오늘 뭐 할까?"
- 🗣️ "어제 회의록 찾아줘"
- 🗣️ "이 내용 노트로 저장해줘"
- 🗣️ "내 태스크 목록 보여줘"

### 직접 모드 예시 (⌨️)

```
/agent summarize project
ultrathink 복잡한 분석 요청...
```

---

## 📚 더 알아보기

자세한 내용은 [docs 폴더](./docs/)를 확인하세요:

- 📖 [유지관리 가이드](./docs/maintenance.md) - 서버 관리, 자동 시작 설정
- 🔧 [트러블슈팅](./docs/troubleshooting.md) - 문제 해결
- ❓ [FAQ](./docs/faq.md) - 자주 묻는 질문

---

## 🤝 기여

이슈와 PR 환영합니다! 질문도 편하게 올려주세요 😊

## 📄 라이선스

MIT License

---

**Made with ❤️ for Obsidian lovers**

*"손가락 대신 목소리로, Obsidian과 대화하세요"*
