import streamlit as st
import pandas as pd
from supabase import create_client

url = "https://yzupjrzhqmojefurpmrx.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6dXBqcnpocW1vamVmdXJwbXJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM0MTY0ODcsImV4cCI6MjA4ODk5MjQ4N30.4qYKmPfDagkicbC31aob3egY2msh7mzuk7ECRJ2-M1A"

supabase = create_client(url, key)

st.title("⚖️ Application arbitre")

terrain = st.selectbox("Terrain",[1,2,3,4,5,6])

# division
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
equipes = {e["id"]: e["nom"] for e in equipes_data.data}

# matchs
data = supabase.table(table_matchs)\
    .select("*")\
    .eq("terrain", terrain)\
    .order("heure")\
    .execute()

df = pd.DataFrame(data.data)

df = df[df["termine"] == False]

if df.empty:
    st.success("Tous les matchs terminés")
    st.stop()

match = df.iloc[0]

equipe1_id = int(match["equipe1"])
equipe2_id = int(match["equipe2"])

equipe1 = equipes[equipe1_id]
equipe2 = equipes[equipe2_id]

heure = pd.to_datetime(str(match["heure"])).strftime("%H:%M")

st.header(f"{heure} | Terrain {terrain}")
st.subheader(f"{equipe1} vs {equipe2}")

# ==========================
# D2
# ==========================

if division == "D2":

    choix = [equipe1, equipe2, "Match nul"]

    m1 = st.radio("Manche 1", choix)
    m2 = st.radio("Manche 2", choix)
    m3 = st.radio("Manche 3", choix)

    if st.button("Valider résultat"):

        wins1 = 0
        wins2 = 0

        for m in [m1,m2,m3]:

            if m == equipe1:
                wins1 += 1
            elif m == equipe2:
                wins2 += 1

        if wins1 > wins2:
            vainqueur = equipe1_id
            match_nul = False
        elif wins2 > wins1:
            vainqueur = equipe2_id
            match_nul = False
        else:
            vainqueur = None
            match_nul = True

        # enregistrer match
        supabase.table("matchs").update({

            "score1": int(wins1),
            "score2": int(wins2),
            "vainqueur": vainqueur,
            "match_nul": match_nul,
            "termine": True

        }).eq("id", int(match["id"])).execute()

        # récupérer équipes
        team1 = supabase.table("equipes").select("*").eq("id", equipe1_id).execute().data[0]
        team2 = supabase.table("equipes").select("*").eq("id", equipe2_id).execute().data[0]

        # manches
        supabase.table("equipes").update({
            "manches_pour": team1["manches_pour"] + wins1,
            "manches_contre": team1["manches_contre"] + wins2
        }).eq("id", equipe1_id).execute()

        supabase.table("equipes").update({
            "manches_pour": team2["manches_pour"] + wins2,
            "manches_contre": team2["manches_contre"] + wins1
        }).eq("id", equipe2_id).execute()

        # classement
        if wins1 > wins2:

            supabase.table("equipes").update({
                "victoires": team1["victoires"] + 1,
                "points": team1["points"] + 3
            }).eq("id", equipe1_id).execute()

            supabase.table("equipes").update({
                "defaites": team2["defaites"] + 1
            }).eq("id", equipe2_id).execute()

        elif wins2 > wins1:

            supabase.table("equipes").update({
                "victoires": team2["victoires"] + 1,
                "points": team2["points"] + 3
            }).eq("id", equipe2_id).execute()

            supabase.table("equipes").update({
                "defaites": team1["defaites"] + 1
            }).eq("id", equipe1_id).execute()

        else:

            supabase.table("equipes").update({
                "nuls": team1["nuls"] + 1,
                "points": team1["points"] + 1
            }).eq("id", equipe1_id).execute()

            supabase.table("equipes").update({
                "nuls": team2["nuls"] + 1,
                "points": team2["points"] + 1
            }).eq("id", equipe2_id).execute()

        st.rerun()

# ==========================
# D1
# ==========================

else:

    score1 = st.number_input(equipe1,0)
    score2 = st.number_input(equipe2,0)

    if st.button("Valider score"):

        if score1 > score2:
            vainqueur = equipe1_id
            match_nul = False
        elif score2 > score1:
            vainqueur = equipe2_id
            match_nul = False
        else:
            vainqueur = None
            match_nul = True

        supabase.table("d1_matchs").update({

            "score1": score1,
            "score2": score2,
            "vainqueur": vainqueur,
            "match_nul": match_nul,
            "termine": True

        }).eq("id", int(match["id"])).execute()

        team1 = supabase.table("d1_equipes").select("*").eq("id", equipe1_id).execute().data[0]
        team2 = supabase.table("d1_equipes").select("*").eq("id", equipe2_id).execute().data[0]

        # score total
        supabase.table("d1_equipes").update({
            "score_total": team1["score_total"] + score1
        }).eq("id", equipe1_id).execute()

        supabase.table("d1_equipes").update({
            "score_total": team2["score_total"] + score2
        }).eq("id", equipe2_id).execute()

        # classement
        if score1 > score2:

            supabase.table("d1_equipes").update({
                "victoires": team1["victoires"] + 1,
                "points": team1["points"] + 3
            }).eq("id", equipe1_id).execute()

            supabase.table("d1_equipes").update({
                "defaites": team2["defaites"] + 1
            }).eq("id", equipe2_id).execute()

        elif score2 > score1:

            supabase.table("d1_equipes").update({
                "victoires": team2["victoires"] + 1,
                "points": team2["points"] + 3
            }).eq("id", equipe2_id).execute()

            supabase.table("d1_equipes").update({
                "defaites": team1["defaites"] + 1
            }).eq("id", equipe1_id).execute()

        else:

            supabase.table("d1_equipes").update({
                "nuls": team1["nuls"] + 1,
                "points": team1["points"] + 1
            }).eq("id", equipe1_id).execute()

            supabase.table("d1_equipes").update({
                "nuls": team2["nuls"] + 1,
                "points": team2["points"] + 1
            }).eq("id", equipe2_id).execute()

        st.rerun()      
