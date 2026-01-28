import streamlit as st
import streamlit.components.v1 as components

# ページ設定
st.set_page_config(
    page_title="和風ししおどしシミュレーター",
    page_icon="🎋",
    layout="centered"
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
    </style>
""", unsafe_allow_html=True)

st.title("🎋 全方位ししおどし (360°回転Ver) 🎋")
st.write("上の竹の**「ピンクの丸」**を掴むと、360°自由に回転できるよ！🌀")
st.write("真上に飛ばしたり、遠投したりして遊んでみてね！🍄")

# シミュレーター本体（HTML/JS）
html_code = """
<!DOCTYPE html>
<html>
<head>
<style>
    canvas {
        background-color: transparent;
        border-radius: 8px;
        /* box-shadow: 0 4px 6px rgba(0,0,0,0.1); */
        display: block;
        margin: 0 auto;
        cursor: grab;
        touch-action: none;
    }
    canvas:active {
        cursor: grabbing;
    }
    .container {
        position: relative;
        width: 100%;
        text-align: center;
        user-select: none;
    }
    #sound-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 3rem;
        font-weight: bold;
        color: #8b4513;
        opacity: 0;
        pointer-events: none;
        font-family: serif;
        transition: opacity 0.1s;
        text-shadow: 2px 2px 0px #fff;
    }
</style>
</head>
<body>

<div class="container">
    <canvas id="simCanvas" width="600" height="550"></canvas>
    <div id="sound-text">カコーン！</div>
</div>

