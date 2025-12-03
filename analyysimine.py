import pandas as pd
from konstandid import *
from abifunktsioonid import *
import matplotlib.pyplot as plt
import streamlit as st

def analyysi():
    st.header("📊 Analüüs ja graafikud")

    # Kasutame andmeid otse session_state-ist
    if "sisestused_df" not in st.session_state or st.session_state["sisestused_df"].empty:
        st.info("Andmed puuduvad. Palun lae fail külgribalt või sisesta andmed käsitsi.")
        return

    df_raw = st.session_state["sisestused_df"].copy()
    df, eemaldatud = puhasta_andmed(df_raw)

    if eemaldatud > 0:
        st.warning(f"{eemaldatud} rida eemaldati analüüsist (vigased andmed või summa=0).")

    if df.empty:
        st.warning("Pärast puhastust ei jäänud kehtivaid ridu.")
        return

    # -----------------------------
    # 1. FILTRID
    # -----------------------------
    st.markdown("### 1. Filtrid")

    col1, col2 = st.columns(2)
    with col1:
        tyyp_filter = st.selectbox(
            "Millist tüüpi kirjeid vaadata?",
            ["Kõik", "Ainult kulud", "Ainult sissetulekud"],
        )

    with col2:
        min_date = df["Kuupäev"].min().date()
        max_date = df["Kuupäev"].max().date()
        date_range = st.date_input(
            "Vali kuupäevavahemik",
            (min_date, max_date),
            format="YYYY-MM-DD",
        )

    # Filter type
    if tyyp_filter == "Ainult kulud":
        df = df[df["Tulu/kulu"] == "Kulu"]
    elif tyyp_filter == "Ainult sissetulekud":
        df = df[df["Tulu/kulu"] == "Tulu"]

    # Filter by date range
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start, end = date_range
        df = df[(df["Kuupäev"].dt.date >= start) & (df["Kuupäev"].dt.date <= end)]

    if df.empty:
        st.warning("Filtrite järel andmeid ei jäänud.")
        return

    # -----------------------------
    # 2. KOGUPILT KATEGOORIATE KAUPA
    # -----------------------------
    st.markdown("### 2. Kogupilt kategooriate kaupa")

    by_cat = df.groupby("Kategooria")["Summa"].sum().sort_values(ascending=False)
    total = by_cat.sum()

    summary = pd.DataFrame({
        "Summa": by_cat,
        "Osakaal %": (by_cat / total * 100).round(1)
    })

    st.write("Kokku:", float(total))
    st.dataframe(summary)

    # Chart colors
    def get_category_color(cat):
        t = df[df["Kategooria"] == cat]["Tulu/kulu"].iloc[0]
        return "green" if t == "Tulu" else "red"

    colors = [get_category_color(cat) for cat in by_cat.index]

    # Main chart
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(by_cat.index.astype(str), by_cat.values, color=colors)

    # Bar labels
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.0f}", (bar.get_x() + bar.get_width()/2, h),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", fontsize=10)

    ax.set_title("Summa kategooriate kaupa (roheline=Tulu, punane=Kulu)")
    ax.set_ylabel("Summa")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    st.pyplot(fig)

    # -----------------------------
    # 3. DETAILNE AJA ANALÜÜS
    # -----------------------------
    st.markdown("### 3. Ajavahemiku analüüs ühe kategooria kaupa")

    valitav_kategooria = st.selectbox("Vali kategooria", by_cat.index)
    ajavahemik = st.selectbox("Ajavahemik", ["Päev", "Nädal", "Kuu", "Kvartal", "Aasta"])

    df_kat = df[df["Kategooria"] == valitav_kategooria]

    if not df_kat.empty:
        if ajavahemik == "Päev":
            grp = df_kat.groupby(df_kat["Kuupäev"].dt.date)["Summa"].sum()
        elif ajavahemik == "Nädal":
            grp = df_kat.groupby(df_kat["Kuupäev"].dt.to_period("W"))["Summa"].sum()
        elif ajavahemik == "Kuu":
            grp = df_kat.groupby(df_kat["Kuupäev"].dt.to_period("M"))["Summa"].sum()
        elif ajavahemik == "Kvartal":
            grp = df_kat.groupby(df_kat["Kuupäev"].dt.to_period("Q"))["Summa"].sum()
        else:
            grp = df_kat.groupby(df_kat["Kuupäev"].dt.to_period("Y"))["Summa"].sum()

        labels = grp.index.astype(str)

        fig2, ax2 = plt.subplots(figsize=(10, 4))
        bars2 = ax2.bar(labels, grp.values,
                        color=get_category_color(valitav_kategooria))

        # Numeric labels
        for bar in bars2:
            h = bar.get_height()
            ax2.annotate(f"{h:.0f}", (bar.get_x() + bar.get_width()/2, h),
                         xytext=(0, 4), textcoords="offset points",
                         ha="center", fontsize=10)

        ax2.set_title(f"{valitav_kategooria} – {ajavahemik} lõikes")
        plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")
        st.pyplot(fig2)

    # -----------------------------
    # 4. VÕRDLUSGRAAFIK (UUS)
    # -----------------------------
    st.markdown("### 4. Kategooriate võrdlusgraafik")

    st.write("Vali kuni 2 kategooriat, mida soovid omavahel võrrelda:")

    # Checkbox-based selection UI
    selected = []
    for cat in by_cat.index:
        if st.checkbox(cat):
            selected.append(cat)

    if len(selected) == 0:
        st.info("Vali vähemalt 1 kategooria.")
    elif len(selected) > 2:
        st.warning("Saad valida maksimaalselt 2 kategooriat.")
    else:
        # Prepare data
        comp = df[df["Kategooria"].isin(selected)]
        comp_group = comp.groupby("Kategooria")["Summa"].sum()

        # Colors based on income/expense
        comp_colors = [get_category_color(cat) for cat in comp_group.index]

        figc, axc = plt.subplots(figsize=(8, 5))
        barsc = axc.bar(comp_group.index.astype(str), comp_group.values, color=comp_colors)

        # Numeric bar labels
        for bar in barsc:
            h = bar.get_height()
            axc.annotate(f"{h:.0f}", (bar.get_x() + bar.get_width()/2, h),
                         xytext=(0, 4), textcoords="offset points",
                         ha="center", fontsize=10)

        axc.set_title("Kategooriate võrdlus")
        axc.set_ylabel("Summa")
        st.pyplot(figc)
