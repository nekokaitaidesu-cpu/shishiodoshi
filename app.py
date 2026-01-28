import streamlit as st

# ページ設定
st.set_page_config(page_title="スーパーししおどしCustom", page_icon="🎋", layout="centered")

st.title("🎋 スーパーししおどしじぇみにっちスペシャル ver.2.0")
st.write("ついに「全部入り」だっち！チェックボックスで要素を召喚するっち🍄")

# --- サイドバー設定 ---
st.sidebar.header("⚙️ カスタム設定")
speed = st.sidebar.slider("周期（秒）", 1.0, 10.0, 3.0, 0.1)

st.sidebar.subheader("盛り付けオプション 🍄")
# 各要素の表示スイッチ
show_feeder = st.sidebar.checkbox("上の竹＆水流（チョロチョロ）", value=True)
show_detail_bamboo = st.sidebar.checkbox("竹のリアル質感（節）", value=True)
show_detail_stone = st.sidebar.checkbox("石のリアル質感（ザラザラ）", value=True)
show_splash = st.sidebar.checkbox("水しぶき（バシャーン！）", value=True)
show_grass = st.sidebar.checkbox("背景の草（わさわさ）", value=True)
show_mushroom = st.sidebar.checkbox("謎の光るキノコ（！？）", value=True)

# --- CSS 生成ロジック ---

# 竹の質感切り替え
bamboo_bg = """
    background: 
        linear-gradient(90deg, transparent 38%, #3a7d25 40%, #3a7d25 42%, transparent 44%),
        linear-gradient(90deg, transparent 78%, #3a7d25 80%, #3a7d25 82%, transparent 84%),
        linear-gradient(to bottom, #69b34c 0%, #a4d96c 30%, #a4d96c 70%, #4e8c35 100%);
    border-right: 4px solid #2e631d;
""" if show_detail_bamboo else "background-color: #55a630;"

# 石の質感切り替え
stone_bg = """
    background-color: #808080;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.3'/%3E%3C/svg%3E"),
                      linear-gradient(to bottom right, #a0a0a0, #606060);
    box-shadow: inset 5px 5px 10px rgba(255,255,255,0.2), inset -10px -10px 20px rgba(0,0,0,0.5);
""" if show_detail_stone else "background-color: #6c757d;"

