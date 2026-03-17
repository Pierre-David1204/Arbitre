import streamlit as st
import pandas as pd
from supabase import create_client

url = "https://yzupjrzhqmojefurpmrx.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6dXBqcnpocW1vamVmdXJwbXJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM0MTY0ODcsImV4cCI6MjA4ODk5MjQ4N30.4qYKmPfDagkicbC31aob3egY2msh7mzuk7ECRJ2-M1A"

supabase = create_client(url,key)

st.title("⚖️ Application arbitre")

# ========================
# TERRAIN
# ========================

terrain = st.selectbox("Terrain",[1,2,3,4,5,6])

if terrain <=4:
    division = "D2"
    table_matchs = "matchs"
    table_equipes = "equipes"
else:
    division = "D1"
    table_matchs = "d1_matchs"
    table_equipes = "d1_equipes"

# ========================
# EQUIPES
# ========================

equipes_data = supabase.table(table_equipes).select("*").execute()
equipes = {e["id"]:e["nom"] for e in equipes_data.data}

# ========================
# MATCHS
# ========================

data = supabase.table(table_matchs)\
    .select("*")\
    .eq("terrain",terrain)\
    .order("heure")\
    .execute()

df = pd.DataFrame(data.data)

df = df[df["termine"] == False]

if df.empty:
    st.success("Tous les matchs sont terminés")
    st.stop()

match = df.iloc[0]

match_key = f"match_{match['id']}"

equipe1 = equipes[int(match["equipe1"])]
equipe2 = equipes[int(match["equipe2"])]

heure = pd.to_datetime(str(match["heure"])).strftime("%H:%M")

st.header(f"{heure} | Terrain {terrain}")
st.subheader(f"{equipe1} vs {equipe2}")

# ========================
# D2 BO3
# ========================

if division == "D2":

    choix = [equipe1,equipe2,"Match nul"]

    st.write("### Manches")

    m1 = st.radio("Manche 1",choix,key=f"{match_key}_m1")
    m2 = st.radio("Manche 2",choix,key=f"{match_key}_m2")
    m3 = st.radio("Manche 3",choix,key=f"{match_key}_m3")

    if st.button("Valider résultat"):

        wins1 = 0
        wins2 = 0

        for m in [m1,m2,m3]:

            if m == equipe1:
                wins1 +=1
            elif m == equipe2:
                wins2 +=1

        if wins1 > wins2:
            vainqueur = int(match["equipe1"])
            match_nul = False

        elif wins2 > wins1:
            vainqueur = int(match["equipe2"])
            match_nul = False

        else:
            vainqueur = None
            match_nul = True

        update_data = {

            "score1":wins1,
            "score2":wins2,
            "vainqueur":vainqueur,
            "match_nul":match_nul,
            "termine":True

        }

        supabase.table(table_matchs)\
            .update(update_data)\
            .eq("id",int(match["id"]))\
            .execute()

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

        for action,val in actions.items():

            n = st.number_input(action,0,10,key=f"{match_key}_a1_{action}")
            score_actions1 += n * val

        for pen,val in penalites.items():

            n = st.number_input(pen,0,10,key=f"{match_key}_p1_{pen}")
            score_pen1 += n * val

    with col2:

        st.subheader(equipe2)

        for action,val in actions.items():

            n = st.number_input(action+" ",0,10,key=f"{match_key}_a2_{action}")
            score_actions2 += n * val

        for pen,val in penalites.items():

            n = st.number_input(pen+" ",0,10,key=f"{match_key}_p2_{pen}")
            score_pen2 += n * val

    score1 = score_actions1 - score_pen1
    score2 = score_actions2 - score_pen2

    st.write("## Score")

    c1,c2 = st.columns(2)

    c1.metric(equipe1,score1)
    c2.metric(equipe2,score2)

    if st.button("Valider score"):

        if score1 > score2:
            vainqueur = int(match["equipe1"])
            match_nul = False

        elif score2 > score1:
            vainqueur = int(match["equipe2"])
            match_nul = False

        else:
            vainqueur = None
            match_nul = True

        update_data = {

            "score1":score1,
            "score2":score2,
            "vainqueur":vainqueur,
            "match_nul":match_nul,
            "termine":True

        }

        supabase.table(table_matchs)\
            .update(update_data)\
            .eq("id",int(match["id"]))\
            .execute()

        st.rerun()
