import streamlit as st
import pandas as pd
from supabase import create_client

url = "https://yzupjrzhqmojefurpmrx.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6dXBqcnpocW1vamVmdXJwbXJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM0MTY0ODcsImV4cCI6MjA4ODk5MjQ4N30.4qYKmPfDagkicbC31aob3egY2msh7mzuk7ECRJ2-M1A"

supabase = create_client(url,key)

st.title("⚖️ Application arbitre")

terrain = st.selectbox("Terrain",[1,2,3,4,5,6])

if terrain <=4:
    division = "D2"
    table_matchs = "matchs"
    table_equipes = "equipes"
else:
    division = "D1"
    table_matchs = "d1_matchs"
    table_equipes = "d1_equipes"

equipes_data = supabase.table(table_equipes).select("*").execute()
equipes = {e["id"]:e["nom"] for e in equipes_data.data}

data = supabase.table(table_matchs)\
.select("*")\
.eq("terrain",terrain)\
.order("heure")\
.execute()

df = pd.DataFrame(data.data)

df = df[df["termine"]==False]

if df.empty:
    st.success("Tous les matchs terminés")
    st.stop()

match = df.iloc[0]

equipe1_id = match["equipe1"]
equipe2_id = match["equipe2"]

equipe1 = equipes[equipe1_id]
equipe2 = equipes[equipe2_id]

st.header(f"{equipe1} vs {equipe2}")

# =====================
# D2
# =====================

if division == "D2":

    choix=[equipe1,equipe2,"Match nul"]

    m1=st.radio("Manche 1",choix)
    m2=st.radio("Manche 2",choix)
    m3=st.radio("Manche 3",choix)

    if st.button("Valider"):

        wins1=0
        wins2=0

        for m in [m1,m2,m3]:

            if m==equipe1:
                wins1+=1
            elif m==equipe2:
                wins2+=1

        supabase.table("matchs").update({

            "score1":wins1,
            "score2":wins2,
            "vainqueur":None if wins1==wins2 else (equipe1_id if wins1>wins2 else equipe2_id),
            "match_nul":wins1==wins2,
            "termine":True

        }).eq("id",match["id"]).execute()

        recalcul_classement_d2()

        st.rerun()

# =====================
# D1
# =====================

else:

    score1=st.number_input(equipe1,0)
    score2=st.number_input(equipe2,0)

    if st.button("Valider"):

        supabase.table("d1_matchs").update({

            "score1":score1,
            "score2":score2,
            "vainqueur":None if score1==score2 else (equipe1_id if score1>score2 else equipe2_id),
            "match_nul":score1==score2,
            "termine":True

        }).eq("id",match["id"]).execute()

        recalcul_classement_d1()

        st.rerun()
        
        

        