# HTML & CSS 組み立て
html_code = f"""
<style>
    /* 全体コンテナ */
    .shishiodoshi-container {{
        display: flex;
        justify_content: center;
        align_items: center;
        height: 450px;
        background-color: #f0f2f6;
        {'''background-image: radial-gradient(circle, #e6e6e6 10%, transparent 10%); background-size: 20px 20px;''' if show_detail_stone else ''}
        border-radius: 20px;
        position: relative;
        overflow: hidden;
        border: 3px solid #d4d7d1;
    }}

    /* --- メインの竹 --- */
    .bamboo {{
        width: 220px;
        height: 60px;
        {bamboo_bg}
        border-radius: 5px 30px 30px 5px;
        position: relative;
        transform-origin: 65% 50%;
        animation: shishiodoshi-move {speed}s cubic-bezier(0.5, 0, 0.3, 1) infinite;
        z-index: 10;
        box-shadow: 10px 15px 20px rgba(0,0,0,0.3);
    }}
    .bamboo::before {{ /* 竹の口 */
        content: ''; position: absolute; right: 0; top: 10%; width: 15px; height: 80%;
        background-color: #222; border-radius: 50%; transform: rotateY(70deg);
    }}

    /* --- 上の竹（給水用） --- */
    .feeder-bamboo {{
        position: absolute;
        top: 20px;
        right: 150px;
        width: 150px;
        height: 40px;
        {bamboo_bg}
        transform: rotate(-20deg);
        border-radius: 5px;
        z-index: 5;
        box-shadow: 5px 10px 10px rgba(0,0,0,0.2);
    }}
    
    /* --- 水流 --- */
    .water-stream {{
        position: absolute;
        top: 45px;
        right: 285px; /* 上の竹の先端に合わせる */
        width: 8px;
        height: 200px;
        background: linear-gradient(to bottom, rgba(255,255,255,0.8), rgba(200,230,255,0.6));
        z-index: 4;
        border-radius: 4px;
        opacity: 0.8;
    }}

    /* --- 支柱 --- */
    .pivot-group {{
        position: absolute;
        top: 50%;
        left: calc(50% + 50px);
        transform: translateY(-30%);
        z-index: 5;
        display: flex; gap: 10px;
    }}
    .pivot {{
        width: 18px; height: 100px;
        background: linear-gradient(to right, #4e8c35, #a4d96c, #4e8c35);
        border-radius: 5px;
    }}

    /* --- 石 --- */
    .stone {{
        position: absolute;
        width: 140px; height: 90px;
        {stone_bg}
        border-radius: 50% 40% 30% 40% / 60% 50% 40% 40%;
        top: 65%; left: calc(50% - 100px);
        z-index: 1;
    }}
    .stone::after {{ /* 水たまり */
        content: ''; position: absolute; top: 20%; left: 25%; width: 50%; height: 30%;
        background-color: #a7c7d7; border-radius: 50%; opacity: 0.8;
    }}

    /* --- 水しぶき --- */
    .splash {{
        position: absolute;
        width: 80px; height: 80px;
        top: 60%; left: calc(50% - 110px);
        background: radial-gradient(circle, #e0f7fa 10%, transparent 10%), radial-gradient(circle, #e0f7fa 10%, transparent 10%);
        background-size: 15px 15px;
        background-position: 0 0, 7px 7px;
        opacity: 0;
        z-index: 15;
        animation: splash-anim {speed}s infinite;
    }}

    /* --- 草 --- */
    .grass {{
        position: absolute;
        bottom: 20px;
        width: 0; height: 0;
        border-left: 10px solid transparent;
        border-right: 10px solid transparent;
        border-bottom: 40px solid #2d6a4f;
        transform-origin: bottom center;
    }}
    .grass-1 {{ left: 20%; transform: rotate(-15deg); }}
    .grass-2 {{ left: 22%; transform: rotate(10deg); height: 50px; border-bottom-color: #40916c; }}
    .grass-3 {{ right: 20%; transform: rotate(5deg); }}

    /* --- キノコ --- */
    .mushroom {{
        position: absolute;
        bottom: 40px; right: 50px;
        width: 30px; height: 30px;
        background: radial-gradient(circle at 30% 30%, #ff0055, #990033);
        border-radius: 50% 50% 10% 10%;
        z-index: 20;
        animation: glow 2s ease-in-out infinite alternate;
    }}
    .mushroom::after {{ /* 軸 */
        content: ''; position: absolute; bottom: -15px; left: 8px;
        width: 14px; height: 20px; background: #fff; border-radius: 4px; z-index: -1;
    }}

    /* --- アニメーション定義 --- */
    @keyframes shishiodoshi-move {{
        0% {{ transform: rotate(-8deg); }}
        55% {{ transform: rotate(0deg); }}
        65% {{ transform: rotate(50deg); }} /* ヒット */
        75% {{ transform: rotate(-12deg); }}
        85% {{ transform: rotate(-8deg); }}
        100% {{ transform: rotate(-8deg); }}
    }}

    @keyframes splash-anim {{
        0%, 62% {{ opacity: 0; transform: scale(0.5); }}
        65% {{ opacity: 1; transform: scale(1.5) translateY(-20px); }} /* ヒットに合わせて出現 */
        75% {{ opacity: 0; transform: scale(2.0); }}
        100% {{ opacity: 0; }}
    }}

    @keyframes glow {{
        from {{ box-shadow: 0 0 5px #ff0055; }}
        to {{ box-shadow: 0 0 20px #ff0055, 0 0 30px #ff99cc; }}
    }}
</style>

<div class="shishiodoshi-container">
    {'<div class="grass grass-1"></div><div class="grass grass-2"></div><div class="grass grass-3"></div>' if show_grass else ''}
    {'<div class="mushroom"></div>' if show_mushroom else ''}

    <div class="stone"></div>
    <div class="pivot-group">
        <div class="pivot" style="height: 120px; margin-top: -20px;"></div>
        <div class="pivot"></div>
    </div>
    
    {'<div class="feeder-bamboo"></div><div class="water-stream"></div>' if show_feeder else ''}
    {'<div class="splash"></div>' if show_splash else ''}
    
    <div class="bamboo"></div>
</div>
"""

st.markdown(html_code, unsafe_allow_html=True)
st.write("---")
st.caption("全部ONにすると、もはや「わびさび」というより「パーティ」だっち🎉")
