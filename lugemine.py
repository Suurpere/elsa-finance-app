import streamlit as st

def loe():
    st.header("📂 Andmete eelvaade")
    
    # Kontrollime, kas andmed on olemas
    if "sisestused_df" in st.session_state and not st.session_state["sisestused_df"].empty:
        st.success(f"Andmed mälus olemas. Kokku {len(st.session_state['sisestused_df'])} rida.")
        st.dataframe(st.session_state["sisestused_df"])
    else:
        st.info("Andmeid pole veel laetud ega sisestatud. Kasuta vasakmenüüd andmete laadimiseks.")
