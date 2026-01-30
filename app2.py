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
        margin-top: 60px; /* スライダーとかぶらないように余白 */
    }
    iframe { border: none; }
    </style>
""", unsafe_allow_html=True)

st.title("🎋 無限カオスししおどし (修正完了Ver) 🎋")
st.write("カコーンのキレを戻して、スライダーを上に固定！")
st.write("受け口の形もリクエスト通りに整形したっち🍄")

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
    
    /* --- コントロールパネルを「上」に固定 --- */
    .controls {
        position: fixed;
        top: 10px; /* 上部に固定 */
        left: 50%;
        transform: translateX(-50%);
        padding: 8px 20px;
        background: rgba(255,255,255,0.9);
        border-radius: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        display: flex;
        gap: 15px;
        z-index: 100;
        width: 90%;
        max-width: 400px;
        flex-wrap: nowrap; /* 1行に収める */
    }
    .control-group {
        display: flex;
        align-items: center;
        flex-grow: 1;
    }
    label { font-size: 0.8rem; font-weight: bold; color: #556b2f; margin-right: 5px; white-space: nowrap; }
    input[type=range] { flex-grow: 1; cursor: pointer; }

    /* --- カコーン！テキスト（シュールVerに戻す） --- */
    #sound-text {
        position: absolute;
        top: 50%;
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
        /* アニメーション削除：パッと出てパッと消える */
        transition: opacity 0.1s; 
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
        funnelSize: 70
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
            // --- 下の竹（改造Ver 4.0）---
            
            // ★4. 受け口の形状変更（主さんの赤ペン修正版）
            // 下のラインは真っ直ぐ、上のラインだけが開く
            ctx.beginPath();
            ctx.moveTo(relX + w, relY); // 竹の右上
            ctx.lineTo(relX + w + obj.funnelSize, relY - 30); // 上に大きく開く
            ctx.lineTo(relX + w + obj.funnelSize, relY + h);  // 下は竹の太さのまま延長
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

        // --- 3. 当たり判定 & 排出処理 ---
        let pivotX = bamboo.pivotX; let pivotY = bamboo.y;
        bamboo.waterMass = 0; 
        
        // ★2. 水の排出ロジック調整（バラけさせる）
        // ランダムなオフセット用の種
        
        for (let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            
            if (p.state === 'falling') {
                p.vy += gravity; p.x += p.vx; p.y += p.vy;
                let rx = p.x - pivotX; let ry = p.y - pivotY;
                let localX = rx * Math.cos(-bamboo.angle) - ry * Math.sin(-bamboo.angle);
                let localY = rx * Math.sin(-bamboo.angle) + ry * Math.cos(-bamboo.angle);

                let tipStart = bamboo.width * 0.7; 
                let funnelEnd = tipStart + bamboo.funnelSize + 10;
                
                let inFunnelX = (localX > tipStart && localX < funnelEnd);
                let inFunnelY = (localY > -80 && localY < 20); 
                
                if (inFunnelX && inFunnelY && p.vy > 0) { p.state = 'trapped'; p.vx = 0; p.vy = 0; }
                if (p.y > canvas.height) { particles.splice(i, 1); continue; }
            }
            else if (p.state === 'trapped') {
                bamboo.waterMass += p.radius * 3;
                
                // 竹が傾いたら排出
                if (bamboo.angle > 0.4) {
                    p.state = 'dumped';
                    // 勢いを少しランダムにして「流れ」を作る
                    let randomSpeed = 3 + Math.random() * 4; 
                    p.vx = Math.cos(bamboo.angle) * randomSpeed; 
                    p.vy = Math.sin(bamboo.angle) * randomSpeed;
                    
                    // 位置も少しバラつかせる（一箇所からビームみたいに出ないように）
                    let offset = (Math.random() - 0.5) * 20;
                    p.x = bamboo.pivotX + Math.cos(bamboo.angle) * (bamboo.width*0.9) + offset;
                    p.y = bamboo.y + Math.sin(bamboo.angle) * (bamboo.width*0.9) + offset;
                }
            }
            else if (p.state === 'dumped') {
                p.vy += gravity; p.x += p.vx; p.y += p.vy;
                if (p.y > canvas.height) { particles.splice(i, 1); continue; }
            }
            
            // 描画
            if (p.state !== 'trapped') { 
                ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2); 
                ctx.fillStyle = "rgba(100, 200, 255, 0.9)"; ctx.fill(); 
            }
        }

        // --- 4. 描画 ---
        ctx.fillStyle = "#3e2723"; ctx.fillRect(bamboo.pivotX - 5, bamboo.y + 10, 10, 400);
        drawBambooRect(bamboo, false); drawBambooRect(source, true);

        requestAnimationFrame(update);
    }

    // ★1. カコーン！をシンプルに
    function showSoundText() {
        soundText.style.opacity = 1;
        // 回転や拡大などの派手なtransformを削除
        soundText.style.transform = "translate(-50%, -50%)"; 
        
        setTimeout(() => {
            soundText.style.opacity = 0;
        }, 800); // 消えるまでの時間
    }

    update();
</script>
</body>
</html>
"""

components.html(html_code, height=1250)
