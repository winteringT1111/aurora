document.addEventListener('DOMContentLoaded', () => {
    const numberOfSnowflakes = 150;
    const body = document.body;

    for (let i = 0; i < numberOfSnowflakes; i++) {
        const snowflake = document.createElement('div');
        snowflake.className = 'snowflake';

        // Set the initial position and animation properties
        snowflake.style.left = `${Math.random() * 100}vw`; // Random horizontal position
        snowflake.style.animationDuration = `${Math.random() * 10 + 20}s`; // Duration of rise
        snowflake.style.animationDelay = `${Math.random() * 20}s`; // Delay for staggered effect
        snowflake.style.transform = `scale(${Math.random() * 0.5 + 0.5})`; // Random size
        snowflake.style.opacity = Math.random(); // Random opacity

        body.appendChild(snowflake);
    }

    // Fade-in effect for paragraphs
    const paragraphs = document.querySelectorAll('.intro p');
    const initialDelay = 1000; // Initial delay for the first paragraph
    paragraphs.forEach((p, index) => {
        setTimeout(() => {
            p.classList.add('show'); // Add show class to make it appear
        }, initialDelay + index * 850); // Delay for subsequent paragraphs
    });

    // 💡 수정됨: 요소가 존재하는지 먼저 확인한 후 타이머와 이벤트를 실행합니다.
    const clickableImage = document.getElementById('clickableImage');
    if (clickableImage) {
        // Set initial visibility for the clickable image
        setTimeout(() => {
            clickableImage.style.opacity = 1; // Make image visible
            clickableImage.style.transition = 'opacity 1s ease'; // Add animation
        }, 6600); // Set delay

        // Image click event
        clickableImage.addEventListener('click', () => {
            // Fade out all paragraphs
            paragraphs.forEach(p => {
                p.style.transition = 'opacity 1s ease';
                p.style.opacity = 0;
            });

            const fadeOutDuration = 600; // Fade out duration
            setTimeout(() => {
                clickableImage.style.transition = 'transform 1s ease';
                clickableImage.style.transform = 'translateY(-430px)'; // Move image up

                // Show new content
                const newContent = document.querySelector('.new-content');
                if (newContent) {
                    newContent.style.display = 'block';
                    setTimeout(() => {
                        newContent.classList.add('show');
                    }, 1000); // Show content after image moves
                }
            }, fadeOutDuration);
        });
    }

    // Timeline button click event
    const timelineButton = document.getElementById('timelineBtn');
    if (timelineButton) {
        timelineButton.addEventListener('click', () => {
            const newContent = document.querySelector('.new-content');
            const timelineContent = document.querySelector('.timeline');

            if(newContent) {
                newContent.style.transition = 'opacity 1s ease';
                newContent.style.opacity = 0;
            }

            setTimeout(() => {
                if (clickableImage) {
                    clickableImage.style.transition = 'opacity 0.5s ease'; 
                    clickableImage.style.opacity = 0;
                    clickableImage.style.display = 'none';
                }
                if (newContent) newContent.style.display = 'none';
                
                if (timelineContent) {
                    timelineContent.style.display = 'block'; 
                    timelineContent.style.opacity = 0; 
                    timelineContent.style.transition = 'opacity 1s ease'; 
                    setTimeout(() => {
                        timelineContent.style.opacity = 1; 
                    }, 10); 
                }
            }, 1000); 
        });
    }

    // Camp button click event
    const campButton = document.getElementById('campBtn');
    if (campButton) {
        campButton.addEventListener('click', () => { 
            const newContent = document.querySelector('.new-content');
            const campContent = document.querySelector('.camp');

            if(newContent) {
                newContent.style.transition = 'opacity 1s ease';
                newContent.style.opacity = 0;
            }

            setTimeout(() => {
                if (clickableImage) {
                    clickableImage.style.transition = 'opacity 0.5s ease'; 
                    clickableImage.style.opacity = 0;
                    clickableImage.style.display = 'none';
                }
                if (newContent) newContent.style.display = 'none';
                
                if (campContent) {
                    campContent.style.display = 'block'; 
                    campContent.style.opacity = 0; 
                    campContent.style.transition = 'opacity 1s ease'; 
                    setTimeout(() => {
                        campContent.style.opacity = 1; 
                    }, 10); 
                }
            }, 1000); 
        });
    }

    // 💡 수정됨: button2 이벤트들도 DOMContentLoaded 안으로 들어왔습니다.
    const timelineButton2 = document.getElementById('timelineBtn2');
    if (timelineButton2) {
        timelineButton2.addEventListener('click', () => { 
            const campContent = document.querySelector('.camp');
            const timelineContent = document.querySelector('.timeline');

            if (campContent) {
                campContent.style.transition = 'opacity 1s ease';
                campContent.style.opacity = 0;
            }

            setTimeout(() => {
                if (campContent) campContent.style.display = 'none'; 
                
                if (timelineContent) {
                    timelineContent.style.display = 'block'; 
                    timelineContent.style.opacity = 0; 
                    timelineContent.style.transition = 'opacity 1s ease'; 
                    setTimeout(() => {
                        timelineContent.style.opacity = 1; 
                    }, 10); 
                }
            }, 1000); 
        });
    }

    const campButton2 = document.getElementById('campBtn2');
    if (campButton2) {
        campButton2.addEventListener('click', () => { 
            const campContent = document.querySelector('.camp');
            const timelineContent = document.querySelector('.timeline');

            if (timelineContent) {
                timelineContent.style.transition = 'opacity 1s ease';
                timelineContent.style.opacity = 0;
            }

            setTimeout(() => {
                if (timelineContent) timelineContent.style.display = 'none'; 
                
                if (campContent) {
                    campContent.style.display = 'block'; 
                    campContent.style.opacity = 0; 
                    campContent.style.transition = 'opacity 1s ease'; 
                    setTimeout(() => {
                        campContent.style.opacity = 1; 
                    }, 10); 
                }
            }, 1000); 
        });
    }
}); // <-- 전체 DOMContentLoaded 블록이 여기서 끝납니다.    