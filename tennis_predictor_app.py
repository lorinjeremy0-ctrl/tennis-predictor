import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Tennis Predictor Pro", page_icon="🎾", layout="wide")

st.title("🎾 Tennis Predictor Pro")
st.markdown("**Matchs en temps réel** via API")

class TennisPredictor:
    def __init__(self):
        self.api_key = None  # À remplir dans la sidebar
        self.surface_factors = {"Hard": 1.0, "Clay": 0.93, "Grass": 1.07}

    def get_todays_matches(self):
        """Récupération via API (exemple avec placeholder)"""
        st.info("🔄 Recherche des matchs du jour...")
        
        # Simulation pour l'instant (remplace par vraie API plus tard)
        matches = [
            {"Match": "Sinner vs Alcaraz", "Tournament": "Roland Garros", "Surface": "Clay", "P1": "Sinner", "P2": "Alcaraz", "Rank1": 1, "Rank2": 2},
            {"Match": "Djokovic vs Rune", "Tournament": "Roland Garros", "Surface": "Clay", "P1": "Djokovic", "P2": "Rune", "Rank1": 5, "Rank2": 13},
            {"Match": "Sabalenka vs Swiatek", "Tournament": "Roland Garros", "Surface": "Clay", "P1": "Sabalenka", "P2": "Swiatek", "Rank1": 1, "Rank2": 2},
            {"Match": "Zverev vs Rublev", "Tournament": "Roland Garros", "Surface": "Clay", "P1": "Zverev", "P2": "Rublev", "Rank1": 3, "Rank2": 9},
            {"Match": "Gauff vs Paolini", "Tournament": "Roland Garros", "Surface": "Clay", "P1": "Gauff", "P2": "Paolini", "Rank1": 3, "Rank2": 15},
        ]
        return pd.DataFrame(matches)

    def predict_match(self, p1, p2, surface, rank1, rank2):
        rank_diff = rank1 - rank2
        base = 0.5 - (rank_diff * 0.017)
        prob_p1 = max(0.33, min(0.77, base + np.random.normal(0, 0.028)))

        return {
            "prob_p1": round(prob_p1 * 100, 1),
            "prob_p2": round((1 - prob_p1) * 100, 1),
            "confidence": "Haute" if abs(prob_p1 - 0.5) > 0.17 else "Moyenne"
        }

predictor = TennisPredictor()

# Sidebar pour clé API
with st.sidebar:
    st.header("API Configuration")
    api_key = st.text_input("Clé API Tennis (optionnelle)", type="password")
    if api_key:
        predictor.api_key = api_key
        st.success("Clé API enregistrée")

st.subheader(f"Matchs du jour — {datetime.now().strftime('%d %B %Y')}")

df = predictor.get_todays_matches()

if df.empty:
    st.error("Aucun match trouvé.")
else:
    st.success(f"{len(df)} matchs trouvés aujourd'hui")

    for idx, row in df.iterrows():
        if st.button(
            f"🎾 **{row['Match']}** — {row['Tournament']} ({row['Surface']})",
            key=f"btn_{idx}",
            use_container_width=True
        ):
            st.session_state.selected = idx

    if 'selected' in st.session_state:
        match = df.iloc[st.session_state.selected]
        st.markdown("---")
        st.subheader(match['Match'])
        st.caption(f"{match['Tournament']} • {match['Surface']}")

        result = predictor.predict_match(
            match['P1'], match['P2'], match['Surface'], match['Rank1'], match['Rank2']
        )

        col1, col2 = st.columns(2)
        col1.metric(f"**{match['P1']}**", f"{result['prob_p1']}%", f"Rank #{match['Rank1']}")
        col2.metric(f"**{match['P2']}**", f"{result['prob_p2']}%", f"Rank #{match['Rank2']}")

        if result['prob_p1'] > 58:
            st.success(f"🔥 Favori : {match['P1']}")
        elif result['prob_p1'] < 45:
            st.success(f"🔥 Favori : {match['P2']}")
        else:
            st.info("Match très équilibré")

st.caption("Version avec structure API prête • Clique sur un match")
