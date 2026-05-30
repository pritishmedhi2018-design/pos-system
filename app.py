import streamlit as st
import sqlite3
import pandas as pd

from rapidfuzz import fuzz
from deep_translator import GoogleTranslator

# ====================================
# PAGE CONFIG
# ====================================

st.set_page_config(
    page_title="Smart Shop",
    page_icon="🛍️",
    layout="wide"
)

# ====================================
# LOAD DATA
# ====================================

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

# ====================================
# ASSAMESE DICTIONARY
# ====================================

ASSAMESE_MAP = {

    "কলম": "pen",
    "নীলা কলম": "blue pen",
    "ক'লা কলম": "black pen",

    "পেঞ্চিল": "pencil",
    "পেন্সিল": "pencil",

    "খাতা": "notebook",
    "বহী": "notebook",
    "নোটবুক": "notebook",

    "ৰাবাৰ": "eraser",
    "ইৰেজাৰ": "eraser",

    "স্কেল": "scale",
    "ৰুলাৰ": "scale",

    "ফাইল": "file",
    "ষ্টিক ফাইল": "stick file",

    "বুক কভাৰ": "book cover",
    "কভাৰ": "cover",

    "লেবেল": "label",
    "নাম লেবেল": "name label",

    "মাৰ্কাৰ": "marker",

    "গ্লু": "glue",
    "গাম": "gum",

    "কেঁচি": "scissor",

    "গিফ্ট": "gift",
    "উপহাৰ": "gift",

    "খেলনা": "toy",

    "কালাৰ পেঞ্চিল": "colour pencil",
    "ৰং পেঞ্চিল": "colour pencil",

    "ক্ৰেয়ন": "crayon"
}

# ====================================
# CART SESSION
# ====================================

if "cart" not in st.session_state:
    st.session_state.cart = {}

# ====================================
# HEADER
# ====================================

st.title("🛍️ Smart Shop")
st.caption("Stationery • Gifts • Toys")

# ====================================
# SEARCH
# ====================================

st.subheader("🔍 Product Search")

search = st.text_input(
    "Search Product",
    placeholder="Type product name in English or Assamese",
    label_visibility="collapsed"
)

search_query = search.strip().lower()

# ====================================
# ASSAMESE TRANSLATION
# ====================================

if search_query:

    if search_query in ASSAMESE_MAP:

        search_query = ASSAMESE_MAP[
            search_query
        ]

    else:

        try:

            translated = GoogleTranslator(
                source="auto",
                target="en"
            ).translate(search_query)

            if translated:
                search_query = translated.lower()

        except:
            pass

# Optional Debug

if search and search_query != search.lower():

    st.info(
        f"Searching as: {search_query}"
    )

# ====================================
# CATEGORY FILTER
# ====================================

categories = ["All"]

if "category" in df.columns:

    categories += sorted(
        df["category"]
        .dropna()
        .astype(str)
        .unique()
    )

selected_category = st.selectbox(
    "Category",
    categories
)

# ====================================
# FILTER PRODUCTS
# ====================================

filtered_df = df.copy()

if selected_category != "All":

    filtered_df = filtered_df[
        filtered_df["category"].astype(str)
        == selected_category
    ]

# ====================================
# SEARCH LOGIC
# ====================================

if search_query:

    scores = []

    for _, row in filtered_df.iterrows():

        text = f"""
        {row.get('clean_name','')}
        {row.get('simple_name','')}
        {row.get('brand','')}
        {row.get('category','')}
        """

        text = text.lower()

        score = max(

            fuzz.partial_ratio(
                search_query,
                text
            ),

            fuzz.token_sort_ratio(
                search_query,
                text
            )

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

# ====================================
# SIDEBAR CART
# ====================================

with st.sidebar:

    st.header("🛒 Shopping Cart")

    total = 0

    if not st.session_state.cart:

        st.info("Cart Empty")

    else:

        for product_name, item in st.session_state.cart.items():

            qty = item["qty"]
            price = float(item["price"])

            subtotal = qty * price

            total += subtotal

            st.write(
                f"**{product_name}**"
            )

            col1, col2, col3 = st.columns([1,1,1])

            if col1.button(
                "➖",
                key=f"minus_{product_name}"
            ):

                item["qty"] -= 1

                if item["qty"] <= 0:
                    del st.session_state.cart[
                        product_name
                    ]

                st.rerun()

            col2.write(
                f"{qty}"
            )

            if col3.button(
                "➕",
                key=f"plus_{product_name}"
            ):

                item["qty"] += 1

                st.rerun()

            st.write(
                f"₹{price:.2f} × {qty}"
            )

            st.write(
                f"Subtotal: ₹{subtotal:.2f}"
            )

            st.divider()

        st.success(
            f"Total = ₹{total:.2f}"
        )

        if st.button(
            "🗑 Clear Cart"
        ):

            st.session_state.cart = {}

            st.rerun()

# ====================================
# PRODUCT GRID
# ====================================

cols = st.columns(3)

for i, (_, row) in enumerate(
    filtered_df.iterrows()
):

    with cols[i % 3]:

        simple_name = (
            str(row["simple_name"])
            if pd.notna(row["simple_name"])
            else "Unknown Product"
        )

        actual_name = (
            str(row["clean_name"])
            if pd.notna(row["clean_name"])
            else ""
        )

        mrp = (
            float(row["mrp"])
            if pd.notna(row["mrp"])
            else 0
        )

        cost = (
            float(row["purchase_price"])
            if pd.notna(row["purchase_price"])
            else 0
        )

        qty = (
            int(row["qty"])
            if pd.notna(row["qty"])
            else 0
        )

        st.markdown(
            f"### 📦 {simple_name}"
        )

        st.caption(
            actual_name
        )

        st.markdown(
            f"""
            <h2 style="
            color:#198754;
            font-weight:bold;
            ">
            ₹ {mrp:.2f}
            </h2>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            f"Cost Price: ₹ {cost:.2f}"
        )

        if qty < 5:

            st.error(
                f"⚠ Low Stock ({qty})"
            )

        else:

            st.info(
                f"📦 Stock: {qty}"
            )

        if st.button(
            "🛒 Add To Cart",
            key=f"cart_{i}"
        ):

            if simple_name in st.session_state.cart:

                st.session_state.cart[
                    simple_name
                ]["qty"] += 1

            else:

                st.session_state.cart[
                    simple_name
                ] = {
                    "price": mrp,
                    "qty": 1
                }

            st.rerun()

        st.divider()
