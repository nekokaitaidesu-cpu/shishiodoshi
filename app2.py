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
    }
    iframe { border: none; }
    </style>
""", unsafe_allow_html=True)

st.title("🎋 無限カオスししおどし (スマホ最適化Ver) 🎋")
st.write("受け口を**上向きに開いた形**に変更！")
st.write("スマホでも「カッコォォン！！」が**折り返してド迫力表示**されるよ！🍄")

# シミュレーター本体（HTML/JS）
html_code = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; overflow: hidden; font-family: sans-serif; }
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
        position: fixed;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        padding: 10px 20px;
        background: rgba(255,255,255,0.9);
        border-radius: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        display: flex;
        gap: 20px;
        z-index: 100;
        width: 90%;
        max-width: 400px;
        flex-wrap: wrap;
    }
    .control-group {
        display: flex;
        align-items: center;
        flex-grow: 1;
    }
    label { font-size: 0.8rem; font-weight: bold; color: #556b2f; margin-right: 5px; white-space: nowrap; }
    input[type=range] { flex-grow: 1; cursor: pointer; }

    /* --- カコーン！テキストのスタイル修正 --- */
    #sound-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%); /* 画面中央に固定 */
        
        font-size: 4rem; /* サイズはそのままデカく！ */
        font-weight: 900;
        color: #8b4513;
        opacity: 0;
        pointer-events: none;
        font-family: serif;
        text-shadow: 3px 3px 0px #fff, -1px -1px 0 #fff;
        
        /* ★スマホ対応：折り返し設定 */
        white-space: normal; /* 折り返しを許可 */
        word-break: break-all; /* 単語の途中でも強制的に折り返す */
        text-align: center; /* 中央揃え */
        width: 90%; /* 画面幅いっぱいまで使う */
        
        z-index: 50;
        transition: opacity 0.1s, transform 1s; /* アニメーション調整 */
    }
</style>
</head>
<body>

<div class="container">
    <canvas id="simCanvas"></canvas>
    <div id="sound-text">カッコォォン！！</div>
    
    <div class="controls">
        <div class="control-group">
            <label>💧水量</label>
            <input type="range" id="amountSlider" min="1" max="50" value="5">
        </div>
        <div class="control-group">
            <label>🚀勢い</label>
            <input type="range" id="powerSlider" min="1" max="30" value="5">
        </div>
    </div>
</div>

<script>
    const canvas = document.getElementById('simCanvas');
    const ctx = canvas.getContext('2d');
    const soundText = document.getElementById('sound-text');
    const amountSlider = document.getElementById('amountSlider');
    const powerSlider = document.getElementById('powerSlider');

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = 1200;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const gravity = 0.15;

    const bamboo = {
        x: canvas.width / 2 + 20, 
        y: 400,
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
        funnelSize: 70 // 少し大きくした
    };
    bamboo.pivotX = bamboo.x - bamboo.width * 0.3;

    const source = {
        x: canvas.width / 2 - 80,
        y: 200,
        width: 120,
        height: 24,
        angle: 0.2, 
        name: 'source',
        handleRadius: 15
    };

    let particles = [];
    let dragTarget = null;
    let dragOffsetX = 0;
    let dragOffsetY = 0;

    // --- イベント (省略) ---
    function getPos(e) {
        const rect = canvas.getBoundingClientRect();
        let clientX = e.clientX; let clientY = e.clientY;
        if (e.touches && e.touches.length > 0) { clientX = e.touches[0].clientX; clientY = e.touches[0].clientY; }
        else if (e.changedTouches && e.changedTouches.length > 0) { clientX = e.changedTouches[0].clientX; clientY = e.changedTouches[0].clientY; }
        return { x: clientX - rect.left, y: clientY - rect.top };
    }
    function getDist(x1, y1, x2, y2) { return Math.sqrt((x1-x2)**2 + (y1-y2)**2); }

    function handleStart(e) {
        const pos = getPos(e);
        if (getDist(pos.x, pos.y, source.x, source.y) < source.handleRadius + 15) { dragTarget = 'rotator'; return; }
        let srcCX = source.x + Math.cos(source.angle) * (source.width/2);
        let srcCY = source.y + Math.sin(source.angle) * (source.width/2);
        if (getDist(pos.x, pos.y, srcCX, srcCY) < 60) { dragTarget = source; dragOffsetX = pos.x - source.x; dragOffsetY = pos.y - source.y; return; }
        if (getDist(pos.x, pos.y, bamboo.pivotX, bamboo.y) < 70) { dragTarget = bamboo; dragOffsetX = pos.x - bamboo.pivotX; dragOffsetY = pos.y - bamboo.y; return; }
    }
    function handleMove(e) {
        if (!dragTarget) return; e.preventDefault(); const pos = getPos(e);
        if (dragTarget === 'rotator') { let dx = pos.x - source.x; let dy = pos.y - source.y; source.angle = Math.atan2(dy, dx); }
        else if (dragTarget === source) { source.x = pos.x - dragOffsetX; source.y = pos.y - dragOffsetY; }
        else if (dragTarget === bamboo) { let newPivotX = pos.x - dragOffsetX; let newY = pos.y - dragOffsetY; let offset = bamboo.x - bamboo.pivotX; bamboo.pivotX = newPivotX; bamboo.y = newY; bamboo.x = newPivotX + offset; }
    }
    function handleEnd(e) { dragTarget = null; }
    canvas.addEventListener('mousedown', handleStart); canvas.addEventListener('mousemove', handleMove); canvas.addEventListener('mouseup', handleEnd);
    canvas.addEventListener('touchstart', handleStart, {passive: false}); canvas.addEventListener('touchmove', handleMove, {passive: false}); canvas.addEventListener('touchend', handleEnd);

    // --- 描画関数 ---
    function drawBambooRect(obj, isSource) {
        ctx.save();
        let transX = isSource ? obj.x : obj.pivotX; let transY = obj.y;
        ctx.translate(transX, transY); ctx.rotate(obj.angle);
        let w = obj.width; let h = obj.height;
        let relX = isSource ? 0 : -w * 0.3; let relY = -h/2;

        if (isSource) {
            // 上の竹
            let grd = ctx.createLinearGradient(0, -h/2, 0, h/2);
            grd.addColorStop(0, "#556b2f"); grd.addColorStop(1, "#2e3b1f");
            ctx.fillStyle = grd; ctx.fillRect(relX, relY, w, h);
            ctx.beginPath(); ctx.arc(0, 0, obj.handleRadius, 0, Math.PI*2);
            ctx.fillStyle = "#ff6b6b"; ctx.fill(); ctx.lineWidth=2; ctx.strokeStyle="#fff"; ctx.stroke();
        } else {
            // --- 下の竹（改造Ver 3.0）---
            
            // ★1. 受け口の形状変更（上向きに開く）
            ctx.beginPath();
            ctx.moveTo(relX + w, relY); // 竹の右上
            // 斜め上へ広がる頂点 (Yをマイナスに)
            ctx.lineTo(relX + w + obj.funnelSize, relY - 25); 
            // 下側は竹の延長線上 (Yはそのまま)
            ctx.lineTo(relX + w + obj.funnelSize, relY + h); 
            ctx.lineTo(relX + w, relY + h); // 竹の右下
            ctx.closePath();
            
            ctx.fillStyle = "rgba(50, 205, 50, 0.4)"; ctx.fill();
            ctx.strokeStyle = "#32cd32"; ctx.stroke();

            // 水の描画
            ctx.save(); ctx.beginPath(); ctx.rect(relX, relY, w, h); ctx.clip();
            let fillRate = Math.min(obj.waterMass / 250, 1.0); let waterLevel = fillRate * h;
            if (waterLevel > 0) { ctx.fillStyle = "rgba(100, 200, 255, 0.85)"; ctx.fillRect(relX, relY + h - waterLevel, w, waterLevel); }
            ctx.restore();

            // 竹本体
            ctx.fillStyle = "rgba(144, 238, 144, 0.2)"; ctx.fillRect(relX, relY, w, h);
            ctx.strokeStyle = "#556b2f"; ctx.lineWidth = 3; ctx.strokeRect(relX, relY, w, h);
        }
        ctx.restore();
    }

    function update() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        let amountVal = parseInt(amountSlider.value); let powerVal = parseInt(powerSlider.value);

        // --- 1. 水の生成 ---
        if (Math.random() * 50 < amountVal * 2) { 
            let tipX = source.x + Math.cos(source.angle) * source.width;
            let tipY = source.y + Math.sin(source.angle) * source.width;
            let speed = (powerVal * 0.5) + Math.random(); 
            let velX = Math.cos(source.angle) * speed; let velY = Math.sin(source.angle) * speed;
            particles.push({ x: tipX, y: tipY + (Math.random()*6-3), vx: velX, vy: velY, radius: 2 + Math.random() * 3, state: 'falling' });
        }

        // --- 2. 竹の物理計算 ---
        let k = 0.02; let force = (bamboo.targetAngle - bamboo.angle) * k;
        let waterForce = bamboo.waterMass * 0.0003; 
        bamboo.velocity += force + waterForce; bamboo.velocity *= 0.98; bamboo.angle += bamboo.velocity;

        if (bamboo.angle > 0.8) {
            bamboo.angle = 0.8; bamboo.velocity *= -0.2; 
            if (!bamboo.isDumping && bamboo.waterMass > 150) { showSoundText(); }
            bamboo.isDumping = true;
        }
        if (bamboo.angle < bamboo.targetAngle) { bamboo.angle = bamboo.targetAngle; bamboo.velocity = 0; bamboo.isDumping = false; }

        // --- 3. 当たり判定 ---
        let pivotX = bamboo.pivotX; let pivotY = bamboo.y;
        bamboo.waterMass = 0; 
        for (let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            if (p.state === 'falling') {
                p.vy += gravity; p.x += p.vx; p.y += p.vy;
                let rx = p.x - pivotX; let ry = p.y - pivotY;
                let localX = rx * Math.cos(-bamboo.angle) - ry * Math.sin(-bamboo.angle);
                let localY = rx * Math.sin(-bamboo.angle) + ry * Math.cos(-bamboo.angle);

                let tipStart = bamboo.width * 0.7; 
                let funnelEnd = tipStart + bamboo.funnelSize + 10;
                
                // ★判定エリア調整：上向きに開いたので、Yの許容範囲を上にずらす
                let inFunnelX = (localX > tipStart && localX < funnelEnd);
                // 下は狭く(-20)、上は広く(80)して、上からの水を受けやすく
                let inFunnelY = (localY > -80 && localY < 20); 
                
                let trapped = false;
                if (inFunnelX && inFunnelY) trapped = true;

                if (trapped && p.vy > 0) { p.state = 'trapped'; p.vx = 0; p.vy = 0; }
                if (p.y > canvas.height) { particles.splice(i, 1); continue; }
            }
            else if (p.state === 'trapped') {
                bamboo.waterMass += p.radius * 3;
                if (bamboo.angle > 0.4) {
                    p.state = 'dumped'; p.vx = Math.cos(bamboo.angle) * 5; p.vy = Math.sin(bamboo.angle) * 5;
                    p.x = bamboo.pivotX + Math.cos(bamboo.angle) * (bamboo.width*0.9);
                    p.y = bamboo.y + Math.sin(bamboo.angle) * (bamboo.width*0.9);
                }
            }
            else if (p.state === 'dumped') {
                p.vy += gravity; p.x += p.vx; p.y += p.vy;
                if (p.y > canvas.height) { particles.splice(i, 1); continue; }
            }
            if (p.state !== 'trapped') { ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2); ctx.fillStyle = "rgba(100, 200, 255, 0.9)"; ctx.fill(); }
        }

        // --- 4. 描画 ---
        ctx.fillStyle = "#3e2723"; ctx.fillRect(bamboo.pivotX - 5, bamboo.y + 10, 10, 400);
        drawBambooRect(bamboo, false); drawBambooRect(source, true);
        
        // ★竹への追従はオフにする（CSSで中央固定）
        // if(soundText.style.opacity > 0) { ... } 

        requestAnimationFrame(update);
    }

    function showSoundText() {
        soundText.style.opacity = 1;
        // アニメーションも少し派手に
        soundText.style.transform = "translate(-50%, -50%) scale(1.2) rotate(-5deg)";
        setTimeout(() => {
            soundText.style.opacity = 0;
            soundText.style.transform = "translate(-50%, -50%) scale(1.0) rotate(0deg)";
        }, 1200);
    }

    update();
</script>
</body>
</html>
"""

components.html(html_code, height=1250)
