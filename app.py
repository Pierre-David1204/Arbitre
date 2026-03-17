import streamlit as st
import pandas as pd
from supabase import create_client

url = "https://yzupjrzhqmojefurpmrx.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6dXBqcnpocW1vamVmdXJwbXJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM0MTY0ODcsImV4cCI6MjA4ODk5MjQ4N30.4qYKmPfDagkicbC31aob3egY2msh7mzuk7ECRJ2-M1A"

supabase = create_client(url,key)

st.title("⚖️ Application arbitre")

# choisir terrain
terrain = st.selectbox(
    "Terrain",
    [1,2,3,4,5,6]
)

# récupérer équipes
equipes_data = supabase.table("equipes").select("*").execute()
equipes = {e["id"]:e["nom"] for e in equipes_data.data}

# récupérer matchs du terrain
data = supabase.table("matchs") \
    .select("*") \
    .eq("terrain",terrain) \
    .order("heure") \
    .execute()

df = pd.DataFrame(data.data)

# garder seulement matchs non terminés
df = df[df["termine"] == False]

if df.empty:

    st.success("Tous les matchs sont terminés")
    st.stop()

# match en cours
match = df.iloc[0]

equipe1 = equipes[match["equipe1"]]
equipe2 = equipes[match["equipe2"]]

heure = pd.to_datetime(str(match["heure"])).strftime("%H:%M")

st.header(f"{heure} | Terrain {terrain}")

st.subheader(f"{equipe1} vs {equipe2}")

# vérifier division
if terrain <= 4:
    division = "D2"
else:
    division = "D1"

# D2
if division == "D2":

    resultat = st.radio(
        "Résultat",
        [equipe1,equipe2,"Match nul"]
    )

    if st.button("Valider résultat"):

        if resultat == equipe1:
            vainqueur = match["equipe1"]

        elif resultat == equipe2:
            vainqueur = match["equipe2"]

        else:
            vainqueur = None

        supabase.table("matchs").update({

            "vainqueur":vainqueur,
            "termine":True

        }).eq("id",match["id"]).execute()

        st.rerun()

# D1
else:

    st.write("### Score D1")

    p1 = st.number_input("Points équipe 1",0)
    pen1 = st.number_input("Pénalités équipe 1",0)

    p2 = st.number_input("Points équipe 2",0)
    pen2 = st.number_input("Pénalités équipe 2",0)

    if st.button("Valider score"):

        score1 = p1 - pen1
        score2 = p2 - pen2

        if score1 > score2:
            vainqueur = match["equipe1"]

        elif score2 > score1:
            vainqueur = match["equipe2"]

        else:
            vainqueur = None

        supabase.table("matchs").update({

            "points1":p1,
            "penalites1":pen1,

            "points2":p2,
            "penalites2":pen2,

            "score1":score1,
            "score2":score2,

            "vainqueur":vainqueur,
            "termine":True

        }).eq("id",match["id"]).execute()

        st.rerun()
