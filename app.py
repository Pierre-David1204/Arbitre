import streamlit as st

st.title("⚖️ Application arbitre")

terrains = [1,2,3,4,5,6]

terrain = st.selectbox(
    "Choisir un terrain",
    terrains
)

if st.button("Valider"):

    st.session_state.terrain = terrain

    st.switch_page("pages/1_Matchs.py")
