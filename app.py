import streamlit as st
import sqlite3
import pandas as pd
from rapidfuzz import fuzz

# --------------------------------
# PAGE CONFIG
# --------------------------------

st.set_page_config(
    page_title="Smart Shop",
    page_icon="🛍️",
    layout="wide"
)

# --------------------------------
# LOAD DATA
# --------------------------------

@st.cache_data
def load_data():

    conn = sqlite3.connect("inventory.db")

    df = pd.read_sql(
        "SELECT * FROM products",
        conn
    )

    conn.close()

    return df

df = load_data()

# --------------------------------
# HEADER
# --------------------------------

st.title("🛍️ Smart Shop")

st.caption(
    "Stationery • Gifts • Toys"
)

# --------------------------------
# SEARCH
# --------------------------------

search = st.text_input(
    "🔍 Search Product"
)

# --------------------------------
# CATEGORY FILTER
# --------------------------------

categories = ["All"] + sorted(
    df["category"].dropna().unique()
)

selected_category = st.selectbox(
    "Category",
    categories
)

# --------------------------------
# FILTER DATA
# --------------------------------

filtered_df = df.copy()

if selected_category != "All":

    filtered_df = filtered_df[
        filtered_df["category"]
        == selected_category
    ]

# --------------------------------
# TYPO SEARCH
# --------------------------------

if search:

    scores = []

    for _, row in filtered_df.iterrows():

        text = f"""
        {row['clean_name']}
        {row['simple_name']}
        {row['brand']}
        """

        score = fuzz.partial_ratio(
            search.lower(),
            text.lower()
        )

        scores.append(score)

    filtered_df["score"] = scores

    filtered_df = filtered_df[
        filtered_df["score"] > 60
    ]

    filtered_df = filtered_df.sort_values(
        "score",
        ascending=False
    )

# --------------------------------
# PRODUCT GRID
# --------------------------------

cols = st.columns(4)

for i, (_, row) in enumerate(
    filtered_df.iterrows()
):

    with cols[i % 4]:

        st.markdown(
            f"""
            ### {row['simple_name']}
            """
        )

        st.caption(
            row["brand"]
        )

        st.success(
            f"₹ {row['mrp']}"
        )

        qty = (
            row["qty"]
            if pd.notna(row["qty"])
            else 0
        )

        if qty < 5:

            st.error(
                f"⚠ Low Stock ({qty})"
            )

        else:

            st.info(
                f"📦 Stock : {qty}"
            )

        st.button(
            "➕ Add To Cart",
            key=i
        )