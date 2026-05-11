document.addEventListener('DOMContentLoaded', () => {
        const audio = document.getElementById('background-music');
        const playPauseButton = document.getElementById('play-pause-button');
        const status = document.getElementById('status');
        const toStart = document.getElementById('to-start-button');
    
        let isPlaying = false;

        // 페이지 로드 시 저장된 오디오 상태 불러오기
        const loadAudioState = () => {
            const savedTime = localStorage.getItem('audio-currentTime');
            const savedIsPlaying = localStorage.getItem('audio-isPlaying');
            if (savedTime) {
                audio.currentTime = parseFloat(savedTime);
            }
            if (savedIsPlaying === 'true') {
                playAudio();
            }
        };

        // 오디오 상태 저장
        const saveAudioState = () => {
            localStorage.setItem('audio-currentTime', audio.currentTime);
            localStorage.setItem('audio-isPlaying', isPlaying);
        };

        // 음악 재생 함수
        const playAudio = () => {
            audio.play().then(() => {
                isPlaying = true;
                status.classList = 'fa-solid fa-pause';
            }).catch(error => {
                console.log('Auto play failed.', error);
            });
        };

        // 재생/일시정지 버튼
        playPauseButton.addEventListener('click', () => {
            if (audio.paused) {
                playAudio();
            } else {
                audio.pause();
                isPlaying = false;
                status.classList = 'fa-solid fa-play';
            }
            saveAudioState();
        });

        // 처음부터 재생 버튼
        toStart.addEventListener('click', () => {
            audio.currentTime = 0;
            if (!isPlaying) {
                playAudio();
            }
            saveAudioState();
        });

        // 오디오 진행 상태 저장
        audio.addEventListener('timeupdate', () => {
            saveAudioState();
        });

        // 페이지 로드 시 상태 복원
        loadAudioState();

        // 특수 비지엠 처리
        const userBox = document.getElementById('profile_music');
        if (userBox) {
            const musicFile = userBox.getAttribute('data-music'); 
            if (musicFile) {
                const musicSource = `{% static 'audio/' %}${musicFile}`;
                const sourceElement = audio.querySelector('source');
                sourceElement.src = musicSource;
                audio.load();
                playAudio();
            }
        }
    });