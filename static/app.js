const recordBtn = document.getElementById('recordBtn');
const clearBtn = document.getElementById('clearBtn');
const status = document.getElementById('status');
const chatContainer = document.getElementById('chatContainer');
const audioPlayer = document.getElementById('audioPlayer');

let mediaRecorder, audioChunks = [], isRecording = false;

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

async function sendAudio() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

    // FormData로 오디오 파일 전송
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    try {
        const response = await fetch('/voice?tts=true', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const contentType = response.headers.get('content-type');

            if (contentType && contentType.includes('audio')) {
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                audioPlayer.src = audioUrl;
                audioPlayer.play();
                addMessage('🔊 재생 중...', 'ai');
            } else {
                const data = await response.json();
                if (data.transcript) addMessage(data.transcript, 'user');
                if (data.response) addMessage(data.response, 'ai');
            }
            status.textContent = '대기 중';
        } else {
            status.textContent = '서버 오류';
        }
    } catch (err) {
        console.error('연결 오류:', err);
        status.textContent = '서버 연결 실패';
    }
}

function addMessage(text, type) {
    const div = document.createElement('div');
    div.className = `message ${type}-message`;
    div.textContent = text;
    chatContainer.appendChild(div);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

clearBtn.addEventListener('click', async () => {
    await fetch('/clear', { method: 'POST' });
    chatContainer.innerHTML = '';
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

                // YAML을 키-값 쌍으로 파싱
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
