import streamlit as st
import pandas as pd
from supabase import create_client

# connexion supabase
url = "https://yzupjrzhqmojefurpmrx.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6dXBqcnpocW1vamVmdXJwbXJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM0MTY0ODcsImV4cCI6MjA4ODk5MjQ4N30.4qYKmPfDagkicbC31aob3egY2msh7mzuk7ECRJ2-M1A"


supabase = create_client(url,key)

st.title("⚖️ Application arbitre")

# =========================
# CHOIX TERRAIN
# =========================

terrain = st.selectbox("Terrain",[1,2,3,4,5,6])

# déterminer division
if terrain <= 4:
    division = "D2"
    table_matchs = "matchs"
    table_equipes = "equipes"
else:
    division = "D1"
    table_matchs = "d1_matchs"
    table_equipes = "d1_equipes"

# =========================
# EQUIPES
# =========================

equipes_data = supabase.table(table_equipes).select("*").execute()
equipes = {e["id"]:e["nom"] for e in equipes_data.data}

# =========================
# MATCHS DU TERRAIN
# =========================

data = supabase.table(table_matchs)\
    .select("*")\
    .eq("terrain",terrain)\
    .order("heure")\
    .execute()

if not data.data:
    st.info("Aucun match")
    st.stop()

df = pd.DataFrame(data.data)

df = df[df["termine"] == False]

if df.empty:
    st.success("Tous les matchs sont terminés")
    st.stop()

match = df.iloc[0]

equipe1 = equipes[int(match["equipe1"])]
equipe2 = equipes[int(match["equipe2"])]

heure = pd.to_datetime(str(match["heure"])).strftime("%H:%M")

st.header(f"{heure} | Terrain {terrain}")
st.subheader(f"{equipe1} vs {equipe2}")

# =========================
# D2 : BO3
# =========================

if division == "D2":

    st.write("### Manches BO3")

    manche1 = st.radio("Manche 1",[equipe1,equipe2],key="m1")
    manche2 = st.radio("Manche 2",[equipe1,equipe2],key="m2")
    manche3 = st.radio("Manche 3",[equipe1,equipe2],key="m3")

    if st.button("Valider résultat"):

        wins1 = 0
        wins2 = 0

        for m in [manche1,manche2,manche3]:

            if m == equipe1:
                wins1 +=1
            else:
                wins2 +=1

        if wins1 > wins2:
            vainqueur = int(match["equipe1"])
        elif wins2 > wins1:
            vainqueur = int(match["equipe2"])
        else:
            vainqueur = None

        supabase.table("matchs").update({

            "score1":wins1,
            "score2":wins2,
            "vainqueur":vainqueur,
            "termine":True

        }).eq("id",int(match["id"])).execute()

        st.rerun()

# =========================
# D1 : ACTIONS + PENALITES
# =========================

else:

    st.write("### Actions réalisées")

    actions = {
        "Tâche A":10,
        "Tâche B":20,
        "Tâche C":30
    }

    penalites = {
        "Obstacle touché":5,
        "Sortie terrain":10
    }

    st.write("Equipe 1")

    score_actions1 = 0
    score_pen1 = 0

    for action,valeur in actions.items():

        n = st.number_input(
            f"{action}",
            0,
            10,
            key=f"a1_{action}"
        )

        score_actions1 += n * valeur

    for pen,valeur in penalites.items():

        n = st.number_input(
            f"{pen}",
            0,
            10,
            key=f"p1_{pen}"
        )

        score_pen1 += n * valeur

    st.write("Equipe 2")

    score_actions2 = 0
    score_pen2 = 0

    for action,valeur in actions.items():

        n = st.number_input(
            f"{action} ",
            0,
            10,
            key=f"a2_{action}"
        )

        score_actions2 += n * valeur

    for pen,valeur in penalites.items():

        n = st.number_input(
            f"{pen} ",
            0,
            10,
            key=f"p2_{pen}"
        )

        score_pen2 += n * valeur

    if st.button("Valider score"):

        score1 = score_actions1 - score_pen1
        score2 = score_actions2 - score_pen2

        if score1 > score2:
            vainqueur = int(match["equipe1"])
        elif score2 > score1:
            vainqueur = int(match["equipe2"])
        else:
            vainqueur = None

        supabase.table("d1_matchs").update({

            "score1":score1,
            "score2":score2,

            "vainqueur":vainqueur,
            "termine":True

        }).eq("id",int(match["id"])).execute()

        st.rerun()
