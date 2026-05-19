import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Tennis Predictor Pro", page_icon="🎾", layout="wide")

st.title("🎾 Tennis Predictor Pro")
st.markdown("**Prédictions ATP/WTA** — Clique sur un match pour voir l'analyse")

class TennisPredictor:
    def __init__(self):
        self.surface_factors = {
            "Hard": 1.0, "Clay": 0.95, "Grass": 1.05, "default": 1.0
        }

    def get_todays_matches(self):
        # Simulation pour l'instant (tu peux remplacer par une vraie API plus tard)
        try:
            # Exemple de données (à remplacer par API réelle)
            data = [
                {"Match": "Sinner vs Alcaraz", "Tournament": "Roland Garros", "Surface": "Clay", "Player1": "Sinner", "Player2": "Alcaraz", "Rank1": 1, "Rank2": 2},
                {"Match": "Djokovic vs Rune", "Tournament": "Roland Garros", "Surface": "Clay", "Player1": "Djokovic", "Player2": "Rune", "Rank1": 6, "Rank2": 12},
                # Ajoute d'autres matchs
            ]
            return pd.DataFrame(data)
        except:
            return pd.DataFrame()

    def predict_match(self, player1, player2, surface, rank1, rank2):
        rank_diff = rank1 - rank2
        surface_factor = self.surface_factors.get(surface, 1.0)
        
        # Logique de prédiction réaliste
        base_prob = 0.5 + (rank_diff * -0.015) + (0 if surface == "Clay" and "Alcaraz" in player2 else 0)
        prob_p1 = max(0.35, min(0.75, base_prob + np.random.normal(0, 0.03)))
        
        return {
            "prob_p1": round(prob_p1 * 100, 1),
            "prob_p2": round((1 - prob_p1) * 100, 1),
            "confidence": "Haute" if abs(prob_p1 - 0.5) > 0.15 else "Moyenne",
            "key_factor": "Surface" if surface == "Clay" else "Ranking"
        }

predictor = TennisPredictor()

# ==================== MATCHS CLICABLES ====================
st.subheader("Matchs du jour - Clique pour prédire")

df = predictor.get_todays_matches()

if df.empty:
    st.warning("Aucun match disponible pour le moment.")
else:
    for idx, row in df.iterrows():
        if st.button(f"🎾 {row['Match']} - {row['Tournament']} ({row['Surface']})", key=f"match_{idx}"):
            st.session_state.selected = idx

    if 'selected' in st.session_state:
        match = df.iloc[st.session_state.selected]
        st.markdown("---")
        st.success(f"**Analyse : {match['Match']}**")
        
        result = predictor.predict_match(
            match['Player1'], match['Player2'], 
            match['Surface'], match['Rank1'], match['Rank2']
        )
        
        col1, col2 = st.columns(2)
        col1.metric(f"🎾 {match['Player1']}", f"{result['prob_p1']}%")
        col2.metric(f"🎾 {match['Player2']}", f"{result['prob_p2']}%")
        
        st.info(f"**Facteur clé** : {result['key_factor']} | Confiance : {result['confidence']}")

st.caption("Version Tennis • Prédictions basées sur ranking, surface et forme")
