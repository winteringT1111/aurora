// ==========================================
// 1. Drawflow 초기화 및 설정
// ==========================================
const container = document.getElementById('drawflow');
const editor = new Drawflow(container);
editor.start();
editor.editor_mode = 'edit'; // 마우스로 노드 조작 가능하게 설정

// 서버에서 넘겨받은 기존 맵 데이터가 있으면 불러오기
if (typeof INITIAL_DATA !== 'undefined' && INITIAL_DATA) {
    editor.import(INITIAL_DATA);
}

let selectedNodeId = null;

// ==========================================
// 2. 이벤트 리스너: 노드 선택 시
// ==========================================
editor.on('nodeSelected', function(id) {
    selectedNodeId = id;
    const nodeData = editor.getNodeFromId(id).data;

    console.log("노드 선택됨:", id, nodeData);

    // 1) 텍스트 & 숫자 데이터 인스펙터에 채우기
    document.getElementById('node-title').value = nodeData.title || "";
    
    const choiceTitleInput = document.getElementById('node-choice-title');
    if(choiceTitleInput) choiceTitleInput.value = nodeData.choice_title || "";

    const returnIdInput = document.getElementById('node-return-id');
    if(returnIdInput) returnIdInput.value = nodeData.return_id || "";

    document.getElementById('node-content').value = nodeData.content || "";
    document.getElementById('node-speaker').value = nodeData.speaker || "none";
    document.getElementById('node-stamina').value = nodeData.stamina || 10;
    
    const reqLuckInput = document.getElementById('node-req-luck');
    if(reqLuckInput) reqLuckInput.value = nodeData.req_luck || 0;

    const itemNameInput = document.getElementById('node-item-name');
    if(itemNameInput) itemNameInput.value = nodeData.item_name || "";

    // 발화자에 따라 캐릭터 스탠딩 업로드 칸 숨김/표시
    checkSpeaker();

    // 2) 배경 이미지 세팅
    const bgPreview = document.getElementById('bg-preview-img');
    const bgLabel = document.getElementById('bg-file-label');
    if(nodeData.bg_url) {
        bgPreview.src = nodeData.bg_url;
        bgPreview.style.display = 'block';
        bgLabel.style.display = 'none';
    } else {
        bgPreview.src = "";
        bgPreview.style.display = 'none';
        bgLabel.style.display = 'block';
    }

    // 3) 캐릭터 이미지 세팅
    const charPreview = document.getElementById('char-preview-img');
    const charLabel = document.getElementById('char-file-label');
    if(charPreview && charLabel) {
        if(nodeData.char_image) {
            charPreview.src = nodeData.char_image;
            charPreview.style.display = 'block';
            charLabel.style.display = 'none';
        } else {
            charPreview.src = "";
            charPreview.style.display = 'none';
            charLabel.style.display = 'block';
        }
    }

    // 4) 아이템 이미지 세팅
    const itemPreview = document.getElementById('item-preview-img');
    const itemLabel = document.getElementById('item-file-label');
    if(itemPreview && itemLabel) {
        if(nodeData.item_image) {
            itemPreview.src = nodeData.item_image;
            itemPreview.style.display = 'block';
            itemLabel.style.display = 'none';
        } else {
            itemPreview.src = "";
            itemPreview.style.display = 'none';
            itemLabel.style.display = 'block';
        }
    }
});

// 노드 선택 해제 시 (인스펙터 비우기)
editor.on('nodeUnselected', function() {
    selectedNodeId = null;
    document.getElementById('node-title').value = "";
    const choiceTitleInput = document.getElementById('node-choice-title');
    if(choiceTitleInput) choiceTitleInput.value = "";
    document.getElementById('node-content').value = "";
});

