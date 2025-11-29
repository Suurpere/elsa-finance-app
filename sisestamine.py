from abifunktsioonid import *
from konstandid import *


def sisesta():
    st.header("✏️ Lisa uus kulu või sissetulek")

    prepare_session_df()
    df_sisestused = st.session_state["sisestused_df"]

    # 1. Võimalus alustada olemasolevast failist
    st.markdown("### 1. Alusta olemasolevast failist (valikuline)")

    uploaded_base = st.file_uploader(
        "Lae olemasolev CSV, et jätkata sinna lisamist",
        type=["csv"],
        key="write_base",
    )

    if uploaded_base is not None and df_sisestused.empty:
        try:
            df_base = pd.read_csv(uploaded_base, encoding="utf-8")

            # Tagame, et kõigil veergudel on koht
            for col in ALL_COLUMNS:
                if col not in df_base.columns:
                    df_base[col] = "" if col != "Summa" else 0.0

            df_base = df_base[ALL_COLUMNS]
            st.session_state["sisestused_df"] = df_base
            df_sisestused = df_base

            st.success("Olemasolev fail laetud.")
        except Exception as e:
            st.error(f"Faili lugemisel tekkis viga: {e}")

    # 2. Uue kirje sisestamine
    st.markdown("### 2. Lisa uus kirje")

    # Kirje tüüp peab olema VORMIST VÄLJAS
    tyyp = st.radio("Kirje tüüp", ["Kulu", "Sissetulek"], key="kirje_tyyp")

    with st.form("lisa_kirje_form"):
        kuupäev = st.date_input("Kuupäev", format="YYYY-MM-DD")
        summa_str = st.text_input("Summa (näiteks 13.02)")

        # NÜÜD valime kategooria vastavalt tyyp väärtusele
        if tyyp == "Sissetulek":
            kategooria = st.selectbox(
                "Sissetuleku kategooria",
                TULU_KATEGOORIAD,
                key="kategooria_sissetulek",
            )
        else:
            kategooria = st.selectbox(
                "Kulu kategooria",
                KULU_KATEGOORIAD,
                key="kategooria_kulu",
            )

        kaupmees = st.text_input("Kaupmees / allikas (valikuline)")
        kirjeldus = st.text_area("Lühikirjeldus (valikuline)", height=80)

        submitted = st.form_submit_button("Lisa kirje")

    if submitted:
        try:
            summa_clean = summa_str.replace(",", ".")
            summa_val = float(summa_clean)

            from datetime import datetime

            timestamp = datetime.now().isoformat(timespec="seconds")

            new_row = {
                "Timestamp": timestamp,
                "Kuupäev": kuupäev.strftime("%Y-%m-%d"),
                "Summa": summa_val,
                "Tüüp": tyyp,
                "Kategooria": kategooria,
                "Kaupmees": kaupmees,
                "Kirjeldus": kirjeldus,
            }

            st.session_state["sisestused_df"] = pd.concat(
                [st.session_state["sisestused_df"], pd.DataFrame([new_row])],
                ignore_index=True,
            )
            st.success("Kirje lisatud.")
        except ValueError:
            st.error("Vigane summa. Palun sisesta number (nt 13.02).")

    # 3. Näita hetkeandmeid + 4. võimalus CSV luua/uuendada
    if not st.session_state["sisestused_df"].empty:
        st.markdown("### 3. Praegune CSV sisu")
        st.dataframe(st.session_state["sisestused_df"])

        st.markdown("### 4. Laadi CSV alla (loo / uuenda fail)")
        csv_bytes = st.session_state["sisestused_df"].to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Laadi alla CSV-fail",
            data=csv_bytes,
            file_name="elsa_kirjed.csv",
            mime="text/csv",
        )
    else:
        st.info("Kirjeid pole veel lisatud.")


sisesta()