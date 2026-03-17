import streamlit as st
import pandas as pd
from supabase import create_client

url = "https://yzupjrzhqmojefurpmrx.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6dXBqcnpocW1vamVmdXJwbXJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM0MTY0ODcsImV4cCI6MjA4ODk5MjQ4N30.4qYKmPfDagkicbC31aob3egY2msh7mzuk7ECRJ2-M1A"

supabase = create_client(url,key)

st.title("⚖️ Application arbitre")

# terrain
terrain = st.selectbox("Terrain",[1,2,3,4,5,6])

if terrain <=4:
    division = "D2"
    table_matchs = "matchs"
    table_equipes = "equipes"
else:
    division = "D1"
    table_matchs = "d1_matchs"
    table_equipes = "d1_equipes"

# équipes
equipes_data = supabase.table(table_equipes).select("*").execute()
equipes = {e["id"]:e["nom"] for e in equipes_data.data}

# matchs
data = supabase.table(table_matchs)\
    .select("*")\
    .eq("terrain",terrain)\
    .order("heure")\
    .execute()

if not data.data:
    st.info("Aucun match")
    st.stop()

df = pd.DataFrame(data.data)
df = df[df["termine"]==False]

if df.empty:
    st.success("Tous les matchs sont terminés")
    st.stop()

match = df.iloc[0]

equipe1 = equipes[int(match["equipe1"])]
equipe2 = equipes[int(match["equipe2"])]

heure = pd.to_datetime(str(match["heure"])).strftime("%H:%M")

st.header(f"{heure} | Terrain {terrain}")
st.subheader(f"{equipe1} vs {equipe2}")

# ========================
# D2
# ========================

if division == "D2":

    st.write("### Manches BO3")

    col1,col2 = st.columns(2)

    with col1:
        st.subheader(equipe1)

    with col2:
        st.subheader(equipe2)

    manche1 = st.radio("Manche 1",[equipe1,equipe2],horizontal=True)
    manche2 = st.radio("Manche 2",[equipe1,equipe2],horizontal=True)
    manche3 = st.radio("Manche 3",[equipe1,equipe2],horizontal=True)

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

# ========================
# D1
# ========================

else:

    actions = {
        "Tâche A":10,
        "Tâche B":20,
        "Tâche C":30
    }

    penalites = {
        "Obstacle touché":5,
        "Sortie terrain":10
    }

    col1,col2 = st.columns(2)

    score_actions1 = 0
    score_pen1 = 0

    score_actions2 = 0
    score_pen2 = 0

    with col1:

        st.subheader(equipe1)

        for action,valeur in actions.items():

            n = st.number_input(action,0,10,key=f"a1_{action}")
            score_actions1 += n*valeur

        for pen,valeur in penalites.items():

            n = st.number_input(pen,0,10,key=f"p1_{pen}")
            score_pen1 += n*valeur

    with col2:

        st.subheader(equipe2)

        for action,valeur in actions.items():

            n = st.number_input(action+" ",0,10,key=f"a2_{action}")
            score_actions2 += n*valeur

        for pen,valeur in penalites.items():

            n = st.number_input(pen+" ",0,10,key=f"p2_{pen}")
            score_pen2 += n*valeur

    score1 = score_actions1 - score_pen1
    score2 = score_actions2 - score_pen2

    st.write("### Score calculé")
    st.write(f"{equipe1} : {score1}")
    st.write(f"{equipe2} : {score2}")

    if st.button("Valider score"):

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
