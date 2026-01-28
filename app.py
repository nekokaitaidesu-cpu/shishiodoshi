import streamlit as st

# ページ設定
st.set_page_config(page_title="スーパーししおどしParty", page_icon="🎋", layout="centered")

st.title("🎋 スーパーししおどしじぇみにっちスペシャル ver.3.0 (Party Ed.)")
st.write("主さんのリクエストで、ついに限界突破だっち！PCのファンが唸るかもだっち！？😎🎉")

# --- サイドバー設定 ---
st.sidebar.header("⚙️ カスタム設定")
speed = st.sidebar.slider("基本周期（秒）", 1.0, 10.0, 3.0, 0.1)

st.sidebar.subheader("盛り付けオプション 🍄")
show_feeder = st.sidebar.checkbox("上の竹＆水流（主張激しめ）", value=True)
show_detail_bamboo = st.sidebar.checkbox("竹のリアル質感", value=True)
show_detail_stone = st.sidebar.checkbox("石のリアル質感", value=True)
show_splash = st.sidebar.checkbox("水しぶき", value=True)
show_base_deco = st.sidebar.checkbox("基本の装飾（草・キノコ）", value=True)

st.sidebar.markdown("---")
st.sidebar.subheader("🚀 カオス領域")
show_party = st.sidebar.checkbox("🎉 パーティーモード（過労死寸前）", value=False, help="覚悟はいいだっちか？")

# --- CSS 生成ロジック ---

# 竹・石の質感スタイル
bamboo_style = """
    background: linear-gradient(90deg, transparent 38%, #3a7d25 40%, #3a7d25 42%, transparent 44%),
                linear-gradient(90deg, transparent 78%, #3a7d25 80%, #3a7d25 82%, transparent 84%),
                linear-gradient(to bottom, #69b34c 0%, #a4d96c 30%, #a4d96c 70%, #4e8c35 100%);
    border-right: 4px solid #2e631d;
""" if show_detail_bamboo else "background-color: #55a630;"

stone_style = """
    background-color: #808080;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.3'/%3E%3C/svg%3E"),
                      linear-gradient(to bottom right, #a0a0a0, #606060);
    box-shadow: inset 5px 5px 10px rgba(255,255,255,0.2), inset -10px -10px 20px rgba(0,0,0,0.5);
""" if show_detail_stone else "background-color: #6c757d;"

container_bg = "background-image: radial-gradient(circle, #e6e6e6 10%, transparent 10%); background-size: 20px 20px;" if show_detail_stone else ""

# --- HTMLパーツの組み立て ---
html_parts = []

# 1. 背景・基本装飾
if show_base_deco:
    html_parts.append('<div class="grass grass-1"></div><div class="grass grass-2"></div><div class="grass grass-3"></div>')
    html_parts.append('<div class="mushroom"></div>')

# 2. パーティー要素（主さんのリクエスト全部乗せ！）🎉
if show_party:
    html_parts.append('<div class="party-item confetti">🎊</div>') # くす玉
    html_parts.append('<div class="party-item balloon b1">🎈</div><div class="party-item balloon b2">🎈</div>') # 風船
    html_parts.append('<div class="party-item crab">🦀</div>') # カニ
    html_parts.append('<div class="party-item pumpkin">🎃</div>') # カボチャ
    html_parts.append('<div class="party-item hat">🎩</div>') # シルクハット
    html_parts.append('<div class="party-item fan">🪭</div>') # 扇子
    html_parts.append('<div class="party-item grapes">🍇</div><div class="party-item drink">🥤</div>') # 飲食
    html_parts.append('<div class="party-item soccer">⚽</div>') # サッカーボール
    html_parts.append('<div class="party-item curling">🥌</div>') # カーリング

# 3. 構造物
html_parts.append('<div class="stone"></div>')
html_parts.append('<div class="pivot-group"><div class="pivot" style="height: 120px; margin-top: -20px;"></div><div class="pivot"></div></div>')

# 4. 水系（色を濃く変更！）
if show_feeder:
    html_parts.append('<div class="feeder-bamboo"></div><div class="water-stream"></div>')
if show_splash:
    html_parts.append('<div class="splash"></div>')

