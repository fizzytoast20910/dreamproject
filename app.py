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
st.markdown(
    "<div class='title'>🧾 공동구매 정산 시스템</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>"
    "개인별 구매 개수와 공동비용을 바탕으로 각자의 최종 부담금을 자동으로 계산합니다."
    "</div>",
    unsafe_allow_html=True
)

# -----------------------------
# 입력 영역
# -----------------------------
left, right = st.columns([1, 2])

with left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("⚙️ 물품 정보")

    # 기준 개당 가격
    base_price = st.number_input(
        "기준 개당 가격 (원)",
        min_value=0,
        value=10000,
        step=100
    )

    # 배송비
    shipping_cost = st.number_input(
        "배송비 (원)",
        min_value=0,
        value=3000,
        step=100
    )

    # 기타 공동비용
    other_cost = st.number_input(
        "기타 공동비용 (원)",
        min_value=0,
        value=0,
        step=100
    )

    # 전체 할인금액
    total_discount = st.number_input(
        "전체 할인금액 (원)",
        min_value=0,
        value=0,
        step=100
    )

    # 공동비용 분배 방법
    distribution_method = st.radio(
        "공동비용 분배 방법",
        [
            "균등 분배",
            "구매 개수 비례"
        ]
    )

    st.caption(
        "📌 균등 분배는 참여자 수로, "
        "구매 개수 비례는 개인의 구매 개수 비율로 공동비용을 나눕니다."
    )

    st.markdown("</div>", unsafe_allow_html=True)


with right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("👥 구매자 입력")

    # 구매 인원 입력
    people_count = st.slider(
        "구매 인원 수",
        min_value=1,
        max_value=50,
        value=5
    )

    # 기본 구매자 데이터 생성
    default_df = pd.DataFrame({
        "구매자": [
            f"구매자 {i + 1}"
            for i in range(people_count)
        ],
        "구매 개수": [1] * people_count
    })

    # 구매자별 정보 입력
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
                step=1,
                required=True
            )
        }
    )

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# 입력값 검증
# -----------------------------

# 구매 개수를 숫자로 변환
df["구매 개수"] = pd.to_numeric(
    df["구매 개수"],
    errors="coerce"
)

# 비어 있거나 잘못된 값은 1개로 처리
df["구매 개수"] = df["구매 개수"].fillna(1)

# 1개 미만이면 1개로 처리
df.loc[df["구매 개수"] < 1, "구매 개수"] = 1

# 정수로 변환
df["구매 개수"] = df["구매 개수"].astype(int)

# 전체 구매 개수
total_quantity = df["구매 개수"].sum()

# 참여자 수
total_people = len(df)


# -----------------------------
# 계산
# -----------------------------

# 상품 총액
df["상품비"] = base_price * df["구매 개수"]

# -----------------------------
# 공동비용 계산
# -----------------------------

# 배송비 + 기타 공동비용
total_common_cost = shipping_cost + other_cost

if distribution_method == "균등 분배":

    # 모든 참여자가 동일한 금액 부담
    common_cost_per_person = (
        total_common_cost / total_people
    )

    df["공동비용 부담"] = common_cost_per_person

else:

    # 구매 개수 비율에 따라 공동비용 분배
    df["공동비용 부담"] = (
        total_common_cost
        * df["구매 개수"]
        / total_quantity
    )


# -----------------------------
# 할인금액 계산
# -----------------------------

# 개인별 구매 개수 비율에 따라 할인금액 배분
df["할인 배분"] = (
    total_discount
    * df["구매 개수"]
    / total_quantity
)


# -----------------------------
# 최종 부담금
# -----------------------------

df["최종 부담금"] = (
    df["상품비"]
    + df["공동비용 부담"]
    - df["할인 배분"]
)


# -----------------------------
# 전체 통계 계산
# -----------------------------

# 상품 총액
total_product_cost = df["상품비"].sum()

# 최종 지출금액
total_final_cost = (
    total_product_cost
    + shipping_cost
    + other_cost
    - total_discount
)

# 계산 결과의 실제 합계
calculated_total = df["최종 부담금"].sum()


# -----------------------------
# 금액 반올림 차이 보정
# -----------------------------

# 소수점 계산으로 인해 약간의 차이가 발생할 수 있으므로
# 마지막 사람에게 차이를 더하거나 빼서 전체 금액을 맞춤
rounding_difference = (
    total_final_cost - calculated_total
)

if abs(rounding_difference) > 0.0001:

    df.loc[df.index[-1], "최종 부담금"] += rounding_difference


# -----------------------------
# 요약 통계
# -----------------------------

st.markdown("### 📊 구매 요약")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "총 구매 인원",
        f"{total_people}명"
    )

with col2:
    st.metric(
        "총 구매 개수",
        f"{total_quantity:,}개"
    )

with col3:
    st.metric(
        "최종 지출금액",
        f"{total_final_cost:,.0f}원"
    )


# -----------------------------
# 추가 전체 비용 정보
# -----------------------------

col4, col5, col6 = st.columns(3)

with col4:
    st.metric(
        "상품 총액",
        f"{total_product_cost:,.0f}원"
    )

with col5:
    st.metric(
        "공동비용",
        f"{total_common_cost:,.0f}원"
    )

with col6:
    st.metric(
        "전체 할인금액",
        f"{total_discount:,.0f}원"
    )


# -----------------------------
# 결과 표
# -----------------------------

st.markdown("### 💰 개인별 정산 결과")

# 화면 표시용 데이터 복사
result = df[
    [
        "구매자",
        "구매 개수",
        "상품비",
        "공동비용 부담",
        "할인 배분",
        "최종 부담금"
    ]
].copy()


# 금액을 보기 좋은 형태로 표시
result["상품비"] = result["상품비"].map(
    lambda x: f"{x:,.0f}원"
)

result["공동비용 부담"] = result["공동비용 부담"].map(
    lambda x: f"{x:,.0f}원"
)

result["할인 배분"] = result["할인 배분"].map(
    lambda x: f"{x:,.0f}원"
)

result["최종 부담금"] = result["최종 부담금"].map(
    lambda x: f"{x:,.0f}원"
)

# 결과 표 출력
st.dataframe(
    result,
    use_container_width=True,
    hide_index=True
)


# -----------------------------
# 전체 금액 검증
# -----------------------------

st.markdown("### ✅ 금액 검증")

# 실제 결과표의 합계
final_sum = df["최종 부담금"].sum()

# 목표 금액과 비교
if abs(final_sum - total_final_cost) < 0.01:

    st.success(
        "개인별 최종 부담금의 합계가 "
        "전체 최종 지출금액과 일치합니다."
    )

else:

    st.error(
        "계산 과정에서 금액 차이가 발생했습니다. "
        "입력값을 확인해주세요."
    )


# -----------------------------
# CSV 다운로드
# -----------------------------

csv = df[
    [
        "구매자",
        "구매 개수",
        "상품비",
        "공동비용 부담",
        "할인 배분",
        "최종 부담금"
    ]
].copy()

csv = csv.to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    "📥 정산 결과 CSV 다운로드",
    data=csv,
    file_name="공동구매_정산결과.csv",
    mime="text/csv"
)


# -----------------------------
# 하단 설명
# -----------------------------

st.markdown("---")

st.caption(
    "행사 운영, 동아리 공동구매, 단체 물품 구매 등의 상황에서 "
    "개인별 부담금을 계산하는 Streamlit 기반 공동구매 정산 시스템"
)
