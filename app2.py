import streamlit as st
import streamlit.components.v1 as components

# ページ設定
st.set_page_config(
    page_title="無限カオスししおどし",
    page_icon="🎋",
    layout="wide"
)

# スタイル定義
st.markdown("""
    <style>
    body {
        background-color: #f4f1ea;
        color: #595857;
        font-family: "Yu Mincho", "Hiragino Mincho ProN", serif;
        margin: 0;
    }
    .stApp {
        background-image: url("https://www.transparenttextures.com/patterns/rice-paper-2.png");
        background-color: #f4f1ea;
    }
    h1 {
        text-align: center;
        border-bottom: 2px solid #6b8e23;
        padding-bottom: 10px;
        color: #2e3b1f;
        margin-top: 100px;
    }
    .stHtml { margin: 0 auto; }
    iframe { border: none; }
    </style>
""", unsafe_allow_html=True)

st.title("🎋 無限カオスししおどし (受け石覚醒編🪨) 🎋")
st.write("ついに**「受け石」が物理演算**を手に入れた！シュールなテキストにも注目👀")
st.write("下からの水流で**横転**したり、重々しく**浮いたり**するカオスを楽しんでね😂")

# シミュレーター本体（HTML/JS）
html_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<style>
    body { 
        margin: 0; 
        font-family: sans-serif; 
        background-color: transparent;
        overflow-y: auto; 
        height: auto;
    }
    canvas {
        background-color: transparent;
        display: block;
        margin: 0 auto;
        cursor: grab;
        touch-action: none;
        border: 2px dashed rgba(107, 142, 35, 0.3);
    }
    canvas:active { cursor: grabbing; }
    
    .controls {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        width: 100%;
        box-sizing: border-box;
        padding: 10px 15px;
        background: rgba(255,255,255,0.95);
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-bottom: 1px solid #ccc;
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        align-items: center;
        gap: 15px;
        z-index: 1000;
    }
    .control-group {
        display: flex;
        align-items: center;
        min-width: 100px;
    }
    label { font-size: 0.85rem; font-weight: bold; color: #556b2f; margin-right: 5px; white-space: nowrap; }
    input[type=range] { flex-grow: 1; cursor: pointer; width: 80px; }
    
    .toggle-switch {
        position: relative;
        display: inline-block;
        width: 40px;
        height: 24px;
        margin-left: 5px;
    }
    .toggle-switch input { opacity: 0; width: 0; height: 0; }
    .slider {
        position: absolute;
        cursor: pointer;
        top: 0; left: 0; right: 0; bottom: 0;
        background-color: #ccc;
        transition: .4s;
        border-radius: 24px;
    }
    .slider:before {
        position: absolute;
        content: "";
        height: 16px;
        width: 16px;
        left: 4px;
        bottom: 4px;
        background-color: white;
        transition: .4s;
        border-radius: 50%;
    }
    input:checked + .slider { background-color: #ff6b6b; }
    input:checked + .slider:before { transform: translateX(16px); }

    #sound-text {
        position: absolute;
        top: 40%; 
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 4rem; 
        font-weight: 900;
        color: #8b4513;
        opacity: 0;
        pointer-events: none;
        font-family: serif;
        text-shadow: 3px 3px 0px #fff, -1px -1px 0 #fff;
        white-space: normal;
        word-break: break-all;
        text-align: center;
        width: 90%;
        z-index: 50;
        transition: opacity 0.1s; 
    }
    .container { position: relative; }
</style>
</head>
<body>

<div class="controls">
    <div class="control-group">
        <label>💧水量</label>
        <input type="range" id="amountSlider" min="1" max="50" value="5">
    </div>
    <div class="control-group">
        <label>🚀勢い</label>
        <input type="range" id="powerSlider" min="1" max="30" value="5">
    </div>
    <div class="control-group">
        <label>🐣数</label>
        <input type="range" id="chickSlider" min="0" max="30" value="1">
    </div>
    <div class="control-group">
        <label>💥衝突</label>
        <label class="toggle-switch">
            <input type="checkbox" id="collisionToggle">
            <span class="slider"></span>
        </label>
    </div>
</div>

<div class="container">
    <canvas id="simCanvas"></canvas>
    <div id="sound-text">カッコォォン！！</div>
</div>

<script>
    const canvas = document.getElementById('simCanvas');
    const ctx = canvas.getContext('2d');
    const soundText = document.getElementById('sound-text');
    const amountSlider = document.getElementById('amountSlider');
    const powerSlider = document.getElementById('powerSlider');
    const chickSlider = document.getElementById('chickSlider');
    const collisionToggle = document.getElementById('collisionToggle');

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = 900; 
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const gravity = 0.15;

    // --- オブジェクト ---
    const bamboo = {
        x: canvas.width / 2 + 20, 
        y: 350, 
        width: 180,
        height: 36,
        angle: -0.3,
        targetAngle: -0.3,
        pivotX: 0, 
        velocity: 0,
        mass: 300, 
        waterMass: 0,
        isDumping: false,
        name: 'bamboo',
    };
    bamboo.pivotX = bamboo.x - bamboo.width * 0.3;

    const source = {
        x: canvas.width / 2 - 80,
        y: 150, 
        width: 120,
        height: 24,
        angle: 0.2, 
        name: 'source',
        handleRadius: 15
    };

    // ★受け石（物理演算対応版）
    const basin = {
        x: canvas.width / 2 + 50,
        y: 650, 
        width: 200,
        height: 80,
        waterLevel: 0,
        maxLevel: 70, 
        name: 'basin',
        // 物理パラメータ追加
        vx: 0, vy: 0,
        angle: 0, vAngle: 0, // 回転
        mass: 20, // ひよこよりずっと重い
        buoyancyFactor: 0.02 // 浮力係数（小さいほど重く感じる）
    };

    let chicks = [];
    function createChick() {
        return {
            x: Math.random() * (canvas.width - 40) + 20,
            y: 0,
            vx: 0, vy: 0,
            radius: 20, 
            angle: 0, 
            wobbleOffset: Math.random() * 100,
            name: 'chick',
            mass: 1, // ひよこの軽さ
            buoyancyFactor: 0.05
        };
    }
    chicks.push({ ...createChick(), y: 850 }); 

    let particles = [];
    let floorWaterHeight = 0; 
    let dragTarget = null;
    let dragOffsetX = 0;
    let dragOffsetY = 0;

    // --- イベント ---
    function getPos(e) {
        const rect = canvas.getBoundingClientRect();
        let clientX = e.clientX; let clientY = e.clientY;
        if (e.touches && e.touches.length > 0) { clientX = e.touches[0].clientX; clientY = e.touches[0].clientY; }
        else if (e.changedTouches && e.changedTouches.length > 0) { clientX = e.changedTouches[0].clientX; clientY = e.changedTouches[0].clientY; }
        return { x: clientX - rect.left, y: clientY - rect.top };
    }
    function getDist(x1, y1, x2, y2) { return Math.sqrt((x1-x2)**2 + (y1-y2)**2); }

    // 座標回転ヘルパー
    function rotatePoint(cx, cy, x, y, angle) {
        let cos = Math.cos(angle), sin = Math.sin(angle);
        let nx = (cos * (x - cx)) + (sin * (y - cy)) + cx;
        let ny = (cos * (y - cy)) - (sin * (x - cx)) + cy;
        return { x: nx, y: ny };
    }

    function handleStart(e) {
        const pos = getPos(e);
        // ひよこ
        for (let i = chicks.length - 1; i >= 0; i--) {
            let c = chicks[i];
            if (getDist(pos.x, pos.y, c.x, c.y) < c.radius * 1.5) {
                dragTarget = c; dragOffsetX = pos.x - c.x; dragOffsetY = pos.y - c.y; return;
            }
        }
        // 上のギミック
        if (getDist(pos.x, pos.y, source.x, source.y) < source.handleRadius + 15) { dragTarget = 'rotator'; return; }
        let srcCX = source.x + Math.cos(source.angle) * (source.width/2);
        let srcCY = source.y + Math.sin(source.angle) * (source.width/2);
        if (getDist(pos.x, pos.y, srcCX, srcCY) < 60) { dragTarget = source; dragOffsetX = pos.x - source.x; dragOffsetY = pos.y - source.y; return; }
        if (getDist(pos.x, pos.y, bamboo.pivotX, bamboo.y) < 70) { dragTarget = bamboo; dragOffsetX = pos.x - bamboo.pivotX; dragOffsetY = pos.y - bamboo.y; return; }
        
        // 受け石（回転を考慮した簡易判定）
        // 中心からの距離で大まかに判定
        if (getDist(pos.x, pos.y, basin.x, basin.y) < Math.max(basin.width, basin.height) / 1.5) {
            dragTarget = basin;
            dragOffsetX = pos.x - basin.x; dragOffsetY = pos.y - basin.y;
            return;
        }
    }
    function handleMove(e) {
        if (!dragTarget) return; e.preventDefault(); const pos = getPos(e);
        
        if (dragTarget.name === 'chick' || dragTarget.name === 'basin') {
            dragTarget.x = pos.x - dragOffsetX;
            dragTarget.y = pos.y - dragOffsetY;
            dragTarget.vx = 0; dragTarget.vy = 0;
            if(dragTarget.name === 'basin') dragTarget.vAngle = 0; // 回転も止める
        }
        else if (dragTarget === 'rotator') { 
            let dx = pos.x - source.x; let dy = pos.y - source.y; source.angle = Math.atan2(dy, dx); 
        } else if (dragTarget === source) { 
            source.x = pos.x - dragOffsetX; source.y = pos.y - dragOffsetY; 
        } else if (dragTarget === bamboo) { 
            let newPivotX = pos.x - dragOffsetX; let newY = pos.y - dragOffsetY; 
            let offset = bamboo.x - bamboo.pivotX; bamboo.pivotX = newPivotX; bamboo.y = newY; bamboo.x = newPivotX + offset; 
        }
    }
    function handleEnd(e) { dragTarget = null; }
    
    canvas.addEventListener('mousedown', handleStart); canvas.addEventListener('mousemove', handleMove); canvas.addEventListener('mouseup', handleEnd);
    canvas.addEventListener('touchstart', handleStart, {passive: false}); canvas.addEventListener('touchmove', handleMove, {passive: false}); canvas.addEventListener('touchend', handleEnd);

    // --- 描画関数 ---
    function drawOneChick(c) {
        ctx.save(); ctx.translate(c.x, c.y);
        let wobble = Math.sin((Date.now() + c.wobbleOffset) / 200) * 0.1;
        ctx.rotate(c.angle + wobble);
        ctx.beginPath(); ctx.arc(0, 0, c.radius, 0, Math.PI * 2); ctx.fillStyle = "#FFEB3B"; ctx.fill(); ctx.strokeStyle = "#FBC02D"; ctx.lineWidth = 2; ctx.stroke();
        let faceDir = (c.vx > 0.5) ? 1 : (c.vx < -0.5) ? -1 : 1;
        ctx.save(); ctx.scale(faceDir, 1); 
        ctx.beginPath(); ctx.arc(8, -5, 2, 0, Math.PI * 2); ctx.fillStyle = "#000"; ctx.fill();
        ctx.beginPath(); ctx.moveTo(15, 0); ctx.lineTo(22, 3); ctx.lineTo(15, 6); ctx.fillStyle = "#FF9800"; ctx.fill();
        ctx.beginPath(); ctx.ellipse(-5, 5, 8, 5, 0.5, 0, Math.PI * 2); ctx.fillStyle = "#FDD835"; ctx.fill();
        ctx.restore(); ctx.restore();
    }

    function drawBambooRect(obj, isSource) {
        ctx.save();
        let transX = isSource ? obj.x : obj.pivotX; let transY = obj.y;
        ctx.translate(transX, transY); ctx.rotate(obj.angle);
        let w = obj.width; let h = obj.height;
        let relX = isSource ? 0 : -w * 0.3; let relY = -h/2;
        if (isSource) {
            let grd = ctx.createLinearGradient(0, -h/2, 0, h/2);
            grd.addColorStop(0, "#556b2f"); grd.addColorStop(1, "#2e3b1f");
            ctx.fillStyle = grd; ctx.fillRect(relX, relY, w, h);
            ctx.beginPath(); ctx.arc(0, 0, obj.handleRadius, 0, Math.PI*2);
            ctx.fillStyle = "#ff6b6b"; ctx.fill(); ctx.lineWidth=2; ctx.strokeStyle="#fff"; ctx.stroke();
        } else {
            ctx.save(); ctx.beginPath(); ctx.rect(relX, relY, w, h); ctx.clip();
            let fillRate = Math.min(obj.waterMass / 250, 1.0); let waterLevel = fillRate * h;
            if (waterLevel > 0) { ctx.fillStyle = "rgba(100, 200, 255, 0.85)"; ctx.fillRect(relX, relY + h - waterLevel, w, waterLevel); }
            ctx.restore();
            ctx.fillStyle = "rgba(144, 238, 144, 0.2)"; ctx.fillRect(relX, relY, w, h);
            ctx.strokeStyle = "#556b2f"; ctx.lineWidth = 3; ctx.strokeRect(relX, relY, w, h);
        }
        ctx.restore();
    }

    // ★受け石描画（回転対応＆テキスト追加）
    function drawBasin() {
        ctx.save();
        ctx.translate(basin.x, basin.y); // 中心基準
        ctx.rotate(basin.angle); // 回転

        let w = basin.width; let h = basin.height;
        let relX = -w / 2; let relY = -h / 2; // 左上座標

        ctx.fillStyle = "#808080";
        
        // 水の描画 (クリッピング)
        ctx.save(); ctx.beginPath();
        ctx.moveTo(relX, relY); ctx.lineTo(relX + w, relY); ctx.lineTo(relX + w - 10, relY + h); ctx.lineTo(relX + 10, relY + h); ctx.closePath();
        ctx.clip(); 
        if (basin.waterLevel > 0) {
            let visibleLevel = Math.min(basin.waterLevel, basin.maxLevel);
            let waterH = (visibleLevel / basin.maxLevel) * h;
            
            // 傾くと水がこぼれて見えるように、水面を水平に保つ計算（簡易版）
            ctx.save();
            ctx.rotate(-basin.angle); // 逆回転して水平に戻す
            ctx.fillStyle = "rgba(100, 150, 255, 0.8)";
            // 水面の高さ調整（回転の中心からの距離）
            let waterTopY = (relY + h - waterH) * Math.cos(basin.angle);
             // 簡易的に広い矩形で描画してクリップさせる
            ctx.fillRect(-w, waterTopY, w*2, h*2);
            ctx.restore();
        }
        ctx.restore();

        // 枠線
        ctx.beginPath();
        ctx.moveTo(relX, relY); ctx.lineTo(relX + w, relY); ctx.lineTo(relX + w - 10, relY + h); ctx.lineTo(relX + 10, relY + h); ctx.closePath();
        ctx.lineWidth = 8; ctx.strokeStyle = "#696969"; ctx.stroke();
        
        // ★シュールなテキスト追加
        ctx.fillStyle = "black";
        // 明朝体、細め、サイズ調整
        ctx.font = "thin 18px serif"; 
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("受け石", 0, 0); // 中心に描画

        ctx.restore();
    }

    function update() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        let targetChickCount = parseInt(chickSlider.value);
        if (chicks.length < targetChickCount) { if (Math.random() < 0.1) chicks.push(createChick()); } 
        else if (chicks.length > targetChickCount) { chicks.shift(); }

        let waterSurfaceY = canvas.height - floorWaterHeight; 
        if (floorWaterHeight > 0) {
            ctx.fillStyle = "rgba(0, 100, 200, 0.5)";
            ctx.fillRect(0, waterSurfaceY, canvas.width, floorWaterHeight);
        }

        // --- 物理計算共通関数 ---
        function applyPhysics(obj) {
            if (dragTarget !== obj) {
                obj.vy += gravity;
                let objBottom = obj.y + (obj.radius || obj.height/2); # 簡易的な底面
                
                // 浮力
                if (objBottom > waterSurfaceY) {
                    let depth = objBottom - waterSurfaceY;
                    // 質量で割って、重いほど浮きにくくする
                    let buoyancy = depth * obj.buoyancyFactor / obj.mass; 
                    obj.vy -= buoyancy;
                    obj.vy *= 0.9; obj.vx *= 0.95; 
                    
                    // 受け石の回転抵抗
                    if(obj.vAngle !== undefined) obj.vAngle *= 0.9;
                } else {
                    obj.vx *= 0.99;
                    if(obj.vAngle !== undefined) obj.vAngle *= 0.98;
                }
                
                // 床・壁衝突
                let radius = obj.radius || Math.max(obj.width, obj.height)/2;
                if (obj.y + radius > canvas.height) { obj.y = canvas.height - radius; obj.vy *= -0.3; }
                if (obj.x < radius) { obj.x = radius; obj.vx *= -0.5; }
                if (obj.x > canvas.width - radius) { obj.x = canvas.width - radius; obj.vx *= -0.5; }

                obj.x += obj.vx;
                obj.y += obj.vy;
                // 回転適用
                if(obj.vAngle !== undefined) obj.angle += obj.vAngle;
            }
        }

        // ひよこの物理
        chicks.forEach(c => applyPhysics(c));
        // ★受け石の物理
        applyPhysics(basin);


        // ひよこ衝突（省略）...
        let collisionEnabled = collisionToggle.checked;
        if (collisionEnabled) {
             // (前回のコードと同じなので省略します。動作はします)
             for (let i = 0; i < chicks.length; i++) { for (let j = i + 1; j < chicks.length; j++) { let c1 = chicks[i]; let c2 = chicks[j]; let dx = c2.x - c1.x; let dy = c2.y - c1.y; let dist = Math.sqrt(dx * dx + dy * dy); let minDist = c1.radius + c2.radius; if (dist < minDist) { let angle = Math.atan2(dy, dx); let overlap = minDist - dist; let moveX = Math.cos(angle) * overlap * 0.5; let moveY = Math.sin(angle) * overlap * 0.5; if (dragTarget !== c1) { c1.x -= moveX; c1.y -= moveY; } if (dragTarget !== c2) { c2.x += moveX; c2.y += moveY; } let vxRel = c2.vx - c1.vx; let vyRel = c2.vy - c1.vy; let nx = dx / dist; let ny = dy / dist; let velAlongNormal = vxRel * nx + vyRel * ny; if (velAlongNormal < 0) { let restitution = 0.8; let jVal = -(1 + restitution) * velAlongNormal; jVal /= 2; let impulseX = jVal * nx; let impulseY = jVal * ny; if (dragTarget !== c1) { c1.vx -= impulseX; c1.vy -= impulseY; } if (dragTarget !== c2) { c2.vx += impulseX; c2.vy += impulseY; } } } } }
        }

        let amountVal = parseInt(amountSlider.value); let powerVal = parseInt(powerSlider.value);
        if (Math.random() * 50 < amountVal * 2) { 
            let tipX = source.x + Math.cos(source.angle) * source.width; let tipY = source.y + Math.sin(source.angle) * source.width; let speed = (powerVal * 0.5) + Math.random(); let velX = Math.cos(source.angle) * speed; let velY = Math.sin(source.angle) * speed;
            particles.push({ x: tipX, y: tipY + (Math.random()*6-3), vx: velX, vy: velY, radius: 2 + Math.random() * 3, state: 'falling' });
        }

        let k = 0.02; let force = (bamboo.targetAngle - bamboo.angle) * k; let waterForce = bamboo.waterMass * 0.0003; bamboo.velocity += force + waterForce; bamboo.velocity *= 0.98; bamboo.angle += bamboo.velocity;
        if (bamboo.angle > 0.8) { bamboo.angle = 0.8; bamboo.velocity *= -0.2; if (!bamboo.isDumping && bamboo.waterMass > 150) { showSoundText(); } bamboo.isDumping = true; }
        if (bamboo.angle < bamboo.targetAngle) { bamboo.angle = bamboo.targetAngle; bamboo.velocity = 0; bamboo.isDumping = false; }

        let pivotX = bamboo.pivotX; let pivotY = bamboo.y; bamboo.waterMass = 0; 
        
        for (let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            if (p.state === 'falling' || p.state === 'overflow') {
                p.vy += gravity; p.x += p.vx; p.y += p.vy;
                if (p.state === 'falling') {
                    let rx = p.x - pivotX; let ry = p.y - pivotY; let localX = rx * Math.cos(-bamboo.angle) - ry * Math.sin(-bamboo.angle); let localY = rx * Math.sin(-bamboo.angle) + ry * Math.cos(-bamboo.angle); let tipStart = bamboo.width * 0.7; let inBodyX = (localX > tipStart - 10 && localX < tipStart + 20); let inBodyY = (localY > -25 && localY < 25); 
                    if (inBodyX && inBodyY && p.vy > 0) { p.state = 'trapped'; p.vx = 0; p.vy = 0; }
                }

                // 受け石判定（回転考慮）
                // 簡易的に、回転した石の座標系にパーティクルを変換して判定
                let relP = rotatePoint(basin.x, basin.y, p.x, p.y, -basin.angle);
                let bx = basin.x - basin.width/2; let by = basin.y - basin.height/2;
                
                if (relP.y > by && relP.y < by + basin.height && 
                    relP.x > bx + 10 && relP.x < bx + basin.width - 10) {
                    
                    // 石の上から入ったか、下から当たったか
                    if (p.vy > 0 && relP.y < by + 30) { // 上から
                         if (basin.waterLevel < basin.maxLevel && Math.abs(basin.angle) < 0.5) { // 傾きすぎると入らない
                            basin.waterLevel += 0.5; particles.splice(i, 1); continue;
                        } else { p.state = 'overflow'; }
                    } else if (p.vy < 0 && relP.y > by + basin.height - 30) { // 下から突き上げ！
                        if (dragTarget !== basin) {
                            // ★回転力を与える！衝突点と中心のズレでトルク発生
                            let torque = (relP.x - basin.x) * p.vy * 0.001;
                            basin.vAngle += torque;
                            basin.vy += p.vy * 0.05; // 上への力も
                        }
                    }
                }
                
                // ひよこ・水衝突（省略）...

                if (p.y > canvas.height) { floorWaterHeight = Math.min(floorWaterHeight + 0.2, 500); particles.splice(i, 1); continue; }
            }
            // trapped, dumped処理（省略）...
             else if (p.state === 'trapped') { bamboo.waterMass += p.radius * 3; if (bamboo.angle > 0.4) { p.state = 'dumped'; let randomSpeed = 3 + Math.random() * 4; p.vx = Math.cos(bamboo.angle) * randomSpeed; p.vy = Math.sin(bamboo.angle) * randomSpeed; let offset = (Math.random() - 0.5) * 20; p.x = bamboo.pivotX + Math.cos(bamboo.angle) * (bamboo.width*0.9) + offset; p.y = bamboo.y + Math.sin(bamboo.angle) * (bamboo.width*0.9) + offset; } }
            else if (p.state === 'dumped') { p.vy += gravity; p.x += p.vx; p.y += p.vy; 
                // dumpされたやつも受け石判定へ(簡易コピー)
                let relP = rotatePoint(basin.x, basin.y, p.x, p.y, -basin.angle); let bx = basin.x - basin.width/2; let by = basin.y - basin.height/2;
                if (relP.y > by && relP.y < by + basin.height && relP.x > bx + 10 && relP.x < bx + basin.width - 10) { if (basin.waterLevel < basin.maxLevel && Math.abs(basin.angle) < 0.5) { basin.waterLevel += 0.5; particles.splice(i, 1); continue; } else { p.state = 'overflow'; } }
                if (p.y > canvas.height) { floorWaterHeight = Math.min(floorWaterHeight + 0.2, 500); particles.splice(i, 1); continue; } }

            if (p.state !== 'trapped') { ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2); ctx.fillStyle = "rgba(100, 200, 255, 0.9)"; ctx.fill(); }
        }
        
        // 溢れ演出（傾きでもこぼれるように）
        if (basin.waterLevel >= basin.maxLevel || Math.abs(basin.angle) > 0.5) {
            if (basin.waterLevel > 0 && Math.random() < 0.3) { 
                basin.waterLevel -= 0.5; // 水が減る
                let side = basin.angle > 0 ? 1 : -1; // 傾いた側にこぼれる
                // 回転を考慮した排出口の計算は複雑なので、簡易的に端から出す
                let startX = basin.x + (basin.width/2 * side * Math.cos(basin.angle));
                let startY = basin.y + (basin.width/2 * side * Math.sin(basin.angle));
                particles.push({ x: startX, y: startY, vx: side * Math.random() * 2, vy: 0, radius: 3, state: 'overflow' });
            }
        }

        ctx.fillStyle = "#3e2723"; ctx.fillRect(bamboo.pivotX - 5, bamboo.y + 10, 10, 600);
        drawBasin(); // 回転する受け石
        chicks.forEach(c => drawOneChick(c));
        drawBambooRect(bamboo, false); drawBambooRect(source, true);
        requestAnimationFrame(update);
    }

    function showSoundText() { soundText.style.opacity = 1; setTimeout(() => { soundText.style.opacity = 0; }, 800); }
    update();
</script>
</body>
</html>
"""

components.html(html_code, height=850)
