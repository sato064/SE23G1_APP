import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd
import japanize_matplotlib
import requests
import json
import os

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

st.set_page_config(
    page_title="Inspection Dashboard",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        'About': """
        # Inspection Dashboard
        インスペクション結果の可視化を行うアプリケーションです．
        """
    })


y = [0, 0, 0, 0]
filename = 'data/srs_inspection.csv'
with open(filename, encoding='utf8', newline='') as f:
    csvreader = csv.reader(f)
    for row in csvreader:
        row_num = 0
        for content in row:
            row_num += 1
            if(content == '1'):
                y[row_num - 2] = y[row_num - 2] + 1
                
y = [25,6,7,6]
# データの準備
def get_data():
    data = np.array(
        [[1872, 2244, 1236, 1200], y]
    )
    row_labels = ["今までの平均", "今回のインスペクション"]
    col_labels = ["不足・不明", "誤り", "改善要求", "文書形式・誤字脱字・命名規則"]

    return pd.DataFrame(data, index=row_labels, columns=col_labels,)

df = get_data()

# 正規化する
df = df.div(df.sum(axis=1), axis=0)

n_rows, n_cols = df.shape
positions = np.arange(n_rows)
offsets = np.zeros(n_rows, dtype=df.values.dtype)
colors = plt.get_cmap("tab20c")(np.linspace(0, 1, n_cols))
fig, ax = plt.subplots()
ax.set_yticks(positions)
ax.set_yticklabels(df.index)

for i in range(len(df.columns)):
    # 棒グラフを描画する。
    bar = ax.barh(
        positions, df.iloc[:, i], left=offsets, color=colors[i], label=df.columns[i]
    )
    offsets += df.iloc[:, i]

    # 棒グラフのラベルを描画する。
    for rect, value in zip(bar, df.iloc[:, i]):
        cx = rect.get_x() + rect.get_width() / 2
        cy = rect.get_y() + rect.get_height() / 2
        ax.text(cx, cy, f"{value:.0%}", color="k", ha="center", va="center")

ax.legend(bbox_to_anchor=(1, 1))

short = "情報の不足・不明が多く指摘されています．不足・不明を指摘するコメントは，間違いを指摘しているコメントではありません．再度，自分たちの作った文書が誰の目から見ても一意に定まる表現になっているか確認しましょう．また，チーム内で解釈が分かれる表現がないか相互チェックを行うのも，効果的です．"
miss = "情報の誤りが多く指摘されています．誤りは，多くの場合モデルや要件の確認不足や型選択のミスなど，確認で修正ができるものです 再度，要件や過去の設計文書と照らし合わせて，矛盾点や見落としが発生していないか確認しましょう． また，チーム内でこういた見落としがないか相互チェックを行うのも，効果的です．"
enhance = "改善提案が多く指摘されています．改善提案は，間違いが指摘されているわけではありません．ただし，システムの要件について自分たちの設計で完全に満たされているものか今一度確認するとともに提案された改善案の周辺知識をしっかりと学習すると良いでしょう．"
other = "形式・誤字脱字・命名規則が多く指摘されています．形式・誤字脱字は，事前のチェックで防げた指摘です． 今一度文書の形式や命名規則について再度学習を行い，チーム内で確認してからインスペクションを行うとよいでしょう．"
df = pd.DataFrame({'第1回機能仕様書インスペクション結果': y},
                    index=["不足・不明", "誤り", "改善要求", "文書形式・誤字脱字・命名規則"])

st.title("第1回機能仕様書インスペクションの結果") # タイトル
st.subheader('指摘数')
st.table(df.T) # 表の表示
st.subheader('指摘数の割合')
st.pyplot(plt, transparent=True) # グラフ表示
st.subheader('アドバイス文')
st.info(short)
st.subheader('振り返り')

f = open('files/srs_1.txt', 'r')
data = f.read()
if data == "T":
    sub = True
else:
    sub = False
f.close()

if not sub:
    with st.form("my_form", clear_on_submit=False):
        review = st.text_area('今回のインスペクションをの振り返りを記入してください')
        submitted = st.form_submit_button("記録")

    if submitted:
        url = "https://api.github.com/repos/sato064/SE23G1_APP/issues/1/comments"
        headers = {"Accept": "application/vnd.github+json",
            "Authorization": GITHUB_TOKEN,
        "X-GitHub-Api-Version": "2022-11-28"
        }
        data = {'body': 'SRS1\n' + review}
        res = requests.post(url, headers=headers,data=json.dumps(data))
        print(res)

else:
    f = open('files/srs_1_com.txt', 'r')
    data = f.read()
    st.text(data)
    f.close()
