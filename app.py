import streamlit as st

# ページ設定
st.set_page_config(page_title="スーパーししおどし", page_icon="🎋", layout="centered")

st.title("🎋 スーパーししおどしじぇみにっちスペシャル ver.1.1")
st.write("まずはCSSで「質感」を再現してみたっち！ここから盛り上げていくっちよー！🍄")

# サイドバー設定
st.sidebar.header("⚙️ 設定")
speed = st.sidebar.slider("周期（秒）", 1.0, 10.0, 3.0, 0.1)
# 色は一旦固定にして、質感表現に集中します！

# CSSアニメーションとスタイルの定義
html_code = f"""
<style>
    /* 全体のコンテナ（背景も少しリッチに） */
    .shishiodoshi-container {{
        display: flex;
        justify_content: center;
        align_items: center;
        height: 400px;
        /* 和風な砂利っぽい背景 */
        background-image: radial-gradient(circle, #e6e6e6 10%, transparent 10%), radial-gradient(circle, #e6e6e6 10%, transparent 10%);
        background-size: 20px 20px;
        background-position: 0 0, 10px 10px;
        background-color: #f8f9fa;
        border-radius: 20px;
        position: relative;
        overflow: hidden;
        border: 3px solid #d4d7di;
    }}

    /* --- 竹（本体）の表現強化 --- */
    .bamboo {{
        width: 220px;
        height: 60px;
        /* グラデーションを重ねて「竹の節と丸み」を表現！ */
        background: 
            /* 節の線（濃い緑） */
            linear-gradient(90deg, transparent 38%, #3a7d25 40%, #3a7d25 42%, transparent 44%),
            linear-gradient(90deg, transparent 78%, #3a7d25 80%, #3a7d25 82%, transparent 84%),
            /* 竹の丸み（上下の影とハイライト） */
            linear-gradient(to bottom, #69b34c 0%, #a4d96c 30%, #a4d96c 70%, #4e8c35 100%);
        
        border-radius: 5px 30px 30px 5px; /* 先端を少し丸く */
        border-right: 4px solid #2e631d; /* 切り口 */
        
        position: relative;
        transform-origin: 65% 50%;
        animation: shishiodoshi-move {speed}s cubic-bezier(0.5, 0, 0.3, 1) infinite;
        z-index: 10;
        box-shadow: 10px 15px 20px rgba(0,0,0,0.3); /* 影を強くして立体感 */
    }}

    /* 竹の注ぎ口（水がたまるところ）を黒く塗る */
    .bamboo::before {{
        content: '';
        position: absolute;
        right: 0;
        top: 10%;
        width: 15px;
        height: 80%;
        background-color: #222; /* 穴の暗闇 */
        border-radius: 50%;
        transform: rotateY(70deg); /* 楕円に見せる */
    }}

    /* --- 支柱の表現強化 --- */
    .pivot-group {{
        position: absolute;
        top: 50%;
        left: calc(50% + 50px);
        transform: translateY(-30%);
        z-index: 5;
        display: flex;
        gap: 10px;
    }}
    /* 2本の支柱を作る */
    .pivot {{
        width: 18px;
        height: 100px;
        /* 支柱も竹っぽく塗る */
        background: linear-gradient(to right, #4e8c35, #a4d96c, #4e8c35);
        border-radius: 5px;
        position: relative;
    }}
    .pivot::after {{ /* 支柱の節 */
         content: ''; position: absolute; top: 30%; left:0; width:100%; height:3px; background:#3a7d25;
    }}

    /* --- 石の表現強化 --- */
    .stone {{
        position: absolute;
        width: 140px;
        height: 90px;
        /* ザラザラした石の質感 */
        background-color: #808080;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.3'/%3E%3C/svg%3E"),
                          linear-gradient(to bottom right, #a0a0a0, #606060);
        border-radius: 50% 40% 30% 40% / 60% 50% 40% 40%; /* いびつな形 */
        top: 60%;
        left: calc(50% - 100px);
        z-index: 1;
        box-shadow: inset 5px 5px 10px rgba(255,255,255,0.2), inset -10px -10px 20px rgba(0,0,0,0.5);
    }}
    
    /* 水たまり部分 */
    .stone::after {{
        content: '';
        position: absolute;
        top: 20%;
        left: 25%;
        width: 50%;
        height: 30%;
        background-color: #a7c7d7; /* 水色 */
        border-radius: 50%;
        box-shadow: inset 2px 2px 5px rgba(0,0,0,0.4);
        opacity: 0.8;
    }}

    /* アニメーション（動きにタメを作る） */
    @keyframes shishiodoshi-move {{
        0% {{ transform: rotate(-8deg); }}
        55% {{ transform: rotate(0deg); }} /* ゆっくり溜まる */
        65% {{ transform: rotate(50deg); }} /* カコーン！ */
        75% {{ transform: rotate(-12deg); }} /* 跳ね返り */
        85% {{ transform: rotate(-8deg); }}
        100% {{ transform: rotate(-8deg); }}
    }}

</style>

<div class="shishiodoshi-container">
    <div class="stone"></div>
    <div class="pivot-group">
        <div class="pivot" style="height: 120px; margin-top: -20px;"></div>
        <div class="pivot"></div>
    </div>
    <div class="bamboo"></div>
</div>
"""

st.markdown(html_code, unsafe_allow_html=True)

st.write("---")
st.write("#### 盛り付け計画（案）🍄")
st.checkbox("✅ 竹に「節」を描いてリアルにする")
st.checkbox("✅ 石をザラザラした質感にする")
st.checkbox("⬜️ 竹から水がチョロチョロ出るようにする（難易度：中）")
st.checkbox("⬜️ カコーン！した時に水しぶきをあげる（難易度：高）")
st.checkbox("⬜️ 背景に草を生やす（難易度：低）")
st.checkbox("⬜️ 謎の光るキノコを配置する（！？）")
