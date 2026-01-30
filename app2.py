import streamlit as st
import streamlit.components.v1 as components

# ページ設定
st.set_page_config(
    page_title="無限カオスししおどし",
    page_icon="🎋",
    layout="wide" # 横幅も広く使えるように
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
    /* iframeの枠を消す */
    iframe { border: none; }
    </style>
""", unsafe_allow_html=True)

st.title("🎋 無限カオスししおどし (縦長Ver) 🎋")
st.write("受け口を**△**にして、判定バグを修正！")
st.write("さらに画面を**縦にどーんと伸ばした**から、スマホでも広々置けるよ！🍄")

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
        touch-action: none; /* スクロールはCanvas外でやってもらう */
        border: 2px dashed rgba(107, 142, 35, 0.3); /* エリアが見えるように薄い枠 */
    }
    canvas:active { cursor: grabbing; }
    
    /* コントロールパネルを固定配置に変更 */
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

    #sound-text {
        position: absolute;
        /* 文字の位置はJSで制御 */
        font-size: 4rem;
        font-weight: 900;
        color: #8b4513;
        opacity: 0;
        pointer-events: none;
        font-family: serif;
        text-shadow: 3px 3px 0px #fff, -1px -1px 0 #fff;
        white-space: nowrap;
        z-index: 50;
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

    // 画面サイズに合わせてキャンバス幅を設定
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = 1200; // ★縦長設定！
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const gravity = 0.15;

    // --- パラメータ ---
    const bamboo = {
        x: canvas.width / 2 + 20, 
        y: 400, // 少し上に配置
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
        funnelSize: 60 
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

    // --- イベント (タッチ操作・ドラッグ) ---
    function getPos(e) {
        const rect = canvas.getBoundingClientRect();
        let clientX = e.clientX;
        let clientY = e.clientY;
        if (e.touches && e.touches.length > 0) {
            clientX = e.touches[0].clientX;
            clientY = e.touches[0].clientY;
        } else if (e.changedTouches && e.changedTouches.length > 0) {
             clientX = e.changedTouches[0].clientX;
             clientY = e.changedTouches[0].clientY;
        }
        return { x: clientX - rect.left, y: clientY - rect.top };
    }
    function getDist(x1, y1, x2, y2) { return Math.sqrt((x1-x2)**2 + (y1-y2)**2); }

    function handleStart(e) {
        const pos = getPos(e);
        // 上の竹
        if (getDist(pos.x, pos.y, source.x, source.y) < source.handleRadius + 15) {
            dragTarget = 'rotator'; return;
        }
        let srcCX = source.x + Math.cos(source.angle) * (source.width/2);
        let srcCY = source.y + Math.sin(source.angle) * (source.width/2);
        if (getDist(pos.x, pos.y, srcCX, srcCY) < 60) {
            dragTarget = source;
            dragOffsetX = pos.x - source.x; dragOffsetY = pos.y - source.y; return;
        }
        // 下の竹
        if (getDist(pos.x, pos.y, bamboo.pivotX, bamboo.y) < 70) {
            dragTarget = bamboo;
            dragOffsetX = pos.x - bamboo.pivotX; dragOffsetY = pos.y - bamboo.y; return;
        }
    }
    
    function handleMove(e) {
        if (!dragTarget) return;
        e.preventDefault(); // キャンバス内の操作中はスクロール防止
        const pos = getPos(e);
        
        if (dragTarget === 'rotator') {
            let dx = pos.x - source.x; let dy = pos.y - source.y;
            source.angle = Math.atan2(dy, dx);
        } else if (dragTarget === source) {
            source.x = pos.x - dragOffsetX; source.y = pos.y - dragOffsetY;
        } else if (dragTarget === bamboo) {
            let newPivotX = pos.x - dragOffsetX; let newY = pos.y - dragOffsetY;
            let offset = bamboo.x - bamboo.pivotX;
            bamboo.pivotX = newPivotX; bamboo.y = newY; bamboo.x = newPivotX + offset;
        }
    }
    function handleEnd(e) { dragTarget = null; }
    
    canvas.addEventListener('mousedown', handleStart);
    canvas.addEventListener('mousemove', handleMove);
    canvas.addEventListener('mouseup', handleEnd);
    canvas.addEventListener('touchstart', handleStart, {passive: false});
    canvas.addEventListener('touchmove', handleMove, {passive: false});
    canvas.addEventListener('touchend', handleEnd);

    // --- 描画関数 ---
    function drawBambooRect(obj, isSource) {
        ctx.save();
        let transX = isSource ? obj.x : obj.pivotX;
        let transY = obj.y;
        ctx.translate(transX, transY);
        ctx.rotate(obj.angle);
        
        let w = obj.width;
        let h = obj.height;
        let relX = isSource ? 0 : -w * 0.3; 
        let relY = -h/2;

        if (isSource) {
            // 上の竹
            let grd = ctx.createLinearGradient(0, -h/2, 0, h/2);
            grd.addColorStop(0, "#556b2f"); grd.addColorStop(1, "#2e3b1f");
            ctx.fillStyle = grd;
            ctx.fillRect(relX, relY, w, h);
            
            // 回転ハンドル
            ctx.beginPath(); ctx.arc(0, 0, obj.handleRadius, 0, Math.PI*2);
            ctx.fillStyle = "#ff6b6b"; ctx.fill(); 
            ctx.lineWidth=2; ctx.strokeStyle="#fff"; ctx.stroke();
        } else {
            // --- 下の竹（改造Ver 2.0）---
            
            // ★2. 受け口を「三角形」に変更
            ctx.beginPath();
            ctx.moveTo(relX + w, relY); // 竹の上端
            ctx.lineTo(relX + w + obj.funnelSize, relY - 10); // 三角の頂点（外側・上）
            // 三角形の形にするため、下側も同じ頂点に向かうか、あるいは底辺を広くするか
            // 主さんの絵のイメージ：竹の断面全体から広がってキャッチする感じ
            ctx.lineTo(relX + w, relY + h); // 竹の下端
            ctx.closePath();
            
            // ファンネル着色
            ctx.fillStyle = "rgba(50, 205, 50, 0.4)"; 
            ctx.fill();
            ctx.strokeStyle = "#32cd32";
            ctx.stroke();

            // 水の描画
            ctx.save();
            ctx.beginPath();
            ctx.rect(relX, relY, w, h); 
            ctx.clip();
            
            let fillRate = Math.min(obj.waterMass / 250, 1.0);
            let waterLevel = fillRate * h;
            
            if (waterLevel > 0) {
                ctx.fillStyle = "rgba(100, 200, 255, 0.85)";
                ctx.fillRect(relX, relY + h - waterLevel, w, waterLevel);
            }
            ctx.restore();

            // 竹本体
            ctx.fillStyle = "rgba(144, 238, 144, 0.2)";
            ctx.fillRect(relX, relY, w, h);
            ctx.strokeStyle = "#556b2f"; ctx.lineWidth = 3;
            ctx.strokeRect(relX, relY, w, h);
        }
        ctx.restore();
    }

    function update() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        let amountVal = parseInt(amountSlider.value);
        let powerVal = parseInt(powerSlider.value);

        // --- 1. 水の生成 ---
        if (Math.random() * 50 < amountVal * 2) { 
            let tipX = source.x + Math.cos(source.angle) * source.width;
            let tipY = source.y + Math.sin(source.angle) * source.width;
            let speed = (powerVal * 0.5) + Math.random(); 
            let velX = Math.cos(source.angle) * speed;
            let velY = Math.sin(source.angle) * speed;

            particles.push({
                x: tipX, y: tipY + (Math.random()*6-3),
                vx: velX, vy: velY,
                radius: 2 + Math.random() * 3,
                state: 'falling'
            });
        }

        // --- 2. 竹の物理計算 ---
        let k = 0.02; 
        let force = (bamboo.targetAngle - bamboo.angle) * k;
        let waterForce = bamboo.waterMass * 0.0003; 
        
        bamboo.velocity += force + waterForce;
        bamboo.velocity *= 0.98; 
        bamboo.angle += bamboo.velocity;

        if (bamboo.angle > 0.8) {
            bamboo.angle = 0.8;
            bamboo.velocity *= -0.2; 
            if (!bamboo.isDumping && bamboo.waterMass > 150) {
                 showSoundText();
            }
            bamboo.isDumping = true;
        }
        if (bamboo.angle < bamboo.targetAngle) {
            bamboo.angle = bamboo.targetAngle;
            bamboo.velocity = 0; 
            bamboo.isDumping = false;
        }

        // --- 3. 当たり判定（修正版） ---
        let bambooVecX = Math.cos(bamboo.angle);
        let bambooVecY = Math.sin(bamboo.angle);
        let pivotX = bamboo.pivotX;
        let pivotY = bamboo.y;

        bamboo.waterMass = 0; 

        for (let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            
            if (p.state === 'falling') {
                p.vy += gravity; p.x += p.vx; p.y += p.vy;
                
                // ローカル座標変換
                let rx = p.x - pivotX;
                let ry = p.y - pivotY;
                let localX = rx * Math.cos(-bamboo.angle) - ry * Math.sin(-bamboo.angle);
                let localY = rx * Math.sin(-bamboo.angle) + ry * Math.cos(-bamboo.angle);

                // ★判定エリアの修正
                // 1. 竹の本体エリア
                // 2. 三角ファンネルエリア
                
                // 竹の右端
                let tipStart = bamboo.width * 0.7; // (-0.3 + 1.0)
                let funnelEnd = tipStart + bamboo.funnelSize + 10;
                
                // ★バグ修正：角度制限を撤廃！
                // 単純に「ファンネルの範囲内にあり」かつ「縦位置（localY）が許容範囲」なら入る
                
                let inFunnelX = (localX > tipStart && localX < funnelEnd);
                // 三角形なので、先に行くほど許容Yを広くする...といきたいけど
                // まずは「ガバガバ」にするため、広めの長方形判定にしちゃう（吸い込み重視）
                let inFunnelY = (localY > -50 && localY < 50); 
                
                // 本体に入ってるか
                let inBodyX = (localX > 0 && localX <= tipStart);
                let inBodyY = (localY > -15 && localY < 15);

                // どちらかに入っていればOK
                let trapped = false;
                if (inFunnelX && inFunnelY) trapped = true;
                // 本体判定は厳密にしないと、下から抜けたやつが入っちゃうので注意
                // 今回はファンネルメインで吸う

                if (trapped && p.vy > 0) { // ★角度チェック(bamboo.angle < 0)を削除！
                     p.state = 'trapped';
                     p.vx = 0; p.vy = 0;
                }
                
                if (p.y > canvas.height) { particles.splice(i, 1); continue; }
            }
            else if (p.state === 'trapped') {
                bamboo.waterMass += p.radius * 3;
                if (bamboo.angle > 0.4) {
                    p.state = 'dumped';
                    p.vx = Math.cos(bamboo.angle) * 5; 
                    p.vy = Math.sin(bamboo.angle) * 5;
                    p.x = bamboo.pivotX + Math.cos(bamboo.angle) * (bamboo.width*0.9);
                    p.y = bamboo.y + Math.sin(bamboo.angle) * (bamboo.width*0.9);
                }
            }
            else if (p.state === 'dumped') {
                p.vy += gravity; p.x += p.vx; p.y += p.vy;
                if (p.y > canvas.height) { particles.splice(i, 1); continue; }
            }
            
            if (p.state !== 'trapped') {
                ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = "rgba(100, 200, 255, 0.9)"; ctx.fill();
            }
        }

        // --- 4. 描画 ---
        // 支柱
        ctx.fillStyle = "#3e2723";
        ctx.fillRect(bamboo.pivotX - 5, bamboo.y + 10, 10, 400); // 支柱も長く

        drawBambooRect(bamboo, false);
        drawBambooRect(source, true);
        
        // カコーンテキストの位置を竹に追従させる
        if(soundText.style.opacity > 0) {
             soundText.style.left = (bamboo.x + 100) + 'px';
             soundText.style.top = (bamboo.y - 50) + 'px';
        }

        requestAnimationFrame(update);
    }

    function showSoundText() {
        soundText.style.opacity = 1;
        soundText.style.transform = "scale(1.5)";
        setTimeout(() => {
            soundText.style.opacity = 0;
            soundText.style.transform = "scale(1.0)";
        }, 1000);
    }

    update();
</script>
</body>
</html>
"""

# 高さをガツンと確保！
components.html(html_code, height=1250)
