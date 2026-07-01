import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

# 網頁基礎設定
st.set_page_config(page_title="VOO/QQQ 50% Benchmark", layout="wide")
st.title("📊 VOO & QQQ (50/50) 總回報即時基準線")
st.caption("基準日：2026年6月30日 (初始 NAV = 100.00)")

# 1. 設定基準日與抓取範圍
start_date = "2026-06-30"
today = datetime.date.today().strftime("%Y-%m-%d")
tickers = ["VOO", "QQQ"]

# 2. 自動抓取數據（快取 10 分鐘，避免頻繁請求）
@st.cache_data(ttl=600)
def load_data():
    # 抓取 Adj Close 確保包含股息總回報（Total Return）
    df = yf.download(tickers, start=start_date, end=today)['Adj Close']
    return df

try:
    data = load_data()
    
    # 3. 計算 Total Return 基準線 (以 2026-06-30 為 100 基點)
    normalized_data = data / data.iloc[0]
    normalized_data['Benchmark'] = (normalized_data['VOO'] * 0.5 + normalized_data['QQQ'] * 0.5) * 100
    normalized_data['Return_%'] = normalized_data['Benchmark'] - 100

    # 4. 顯示即時關鍵數據卡片
    latest_nav = normalized_data['Benchmark'].iloc[-1]
    latest_return = normalized_data['Return_%'].iloc[-1]
    last_update = normalized_data.index[-1].strftime('%Y-%m-%d')

    col1, col2, col3 = st.columns(3)
    col1.metric(label="📈 當前 Benchmark 淨值 (NAV)", value=f"{latest_nav:.2f}")
    col2.metric(label="💰 累積總投資報酬率", value=f"{latest_return:+.2f}%")
    col3.metric(label="🕒 數據最後更新日 (美股盤後)", value=last_update)

    st.markdown("---")

    # 5. 繪製互動式即時走勢圖
    st.subheader("📉 基準線淨值走勢走勢 (Total Return)")
    st.line_chart(normalized_data[['Benchmark']], y="Benchmark", use_container_width=True)

    # 6. 顯示數據表格
    with st.expander("查看歷史明細數據"):
        st.dataframe(normalized_data[['VOO', 'QQQ', 'Benchmark', 'Return_%']].tail(10))

except Exception as e:
    st.error(f"數據加載中或發生錯誤。提示：美股開盤期間數據可能有延遲。錯誤訊息: {e}")
