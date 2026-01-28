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

st.title("🎋 カオス・ししおどし (改造Ver) 🎋")
st.write("受け口を**ガバッと**広げて、動きを**ドッシリ**重くしたっち！🍄")
st.write("下のスライダーで「水量」と「勢い」をMAXにして遊んでみて😂")

# シミュレーター本体（HTML/JS）
# スライダーをHTML内に埋め込んで、リロードなしでグリグリ調整できるようにしたよ！
html_code = """
<!DOCTYPE html>
<html>
<head>
<style>
    body { margin: 0; overflow: hidden; font-family: sans-serif; }
    canvas {
        background-color: transparent;
        display: block;
        margin: 0 auto;
        cursor: grab;
        touch-action: none;
    }
    canvas:active { cursor: grabbing; }
    .container {
        position: relative;
        width: 100%;
        text-align: center;
        user-select: none;
    }
    /* スライダー群のスタイル */
    .controls {
        margin-top: 10px;
        padding: 10px;
        background: rgba(255,255,255,0.6);
        border-radius: 10px;
        display: inline-block;
    }
    .control-group {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 5px 0;
        width: 300px;
    }
    label { font-weight: bold; color: #556b2f; margin-right: 10px; }
    input[type=range] { flex-grow: 1; cursor: pointer; }
    
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
        white-space: nowrap;
    }
</style>
</head>
<body>

<div class="container">
    <canvas id="simCanvas" width="600" height="500"></canvas>
    <div id="sound-text">カッコォォン！！</div>
    
    <div class="controls">
        <div class="control-group">
            <label>💧 水量 (Amount)</label>
            <input type="range" id="amountSlider" min="1" max="50" value="5">
        </div>
        <div class="control-group">
            <label>🚀 勢い (Power)</label>
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

    const CW = canvas.width;
    const CH = canvas.height;
    const gravity = 0.15;

    // --- パラメータ ---
    // 下の竹（ししおどし・重厚長大Ver）
    const bamboo = {
        x: CW / 2 + 20, 
        y: CH / 2 + 50,
        width: 180,
        height: 36,
        angle: -0.3,
        targetAngle: -0.3,
        pivotX: 0, 
        velocity: 0,
        mass: 300, // 質量マシマシ
        waterMass: 0,
        isDumping: false,
        name: 'bamboo',
        // 受け口の拡張部分
        funnelSize: 50 
    };
    bamboo.pivotX = bamboo.x - bamboo.width * 0.3;

    // 上の竹（水源）
    const source = {
        x: CW / 2 - 80,
        y: CH / 2 - 120,
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
        if (getDist(pos.x, pos.y, source.x, source.y) < source.handleRadius + 10) {
            dragTarget = 'rotator'; return;
        }
        let srcCX = source.x + Math.cos(source.angle) * (source.width/2);
        let srcCY = source.y + Math.sin(source.angle) * (source.width/2);
        if (getDist(pos.x, pos.y, srcCX, srcCY) < 60) {
            dragTarget = source;
            dragOffsetX = pos.x - source.x; dragOffsetY = pos.y - source.y; return;
        }
        if (getDist(pos.x, pos.y, bamboo.pivotX, bamboo.y) < 70) {
            dragTarget = bamboo;
            dragOffsetX = pos.x - bamboo.pivotX; dragOffsetY = pos.y - bamboo.y; return;
        }
    }
    function handleMove(e) {
        if (!dragTarget) return;
        e.preventDefault();
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
            // 下の竹（改造Ver）
            
            // ★1. 受け口拡張ファンネル（じょうご）のパス定義
            // 竹の先端(relX + w)からさらに外側に広がる台形
            let funnelLen = obj.funnelSize;
            let funnelTopW = 20; // 上への広がり
            let funnelBotW = 10; // 下への広がり（控えめ）

            // ファンネルの描画パス
            ctx.beginPath();
            ctx.moveTo(relX + w, relY); // 竹の上端
            ctx.lineTo(relX + w + funnelLen, relY - funnelTopW); // 広がった先(上)
            ctx.lineTo(relX + w + funnelLen, relY + h + funnelBotW); // 広がった先(下)
            ctx.lineTo(relX + w, relY + h); // 竹の下端
            ctx.closePath();
            
            // ファンネル着色 (半透明緑)
            ctx.fillStyle = "rgba(50, 205, 50, 0.4)"; 
            ctx.fill();
            ctx.strokeStyle = "#32cd32";
            ctx.stroke();

            // 水の描画（竹本体 + ファンネル内）
            ctx.save();
            ctx.beginPath();
            ctx.rect(relX, relY, w, h); // 竹本体
            // ファンネル部分も水が入るようにクリップ領域に追加してもいいけど
            // 簡易的に竹本体のみに水が溜まる表現にする（その方が満タン感が出る）
            ctx.clip();
            
            // 水位（ゆっくり溜まる演出のため、溜まった量に応じて高さを変える）
            // massが大きいので、hいっぱいになるには相当溜まる必要がある
            let fillRate = Math.min(obj.waterMass / 250, 1.0); // 250溜まると満タン
            let waterLevel = fillRate * h;
            
            if (waterLevel > 0) {
                ctx.fillStyle = "rgba(100, 200, 255, 0.85)";
                ctx.fillRect(relX, relY + h - waterLevel, w, waterLevel);
                // 水面揺れ
                ctx.strokeStyle = "rgba(255,255,255,0.8)";
                ctx.beginPath(); ctx.moveTo(relX, relY + h - waterLevel);
                ctx.lineTo(relX + w, relY + h - waterLevel); ctx.stroke();
            }
            ctx.restore();

            // 竹本体（クリア）
            ctx.fillStyle = "rgba(144, 238, 144, 0.2)";
            ctx.fillRect(relX, relY, w, h);
            ctx.strokeStyle = "#556b2f"; ctx.lineWidth = 3;
            ctx.strokeRect(relX, relY, w, h);
        }
        ctx.restore();
    }

    function update() {
        ctx.clearRect(0, 0, CW, CH);
        
        // パラメータ取得
        let amountVal = parseInt(amountSlider.value);
        let powerVal = parseInt(powerSlider.value);

        // --- 1. 水の生成 ---
        // amountValが高いほど確率UP & 一度に出る量UP
        if (Math.random() * 50 < amountVal * 2) { 
            let tipX = source.x + Math.cos(source.angle) * source.width;
            let tipY = source.y + Math.sin(source.angle) * source.width;
            
            // 勢い (powerVal)
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

        // --- 2. 竹の物理計算 (重量級チューニング) ---
        // 復元力（バネ）を弱く、反応を遅く
        let k = 0.02; // バネ定数 (前の1/4くらい)
        let force = (bamboo.targetAngle - bamboo.angle) * k;
        
        // 水の重み係数も小さくして「たくさん溜めないと動かない」ようにする
        let waterForce = bamboo.waterMass * 0.0003; 
        
        bamboo.velocity += force + waterForce;
        bamboo.velocity *= 0.98; // 減衰少なめ（慣性で動く感じ）
        bamboo.angle += bamboo.velocity;

        // 下限（カコーン）
        if (bamboo.angle > 0.8) {
            bamboo.angle = 0.8;
            bamboo.velocity *= -0.2; // 跳ね返り小さく（重いから）
            
            // ある程度溜まってたら音（文字）出す
            if (!bamboo.isDumping && bamboo.waterMass > 150) {
                 showSoundText();
            }
            bamboo.isDumping = true;
        }
        // 上限（戻り位置）
        if (bamboo.angle < bamboo.targetAngle) {
            bamboo.angle = bamboo.targetAngle;
            bamboo.velocity = 0; // ピタッと止める
            bamboo.isDumping = false;
        }

        // --- 3. 当たり判定（ガバガバ拡張） ---
        // 受け口の定義：竹の右端 + ファンネル分
        // 単純な点と点ではなく、ライン（線分）との距離で判定してあげると入りやすい
        // ここでは簡易的に「竹の軸線に近く、かつ先端付近にあるか」で判定
        
        let bambooVecX = Math.cos(bamboo.angle);
        let bambooVecY = Math.sin(bamboo.angle);
        
        // 判定基準点：回転軸
        let pivotX = bamboo.pivotX;
        let pivotY = bamboo.y;

        bamboo.waterMass = 0; 

        for (let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            
            if (p.state === 'falling') {
                p.vy += gravity; p.x += p.vx; p.y += p.vy;
                
                // 竹のローカル座標系に変換して判定
                let rx = p.x - pivotX;
                let ry = p.y - pivotY;
                // 回転を戻す
                let localX = rx * Math.cos(-bamboo.angle) - ry * Math.sin(-bamboo.angle);
                let localY = rx * Math.sin(-bamboo.angle) + ry * Math.cos(-bamboo.angle);

                // 判定エリア（竹の内部 〜 ファンネルの先端まで）
                // 竹の長さ: width, ファンネル: +funnelSize
                // 幅: height
                
                // 右端(先端)付近のエリアを広くとる
                // 竹の右端(-w*0.3 + w = w*0.7) から ファンネル先まで
                let tipStart = bamboo.width * 0.7;
                let tipEnd = tipStart + bamboo.funnelSize + 20; // ちょっとおまけ
                
                let inRangeX = (localX > tipStart - 20 && localX < tipEnd);
                let inRangeY = (localY > -30 && localY < 30); // 縦幅ガバガバ(本来height/2=18)

                if (inRangeX && inRangeY && p.vy > 0 && bamboo.angle < 0) {
                     p.state = 'trapped';
                     p.vx = 0; p.vy = 0;
                }
                
                if (p.y > CH) { particles.splice(i, 1); continue; }
            }
            else if (p.state === 'trapped') {
                bamboo.waterMass += p.radius * 3;
                // 排出
                if (bamboo.angle > 0.4) {
                    p.state = 'dumped';
                    p.vx = Math.cos(bamboo.angle) * 5; // 勢いよく
                    p.vy = Math.sin(bamboo.angle) * 5;
                    // 先端から飛ばす
                    p.x = bamboo.pivotX + Math.cos(bamboo.angle) * (bamboo.width*0.9);
                    p.y = bamboo.y + Math.sin(bamboo.angle) * (bamboo.width*0.9);
                }
            }
            else if (p.state === 'dumped') {
                p.vy += gravity; p.x += p.vx; p.y += p.vy;
                if (p.y > CH) { particles.splice(i, 1); continue; }
            }
            
            if (p.state !== 'trapped') {
                ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = "rgba(100, 200, 255, 0.9)"; ctx.fill();
            }
        }

        // --- 4. 描画 ---
        // 支柱
        ctx.fillStyle = "#3e2723";
        ctx.fillRect(bamboo.pivotX - 5, bamboo.y + 10, 10, 200);

        drawBambooRect(bamboo, false);
        drawBambooRect(source, true);
        
        requestAnimationFrame(update);
    }

    function showSoundText() {
        soundText.style.opacity = 1;
        soundText.style.transform = "translate(-50%, -60%) scale(1.5)";
        setTimeout(() => {
            soundText.style.opacity = 0;
            soundText.style.transform = "translate(-50%, -50%) scale(1.0)";
        }, 1000); // 表示時間も長く
    }

    update();
</script>
</body>
</html>
"""

components.html(html_code, height=650)
