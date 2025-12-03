from andmebaas import ALL_COLUMNS
import pandas as pd
import streamlit as st

def prepare_session_df():
    """
    Valmistab ette Streamliti sessiooni andmete hoidmiseks.
    Kui 'sisestused_df' puudub, luuakse tühi tabel õigete veergudega.
    """
    if "sisestused_df" not in st.session_state:
        st.session_state["sisestused_df"] = pd.DataFrame(columns=ALL_COLUMNS)


def puhasta_andmed(df: pd.DataFrame):
    """
    Puhastab ja korrastab andmed analüüsi jaoks.
    
    Tegevused:
    1. Lisab puuduolevad veerud.
    2. Teisendab 'Timestamp' ja 'Kuupäev' veerud õigesse ajavormingusse.
    3. Teisendab 'Summa' veeru numbriteks.
    4. Eemaldab read, kus kuupäev või summa on vigane/tühi.
    5. Täidab tühjad lüngad tekstiveergudes "Määramata".
    
    Tagastab:
        - df: Puhastatud DataFrame
        - eemaldatud: Arv, mitu rida eemaldati (nt null-summade tõttu)
    """
    # 1. Lisa puuduolevad veerud
    for col in ALL_COLUMNS:
        if col not in df.columns:
            if col == "Summa":
                df[col] = 0.0
            else:
                df[col] = ""

    # 2. Ajatemplid korda
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    # Kuupäeva loogika
    if "Kuupäev" in df.columns:
        df["Kuupäev"] = pd.to_datetime(df["Kuupäev"], errors="coerce")
    else:
        df["Kuupäev"] = df["Timestamp"].dt.date
        df["Kuupäev"] = pd.to_datetime(df["Kuupäev"], errors="coerce")

    # 3. Summad numbriks
    df["Summa"] = pd.to_numeric(df["Summa"], errors="coerce")

    # 4. Eemalda vigased read
    df.dropna(subset=["Kuupäev", "Summa"], inplace=True)

    # 5. Täida tühimikud
    df["Kategooria"] = df["Kategooria"].fillna("Määramata")
    
    if "Tulu/kulu" not in df.columns:
        df["Tulu/kulu"] = "Määramata"
    else:
        df["Tulu/kulu"] = df["Tulu/kulu"].fillna("Määramata")

    algne_pikkus = len(df)
    # Eemalda read, kus summa on 0
    df = df[df["Summa"] != 0]
    eemaldatud = algne_pikkus - len(df)

    return df, eemaldatud
