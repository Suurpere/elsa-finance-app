
from sisestamine import *
from analyysimine import *

# --- Üldine seadistus ---
st.set_page_config(page_title="Kulutuste analüüs ELSA", layout="wide")

# --- UI: pealkiri ja menüü ---
st.title("💸 ELSA – Kulude ja sissetulekute jälgimine")

st.sidebar.header("Menüü")
mode = st.sidebar.radio(
    "Mida soovid teha?",
    ["Selgitus", "Failist lugemine", "Kulu / sissetuleku sisestamine", "Analüüs ja graafikud"],
)

# --- Selgitus / probleemikirjeldus ---
if mode == "Selgitus":
    selgita()

# --- CSV lugemine (Failist lugeda) ---
elif mode == "Failist lugemine":
    loe()

# --- CSV loomine / kirjutamine (Faili kirjutada) ---
elif mode == "Kulu / sissetuleku sisestamine":
    sisesta()

# --- Analüüs / graafikud (Analüüsida kulutusi) ---
elif mode == "Analüüs ja graafikud":
    analyysi()
