import streamlit as st
import pulp
import pandas as pd
import matplotlib.pyplot as plt

# ShiftSchedulerクラスとoptimization関数をインポート
from ShiftScheduler import ShiftScheduler

def optimization(calendar_df, staff_df):
    shift_sch = ShiftScheduler()
    shift_sch.set_data(staff_df, calendar_df)
    shift_sch.build_model()
    shift_sch.solve()

    return shift_sch.sch_df

# タイトル
st.title("シフトスケジューリングアプリ")

# セッション状態の初期化
if "shift_schedule" not in st.session_state:
    st.session_state["shift_schedule"] = None

# サイドバー
st.sidebar.header("データのアップロード")
calendar_file = st.sidebar.file_uploader("カレンダー", type=["csv"])
staff_file = st.sidebar.file_uploader("スタッフ", type=["csv"])

# タブ
tab1, tab2, tab3 = st.tabs(["カレンダー情報", "スタッフ情報", "シフト表作成"])

# カレンダー情報タブ
with tab1:
    st.markdown("## カレンダー情報")
    if calendar_file is not None:
        # CSVファイルをデータフレームとして読み込む
        calendar_df = pd.read_csv(calendar_file)
        st.dataframe(calendar_df)
    else:
        st.info("カレンダー情報のCSVファイルをアップロードしてください。")

# スタッフ情報タブ
with tab2:
    st.markdown("## スタッフ情報")
    if staff_file is not None:
        # CSVファイルをデータフレームとして読み込む
        staff_df = pd.read_csv(staff_file)
        st.dataframe(staff_df)
    else:
        st.info("スタッフ情報のCSVファイルをアップロードしてください。")

# シフト表作成タブ
with tab3:
    st.markdown("## 最適化結果")
    
    # 両方のファイルがアップロードされた場合にのみ最適化ボタンを表示
    if calendar_file is not None and staff_file is not None:
        if st.button("最適化実行"):
            st.session_state["shift_schedule"] = optimization(calendar_df, staff_df)
        
    # シフトスケジュールが存在する場合に表示
    if st.session_state["shift_schedule"] is not None:
        st.markdown("### 最適化されたシフト表")
        st.dataframe(st.session_state["shift_schedule"])
        
        # シフト数の合計計算
        shift_totals = st.session_state["shift_schedule"].sum(axis=1)
        
        # 棒グラフの描画
        st.markdown("## シフト数の充足確認")
        st.bar_chart(shift_totals)
         # 日ごとの合計計算（各日の出勤人数の合計）
        daily_totals = st.session_state["shift_schedule"].sum(axis=0)
        
        # 棒グラフの描画（各日のシフト人数）
        st.markdown("## スタッフの希望の確認")
        st.bar_chart(daily_totals)

         # 責任者の合計計算（責任者フラグを使用）
        leader_totals = (st.session_state["shift_schedule"].T * staff_df.set_index("スタッフID")["責任者フラグ"]).sum(axis=1)
        
        # 責任者のシフト数を棒グラフで表示
        st.markdown("## 責任者の合計シフト数の充足確認")
        st.bar_chart(leader_totals)

        csv = st.session_state["shift_schedule"].to_csv(index=True).encode('utf-8')
        st.download_button(
            label="シフト表をダウンロード",
            data=csv,
            file_name='shift_schedule.csv',
            mime='text/csv',
        )
    else:
        st.info("最適化を実行してください。")

