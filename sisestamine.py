from abifunktsioonid import *
from konstandid import *
from datetime import datetime
from kategoriseerimine import kategoriseeri
from andmebaas import load_db, save_db
import streamlit as st # Igaks juhuks importime otse

def sisesta():
    st.header("✏️ Lisa uus kulu või sissetulek")

    prepare_session_df()
    # Kasutame andmeid, mis on laetud pealehelt (elsa_app.py) või tühja põhja
    df_sisestused = st.session_state["sisestused_df"]

    # --- 1. Uue sissetuleku sisestamine ---
    st.markdown("### 1. Lisa uus sissetulek")

    with st.form("lisa_sissetulek_form"):
        kuupäev_sisse = st.date_input("Kuupäev", format="YYYY-MM-DD", key="kuupäev_sisse")
        summa_str_sisse = st.text_input("Summa (näiteks 13.02)", key="summa_sisse")
        kategooria_sisse = st.selectbox("Sissetuleku allikas", TULU_KATEGOORIAD, key="kategooria_sissetulek")
        submitted_sisse = st.form_submit_button("Lisa sissetulek")

    if submitted_sisse:
        try:
            summa_clean = summa_str_sisse.replace(",", ".")
            summa_val = float(summa_clean)
            timestamp = datetime.now().isoformat(timespec="seconds")

            new_row = {
                "Timestamp": timestamp,
                "Kuupäev": kuupäev_sisse.strftime("%Y-%m-%d"),
                "Summa": summa_val,
                "Tulu/kulu": "Tulu",
                "Kategooria": kategooria_sisse,
            }

            st.session_state["sisestused_df"] = pd.concat(
                [st.session_state["sisestused_df"], pd.DataFrame([new_row])],
                ignore_index=True,
            )
            st.success("Sissetulek lisatud.")
        except ValueError:
            st.error("Vigane summa. Palun sisesta number (nt 13.02).")

    # ------------------------------------------------------------------
    # 2. Uue väljamineku sisestamine
    # ------------------------------------------------------------------
    st.markdown("### 2. Lisa uus väljaminek")

    # Laeme andmebaasi SIIN, et see oleks värske nii abiplokkidele kui vormile
    db = load_db()
    kategooriad = db["categories"]
    kaupmehed_map = db["merchants"]
    kaupmehed_list = sorted([""] + list(kaupmehed_map.keys()))
    kateg_list = sorted([""] + kategooriad)

    # --- ABIPLOKID (VORMIST VÄLJASPOOL) ---
    # Need peavad olema väljaspool vormi, sest st.button teeb rerun-i.
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("➕ Lisa uus kaupmees"):
            uus_kaup = st.text_input("Uus kaupmees", key="uus_kaupmees_input")
            uus_kateg_seos = st.selectbox("Seosta kategooriaga", [""] + kateg_list, key="uus_kaup_kateg")
            
            if st.button("Salvesta kaupmees"):
                if uus_kaup in kaupmehed_map:
                    st.warning("Kaupmees juba olemas")
                elif not uus_kaup:
                    st.warning("Sisesta kaupmehe nimi")
                elif not uus_kateg_seos:
                    st.warning("Vali kategooria")
                else:
                    kaupmehed_map[uus_kaup] = uus_kateg_seos
                    save_db(db)
                    st.success(f"Lisatud: {uus_kaup}")
                    st.rerun() # Värskendab lehte, et uus kaupmees ilmuks nimekirja

    with col2:
        with st.expander("➕ Lisa uus kategooria"):
            uus_k = st.text_input("Uus kategooria", key="uus_kateg_input")
            if st.button("Salvesta kategooria"):
                if uus_k and uus_k not in kategooriad:
                    kategooriad.append(uus_k)
                    save_db(db)
                    st.success(f"Lisatud: {uus_k}")
                    st.rerun() # Värskendab lehte
                else:
                    st.warning("Vigane või topelt kategooria")

    # --- PÕHIVORM (VÄLJAMINKEKUD) ---
    
    with st.form("lisa_väljaminek_form"):
        # inputs inside the form
        kuupäev_välja = st.date_input("Kuupäev", format="YYYY-MM-DD", key="kuupäev_välja")
        summa_str_välja = st.text_input("Summa (näiteks 13.02)", key="summa_välja")

        # Kasutame siin juba (potentsiaalselt) uuenenud nimekirju
        kaupmees = st.selectbox("Kaupmees (võib jätta tühjaks)", kaupmehed_list, key="kaupmees_väljaminek")
        kategooria_välja = st.selectbox("Kulu kategooria (võib jätta tühjaks)", kateg_list, key="kategooria_kulu")
        
        kirjeldus_välja = st.text_area("Lühikirjeldus (valikuline)", height=80)

        # See on AINUS nupp, mis tohib vormi sees olla
        submitted_välja = st.form_submit_button("Lisa väljaminek")

    # --- VORMI TÖÖTLUS (VÄLJASPOOL VORMI PLOKKI) ---

    if submitted_välja:
        kaupmees_täidetud = bool(kaupmees.strip())
        kategooria_täidetud = bool(kategooria_välja.strip())

        if not kaupmees_täidetud and not kategooria_täidetud:
            st.error("Palun vali vähemalt kaupmees või kategooria.")
        else:
            try:
                summa_clean = summa_str_välja.replace(",", ".")
                summa_val = float(summa_clean)
                timestamp = datetime.now().isoformat(timespec="seconds")

                # Kui kasutaja valis kaupmehe, aga kategooria jättis tühjaks,
                # proovime automaatselt leida kategooria
                kategooria_lõplik = kategooria_välja
                if kaupmees and not kategooria_lõplik:
                    # Otsime, kas sellel kaupmehel on andmebaasis kategooria
                    if kaupmees in kaupmehed_map:
                         kategooria_lõplik = kaupmehed_map[kaupmees]
                    else:
                         kategooria_lõplik = "Määramata" 

                new_row = {
                    "Timestamp": timestamp,
                    "Kuupäev": kuupäev_välja.strftime("%Y-%m-%d"),
                    "Summa": summa_val,
                    "Tulu/kulu": "Kulu",
                    "Kategooria": kategooria_lõplik,
                    "Kaupmees": kaupmees,
                    "Kirjeldus": kirjeldus_välja,
                }

                st.session_state["sisestused_df"] = pd.concat(
                    [st.session_state["sisestused_df"], pd.DataFrame([new_row])],
                    ignore_index=True,
                )
                st.success("Kirje lisatud.")
            except ValueError:
                st.error("Vigane summa. Palun sisesta number (nt 13.02).")

    # 3. Näita hetkeandmeid + CSV
    if not st.session_state["sisestused_df"].empty:
        st.markdown("---")
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
