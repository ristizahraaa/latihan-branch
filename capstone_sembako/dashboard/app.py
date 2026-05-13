import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Dashboard Harga Sembako Nasional",
    layout="wide"
)

# =========================
# STYLE
# =========================
st.markdown(
    """
    <style>
    .main {
        background-color: #f7f9fc;
    }

    .block-container {
        padding: 2rem 3rem;
    }

    div[data-testid="metric-container"] {
        background-color: white;
        border-radius: 15px;
        padding: 18px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #eef0f3;
    }

    h1, h2, h3 {
        color: #111827;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv('data/processed/sembako_nasional_features.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("## 🎛️ Filter Dashboard")
st.sidebar.markdown("---")

komoditas_list = st.sidebar.multiselect(
    "📦 Pilih Komoditas",
    df['komoditas'].unique(),
    default=df['komoditas'].unique()
)

min_date = df['date'].min()
max_date = df['date'].max()

selected_date = st.sidebar.date_input(
    "📅 Rentang Tanggal",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

st.sidebar.markdown("---")

st.sidebar.info(
    "💡 Tips:\n"
    "- Filter komoditas untuk fokus analisis\n"
    "- Persempit tanggal untuk lihat tren detail"
)

# =========================
# FILTER DATA (INI WAJIB DI SINI!)
# =========================
filtered_df = df[
    (df['komoditas'].isin(komoditas_list)) &
    (df['date'] >= pd.to_datetime(selected_date[0])) &
    (df['date'] <= pd.to_datetime(selected_date[1]))
]

# safety check
if filtered_df.empty:
    st.warning("Data tidak tersedia untuk filter yang dipilih.")
    st.stop()

# =========================
# KPI
# =========================
avg_price = filtered_df['price'].mean()

avg_per_komoditas = filtered_df.groupby('komoditas')['price'].mean()
komoditas_termahal = avg_per_komoditas.idxmax()
komoditas_termurah = avg_per_komoditas.idxmin()

trend_change = filtered_df.sort_values('date').groupby('komoditas')['price'].agg(
    lambda x: ((x.iloc[-1] - x.iloc[0]) / x.iloc[0]) * 100 if len(x) > 1 else 0
).sort_values(ascending=False)

komoditas_naik = trend_change.idxmax()
komoditas_turun = trend_change.idxmin()

# =========================
# HEADER
# =========================
st.title("📊 Dashboard Harga Sembako Nasional")
st.caption("Analisis harga sembako Indonesia (2022–2026)")

st.markdown("---")

# =========================
# METRICS
# =========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Data", len(filtered_df))

with col2:
    st.metric("Rata-rata Harga", f"Rp {avg_price:,.0f}")

with col3:
    st.metric("Komoditas Termahal", komoditas_termahal)

with col4:
    st.metric("Komoditas Termurah", komoditas_termurah)

st.markdown("---")

# =========================
# INSIGHT
# =========================
st.subheader("🧠 Insight Utama")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Level Harga")
    st.write(f"🏆 Termahal: **{komoditas_termahal}**")
    st.write(f"💸 Termurah: **{komoditas_termurah}**")

with col2:
    st.markdown("### 📈 Perubahan Harga")
    st.write(f"🔥 Naik tertinggi: **{komoditas_naik}** (+{trend_change.max():.2f}%)")
    st.write(f"📉 Turun terbesar: **{komoditas_turun}** ({trend_change.min():.2f}%)")

st.markdown("---")

st.write(f"💰 Rata-rata harga keseluruhan: **Rp {avg_price:,.0f}**")

st.markdown("---")

# =========================
# TREND
# =========================
st.subheader("📈 Tren Harga per Komoditas")

line_fig = px.line(
    filtered_df,
    x='date',
    y='price',
    color='komoditas',
    facet_col='komoditas',
    facet_col_wrap=2,
    template='plotly_white'
)

st.plotly_chart(line_fig, use_container_width=True)

# =========================
# DISTRIBUSI
# =========================
st.subheader("📊 Distribusi Harga")

hist_fig = px.histogram(
    filtered_df,
    x='price',
    color='komoditas',
    facet_col='komoditas',
    facet_col_wrap=2,
    template='plotly_white'
)

st.plotly_chart(hist_fig, use_container_width=True)

# =========================
# BOXPLOT
# =========================
st.subheader("📦 Perbandingan Harga Antar Komoditas")

box_fig = px.box(
    filtered_df,
    x='komoditas',
    y='price',
    color='komoditas',
    template='plotly_white'
)

st.plotly_chart(box_fig, use_container_width=True)

# =========================
# STATISTIK DESKRIPTIF
# =========================
st.subheader("📌 Statistik Deskriptif")

stats = filtered_df.groupby('komoditas')['price'].describe().sort_values('mean', ascending=False)

st.dataframe(
    stats.style.format("{:,.0f}").background_gradient(cmap="Blues"),
    use_container_width=True
)

# =========================
# DATA PREVIEW
# =========================
st.subheader("🧾 Data Preview")

st.dataframe(
    filtered_df.sort_values('date', ascending=False).head(20),
    use_container_width=True
)

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("Dashboard Sembako Nasional")