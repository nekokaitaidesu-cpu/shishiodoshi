import streamlit as st

# ページ設定
st.set_page_config(page_title="スーパーししおどし", page_icon="🎋", layout="centered")

st.title("🎋 スーパーししおどしじぇみにっちスペシャル")
st.write("CSSアニメーションで、心を「無」にするだっち...🍄")

# サイドバーでカスタマイズ（ジェネレーター要素）
st.sidebar.header("⚙️ 設定")
speed = st.sidebar.slider("周期（秒）: ゆっくり〜せかせか", 1.0, 10.0, 3.0, 0.1)
size = st.sidebar.slider("竹のサイズ（px）", 100, 400, 200, 10)
bamboo_color = st.sidebar.color_picker("竹の色", "#55a630")

# CSSによるアニメーション定義
# Pythonの変数(speed, size, color)をCSSの中に埋め込みます
html_code = f"""
<style>
    /* ししおどし全体のコンテナ */
    .shishiodoshi-container {{
        display: flex;
        justify_content: center;
        align_items: center;
        height: 400px;
        background-color: #f0f2f6; /* 背景色 */
        border-radius: 20px;
        position: relative;
        overflow: hidden;
    }}

    /* 竹（本体）のデザイン */
    .bamboo {{
        width: {size}px;
        height: {size // 4}px;
        background: linear-gradient(90deg, {bamboo_color} 0%, {bamboo_color} 90%, #e9ecef 90%);
        border-radius: 10px;
        position: relative;
        transform-origin: 70% 50%; /* 回転の軸を右寄りに設定 */
        animation: shishiodoshi-move {speed}s cubic-bezier(0.4, 0, 0.2, 1) infinite;
        z-index: 2;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.2);
    }}

    /* 竹の節（飾り） */
    .bamboo::after {{
        content: '';
        position: absolute;
        left: 40%;
        width: 10px;
        height: 100%;
        background-color: rgba(0,0,0,0.1);
        border-radius: 2px;
    }}

    /* 支点（軸） */
    .pivot {{
        position: absolute;
        width: 20px;
        height: 60px;
        background-color: #4a4e69;
        top: 50%;
        left: calc(50% + {size * 0.2}px); /* 竹の軸に合わせて配置 */
        transform: translateY(-20%);
        border-radius: 5px;
        z-index: 1;
    }}

    /* 石（叩く場所） */
    .stone {{
        position: absolute;
        width: 60px;
        height: 40px;
        background-color: #6c757d;
        border-radius: 50% 50% 10px 10px;
        top: 55%;
        left: calc(50% - {size * 0.4}px);
        z-index: 0;
    }}

    /* アニメーションの動き（キーフレーム） */
    @keyframes shishiodoshi-move {{
        0% {{ transform: rotate(-5deg); }}   /* 水が溜まっている状態 */
        60% {{ transform: rotate(0deg); }}   /* 徐々に重くなる */
        70% {{ transform: rotate(45deg); }}  /* カコーン！（水を流す） */
        80% {{ transform: rotate(-8deg); }}  /* 跳ね返り */
        90% {{ transform: rotate(-5deg); }}  /* 落ち着く */
        100% {{ transform: rotate(-5deg); }}
    }}

</style>

<div class="shishiodoshi-container">
    <div class="stone"></div>
    <div class="pivot"></div>
    <div class="bamboo"></div>
</div>
"""

# HTMLを描画
st.markdown(html_code, unsafe_allow_html=True)

st.write("---")
st.caption("サイドバーのスライダーを動かすと、リアルタイムで動きが変わるっち🍄")
