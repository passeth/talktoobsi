# 🔧 유지관리 가이드

## Cloudflare 터널 URL 변경 시

터널을 재시작하면 URL이 변경됩니다:

```bash
cloudflared tunnel --url http://localhost:8000
```

새 URL → iPhone Safari에서 접속 → 홈화면 앱 다시 추가

---

## 맥북 재부팅 후 체크리스트

LaunchAgent 미설정 시:

```bash
# 1. 서버 시작
cd ~/talktoobsi
source venv/bin/activate
nohup python main.py > server.log 2>&1 &

# 2. Cloudflare 터널 시작
cloudflared tunnel --url http://localhost:8000

# 3. Tailscale 연결 확인 (메뉴바 아이콘)
```

---

## 자동 시작 설정 (LaunchAgent)

### 설정
```bash
cat > ~/Library/LaunchAgents/com.talktoobsi.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.talktoobsi</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd ~/talktoobsi && source venv/bin/activate && python main.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF
```

### ON/OFF
```bash
# 활성화
launchctl load ~/Library/LaunchAgents/com.talktoobsi.plist

# 비활성화
launchctl unload ~/Library/LaunchAgents/com.talktoobsi.plist

# 삭제
rm ~/Library/LaunchAgents/com.talktoobsi.plist
```

---

## 서버 관리 명령어

```bash
# 상태 확인
curl http://localhost:8000/health

# 로그 보기
tail -f ~/talktoobsi/server.log

# 서버 중지
pkill -f "python main.py"

# 서버 재시작
kill -9 $(lsof -t -i:8000)
cd ~/talktoobsi && source venv/bin/activate && nohup python main.py > server.log 2>&1 &
```

---

## 대화 기록 관리

```bash
# 대화 기록 확인
cat ~/talktoobsi/chat_history.json

# 대화 초기화 (API)
curl -X POST http://localhost:8000/clear

# 대화 기록 파일 삭제
rm ~/talktoobsi/chat_history.json
```

---

## 서버 업데이트

```bash
cd ~/talktoobsi
git pull origin main
pkill -f "python main.py"
source venv/bin/activate
pip install -r requirements.txt
nohup python main.py > server.log 2>&1 &
```