// ==========================================
// 3. 인스펙터 수정 -> 노드 데이터 업데이트
// ==========================================
function updateNode() {
    if(!selectedNodeId) return;

    // 데이터 읽어오기
    const title = document.getElementById('node-title').value;
    
    const choiceTitleInput = document.getElementById('node-choice-title');
    const choiceTitle = choiceTitleInput ? choiceTitleInput.value : "";

    const returnIdInput = document.getElementById('node-return-id');
    const returnIdValue = returnIdInput ? returnIdInput.value : "";

    const content = document.getElementById('node-content').value;
    const speaker = document.getElementById('node-speaker').value;
    const staminaValue = parseInt(document.getElementById('node-stamina').value) || 0;
    
    const reqLuckInput = document.getElementById('node-req-luck');
    const reqLuckValue = reqLuckInput ? parseInt(reqLuckInput.value) || 0 : 0;

    const itemNameInput = document.getElementById('node-item-name');
    const itemNameValue = itemNameInput ? itemNameInput.value : "";

    const bg_url = document.getElementById('bg-preview-img').src; 
    
    const charPreview = document.getElementById('char-preview-img');
    const char_image = charPreview ? charPreview.src : '';

    const itemPreview = document.getElementById('item-preview-img');
    const item_image = itemPreview ? itemPreview.src : '';

    // Drawflow 내부 데이터 업데이트
    editor.updateNodeDataFromId(selectedNodeId, {
        title: title,
        choice_title: choiceTitle,
        return_id: returnIdValue,
        content: content,
        speaker: speaker,
        stamina: staminaValue, 
        req_luck: reqLuckValue,
        item_name: itemNameValue,
        bg_url: bg_url.includes('data:image') ? bg_url : '', 
        char_image: char_image.includes('data:image') ? char_image : '',
        item_image: item_image.includes('data:image') ? item_image : ''
    });

    // 캔버스에 보이는 노드 디자인 업데이트 (ID 번호 표시 포함)
    const nodeElement = document.querySelector(`#node-${selectedNodeId} .drawflow_content_node`);
    if(nodeElement) {
        nodeElement.innerHTML = `
            <div class="box">
                <div class="title-box">#${selectedNodeId} ${title || '새 스크립트'}</div>
                <div class="content-preview">${content || '대사 없음...'}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                    <span style="font-size:10px; color:#b58c8c;">${itemNameValue ? '🎁' + itemNameValue : ''}</span>
                    <span style="font-size:10px; color:#8c7e6c;">⚡${staminaValue}</span>
                </div>
            </div>
        `;
    }
}

// ==========================================
// 4. 노드 추가 및 삭제
// ==========================================
function addNode() {
    const data = { 
        title: '새 스크립트', 
        choice_title: '',
        return_id: '',
        content: '', 
        speaker: 'none', 
        stamina: 10, 
        req_luck: 0,
        item_name: '',
        bg_url: '',
        char_image: '',
        item_image: ''
    };

    // 캔버스 중앙 위치 계산
    const posX = editor.canvas_x + 300;
    const posY = editor.canvas_y + 300;

    editor.addNode('script', 1, 1, posX, posY, 'script-node', data, `
        <div class="box">
            <div class="title-box">새 스크립트</div>
            <div class="content-preview">대사를 입력하세요...</div>
            <div style="font-size:10px; color:#8c7e6c; margin-top:8px; text-align:right;">⚡10</div>
        </div>
    `);
}

function deleteNode() {
    if (selectedNodeId) {
        editor.removeNodeId("node-" + selectedNodeId);
        selectedNodeId = null;
        document.getElementById('node-title').value = "";
        const choiceTitleInput = document.getElementById('node-choice-title');
        if(choiceTitleInput) choiceTitleInput.value = "";
        document.getElementById('node-content').value = "";
    } else {
        alert("삭제할 노드를 먼저 선택해주세요.");
    }
}

// ==========================================
// 5. 서버에 맵 전체 저장 (AJAX)
// ==========================================
function saveFullMap() {
    const exportData = editor.export();
    
    fetch(SAVE_URL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": CSRF_TOKEN
        },
        body: JSON.stringify({
            "map_id": CURRENT_MAP_ID,
            "content_data": exportData
        })
    })
    .then(res => res.json())
    .then(data => {
        if(data.success) alert("성공적으로 저장되었습니다!");
        else alert("에러 발생: " + data.message);
    })
    .catch(err => alert("네트워크 에러: " + err));
}

// ==========================================
// 6. 이미지 업로드 공용 함수 (배경, 캐릭터, 아이템)
// ==========================================
function handleImage(input, type) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            
            let previewImgId = 'bg-preview-img';
            let labelId = 'bg-file-label';
            
            if (type === 'char') {
                previewImgId = 'char-preview-img';
                labelId = 'char-file-label';
            } else if (type === 'item') {
                previewImgId = 'item-preview-img';
                labelId = 'item-file-label';
            }

            const preview = document.getElementById(previewImgId);
            const label = document.getElementById(labelId);

            if (preview && label) {
                preview.src = e.target.result;
                preview.style.display = 'block';
                label.style.display = 'none';
            }

            updateNode(); // 이미지 업로드 즉시 노드 데이터 반영
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// ==========================================
// 7. 발화자 선택에 따른 UI 변경
// ==========================================
function checkSpeaker() {
    const speakerSelect = document.getElementById("node-speaker");
    const charImageGroup = document.getElementById("char-image-group");

    if (!speakerSelect || !charImageGroup) return;

    if (speakerSelect.value === "none" || speakerSelect.value === "system") {
        charImageGroup.style.display = "none";
    } else {
        charImageGroup.style.display = "block";
        charImageGroup.style.animation = "fadeIn 0.3s ease-in-out";
    }
}