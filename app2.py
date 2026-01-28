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

st.title("🎋 ぬるぬる重力ししおどし 🎋")
st.write("竹を**クリック（タップ）して掴める**ようにしたっち！🍄")
st.write("好きな場所に動かして、水がうまく入るように調整してね！")

# シミュレーター本体（HTML/JS）
html_code = """
<!DOCTYPE html>
<html>
<head>
<style>
    canvas {
        background-color: transparent;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        display: block;
        margin: 0 auto;
        cursor: grab; /* 掴める感を出す */
        touch-action: none; /* スマホでスクロールしないようにする */
    }
    canvas:active {
        cursor: grabbing;
    }
    .container {
        position: relative;
        width: 100%;
        text-align: center;
        user-select: none; /* 文字選択防止 */
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
    <canvas id="simCanvas" width="600" height="400"></canvas>
    <div id="sound-text">カコーン！</div>
</div>

<script>
    const canvas = document.getElementById('simCanvas');
    const ctx = canvas.getContext('2d');
    const soundText = document.getElementById('sound-text');

    // --- 設定 ---
    const gravity = 0.15;
    
    // 竹の設定
    // ドラッグ判定のために isDragging などを追加
    const bamboo = {
        x: 300,
        y: 250,
        width: 160,
        height: 30,
        angle: -0.2,
        targetAngle: -0.2,
        pivotX: 0, 
        velocity: 0,
        mass: 100,
        waterMass: 0,
        isDumping: false,
        name: 'bamboo' // 判定用
    };
    // 軸位置の初期計算
    bamboo.pivotX = bamboo.x - bamboo.width * 0.2;

    const source = {
        x: 200,
        y: 100,
        width: 120,
        angle: 0.1,
        name: 'source' // 判定用
    };

    let particles = [];
    
    // ドラッグ操作用の変数
    let dragTarget = null;
    let dragOffsetX = 0;
    let dragOffsetY = 0;

    // マウス/タッチ座標の取得
    function getPos(e) {
        const rect = canvas.getBoundingClientRect();
        let clientX = e.clientX;
        let clientY = e.clientY;
        
        // スマホ対応
        if (e.touches && e.touches.length > 0) {
            clientX = e.touches[0].clientX;
            clientY = e.touches[0].clientY;
        } else if (e.changedTouches && e.changedTouches.length > 0) {
            // touchend用
             clientX = e.changedTouches[0].clientX;
             clientY = e.changedTouches[0].clientY;
        }

        return {
            x: clientX - rect.left,
            y: clientY - rect.top
        };
    }

    // 距離計算（当たり判定用）
    function getDist(x1, y1, x2, y2) {
        return Math.sqrt((x1-x2)**2 + (y1-y2)**2);
    }

    // --- イベントリスナー登録 ---
    
    function handleStart(e) {
        // e.preventDefault(); // 一旦外す（スクロール阻害の調整）
        const pos = getPos(e);
        
        // 上の竹の判定（中心付近をクリックしたら）
        if (getDist(pos.x, pos.y, source.x, source.y) < 50) {
            dragTarget = source;
            dragOffsetX = pos.x - source.x;
            dragOffsetY = pos.y - source.y;
        }
        // 下の竹の判定（回転軸付近をクリックしたら）
        else if (getDist(pos.x, pos.y, bamboo.pivotX, bamboo.y) < 60) {
            dragTarget = bamboo;
            dragOffsetX = pos.x - bamboo.pivotX; // pivotXを基準に動かす
            dragOffsetY = pos.y - bamboo.y;
        }
    }

    function handleMove(e) {
        if (!dragTarget) return;
        e.preventDefault(); // ドラッグ中はスクロールさせない
        const pos = getPos(e);

        if (dragTarget.name === 'source') {
            source.x = pos.x - dragOffsetX;
            source.y = pos.y - dragOffsetY;
        } else if (dragTarget.name === 'bamboo') {
            // 下の竹は pivotX と y を更新する
            let newPivotX = pos.x - dragOffsetX;
            let newY = pos.y - dragOffsetY;
            
            // 相対関係を維持して x も更新（念のため）
            let offset = bamboo.x - bamboo.pivotX;
            bamboo.pivotX = newPivotX;
            bamboo.y = newY;
            bamboo.x = newPivotX + offset;
        }
    }

    function handleEnd(e) {
        dragTarget = null;
    }

    // PC(マウス)
    canvas.addEventListener('mousedown', handleStart);
    canvas.addEventListener('mousemove', handleMove);
    canvas.addEventListener('mouseup', handleEnd);
    canvas.addEventListener('mouseleave', handleEnd);

    // スマホ(タッチ)
    canvas.addEventListener('touchstart', handleStart, {passive: false});
    canvas.addEventListener('touchmove', handleMove, {passive: false});
    canvas.addEventListener('touchend', handleEnd);


    // --- 描画関数 ---

    function drawBambooRect(bx, by, w, h, angle, isSource) {
        ctx.save();
        ctx.translate(bx, by);
        ctx.rotate(angle);
        
        // 掴んでる時は枠線を出す（わかりやすく）
        let isSelected = false;
        if (dragTarget) {
            if (isSource && dragTarget.name === 'source') isSelected = true;
            if (!isSource && dragTarget.name === 'bamboo') isSelected = true;
        }

        if (isSelected) {
            ctx.shadowBlur = 15;
            ctx.shadowColor = "yellow";
        }

        let grd = ctx.createLinearGradient(0, -h/2, 0, h/2);
        grd.addColorStop(0, "#556b2f");
        grd.addColorStop(0.5, "#8fbc8f");
        grd.addColorStop(1, "#556b2f");
        ctx.fillStyle = grd;
        
        let relX = -bamboo.width * 0.3; // 下の竹用オフセット
        if (isSource) relX = -w/2;      // 上の竹用オフセット
        
        ctx.fillRect(relX, -h/2, w, h);
        
        // 節
        ctx.fillStyle = "#2e3b1f";
        ctx.fillRect(relX + w * 0.1, -h/2, 4, h);
        if (!isSource) ctx.fillRect(relX + w * 0.8, -h/2, 4, h);

        ctx.restore();
    }

    function update() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // --- 1. 水の生成 ---
        if (Math.random() * 10 < 3) {
            let startX = source.x + Math.cos(source.angle) * (source.width/2) + (Math.random()*4 - 2);
            let startY = source.y + Math.sin(source.angle) * (source.width/2) + 10;
            
            particles.push({
                x: startX,
                y: startY,
                vx: Math.cos(source.angle) * 2,
                vy: Math.sin(source.angle) * 2,
                radius: 2 + Math.random() * 2,
                state: 'falling'
            });
        }

        // --- 2. 竹（ししおどし）の物理計算 ---
        let force = (bamboo.targetAngle - bamboo.angle) * 0.05;
        let waterForce = bamboo.waterMass * 0.002;
        bamboo.velocity += force + waterForce;
        bamboo.velocity *= 0.95;
        bamboo.angle += bamboo.velocity;

        if (bamboo.angle > 0.8) {
            bamboo.angle = 0.8;
            bamboo.velocity *= -0.4;
            if (!bamboo.isDumping && bamboo.waterMass > 10) {
                 showSoundText();
            }
            bamboo.isDumping = true;
        }
        if (bamboo.angle < bamboo.targetAngle) {
            bamboo.angle = bamboo.targetAngle;
            bamboo.velocity = 0;
            bamboo.isDumping = false;
        }

        // 先端位置（受け口）の更新（ドラッグで動くので毎回計算）
        let tipOffset = bamboo.width * 0.7; 
        let tipX = bamboo.pivotX + Math.cos(bamboo.angle) * tipOffset;
        let tipY = bamboo.y + Math.sin(bamboo.angle) * tipOffset;

        // --- 3. 水粒子の更新 ---
        bamboo.waterMass = 0; 

        for (let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            
            if (p.state === 'falling') {
                p.vy += gravity;
                p.x += p.vx;
                p.y += p.vy;
                
                // 受け口判定
                let dx = p.x - tipX;
                let dy = p.y - tipY;
                let dist = Math.sqrt(dx*dx + dy*dy);
                
                // 判定半径を少し広げて入りやすくする
                if (dist < 25 && p.vy > 0 && bamboo.angle < 0.2) {
                    p.state = 'trapped';
                    p.vx = 0;
                    p.vy = 0;
                }
                
                if (p.y > canvas.height) {
                    particles.splice(i, 1);
                    continue;
                }
            }
            else if (p.state === 'trapped') {
                bamboo.waterMass += p.radius * 3;
                let trapOffset = bamboo.width * (0.4 + Math.random() * 0.3);
                // pivotX基準で追従
                p.x = bamboo.pivotX + Math.cos(bamboo.angle) * trapOffset;
                p.y = bamboo.y + Math.sin(bamboo.angle) * trapOffset - 5;

                if (bamboo.angle > 0.4) {
                    p.state = 'dumped';
                    p.vx = Math.cos(bamboo.angle) * 3;
                    p.vy = Math.sin(bamboo.angle) * 3;
                }
            }
            else if (p.state === 'dumped') {
                p.vy += gravity;
                p.x += p.vx;
                p.y += p.vy;
                 if (p.y > canvas.height) {
                    particles.splice(i, 1);
                    continue;
                }
            }
            
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = "rgba(135, 206, 250, 0.8)";
            ctx.fill();
        }

        // --- 4. 竹の描画 ---
        // 上の竹
        drawBambooRect(source.x, source.y, source.width, 20, source.angle, true);
        
        // 下の竹（ししおどし）
        drawBambooRect(bamboo.pivotX, bamboo.y, bamboo.width, bamboo.height, bamboo.angle, false);
        
        // 支柱（下の竹と一緒に動く）
        ctx.shadowBlur = 0; // 影リセット
        ctx.fillStyle = "#3e2723";
        ctx.fillRect(bamboo.pivotX - 5, bamboo.y, 10, 150);

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

components.html(html_code, height=500)
