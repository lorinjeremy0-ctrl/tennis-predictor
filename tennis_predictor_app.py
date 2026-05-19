import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Tennis Predictor Pro", page_icon="🎾", layout="wide")

st.title("🎾 Tennis Predictor Pro")
st.markdown("**Vrais matchs du jour via API-Tennis**")

API_KEY = "9246fd22ef69fb3e29f1f480685a6760d623a2a66f7de169ed93af5d60f14fbd"

def get_todays_matches():
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        url = f"https://api.api-tennis.com/tennis/?method=get_fixtures&APIkey={API_KEY}&date_start={today}&date_stop={today}"
        
        response = requests.get(url, timeout=15)
        data = response.json()

        if data.get("success") == "1" and data.get("result"):
            matches = []
            for m in data["result"]:
                matches.append({
                    "Match": f"{m.get('event_home_team')} vs {m.get('event_away_team')}",
                    "Tournament": m.get('league_name', 'Unknown'),
                    "Surface": m.get('surface_type', 'Hard'),
                    "P1": m.get('event_home_team'),
                    "P2": m.get('event_away_team'),
                    "Rank1": int(m.get('event_home_team_rank') or 999),
                    "Rank2": int(m.get('event_away_team_rank') or 999),
                    "Time": m.get('event_time', 'N/A')
                })
            return pd.DataFrame(matches)
        else:
            st.error("L'API n'a retourné aucun match pour aujourd'hui.")
            st.info("Note : Nous sommes en 2026, il est possible qu'il n'y ait pas de tournoi majeur aujourd'hui.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur de connexion à l'API : {e}")
        return pd.DataFrame()

def predict_match(p1, p2, rank1, rank2):
    rank_diff = rank1 - rank2
    prob_p1 = max(0.35, min(0.75, 0.5 - rank_diff * 0.018 + np.random.normal(0, 0.025)))
    return {
        "prob_p1": round(prob_p1 * 100, 1),
        "prob_p2": round((1 - prob_p1) * 100, 1)
    }

# Interface principale
st.subheader(f"Matchs du jour — {datetime.now().strftime('%d %B %Y')}")

df = get_todays_matches()

if not df.empty:
    st.success(f"✅ {len(df)} vrais matchs trouvés aujourd'hui")

    for idx, row in df.iterrows():
        if st.button(f"🎾 **{row['Match']}** — {row['Tournament']} ({row['Surface']})", 
                     key=f"btn_{idx}", use_container_width=True):
            st.session_state.selected = idx

    if 'selected' in st.session_state:
        match = df.iloc[st.session_state.selected]
        st.markdown("---")
        st.subheader(match['Match'])
        st.caption(f"{match['Tournament']} • {match['Surface']} • {match['Time']}")

        result = predict_match(match['P1'], match['P2'], match['Rank1'], match['Rank2'])

        col1, col2 = st.columns(2)
        col1.metric(f"**{match['P1']}**", f"{result['prob_p1']}%", f"Rank #{match['Rank1']}")
        col2.metric(f"**{match['P2']}**", f"{result['prob_p2']}%", f"Rank #{match['Rank2']}")
else:
    st.warning("Aucun match trouvé aujourd'hui via l'API.")

st.caption("Utilisation directe de ta clé API-Tennis")
