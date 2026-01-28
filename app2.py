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

st.title("🎋 ぬるぬる重力ししおどし (クリアVer) 🎋")
st.write("スマホでも真ん中からスタート！竹を反転させて、下の竹は**クリア素材**にしたっち🍄")
st.write("水がタプタプ溜まっていく様子を楽しんでね！もちろん掴んで動かせるよ！")

# シミュレーター本体（HTML/JS）
html_code = """
<!DOCTYPE html>
<html>
<head>
<style>
    canvas {
        background-color: transparent;
        border-radius: 8px;
        // box-shadow: 0 4px 6px rgba(0,0,0,0.1); /* 影は一旦なしでスッキリ */
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
    <canvas id="simCanvas" width="600" height="500"></canvas>
    <div id="sound-text">カコーン！</div>
</div>

<script>
    const canvas = document.getElementById('simCanvas');
    const ctx = canvas.getContext('2d');
    const soundText = document.getElementById('sound-text');

    const CW = canvas.width;
    const CH = canvas.height;

    // --- 設定 ---
    const gravity = 0.15;
    
    // 下の竹（ししおどし）
    const bamboo = {
        // 初期位置を画面中央付近に計算
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
    bamboo.pivotX = bamboo.x - bamboo.width * 0.3; // 回転軸は少し左

    // 上の竹（水源）- 向きを反転
    const source = {
        x: CW / 2 - 80,
        y: CH / 2 - 100,
        width: 120,
        height: 24,
        angle: 0.2, // 右下向き
        name: 'source'
    };

    let particles = [];
    let dragTarget = null;
    let dragOffsetX = 0;
    let dragOffsetY = 0;

    // --- イベント関連 (省略せず記載) ---
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
        if (getDist(pos.x, pos.y, source.x, source.y) < 50) {
            dragTarget = source;
            dragOffsetX = pos.x - source.x;
            dragOffsetY = pos.y - source.y;
        } else if (getDist(pos.x, pos.y, bamboo.pivotX, bamboo.y) < 60) {
            dragTarget = bamboo;
            dragOffsetX = pos.x - bamboo.pivotX;
            dragOffsetY = pos.y - bamboo.y;
        }
    }
    function handleMove(e) {
        if (!dragTarget) return;
        e.preventDefault();
        const pos = getPos(e);
        if (dragTarget.name === 'source') {
            source.x = pos.x - dragOffsetX;
            source.y = pos.y - dragOffsetY;
        } else if (dragTarget.name === 'bamboo') {
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


    // --- 描画関数 (大幅アップデート！) ---

    function drawBambooRect(obj, isSource) {
        ctx.save();
        // 回転の中心を決める
        let transX = isSource ? obj.x : obj.pivotX;
        let transY = obj.y;
        ctx.translate(transX, transY);
        ctx.rotate(obj.angle);
        
        let w = obj.width;
        let h = obj.height;
        
        // 描画の基準点（左上）
        let relX = isSource ? -w * 0.1 : -w * 0.3; // 上の竹は右側から出るように調整
        let relY = -h/2;

        // ドラッグ時のハイライト
        if (dragTarget && dragTarget.name === obj.name) {
            ctx.shadowBlur = 15;
            ctx.shadowColor = "yellow";
        }

        if (isSource) {
            // --- 上の竹（通常描画）---
            let grd = ctx.createLinearGradient(0, -h/2, 0, h/2);
            grd.addColorStop(0, "#556b2f");
            grd.addColorStop(0.5, "#8fbc8f");
            grd.addColorStop(1, "#556b2f");
            ctx.fillStyle = grd;
            ctx.fillRect(relX, relY, w, h);
            // 節
            ctx.fillStyle = "#2e3b1f";
            ctx.fillRect(relX + w * 0.2, relY, 4, h);

        } else {
            // --- 下の竹（クリア＆水溜まり描画）---
            
            // 1. 竹の内部に溜まった水を描画 (クリッピング使用)
            ctx.save(); // クリップ用にsave
            ctx.beginPath();
            ctx.rect(relX, relY, w, h); // 竹の形のパスを作成
            ctx.clip(); // くり抜く

            // 水位の計算（適当な係数で調整）
            let waterLevel = Math.min(obj.waterMass * 0.5, h * 0.9); 
            if (waterLevel > 0) {
                ctx.fillStyle = "rgba(135, 206, 250, 0.8)"; // 水色
                // 竹の下底から水位分の高さを描画
                ctx.fillRect(relX, relY + h - waterLevel, w, waterLevel);
                
                // 水面を少し揺らす（おまけ）
                ctx.beginPath();
                ctx.moveTo(relX, relY + h - waterLevel);
                ctx.lineTo(relX + w, relY + h - waterLevel);
                ctx.strokeStyle = "rgba(255, 255, 255, 0.4)";
                ctx.lineWidth = 2;
                ctx.stroke();
            }
            ctx.restore(); // クリップ解除

            // 2. 半透明の竹の本体を描画
            ctx.fillStyle = "rgba(144, 238, 144, 0.3)"; // 半透明の薄緑
            ctx.fillRect(relX, relY, w, h);

            // 3. 竹の枠線と節を描画
            ctx.strokeStyle = "#556b2f";
            ctx.lineWidth = 3;
            ctx.strokeRect(relX, relY, w, h);
            
            // 節（枠線のみ）
            ctx.beginPath();
            ctx.moveTo(relX + w * 0.3, relY);
            ctx.lineTo(relX + w * 0.3, relY + h);
            ctx.stroke();
        }

        ctx.restore(); // 回転・移動の復帰
    }


    function update() {
        ctx.clearRect(0, 0, CW, CH);

        // --- 1. 水の生成 (位置調整) ---
        if (Math.random() * 10 < 4) { // 少し頻度アップ
            // 上の竹の右端付近から出す
            let startX = source.x + Math.cos(source.angle) * (source.width * 0.8);
            let startY = source.y + Math.sin(source.angle) * (source.width * 0.8) + 5;
            
            particles.push({
                x: startX,
                y: startY,
                // 右下に向かって発射
                vx: Math.cos(source.angle) * 3 + Math.random(),
                vy: Math.sin(source.angle) * 3,
                radius: 2.5 + Math.random() * 2,
                state: 'falling'
            });
        }

        // --- 2. 竹の物理計算 ---
        let force = (bamboo.targetAngle - bamboo.angle) * 0.08; // 復元力強め
        let waterForce = bamboo.waterMass * 0.003; // 水の重み係数調整
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

        // 先端位置（受け口）- 右端に変更
        let tipOffset = bamboo.width * 0.6; 
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
                
                let dx = p.x - tipX;
                let dy = p.y - tipY;
                let dist = Math.sqrt(dx*dx + dy*dy);
                
                // 判定調整
                if (dist < 30 && p.vy > 0 && bamboo.angle < 0) {
                    p.state = 'trapped';
                    p.vx = 0; p.vy = 0;
                }
                if (p.y > CH) { particles.splice(i, 1); continue; }
            }
            else if (p.state === 'trapped') {
                bamboo.waterMass += p.radius * 3; // 質量加算のみ行う（描画はdrawBambooRectで）
                
                // こぼれる処理
                if (bamboo.angle > 0.3) {
                    p.state = 'dumped';
                    // 竹の角度に合わせて放出
                    p.vx = Math.cos(bamboo.angle) * 4;
                    p.vy = Math.sin(bamboo.angle) * 4;
                    // 放出位置を竹の先端に設定
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
            
            // trapped以外の水粒子を描画
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

        // 下の竹（クリア＆水）
        drawBambooRect(bamboo, false);
        // 上の竹（通常）
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

components.html(html_code, height=550)
