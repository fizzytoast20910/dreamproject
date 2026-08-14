import streamlit as st
import pandas as pd

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="공동구매 정산 시스템",
    page_icon="🧾",
    layout="wide"
)

# -----------------------------
# 스타일 적용
# -----------------------------
st.markdown("""
<style>
    .main {
        background-color: #f6f8fb;
    }

    .title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1f2937;
        margin-bottom: 0.3rem;
    }

    .subtitle {
        font-size: 1.05rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }

    .card {
        background: white;
        padding: 1.2rem;
        border-radius: 18px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 헤더
# -----------------------------
st.markdown("<div class='title'>🧾 공동구매 정산 시스템</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>구매 개수에 따라 개당 가격이 0.5%씩 할인되며, 개인별 총 지출 금액을 자동으로 계산합니다.</div>", unsafe_allow_html=True)

# -----------------------------
# 입력 영역
# -----------------------------
left, right = st.columns([1, 2])

with left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("⚙️ 기본 설정")

    base_price = st.number_input(
        "기준 개당 가격 (원)",
        min_value=100,
        value=10000,
        step=100
    )

    people_count = st.slider(
        "구매 인원 수",
        min_value=1,
        max_value=20,
        value=5
    )

    max_discount = st.slider(
        "최대 할인율 (%)",
        min_value=5,
        max_value=50,
        value=30
    )

    st.caption("📌 구매 개수가 1개 증가할 때마다 0.5% 할인 적용")
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("👥 구매자 입력")

    default_df = pd.DataFrame({
        "구매자": [f"구매자 {i+1}" for i in range(people_count)],
        "구매 개수": [1] * people_count
    })

    df = st.data_editor(
        default_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "구매자": st.column_config.TextColumn(
                "구매자 이름",
                required=True
            ),
            "구매 개수": st.column_config.NumberColumn(
                "구매 개수",
                min_value=1,
                step=1
            )
        }
    )

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# 계산
# -----------------------------
df["구매 개수"] = pd.to_numeric(df["구매 개수"], errors="coerce").fillna(1).astype(int)

df["할인율(%)"] = (df["구매 개수"] - 1) * 0.5
df["할인율(%)"] = df["할인율(%)"].clip(upper=max_discount)

df["개당 가격"] = base_price * (1 - df["할인율(%)"] / 100)
df["개인 총액"] = df["개당 가격"] * df["구매 개수"]

# -----------------------------
# 요약 통계
# -----------------------------
st.markdown("### 📊 구매 요약")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "총 구매 인원",
        f"{len(df)}명"
    )

with col2:
    st.metric(
        "총 구매 개수",
        f"{df['구매 개수'].sum():,}개"
    )

with col3:
    st.metric(
        "전체 지출 금액",
        f"{df['개인 총액'].sum():,.0f}원"
    )

# -----------------------------
# 결과 표
# -----------------------------
st.markdown("### 💰 개인별 정산 결과")

result = df.copy()
result["할인율"] = result["할인율(%)"].map(lambda x: f"{x:.1f}%")
result["개당 가격"] = result["개당 가격"].map(lambda x: f"{x:,.0f}원")
result["개인 총액"] = result["개인 총액"].map(lambda x: f"{x:,.0f}원")

st.dataframe(
    result[["구매자", "구매 개수", "할인율", "개당 가격", "개인 총액"]],
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# CSV 다운로드
# -----------------------------
csv = df[["구매자", "구매 개수", "할인율(%)", "개당 가격", "개인 총액"]].to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    "📥 정산 결과 CSV 다운로드",
    data=csv,
    file_name="공동구매_정산결과.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("행사 운영, 동아리 공동구매, 단체 물품 정산 등에 활용할 수 있는 Streamlit 기반 공동구매 비용 계산 시스템")
