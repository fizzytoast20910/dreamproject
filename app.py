# ------------------------------------------------
# 검증 (결과 출력 전에 수행)
# ------------------------------------------------

# 1. 구매 개수 10억 이상 경고
MAX_QUANTITY = 1_000_000_000
too_large = df[df["구매 개수"] >= MAX_QUANTITY]

if not too_large.empty:

    @st.dialog("⚠️ 입력값 경고")
    def quantity_warning():
        st.error(
            "구매 개수가 **10억 개 이상**으로 입력되었습니다.\n\n"
            "현실적인 범위를 초과하는 값입니다."
        )

        st.write("#### 문제가 있는 구매자")

        st.dataframe(
            too_large[["구매자", "구매 개수"]],
            use_container_width=True,
            hide_index=True
        )

        st.info("구매 개수를 수정한 뒤 다시 계산해주세요.")

    quantity_warning()
    st.stop()


# 2. 할인금액 검증
max_possible_discount = total_product_cost + total_common_cost

if total_discount > max_possible_discount:

    @st.dialog("⚠️ 할인금액 오류")
    def discount_warning():
        st.error(
            f"전체 할인금액({total_discount:,.0f}원)이\n\n"
            f"총 지출 가능 금액({max_possible_discount:,.0f}원)보다 큽니다."
        )

        st.info("할인금액을 줄인 뒤 다시 계산해주세요.")

    discount_warning()
    st.stop()


# 3. 개인별 최종 부담금 음수 검증
if (df["최종 부담금"] < 0).any():

    @st.dialog("⚠️ 계산 오류")
    def negative_warning():
        st.error(
            "일부 구매자의 최종 부담금이 음수가 됩니다.\n\n"
            "할인금액을 줄이거나 구매 개수를 확인해주세요."
        )

        st.write("#### 음수 부담금이 발생한 구매자")

        negative_df = df.loc[
            df["최종 부담금"] < 0,
            ["구매자", "최종 부담금"]
        ].copy()

        negative_df["최종 부담금"] = negative_df["최종 부담금"].map(
            lambda x: f"{x:,.0f}원"
        )

        st.dataframe(
            negative_df,
            use_container_width=True,
            hide_index=True
        )

        st.info("입력값을 수정한 뒤 다시 계산해주세요.")

    negative_warning()
    st.stop()
