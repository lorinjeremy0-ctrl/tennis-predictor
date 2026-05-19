import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Tennis Predictor Pro", page_icon="🎾", layout="wide")

st.title("🎾 Tennis Predictor Pro")
st.markdown("**Matchs du jour en temps réel via API-Tennis**")

# Ta clé API
API_KEY = "9246fd22ef69fb3e29f1f480685a6760d623a2a66f7de169ed93af5d60f14fbd"

class TennisPredictor:
    def __init__(self):
        self.surface_factors = {"Hard": 1.0, "Clay": 0.93, "Grass": 1.07, "default": 1.0}

    def get_todays_matches(self):
        try:
            url = f"https://api.api-tennis.com/tennis/?method=get_fixtures&APIkey={API_KEY}&date_start={datetime.now().strftime('%Y-%m-%d')}"
            response = requests.get(url, timeout=15)
            data = response.json()

            if data.get("success") == "1" and "result" in data:
                matches = []
                for m in data["result"][:25]:  # Limite à 25 matchs
                    matches.append({
                        "Match": f"{m.get('event_home_team', 'Player1')} vs {m.get('event_away_team', 'Player2')}",
                        "Tournament": m.get('league_name', 'Unknown Tournament'),
                        "Surface": m.get('surface_type', 'Hard'),
                        "P1": m.get('event_home_team', 'Player1'),
                        "P2": m.get('event_away_team', 'Player2'),
                        "Rank1": int(m.get('event_home_team_rank', 50)) or 50,
                        "Rank2": int(m.get('event_away_team_rank', 50)) or 50,
                        "Time": m.get('event_time', '')
                    })
                return pd.DataFrame(matches)
            else:
                st.error("Erreur API : " + str(data.get("message", "Pas de données")))
                return self.get_simulated_matches()
        except Exception as e:
            st.error(f"Impossible de se connecter à l'API : {e}")
            return self.get_simulated_matches()

    def get_simulated_matches(self):
        # Fallback si l'API ne marche pas
        matches = [
            {"Match": "Sinner vs Alcaraz", "Tournament": "Roland Garros", "Surface": "Clay", "P1": "Sinner", "P2": "Alcaraz", "Rank1": 1, "Rank2": 2},
            {"Match": "Djokovic vs Rune", "Tournament": "Roland Garros", "Surface": "Clay", "P1": "Djokovic", "P2": "Rune", "Rank1": 5, "Rank2": 13},
        ]
        return pd.DataFrame(matches)

    def predict_match(self, p1, p2, surface, rank1, rank2):
        rank_diff = rank1 - rank2
        base = 0.5 - (rank_diff * 0.017)
        prob_p1 = max(0.33, min(0.77, base + np.random.normal(0, 0.028)))

        return {
            "prob_p1": round(prob_p1 * 100, 1),
            "prob_p2": round((1 - prob_p1) * 100, 1),
        }

predictor = TennisPredictor()

st.subheader(f"Matchs du jour — {datetime.now().strftime('%d %B %Y')}")

df = predictor.get_todays_matches()

if not df.empty:
    st.success(f"{len(df)} matchs trouvés aujourd'hui")
    
    for idx, row in df.iterrows():
        if st.button(f"🎾 **{row['Match']}** — {row['Tournament']} ({row['Surface']})", 
                     key=f"btn_{idx}", use_container_width=True):
            st.session_state.selected = idx

    if 'selected' in st.session_state:
        match = df.iloc[st.session_state.selected]
        st.markdown("---")
        st.subheader(match['Match'])
        st.caption(f"{match['Tournament']} • {match['Surface']}")

        result = predictor.predict_match(match['P1'], match['P2'], match['Surface'], match['Rank1'], match['Rank2'])

        col1, col2 = st.columns(2)
        col1.metric(f"**{match['P1']}**", f"{result['prob_p1']}%", f"Rank #{match['Rank1']}")
        col2.metric(f"**{match['P2']}**", f"{result['prob_p2']}%", f"Rank #{match['Rank2']}")

else:
    st.error("Aucun match trouvé.")

st.caption("Utilisation de ta clé API-Tennis")