<script>
    const canvas = document.getElementById('simCanvas');
    const ctx = canvas.getContext('2d');
    const soundText = document.getElementById('sound-text');

    const CW = canvas.width;
    const CH = canvas.height;
    const gravity = 0.15;

    // --- 竹オブジェクト ---
    
    // 下の竹（ししおどし・クリア素材）
    const bamboo = {
        x: CW / 2 + 20, 
        y: CH / 2 + 50,
        width: 180,
        height: 36,
        angle: -0.3,
        targetAngle: -0.3,
        pivotX: 0, 
        velocity: 0,
        mass: 100,
        waterMass: 0,
        isDumping: false,
        name: 'bamboo'
    };
    bamboo.pivotX = bamboo.x - bamboo.width * 0.3;

    // 上の竹（水源）
    const source = {
        x: CW / 2 - 80,
        y: CH / 2 - 100,
        width: 120,
        height: 24,
        angle: 0.2, 
        name: 'source',
        // 回転ハンドルの位置（描画時に計算）
        handleRadius: 15
    };

    let particles = [];
    
    // ドラッグ操作用
    let dragTarget = null;     // 'source', 'bamboo', 'rotator'
    let dragOffsetX = 0;
    let dragOffsetY = 0;

    // --- イベント処理 ---
    
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
        
        // 1. 上の竹の「回転ハンドル」判定 (竹の根元にあると仮定)
        // 回転軸(source.x, source.y)付近をクリックしたら回転モード
        if (getDist(pos.x, pos.y, source.x, source.y) < source.handleRadius + 5) {
            dragTarget = 'rotator'; // 回転モード
            return;
        }

        // 2. 上の竹の「移動」判定 (竹の中心付近)
        // 簡易的に中心座標を計算して判定
        let srcCenterX = source.x + Math.cos(source.angle) * (source.width/2);
        let srcCenterY = source.y + Math.sin(source.angle) * (source.width/2);
        if (getDist(pos.x, pos.y, srcCenterX, srcCenterY) < 50) {
            dragTarget = source;
            dragOffsetX = pos.x - source.x;
            dragOffsetY = pos.y - source.y;
            return;
        }

        // 3. 下の竹の「移動」判定
        if (getDist(pos.x, pos.y, bamboo.pivotX, bamboo.y) < 60) {
            dragTarget = bamboo;
            dragOffsetX = pos.x - bamboo.pivotX;
            dragOffsetY = pos.y - bamboo.y;
            return;
        }
    }

    function handleMove(e) {
        if (!dragTarget) return;
        e.preventDefault();
        const pos = getPos(e);

        if (dragTarget === 'rotator') {
            // マウスの方向に竹を向ける
            let dx = pos.x - source.x;
            let dy = pos.y - source.y;
            source.angle = Math.atan2(dy, dx);
        }
        else if (dragTarget === source) {
            source.x = pos.x - dragOffsetX;
            source.y = pos.y - dragOffsetY;
        } 
        else if (dragTarget === bamboo) {
            let newPivotX = pos.x - dragOffsetX;
            let newY = pos.y - dragOffsetY;
            let offset = bamboo.x - bamboo.pivotX;
            bamboo.pivotX = newPivotX;
            bamboo.y = newY;
            bamboo.x = newPivotX + offset;
        }
    }
    function handleEnd(e) { dragTarget = null; }

    canvas.addEventListener('mousedown', handleStart);
    canvas.addEventListener('mousemove', handleMove);
    canvas.addEventListener('mouseup', handleEnd);
    canvas.addEventListener('mouseleave', handleEnd);
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
        let relX = isSource ? 0 : -w * 0.3; // 上の竹は回転軸(0)から右へ伸びる
        let relY = -h/2;

        if (isSource) {
            // --- 上の竹 ---
            let grd = ctx.createLinearGradient(0, -h/2, 0, h/2);
            grd.addColorStop(0, "#556b2f");
            grd.addColorStop(0.5, "#8fbc8f");
            grd.addColorStop(1, "#556b2f");
            ctx.fillStyle = grd;
            ctx.fillRect(relX, relY, w, h);
            
            // 節
            ctx.fillStyle = "#2e3b1f";
            ctx.fillRect(relX + w * 0.5, relY, 4, h);

            // ★回転ハンドルの描画 (根元の赤い丸)
            ctx.beginPath();
            ctx.arc(0, 0, obj.handleRadius, 0, Math.PI*2);
            ctx.fillStyle = "#ff6b6b"; // 目立つピンク
            ctx.fill();
            ctx.strokeStyle = "#fff";
            ctx.lineWidth = 2;
            ctx.stroke();

        } else {
            // --- 下の竹（クリアVer）---
            // 水
            ctx.save(); 
            ctx.beginPath(); ctx.rect(relX, relY, w, h); ctx.clip();
            let waterLevel = Math.min(obj.waterMass * 0.5, h * 0.9); 
            if (waterLevel > 0) {
                ctx.fillStyle = "rgba(135, 206, 250, 0.8)";
                ctx.fillRect(relX, relY + h - waterLevel, w, waterLevel);
                // 水面ライン
                ctx.beginPath(); ctx.moveTo(relX, relY + h - waterLevel);
                ctx.lineTo(relX + w, relY + h - waterLevel);
                ctx.strokeStyle = "rgba(255, 255, 255, 0.5)"; ctx.stroke();
            }
            ctx.restore();

            // 本体
            ctx.fillStyle = "rgba(144, 238, 144, 0.3)";
            ctx.fillRect(relX, relY, w, h);
            ctx.strokeStyle = "#556b2f"; ctx.lineWidth = 3;
            ctx.strokeRect(relX, relY, w, h);
            // 節
            ctx.beginPath(); ctx.moveTo(relX + w * 0.3, relY);
            ctx.lineTo(relX + w * 0.3, relY + h); ctx.stroke();
        }

        ctx.restore();
    }


    function update() {
        ctx.clearRect(0, 0, CW, CH);

        // --- 1. 水の生成 ---
        if (Math.random() * 10 < 5) { // 勢いよく
            // 竹の先端位置を計算 (回転に対応)
            let tipX = source.x + Math.cos(source.angle) * source.width;
            let tipY = source.y + Math.sin(source.angle) * source.width;
            
            // 発射速度ベクトルの計算
            let speed = 4 + Math.random();
            let velX = Math.cos(source.angle) * speed;
            let velY = Math.sin(source.angle) * speed;

            particles.push({
                x: tipX,
                y: tipY + (Math.random()*6 - 3),
                vx: velX,
                vy: velY,
                radius: 2.5 + Math.random() * 2,
                state: 'falling'
            });
        }

        // --- 2. 竹の物理計算 ---
        let force = (bamboo.targetAngle - bamboo.angle) * 0.08;
        let waterForce = bamboo.waterMass * 0.003;
        bamboo.velocity += force + waterForce;
        bamboo.velocity *= 0.94;
        bamboo.angle += bamboo.velocity;

        if (bamboo.angle > 0.7) {
            bamboo.angle = 0.7;
            bamboo.velocity *= -0.3;
            if (!bamboo.isDumping && bamboo.waterMass > 15) {
                 showSoundText();
            }
            bamboo.isDumping = true;
        }
        if (bamboo.angle < bamboo.targetAngle) {
            bamboo.angle = bamboo.targetAngle;
            bamboo.velocity = 0;
            bamboo.isDumping = false;
        }

        // 下の竹の受け口位置
        let tipOffset = bamboo.width * 0.6; 
        let tipX = bamboo.pivotX + Math.cos(bamboo.angle) * tipOffset;
        let tipY = bamboo.y + Math.sin(bamboo.angle) * tipOffset;

        // --- 3. 水粒子の更新 ---
        bamboo.waterMass = 0; 

        for (let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            
            if (p.state === 'falling') {
                p.vy += gravity; // 重力
                p.x += p.vx;
                p.y += p.vy;
                
                // 画面端バウンド（おまけ：壁で跳ね返ると面白いかも）
                // if (p.x < 0 || p.x > CW) p.vx *= -0.5;

                // 下の竹に入る判定
                let dx = p.x - tipX;
                let dy = p.y - tipY;
                let dist = Math.sqrt(dx*dx + dy*dy);
                
                // 判定
                if (dist < 30 && p.vy > 0 && bamboo.angle < 0) {
                    p.state = 'trapped';
                    p.vx = 0; p.vy = 0;
                }
                if (p.y > CH) { particles.splice(i, 1); continue; }
            }
            else if (p.state === 'trapped') {
                bamboo.waterMass += p.radius * 3;
                
                if (bamboo.angle > 0.3) {
                    p.state = 'dumped';
                    p.vx = Math.cos(bamboo.angle) * 4;
                    p.vy = Math.sin(bamboo.angle) * 4;
                    p.x = bamboo.pivotX + Math.cos(bamboo.angle) * (bamboo.width*0.7);
                    p.y = bamboo.y + Math.sin(bamboo.angle) * (bamboo.width*0.7);
                }
            }
            else if (p.state === 'dumped') {
                p.vy += gravity;
                p.x += p.vx;
                p.y += p.vy;
                 if (p.y > CH) { particles.splice(i, 1); continue; }
            }
            
            if (p.state !== 'trapped') {
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = "rgba(135, 206, 250, 0.8)";
                ctx.fill();
            }
        }

        // --- 4. 描画 ---
        // 支柱
        ctx.shadowBlur = 0;
        ctx.fillStyle = "#3e2723";
        ctx.fillRect(bamboo.pivotX - 5, bamboo.y + 10, 10, 150);

        // 下の竹
        drawBambooRect(bamboo, false);
        // 上の竹
        drawBambooRect(source, true);
        
        requestAnimationFrame(update);
    }

    function showSoundText() {
        soundText.style.opacity = 1;
        soundText.style.transform = "translate(-50%, -60%) scale(1.2)";
        setTimeout(() => {
            soundText.style.opacity = 0;
            soundText.style.transform = "translate(-50%, -50%) scale(1.0)";
        }, 600);
    }

    update();
</script>
</body>
</html>
"""

components.html(html_code, height=600)
