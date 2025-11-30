import pandas as pd
from konstandid import *
from abifunkfunktsioonid import *
import matplotlib.pyplot as plt
import streamlit as st

def analyysi():
    st.header("📊 Analüüs ja graafikud")

    # Kasutame andmeid otse session_state-ist
    if "sisestused_df" not in st.session_state or st.session_state["sisestused_df"].empty:
        st.info("Andmed puuduvad. Palun lae fail külgribalt või sisesta andmed käsitsi.")
        return

    # Teeme koopia, et puhastamine ei muudaks algandmeid sisestusvaates
    df_raw = st.session_state["sisestused_df"].copy()

    # NOTE: See funktsioon (puhasta_andmed) on eeldatavasti defineeritud failis 'abifunktsioonid.py'
    # Kuna seda faili ei ole siin, eeldan selle olemasolu ja funktsionaalsust.
    # Peate tagama, et 'puhasta_andmed' on imporditav abifailist.
    df, eemaldatud = puhasta_andmed(df_raw)

    if eemaldatud > 0:
        st.warning(f"Hoiatus: {eemaldatud} rida eemaldati analüüsist (vigased andmed või summa=0).")

    if df.empty:
        st.warning("Pärast puhastust ei jäänud ühtegi kehtivat rida analüüsiks.")
    else:
        # 1. Filtrid: Tulu/kulu + kuupäevavahemik
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

        # Tüübifilter
        if tyyp_filter == "Ainult kulud":
            df = df[df["Tulu/kulu"] == "Kulu"]
        elif tyyp_filter == "Ainult sissetulekud":
            df = df[df["Tulu/kulu"] == "Tulu"]

        # Kuupäevavahemik
        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            start_date, end_date = date_range
            mask = (df["Kuupäev"].dt.date >= start_date) & (df["Kuupäev"].dt.date <= end_date)
            df = df[mask]

        if df.empty:
            st.warning("Filtrite järel andmeid ei jäänud.")
        else:
            # 2. Kogupilt kategooriate kaupa (protsent + arv)
            st.markdown("### 2. Kogupilt kategooriate kaupa")

            # Grupeerimine ja summa leidmine
            by_cat = (
                df.groupby("Kategooria")["Summa"]
                .sum()
                .sort_values(ascending=False)
            )
            total = by_cat.sum()

            summary = pd.DataFrame(
                {
                    "Summa": by_cat,
                    "Osakaal %": (by_cat / total * 100).round(1),
                }
            )

            st.write("Kokku:", float(total))
            st.dataframe(summary)

            # --- GRAAFIK: Vertikaalne tulpdiagramm värvide ja väärtustega ---

            fig, ax = plt.subplots(figsize=(10, 6))

            # Määrame värvid: Tulu = roheline, Kulu = punane
            color_map = []
            for cat in by_cat.index:
                # Leiame kategooria tüübi, võttes esimene vaste kategooria kohta
                sample_row = df[df["Kategooria"] == cat]
                if not sample_row.empty:
                    # Määra värv vastavalt Tulu/kulu tüübile
                    cat_type = sample_row["Tulu/kulu"].iloc[0]
                    color_map.append("green" if cat_type == "Tulu" else "red")
                else:
                    color_map.append("gray") # Varuvariandina hall

            # Vertikaalne tulpdiagramm (ax.bar)
            bars = ax.bar(by_cat.index.astype(str), by_cat.values, color=color_map)

            # Numbrid tulpade kohale (numbrid peavad olema peal)
            for bar in bars:
                height = bar.get_height()
                ax.annotate(
                    f"{height:.0f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5), # Nihuta teksti veidi kõrgemale
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                )

            ax.set_ylabel("Summa")
            ax.set_title("Summa kategooriate kaupa (Tulu: Roheline, Kulu: Punane)")
            # Pööra x-telje silte, et need mahuksid
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
            plt.tight_layout() # Optimeeri paigutus

            st.pyplot(fig)

            # 3. Detailne vaade
            st.markdown("### 3. Ajavahemiku analüüs ühe kategooria kaupa")

            valitav_kategooria = st.selectbox(
                "Vali kategooria detailsema vaate jaoks",
                options=by_cat.index,
            )

            ajavahemiku_valik = st.selectbox(
                "Vali ajavahemik:",
                options=["Päev", "Nädal", "Kuu", "Kvartal", "Aasta"],
            )

            df_kat = df[df["Kategooria"] == valitav_kategooria]

            if not df_kat.empty:
                # Kuupäeva grupeerimine vastavalt valikule
                if ajavahemiku_valik == "Päev":
                    # Kasutame .dt.date, et saada kuupäev ilma kellaajata
                    jaotus = df_kat.groupby(df_kat["Kuupäev"].dt.date)["Summa"].sum()
                elif ajavahemiku_valik == "Nädal":
                    jaotus = df_kat.groupby(df_kat["Kuupäev"].dt.to_period("W"))["Summa"].sum()
                elif ajavahemiku_valik == "Kuu":
                    jaotus = df_kat.groupby(df_kat["Kuupäev"].dt.to_period("M"))["Summa"].sum()
                elif ajavahemiku_valik == "Kvartal":
                    jaotus = df_kat.groupby(df_kat["Kuupäev"].dt.to_period("Q"))["Summa"].sum()
                elif ajavahemiku_valik == "Aasta":
                    jaotus = df_kat.groupby(df_kat["Kuupäev"].dt.to_period("Y"))["Summa"].sum()
                else:
                    jaotus = None

                if jaotus is not None and not jaotus.empty:
                    labels = jaotus.index.astype(str)

                    fig3, ax3 = plt.subplots(figsize=(10, 4))
                    ax3.bar(labels, jaotus.values)
                    ax3.set_title(f"{valitav_kategooria} – {ajavahemiku_valik} lõikes")
                    ax3.set_xlabel(ajavahemiku_valik)
                    ax3.set_ylabel("Summa")
                    plt.setp(ax3.get_xticklabels(), rotation=45, ha="right")
                    plt.tight_layout()
                    st.pyplot(fig3)
                else:
                    st.info("Selles kategoorias pole valitud perioodi lõikes andmeid.")
            else:
                st.info("Valitud kategoorias pole andmeid.")
