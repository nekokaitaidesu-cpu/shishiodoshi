import streamlit as st
import streamlit.components.v1 as components

# ページ設定
st.set_page_config(
    page_title="和風ししおどしシミュレーター",
    page_icon="🎋",
    layout="centered"
)

# スタイル定義（和風な背景とフォント）
st.markdown("""
    <style>
    body {
        background-color: #f4f1ea; /* 和紙っぽい色 */
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
    .stButton>button {
        background-color: #6b8e23;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #556b2f;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎋 ぬるぬる重力ししおどし 🎋")
st.write("水が溜まると重力で傾いて……カコーン！となる様子を眺めるっち🍄")

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
    }
    .container {
        position: relative;
        width: 100%;
        text-align: center;
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
    const waterSpawnRate = 3; // フレームごとの生成確率(低いほど頻度高)
    
    // 竹の設定
    const bamboo = {
        x: 300,
        y: 250,
        width: 160,
        height: 30,
        angle: -0.2, // ラジアン (初期角度：少し上向き)
        targetAngle: -0.2, // 戻るべき角度
        pivotX: 0, // 相対的な回転軸X
        velocity: 0,
        mass: 100, // 竹自体の重さ感覚
        waterMass: 0, // 溜まった水の重さ
        isDumping: false
    };
    // 回転軸は竹の左寄り(1/3くらいの位置)に設定
    bamboo.pivotX = bamboo.x - bamboo.width * 0.2;

    // 水粒子配列
    let particles = [];
    
    // 上の竹（水源）
    const source = {
        x: 200,
        y: 100,
        width: 120,
        angle: 0.1
    };

    function drawBambooRect(bx, by, w, h, angle) {
        ctx.save();
        ctx.translate(bx, by); // 回転軸へ移動
        ctx.rotate(angle);
        
        // 竹の描画（緑のグラデーション）
        let grd = ctx.createLinearGradient(0, -h/2, 0, h/2);
        grd.addColorStop(0, "#556b2f");
        grd.addColorStop(0.5, "#8fbc8f");
        grd.addColorStop(1, "#556b2f");
        ctx.fillStyle = grd;
        
        // 竹筒（角丸四角形っぽく）
        // 回転軸(0,0)から描画位置を調整
        // bamboo.x, bamboo.yは回転軸の位置として渡されている前提
        // ここではPivotからの相対描画
        let relX = -bamboo.width * 0.3; // 軸の左側
        if (bx === source.x) relX = -w/2; // 上の竹用
        
        ctx.fillRect(relX, -h/2, w, h);
        
        // 節（フシ）を描く
        ctx.fillStyle = "#2e3b1f";
        ctx.fillRect(relX + w * 0.1, -h/2, 4, h);
        if (bx !== source.x) ctx.fillRect(relX + w * 0.8, -h/2, 4, h);

        ctx.restore();
    }

    function update() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // --- 1. 水の生成 ---
        if (Math.random() * 10 < 3) { // 確率で水滴生成
            // 上の竹の先から出る
            let startX = source.x + Math.cos(source.angle) * (source.width/2) + (Math.random()*4 - 2);
            let startY = source.y + Math.sin(source.angle) * (source.width/2) + 10;
            
            particles.push({
                x: startX,
                y: startY,
                vx: Math.cos(source.angle) * 2,
                vy: Math.sin(source.angle) * 2,
                radius: 2 + Math.random() * 2,
                state: 'falling' // falling, trapped, dumped
            });
        }

        // --- 2. 竹（ししおどし）の物理計算 ---
        
        // トルク計算 (簡易版)
        // 水がないときは左側(短い方)が重いので左に傾こうとする -> 結果、右が上がる(targetAngle)
        // 水が溜まると右側(長い方)が重くなり、右に傾く
        
        // 復元力（バネっぽい動き）
        let force = (bamboo.targetAngle - bamboo.angle) * 0.05;
        
        // 水の重みによる力
        // 溜まっている水が多いほど角度が増える力
        let waterForce = bamboo.waterMass * 0.002;
        
        bamboo.velocity += force + waterForce;
        bamboo.velocity *= 0.95; // 減衰（空気抵抗）
        bamboo.angle += bamboo.velocity;

        // 角度制限 (地面に当たる or 戻りすぎ防止)
        if (bamboo.angle > 0.8) { // 下にガコンといった！
            bamboo.angle = 0.8;
            bamboo.velocity *= -0.4; // 跳ね返り
            
            // カコーン判定
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

        // 竹の先端位置（水が入る口）の計算
        // 回転軸からのオフセット
        let tipOffset = bamboo.width * 0.7; 
        let tipX = bamboo.pivotX + Math.cos(bamboo.angle) * tipOffset;
        let tipY = bamboo.y + Math.sin(bamboo.angle) * tipOffset;


        // --- 3. 水粒子の更新 ---
        bamboo.waterMass = 0; // リセットして再集計

        for (let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            
            if (p.state === 'falling') {
                p.vy += gravity;
                p.x += p.vx;
                p.y += p.vy;
                
                // 竹の口に入ったか判定 (簡易的な矩形判定)
                // 竹の角度に合わせて受け口が変わる
                let dx = p.x - tipX;
                let dy = p.y - tipY;
                let dist = Math.sqrt(dx*dx + dy*dy);
                
                if (dist < 20 && p.vy > 0 && bamboo.angle < 0.2) {
                    p.state = 'trapped';
                    p.vx = 0;
                    p.vy = 0;
                }
                
                // 画面外削除
                if (p.y > canvas.height) {
                    particles.splice(i, 1);
                    continue;
                }
            }
            else if (p.state === 'trapped') {
                // 竹の中にいる
                // 竹の角度に合わせて位置を更新
                // 簡易的に、竹の先端から少し内側にランダム配置されているように見せる
                // 実際は物理演算せず、数としてカウントするだけでも見た目はそれっぽい
                bamboo.waterMass += p.radius * 3; // 質量加算
                
                // 描画位置を竹の動きに同期させる
                // ここでは簡易的に「竹の先端付近」に固定して回転させる
                let trapOffset = bamboo.width * (0.4 + Math.random() * 0.3); // 先端寄り
                p.x = bamboo.pivotX + Math.cos(bamboo.angle) * trapOffset;
                p.y = bamboo.y + Math.sin(bamboo.angle) * trapOffset - 5; // 竹の厚み分浮かす

                // 竹が傾きすぎたらこぼれる
                if (bamboo.angle > 0.4) {
                    p.state = 'dumped';
                    p.vx = Math.cos(bamboo.angle) * 3;
                    p.vy = Math.sin(bamboo.angle) * 3;
                    // 水が減る処理はループの最後で自然に行われる(waterMassが次回減る)
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
            
            // 描画
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = "rgba(135, 206, 250, 0.8)"; // 水色
            ctx.fill();
        }

        // --- 4. 竹の描画 ---
        // 上の竹
        drawBambooRect(source.x, source.y, source.width, 20, source.angle);
        
        // 下の竹（ししおどし）
        // 軸を中心に回転
        drawBambooRect(bamboo.pivotX, bamboo.y, bamboo.width, bamboo.height, bamboo.angle);
        
        // 支柱
        ctx.fillStyle = "#3e2723";
        ctx.fillRect(bamboo.pivotX - 5, bamboo.y, 10, 150);

        requestAnimationFrame(update);
    }

    function showSoundText() {
        soundText.style.opacity = 1;
        soundText.style.transform = "translate(-50%, -60%) scale(1.2)"; // ちょっと跳ねる
        setTimeout(() => {
            soundText.style.opacity = 0;
            soundText.style.transform = "translate(-50%, -50%) scale(1.0)";
        }, 600);
    }

    // スタート
    update();
</script>
</body>
</html>
"""

# Streamlitに埋め込み（高さを確保）
components.html(html_code, height=450)

st.write("---")
st.info("💡 解説：竹の中に水粒子（青い丸）が止まると`mass`（重さ）が増える計算をしてるよ。一定以上重くなると、重力に負けて右に回転して水がこぼれるっち！")
