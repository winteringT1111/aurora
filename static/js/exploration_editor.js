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

// [공용 헬퍼 함수]
const getSafeValue = (id, defaultValue = "") => {
    const el = document.getElementById(id);
    return el ? el.value : defaultValue;
};

const setSafeValue = (id, value) => {
    const el = document.getElementById(id);
    if (el) el.value = value || (el.type === 'number' ? 0 : "");
};

// 1. 노드 선택 해제 시: 인스펙터 입력창 비우기
editor.on('nodeUnselected', function() {
    selectedNodeId = null;
    
    // 모든 입력창 초기화
    document.querySelectorAll('.inspector-body input, .inspector-body select, .inspector-body textarea').forEach(el => {
        el.value = el.type === 'number' ? 0 : "";
    });
});

// 2. 노드 선택 시: 해당 노드의 데이터를 인스펙터 입력창에 "강제 주입"
editor.on('nodeSelected', function(id) {
    selectedNodeId = id;
    const nodeData = editor.getNodeFromId(id).data;

    // 데이터 주입
    setSafeValue('node-title', nodeData.title || "새 스크립트");
    setSafeValue('node-content', nodeData.content || "");
    setSafeValue('node-speaker', nodeData.speaker || "");
    
    // 파일 이름 및 아이템 이름 텍스트 주입
    setSafeValue('node-speaker-img-name', nodeData.speaker_img_name || ""); 
    setSafeValue('node-bg-img-name', nodeData.bg_img_name || ""); 
    setSafeValue('node-item-name', nodeData.item_name || ""); // 💡 아이템 이름 주입
    
    setSafeValue('node-return-id', nodeData.return_id || "");
    setSafeValue('node-stamina', nodeData.stamina !== undefined ? nodeData.stamina : 10);

    // 진입 해금 조건 주입
    setSafeValue('node-req-stat', nodeData.req_stat || "");
    setSafeValue('node-req-operator', nodeData.req_operator || "gte");
    setSafeValue('node-req-val', nodeData.req_val || 0);
});

// ==========================================
// 2. 인스펙터 수정 -> 데이터 업데이트
// ==========================================
function updateNode() {
    if (!selectedNodeId) return;

    // 인스펙터 입력창에서 값 가져오기
    const title = getSafeValue('node-title', '새 스크립트');
    const content = getSafeValue('node-content');
    const speaker = getSafeValue('node-speaker');
    const stamina = parseInt(getSafeValue('node-stamina', '10')) || 0;
    const reqStat = getSafeValue('node-req-stat');
    const reqOp = getSafeValue('node-req-operator', 'gte'); 
    const reqVal = parseInt(getSafeValue('node-req-val', '0')) || 0;
    const itemName = getSafeValue('node-item-name'); // 💡 아이템 이름 가져오기
    const returnId = getSafeValue('node-return-id');

    // 이미지 파일명 읽어오기
    const speaker_img_name = getSafeValue('node-speaker-img-name');
    const bg_img_name = getSafeValue('node-bg-img-name');

    // 데이터 업데이트 (기존 대용량 item_image 필드는 제거)
    editor.updateNodeDataFromId(selectedNodeId, {
        title: title,
        content: content,
        speaker: speaker,
        stamina: stamina,
        req_stat: reqStat,
        req_operator: reqOp,
        req_val: reqVal,
        item_name: itemName, // 💡 이것만 있으면 play.html에서 이미지를 자동으로 찾습니다!
        return_id: returnId,
        speaker_img_name: speaker_img_name,
        bg_img_name: bg_img_name
    });

    // 💡 캔버스 노드 디자인 실시간 업데이트
    const nodeElement = document.querySelector(`#node-${selectedNodeId} .drawflow_content_node`);
    if(nodeElement) {
        let infoBadge = "";
        if(reqStat && reqVal > 0) {
            const statLabel = reqStat.replace('stat_', '').toUpperCase();
            const opLabel = (reqOp === 'gte') ? '▲' : '▼'; 
            infoBadge = `🔒 ${statLabel} ${reqVal}${opLabel}`;
        }

        // 노드 캔버스 프리뷰에 아이템 획득 표시 살짝 넣어주기
        let itemBadge = itemName ? `🎁 ${itemName}` : "";

        nodeElement.innerHTML = `
            <div class="box">
                <div class="title-box">#${selectedNodeId} ${title}</div>
                <div class="content-preview">${content.substring(0, 20)}${content.length > 20 ? '...' : ''}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                    <span style="font-size:10px; color:#b58c8c; font-weight:bold;">${infoBadge} ${itemBadge}</span>
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
        req_stat: '', req_operator: 'gte', req_val: 0, item_name: '', return_id: '',
        speaker_img_name: '', bg_img_name: ''
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
// 5. 서버 저장 기능
// ==========================================
function saveFullMap() {
    const exportData = editor.export();
    console.log("저장될 데이터:", exportData);

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
    .then(res => {
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
        console.error("Save Error Detail:", err); 
        alert("⚠️ 저장 중 보안 또는 서버 에러가 발생했습니다.");
    });
}

// 선 연결 시 출발지 배경 파일명을 목적지 배경 파일명으로 자동 복사
editor.on('connectionCreated', function(connection) {
    const outputNodeId = connection.output_id; 
    const inputNodeId = connection.input_id;   

    const outputNodeData = editor.getNodeFromId(outputNodeId).data;
    const inputNode = editor.getNodeFromId(inputNodeId);

    if (outputNodeData.bg_img_name && (!inputNode.data.bg_img_name || inputNode.data.bg_img_name === "")) {
        editor.updateNodeDataFromId(inputNodeId, {
            ...inputNode.data,
            bg_img_name: outputNodeData.bg_img_name
        });
        console.log(`➡️ ${outputNodeId}번 노드의 배경 파일명('${outputNodeData.bg_img_name}')이 ${inputNodeId}번 노드로 자동 복사되었습니다.`);
        
        if (selectedNodeId === inputNodeId) {
            setSafeValue('node-bg-img-name', outputNodeData.bg_img_name);
        }
    }
});