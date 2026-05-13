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
// [공용 헬퍼 함수]
const getSafeValue = (id, defaultValue = "") => {
    const el = document.getElementById(id);
    return el ? el.value : defaultValue;
};

const setSafeValue = (id, value) => {
    const el = document.getElementById(id);
    if (el) el.value = value || (el.type === 'number' ? 0 : "");
};


/// 1. 노드 선택 해제 시: 인스펙터와 모든 프리뷰를 완전히 비움
editor.on('nodeUnselected', function() {
    selectedNodeId = null;
    
    // 모든 입력창 초기화
    document.querySelectorAll('.inspector-group input, .inspector-group select, .inspector-group textarea').forEach(el => {
        el.value = el.type === 'number' ? 0 : "";
    });

    // 모든 이미지 프리뷰 숨기기
    ['bg-preview-img', 'char-preview-img', 'item-preview-img'].forEach(id => {
        const img = document.getElementById(id);
        if (img) {
            img.src = "";
            img.style.display = 'none';
        }
    });
    
    // 레이블 다시 보이기
    ['bg-file-label', 'char-file-label', 'item-file-label'].forEach(id => {
        const label = document.getElementById(id);
        if (label) label.style.display = 'block';
    });
});

// 2. 노드 선택 시: 새로운 노드의 데이터를 인스펙터에 "강제 주입"
editor.on('nodeSelected', function(id) {
    selectedNodeId = id;
    const nodeData = editor.getNodeFromId(id).data;

    // 데이터 주입 (기존 데이터가 없으면 공백으로)
    setSafeValue('node-title', nodeData.title || "새 스크립트");
    setSafeValue('node-content', nodeData.content || "");
    setSafeValue('node-speaker', nodeData.speaker || "");
    setSafeValue('node-bg-url', nodeData.bg_url || ""); // 텍스트 경로가 있다면
    setSafeValue('node-item-name', nodeData.item_name || "");
    setSafeValue('node-return-id', nodeData.return_id || "");
    setSafeValue('node-stamina', nodeData.stamina !== undefined ? nodeData.stamina : 10);

    // 아이템 이미지 프리뷰 갱신
    const itemPreview = document.getElementById('item-preview-img');
    const itemLabel = document.getElementById('item-file-label');
    if (nodeData.item_image) {
        itemPreview.src = nodeData.item_image;
        itemPreview.style.display = 'block';
        itemLabel.style.display = 'none';
    }

    // 💡 프리뷰 업데이트 함수
    const refreshPreview = (imgId, labelId, url) => {
        const img = document.getElementById(imgId);
        const label = document.getElementById(labelId);
        if (img && label) {
            if (url && url.length > 10) { // 유효한 데이터가 있을 때만
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

    refreshPreview('bg-preview-img', 'bg-file-label', nodeData.bg_url);
    refreshPreview('char-preview-img', 'char-file-label', nodeData.char_image);
    refreshPreview('item-preview-img', 'item-file-label', nodeData.item_image);

        
});

// ==========================================
// 2. 인스펙터 수정 -> 데이터 업데이트 (이미지 유실 완벽 방어)
// ==========================================
function updateNode() {
    // 1. 현재 선택된 노드가 없으면 함수를 종료하여 오작동 방지
    if (!selectedNodeId) return;

    // 2. 현재 활성화된 노드의 기존 데이터 백업
    const currentNode = editor.getNodeFromId(selectedNodeId);
    const oldData = currentNode.data;

    

    // 3. 인스펙터 입력창에서 값 가져오기
    const title = getSafeValue('node-title', '새 스크립트');
    const content = getSafeValue('node-content');
    const speaker = getSafeValue('node-speaker');
    const stamina = parseInt(getSafeValue('node-stamina', '10')) || 0;
    const reqStat = getSafeValue('node-req-stat');
    const reqOp = getSafeValue('node-req-operator', 'gte'); // 기본값 '이상'
    const reqVal = parseInt(getSafeValue('node-req-val', '0')) || 0;
    const itemName = getSafeValue('node-item-name');
    
    
    // 💡 [핵심] 귀환 노드 ID 가져오기
    // 특정 노드에서만 수정되어야 하므로, 공통 ID인 'node-return-id'의 값을 정확히 이 노드에만 할당합니다.
    const returnId = getSafeValue('node-return-id');

    // 4. 이미지 유지 로직 (이전과 동일)
    const getFinalImg = (imgId, dataKey) => {
        const imgEl = document.getElementById(imgId);
        if (imgEl && imgEl.style.display !== 'none' && imgEl.src.startsWith('data:image')) {
            return imgEl.src;
        }
        return oldData[dataKey] || "";
    };

    const bg_url = getFinalImg('bg-preview-img', 'bg_url');
    const char_image = getFinalImg('char-preview-img', 'char_image');
    const item_image = getFinalImg('item-preview-img', 'item_image');

    // 5. 선택된 해당 노드 ID(selectedNodeId)의 데이터만 업데이트
    editor.updateNodeDataFromId(selectedNodeId, {
        title: title,
        content: content,
        speaker: speaker,
        stamina: stamina,
        req_stat: reqStat,
        req_operator: reqOp,
        req_val: reqVal,
        bg_url: bg_url,
        char_image: char_image,
        item_image: item_image,
        item_name: itemName,
        stamina: stamina,
        return_id: returnId // 💡 이 노드에만 저장됨
    });

    // 💡 캔버스 노드 디자인 실시간 업데이트
    const nodeElement = document.querySelector(`#node-${selectedNodeId} .drawflow_content_node`);
    if(nodeElement) {
        let infoBadge = "";
        if(reqStat && reqVal > 0) {
            const statLabel = reqStat.replace('stat_', '').toUpperCase();
            const opLabel = (reqOp === 'gte') ? '▲' : '▼'; // 이상/미만 아이콘
            infoBadge = `🔒 ${statLabel} ${reqVal}${opLabel}`;
        }

        nodeElement.innerHTML = `
            <div class="box">
                <div class="title-box">#${selectedNodeId} ${title}</div>
                <div class="content-preview">${content.substring(0, 20)}${content.length > 20 ? '...' : ''}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                    <span style="font-size:10px; color:#b58c8c; font-weight:bold;">${infoBadge}</span>
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
// exploration_editor.js 의 saveFullMap 함수 수정
function saveFullMap() {
    const exportData = editor.export();
    console.log("저장될 데이터:", exportData);

    fetch(SAVE_URL, {
        method: "POST",
        headers: { 
            "Content-Type": "application/json", 
            "X-CSRFToken": CSRF_TOKEN  // CSRF 토큰 확인 필수
        },
        body: JSON.stringify({ 
            "map_id": CURRENT_MAP_ID, 
            "content_data": exportData 
        })
    })
    .then(res => {
        // 💡 403이나 500 에러 발생 시 HTML 응답을 미리 처리
        if (!res.ok) {
            return res.text().then(text => { throw new Error(text) });
        }
        return res.json();
    })
    .then(data => {
        if(data.success) alert("✅ 저장되었습니다!");
        else alert("❌ 실패: " + data.message);
    })
    .catch(err => {
        console.error("Save Error Detail:", err); // 여기서 실제 HTML 에러 페이지를 확인 가능
        alert("⚠️ 저장 중 보안 또는 서버 에러가 발생했습니다.");
    });
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
                
                // 💡 중요: 이미지가 바뀌자마자 현재 선택된 노드의 데이터를 갱신합니다.
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


// exploration_editor.js 하단에 추가

editor.on('connectionCreated', function(connection) {
    const outputNodeId = connection.output_id; // 선이 시작되는 노드
    const inputNodeId = connection.input_id;   // 선이 닿는 노드

    const outputNodeData = editor.getNodeFromId(outputNodeId).data;
    const inputNode = editor.getNodeFromId(inputNodeId);

    // 💡 출발 노드에 배경이 있고, 도착 노드에 아직 배경이 없다면 자동 복사
    if (outputNodeData.bg_url && (!inputNode.data.bg_url || inputNode.data.bg_url === "")) {
        editor.updateNodeDataFromId(inputNodeId, {
            ...inputNode.data,
            bg_url: outputNodeData.bg_url
        });
        console.log(`${inputNodeId}번 노드에 배경 이미지가 자동 복사되었습니다.`);
    }
});