# 5. メインの竹
html_parts.append('<div class="bamboo"></div>')

inner_html = "".join(html_parts)

# --- 最終的なHTML CSS ---
final_html = f"""
<style>
    .shishiodoshi-container {{
        display: flex; justify_content: center; align_items: center;
        height: 450px; background-color: #f0f2f6; {container_bg}
        border-radius: 20px; position: relative; overflow: hidden; border: 3px solid #d4d7d1;
    }}
    /* --- メインの竹 --- */
    .bamboo {{
        width: 220px; height: 60px; {bamboo_style}
        border-radius: 5px 30px 30px 5px; position: relative; transform-origin: 65% 50%;
        animation: shishiodoshi-move {speed}s cubic-bezier(0.5, 0, 0.3, 1) infinite;
        z-index: 10; box-shadow: 10px 15px 20px rgba(0,0,0,0.3);
    }}
    .bamboo::before {{ content: ''; position: absolute; right: 0; top: 10%; width: 15px; height: 80%; background-color: #222; border-radius: 50%; transform: rotateY(70deg); }}

    /* --- 上の竹 --- */
    .feeder-bamboo {{
        position: absolute; top: 20px; right: 150px; width: 150px; height: 40px; {bamboo_style}
        transform: rotate(-20deg); border-radius: 5px; z-index: 5; box-shadow: 5px 10px 10px rgba(0,0,0,0.2);
    }}
    
    /* --- 水流（ご要望通り青くハッキリと！） --- */
    .water-stream {{
        position: absolute; top: 45px; right: 285px; width: 10px; height: 200px;
        /* 鮮やかな青のグラデーションに変更 */
        background: linear-gradient(to bottom, #4facfe 0%, #00f2fe 100%);
        z-index: 4; border-radius: 4px; opacity: 0.9; /* 不透明度UP */
        box-shadow: 0 0 8px rgba(0, 242, 254, 0.6); /* 発光感を追加 */
    }}

    /* --- 支柱・石 --- */
    .pivot-group {{ position: absolute; top: 50%; left: calc(50% + 50px); transform: translateY(-30%); z-index: 5; display: flex; gap: 10px; }}
    .pivot {{ width: 18px; height: 100px; background: linear-gradient(to right, #4e8c35, #a4d96c, #4e8c35); border-radius: 5px; }}
    .stone {{ position: absolute; width: 140px; height: 90px; {stone_style} border-radius: 50% 40% 30% 40% / 60% 50% 40% 40%; top: 65%; left: calc(50% - 100px); z-index: 1; }}
    .stone::after {{ /* 水たまりも青く */
        content: ''; position: absolute; top: 20%; left: 25%; width: 50%; height: 30%;
        background-color: #00f2fe; /* 濃い青 */ box-shadow: inset 0 0 10px rgba(0,0,0,0.3); border-radius: 50%; opacity: 0.8;
    }}

    /* --- 水しぶき（青く強調） --- */
    .splash {{
        position: absolute; width: 80px; height: 80px; top: 60%; left: calc(50% - 110px);
        background: radial-gradient(circle, #00f2fe 15%, transparent 15%), radial-gradient(circle, #4facfe 10%, transparent 10%);
        background-size: 15px 15px; background-position: 0 0, 7px 7px;
        opacity: 0; z-index: 15; animation: splash-anim {speed}s infinite;
    }}
    /* --- 基本装飾（草・キノコ） --- */
    .grass {{ position: absolute; bottom: 20px; width: 0; height: 0; border-left: 10px solid transparent; border-right: 10px solid transparent; border-bottom: 40px solid #2d6a4f; transform-origin: bottom center; z-index: 2;}}
    .grass-1 {{ left: 20%; transform: rotate(-15deg); }} .grass-2 {{ left: 22%; transform: rotate(10deg); height: 50px; border-bottom-color: #40916c; }} .grass-3 {{ right: 20%; transform: rotate(5deg); }}
    .mushroom {{ position: absolute; bottom: 40px; right: 50px; width: 30px; height: 30px; background: radial-gradient(circle at 30% 30%, #ff0055, #990033); border-radius: 50% 50% 10% 10%; z-index: 20; animation: glow 2s ease-in-out infinite alternate; }}
    .mushroom::after {{ content: ''; position: absolute; bottom: -15px; left: 8px; width: 14px; height: 20px; background: #fff; border-radius: 4px; z-index: -1; }}

    /* --- 🎉 パーティーモードのカオスな住人たち 🎉 --- */
    .party-item {{ position: absolute; font-size: 30px; z-index: 30; }}
    
    .confetti {{ top: 10px; left: 50%; animation: swing 2s infinite ease-in-out alternate; font-size: 40px; }}
    .balloon {{ opacity: 0.8; font-size: 45px; }}
    .b1 {{ top: 100px; left: 30px; animation: float 4s ease-in-out infinite alternate; }}
    .b2 {{ top: 120px; right: 30px; animation: float 5s ease-in-out infinite alternate-reverse; }}
    .crab {{ bottom: 30px; left: 100px; animation: crab-walk 3s steps(10) infinite alternate; }}
    .pumpkin {{ bottom: 60px; right: 100px; animation: glow-pumpkin 1.5s infinite alternate; }}
    .hat {{ top: 45%; left: 45%; animation: spin {speed}s linear infinite; }} /* 竹と一緒に回る帽子 */
    .fan {{ top: 20px; right: 20px; animation: fan-swing 1s infinite alternate; }}
    .grapes {{ bottom: 80px; left: 20px; }}
    .drink {{ bottom: 80px; left: 55px; transform: rotate(15deg); }}
    .soccer {{ bottom: 15px; left: -30px; animation: roll-pass 8s linear infinite; }}
    .curling {{ bottom: 10px; right: -40px; font-size: 25px; animation: slide-stone 10s linear infinite; }}

    /* --- アニメーション定義 --- */
    @keyframes shishiodoshi-move {{ 0% {{ transform: rotate(-8deg); }} 55% {{ transform: rotate(0deg); }} 65% {{ transform: rotate(50deg); }} 75% {{ transform: rotate(-12deg); }} 85% {{ transform: rotate(-8deg); }} 100% {{ transform: rotate(-8deg); }} }}
    @keyframes splash-anim {{ 0%, 62% {{ opacity: 0; transform: scale(0.5); }} 65% {{ opacity: 1; transform: scale(1.5) translateY(-20px); }} 75% {{ opacity: 0; transform: scale(2.0); }} 100% {{ opacity: 0; }} }}
    @keyframes glow {{ from {{ box-shadow: 0 0 5px #ff0055; }} to {{ box-shadow: 0 0 20px #ff0055, 0 0 30px #ff99cc; }} }}
    
    /* パーティー用アニメーション */
    @keyframes float {{ from {{ transform: translateY(0) rotate(5deg); }} to {{ transform: translateY(-20px) rotate(-5deg); }} }}
    @keyframes swing {{ from {{ transform: rotate(-10deg); }} to {{ transform: rotate(10deg); }} }}
    @keyframes crab-walk {{ from {{ transform: translateX(0); }} to {{ transform: translateX(50px); }} }}
    @keyframes glow-pumpkin {{ from {{ filter: brightness(1); }} to {{ filter: brightness(1.5) drop-shadow(0 0 10px orange); }} }}
    @keyframes spin {{ 0% {{ transform: rotate(0deg) translateY(-20px); }} 100% {{ transform: rotate(360deg) translateY(-20px); }} }}
    @keyframes fan-swing {{ from {{ transform: rotate(-20deg); }} to {{ transform: rotate(20deg); }} }}
    @keyframes roll-pass {{ 0% {{ left: -30px; transform: rotate(0deg); }} 50% {{ left: 400px; transform: rotate(720deg); }} 50.01% {{ left: 400px; opacity: 0; }} 100% {{ left: -30px; opacity: 0; }} }}
    @keyframes slide-stone {{ 0% {{ right: -40px; }} 40% {{ right: 350px; transform: rotate(-180deg); }} 100% {{ right: 350px; opacity: 0; }} }}
</style>

<div class="shishiodoshi-container">
    {inner_html}
</div>
"""

st.markdown(final_html, unsafe_allow_html=True)
