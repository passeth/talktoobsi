# 🛠️ 트러블슈팅

## 서버가 안 켜질 때

### 포트 충돌
```bash
kill -9 $(lsof -t -i:8000)
```

### 로그 확인
```bash
cat ~/talktoobsi/server.log
```

---

## 마이크 권한 문제 (iOS)

- ✅ HTTPS URL 사용 (`cloudflared tunnel`)
- ✅ Safari 설정 → 웹사이트 → 마이크 → 허용
- ❌ HTTP로는 마이크 작동 안됨

---

## Claude가 파일에 접근 못할 때

1. `.env`의 `VAULT_PATH` 확인
2. 경로가 정확한지 확인:
   ```bash
   ls $VAULT_PATH
   ```
3. Claude Code 권한 테스트:
   ```bash
   claude --dangerously-skip-permissions -p "ls"
   ```

---

## Tailscale 연결 안될 때

1. 메뉴바 Tailscale 아이콘 확인
2. "Connected" 상태인지 확인
3. 재로그인:
   ```bash
   tailscale logout
   tailscale login
   ```

---

## Cloudflare 터널 오류

```bash
# 기존 터널 종료
pkill -f cloudflared

# 새 터널 시작
cloudflared tunnel --url http://localhost:8000
```

---

## Python 의존성 오류

```bash
cd ~/talktoobsi
source venv/bin/activate
pip install --upgrade -r requirements.txt
```
