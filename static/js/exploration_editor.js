// exploration_editor.js

// ==========================================
// 1. Drawflow 초기화 및 설정
// ==========================================
const container = document.getElementById('drawflow');
const editor = new Drawflow(container);

editor.editor_mode = 'edit'; 
editor.start();

// 서버 데이터 로드
if (typeof INITIAL_DATA !== 'undefined' && INITIAL_DATA) {
    editor.import(INITIAL_DATA);
}

let selectedNodeId = null;

// [공용 헬퍼 함수] 중복 선언 방지를 위해 단 한 번만 정의
const getSafeValue = (id, defaultValue = "") => {
    const el = document.getElementById(id);
    return el ? el.value : defaultValue;
};

const setSafeValue = (id, value) => {
    const el = document.getElementById(id);
    if (el) el.value = value || (el.type === 'number' ? 0 : "");
};

// ==========================================
// 2. 이벤트 리스너: 노드 선택 및 해제
// ==========================================
editor.on('nodeSelected', function(id) {
    selectedNodeId = id;
    const nodeData = editor.getNodeFromId(id).data;

    setSafeValue('node-title', nodeData.title);
    setSafeValue('node-content', nodeData.content);
    setSafeValue('node-speaker', nodeData.speaker || "none");
    setSafeValue('node-stamina', nodeData.stamina);
    setSafeValue('node-return-id', nodeData.return_id);
    setSafeValue('node-item-name', nodeData.item_name);
    setSafeValue('node-req-stat', nodeData.req_stat);
    setSafeValue('node-req-val', nodeData.req_val);
    
    const choiceTitleInput = document.getElementById('node-choice-title');
    if(choiceTitleInput) setSafeValue('node-choice-title', nodeData.choice_title);

    const updatePreview = (imgId, labelId, url) => {
        const img = document.getElementById(imgId);
        const label = document.getElementById(labelId);
        if (img && label) {
            if (url && url.trim() !== "" && url !== "none") {
                img.src = url;
                img.style.display = 'block';
                label.style.display = 'none';
            } else {
                img.src = "";
                img.style.display = 'none';
                label.style.display = 'block';
            }
        }
    };

    updatePreview('bg-preview-img', 'bg-file-label', nodeData.bg_url);
    updatePreview('char-preview-img', 'char-file-label', nodeData.char_image);
    updatePreview('item-preview-img', 'item-file-label', nodeData.item_image);

    if (typeof checkSpeaker === "function") checkSpeaker();
});

editor.on('nodeUnselected', function() {
    selectedNodeId = null;
    const fields = ['node-title', 'node-choice-title', 'node-content', 'node-return-id', 'node-stamina', 'node-req-val', 'node-item-name', 'node-req-stat'];
    fields.forEach(id => setSafeValue(id, ""));
});

// ==========================================
// 3. 인스펙터 수정 -> 노드 데이터 업데이트
// ==========================================
function updateNode() {
    if(!selectedNodeId) return;

    const title = getSafeValue('node-title', '새 스크립트');
    const content = getSafeValue('node-content');
    const speaker = getSafeValue('node-speaker', 'none');
    const stamina = parseInt(getSafeValue('node-stamina', '10')) || 0;
    const reqStat = getSafeValue('node-req-stat');
    const reqVal = parseInt(getSafeValue('node-req-val', '0')) || 0;
    const returnId = getSafeValue('node-return-id');
    const itemName = getSafeValue('node-item-name');

    const getSrc = (id) => {
        const img = document.getElementById(id);
        return (img && img.style.display !== 'none') ? img.src : "";
    };
    
    const bg_url = getSrc('bg-preview-img');
    const char_image = getSrc('char-preview-img');
    const item_image = getSrc('item-preview-img');

    editor.updateNodeDataFromId(selectedNodeId, {
        title: title,
        content: content,
        speaker: speaker,
        stamina: stamina,
        req_stat: reqStat,
        req_val: reqVal,
        return_id: returnId,
        item_name: itemName,
        bg_url: bg_url,
        char_image: char_image,
        item_image: item_image
    });

    const nodeElement = document.querySelector(`#node-${selectedNodeId} .drawflow_content_node`);
    if(nodeElement) {
        let infoBadge = itemName ? `🎁 ${itemName}` : "";
        if(!infoBadge && reqStat && reqVal > 0) {
            const shortStat = reqStat.substring(0, 3).toUpperCase();
            infoBadge = `🔒 ${shortStat} ${reqVal}+`;
        }

        nodeElement.innerHTML = `
            <div class="box">
                <div class="title-box">#${selectedNodeId} ${title}</div>
                <div class="content-preview">${content.substring(0, 20)}${content.length > 20 ? '...' : ''}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                    <span style="font-size:10px; color:#b58c8c;">${infoBadge}</span>
                    <span style="font-size:10px; color:#8c7e6c;">⚡${stamina}</span>
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
        title: '새 스크립트', content: '', speaker: 'none', stamina: 10, 
        req_stat: '', req_val: 0, item_name: '', bg_url: '', char_image: '', item_image: ''
    };

    const posX = editor.canvas_x + 150;
    const posY = editor.canvas_y + 150;

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
        editor.removeNodeId(selectedNodeId);
        selectedNodeId = null;
    } else {
        alert("삭제할 노드를 먼저 선택해주세요.");
    }
}

// ==========================================
// 5. 서버 저장 및 기타 기능
// ==========================================
function saveFullMap() {
    const exportData = editor.export();
    fetch(SAVE_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": CSRF_TOKEN },
        body: JSON.stringify({ "map_id": CURRENT_MAP_ID, "content_data": exportData })
    })
    .then(res => res.json())
    .then(data => {
        if(data.success) alert("저장되었습니다.");
        else alert("에러: " + data.message);
    })
    .catch(err => console.error("Save Error:", err));
}

function handleImage(input, type) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            let pId = (type==='char') ? 'char-preview-img' : (type==='item' ? 'item-preview-img' : 'bg-preview-img');
            let lId = (type==='char') ? 'char-file-label' : (type==='item' ? 'item-file-label' : 'bg-file-label');
            const p = document.getElementById(pId);
            const l = document.getElementById(lId);
            if (p && l) {
                p.src = e.target.result;
                p.style.display = 'block';
                l.style.display = 'none';
                updateNode();
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function checkSpeaker() {
    const s = document.getElementById("node-speaker");
    const g = document.getElementById("char-image-group");
    if (s && g) g.style.display = (s.value === "none" || s.value === "system") ? "none" : "block";
}