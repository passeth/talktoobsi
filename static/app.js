const recordBtn = document.getElementById('recordBtn');
const clearBtn = document.getElementById('clearBtn');
const replayBtn = document.getElementById('replayBtn');
const sendBtn = document.getElementById('sendBtn');
const textInput = document.getElementById('textInput');
const status = document.getElementById('status');
const chatContainer = document.getElementById('chatContainer');
const audioPlayer = document.getElementById('audioPlayer');

let mediaRecorder, audioChunks = [], isRecording = false;
let lastAudioUrl = null;

// iOS 오디오 잠금 해제
document.addEventListener('touchstart', () => {
    const audio = new Audio();
    audio.play().catch(() => { });
    audioPlayer.play().catch(() => { });
}, { once: true });

// 탭 전환
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(tab.dataset.tab + 'Tab').classList.add('active');
        if (tab.dataset.tab === 'notes') loadNotes();
        if (tab.dataset.tab === 'history') loadHistory();
    });
});

// 녹음
recordBtn.addEventListener('click', async () => {
    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
            mediaRecorder.onstop = sendAudio;
            mediaRecorder.start();
            isRecording = true;
            recordBtn.textContent = '⏹️ 중지';
            recordBtn.classList.add('recording');
            status.textContent = '🔴 녹음 중...';
        } catch (e) {
            status.textContent = '마이크 권한 필요';
        }
    } else {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(t => t.stop());
        isRecording = false;
        recordBtn.textContent = '🎤 녹음';
        recordBtn.classList.remove('recording');
        status.textContent = '처리 중...';
    }
});

// 음성 전송
async function sendAudio() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    try {
        const response = await fetch('/voice?tts=true', {
            method: 'POST',
            body: formData
        });

        await handleResponse(response);
    } catch (err) {
        console.error('연결 오류:', err);
        status.textContent = '서버 연결 실패';
    }
}

// 텍스트 전송
async function sendText(text) {
    if (!text.trim()) return;

    addMessage(text, 'user');
    status.textContent = '처리 중...';
    textInput.value = '';

    try {
        const response = await fetch(`/chat?message=${encodeURIComponent(text)}&tts=true`, {
            method: 'POST'
        });

        await handleResponse(response);
    } catch (err) {
        console.error('연결 오류:', err);
        status.textContent = '서버 연결 실패';
    }
}

// 응답 처리 (공통)
async function handleResponse(response) {
    if (response.ok) {
        const contentType = response.headers.get('content-type');

        if (contentType && contentType.includes('audio')) {
            const audioBlob = await response.blob();
            lastAudioUrl = URL.createObjectURL(audioBlob);
            audioPlayer.src = lastAudioUrl;

            // 재생 시도
            try {
                await audioPlayer.play();
                addMessage('🔊 재생 중...', 'ai');
            } catch (e) {
                addMessage('🔇 재생 버튼을 눌러주세요', 'ai');
            }

            replayBtn.disabled = false;
        } else {
            const data = await response.json();
            if (data.transcript) addMessage(data.transcript, 'user');
            if (data.response) addMessage(data.response, 'ai');
        }
        status.textContent = '대기 중';
    } else {
        status.textContent = '서버 오류';
    }
}

// 텍스트 전송 버튼
sendBtn.addEventListener('click', () => sendText(textInput.value));

// 엔터키로 전송
textInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendText(textInput.value);
});

// 다시 듣기
replayBtn.addEventListener('click', () => {
    if (lastAudioUrl) {
        audioPlayer.src = lastAudioUrl;
        audioPlayer.play();
        status.textContent = '🔊 재생 중...';
    }
});

// 오디오 재생 끝
audioPlayer.addEventListener('ended', () => {
    status.textContent = '대기 중';
});

function addMessage(text, type) {
    const div = document.createElement('div');
    div.className = `message ${type}-message`;
    div.textContent = text;
    chatContainer.appendChild(div);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// 대화 초기화
clearBtn.addEventListener('click', async () => {
    await fetch('/clear', { method: 'POST' });
    chatContainer.innerHTML = '';
    lastAudioUrl = null;
    replayBtn.disabled = true;
    status.textContent = '새 대화';
});

// 노트 목록
async function loadNotes() {
    try {
        const res = await fetch('/notes');
        const notes = await res.json();
        document.getElementById('noteList').innerHTML = notes.map(n =>
            `<div class="note-item" data-path="${n.path}">${n.name}</div>`
        ).join('');
    } catch (e) {
        document.getElementById('noteList').innerHTML = '<div class="note-item">노트 로딩 실패</div>';
    }
}

document.getElementById('noteList').addEventListener('click', async e => {
    if (e.target.classList.contains('note-item')) {
        try {
            const res = await fetch(`/note?path=${encodeURIComponent(e.target.dataset.path)}`);
            const data = await res.json();
            const content = data.content || '';

            // YAML frontmatter 파싱
            const yamlMatch = content.match(/^---\n([\s\S]*?)\n---/);
            let html = '';

            if (yamlMatch) {
                const yamlContent = yamlMatch[1];
                const bodyContent = content.replace(/^---\n[\s\S]*?\n---\n?/, '');

                const yamlLines = yamlContent.split('\n');
                let yamlHtml = '<div class="yaml-frontmatter"><div class="yaml-header">📋 Properties</div>';
                yamlLines.forEach(line => {
                    const colonIdx = line.indexOf(':');
                    if (colonIdx > 0) {
                        const key = line.substring(0, colonIdx).trim();
                        const value = line.substring(colonIdx + 1).trim();
                        yamlHtml += `<div class="yaml-row"><span class="yaml-key">${key}</span><span class="yaml-value">${value}</span></div>`;
                    }
                });
                yamlHtml += '</div>';

                html = yamlHtml + marked.parse(bodyContent);
            } else {
                html = marked.parse(content);
            }

            document.getElementById('noteContent').innerHTML = html;
        } catch (err) {
            document.getElementById('noteContent').innerHTML = '<p>노트 로딩 실패</p>';
        }
    }
});

// 대화 기록
async function loadHistory() {
    try {
        const res = await fetch('/history');
        const history = await res.json();
        if (history.length === 0) {
            document.getElementById('historyList').innerHTML = '<div class="history-item"><p>대화 기록이 없습니다</p></div>';
            return;
        }
        document.getElementById('historyList').innerHTML = history.slice().reverse().map(h =>
            `<div class="history-item">
                <div class="history-user">👤 ${h.user}</div>
                <div class="history-assistant">🤖 ${h.assistant}</div>
            </div>`
        ).join('');
    } catch (e) {
        document.getElementById('historyList').innerHTML = '<div class="history-item">기록 로딩 실패</div>';
    }
}
