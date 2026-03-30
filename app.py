import streamlit as st
import datetime
import requests
from google import genai
import time
import json
import os
import dateutil.parser
from mapping import LANG_MAP, LEAGUE_CODES, LEAGUE_NAME_MAP, get_team_id

# UI Configuration
st.set_page_config(
    page_title="Football AI",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# --- Disk Caching System ---
CACHE_DIR = "/tmp/data_cache"
try:
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)
except Exception:
    CACHE_DIR = "/tmp"

def get_disk_cache(key):
    safe_key = key.replace("/", "_")
    file_path = os.path.join(CACHE_DIR, f"{safe_key}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                cache_data = json.load(f)
                expiry = datetime.datetime.fromisoformat(cache_data["expiry"])
                if datetime.datetime.now(datetime.timezone.utc) < expiry.replace(tzinfo=datetime.timezone.utc):
                    return cache_data["data"]
        except:
            return None
    return None

def set_disk_cache(key, data, expiry_dt=None, days=19):
    if expiry_dt is None:
        expiry_dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=days)
    
    safe_key = key.replace("/", "_")
    file_path = os.path.join(CACHE_DIR, f"{safe_key}.json")
    try:
        with open(file_path, "w") as f:
            json.dump({"data": data, "expiry": expiry_dt.isoformat()}, f)
    except Exception as e:
        st.sidebar.error(f"Cache Error: {str(e)}")

# Time Handling
now_mm = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=6, minutes=30)
today_mm = now_mm.date()

# Dictionary & Session State
if "lang" not in st.session_state:
    st.session_state.lang = "EN"
if "h_teams" not in st.session_state:
    st.session_state.h_teams = ["Select Team"]
if "a_teams" not in st.session_state:
    st.session_state.a_teams = ["Select Team"]
if "display_matches" not in st.session_state:
    st.session_state.display_matches = []
if "check_performed" not in st.session_state:
    st.session_state.check_performed = False

def toggle_lang():
    st.session_state.lang = "MM" if st.session_state.lang == "EN" else "EN"

lang = st.session_state.lang

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Language Toggle
col_space, col_lang = st.columns([7, 3])
with col_lang:
    st.markdown("<div class=\"lang-wrapper\">", unsafe_allow_html=True)
    st.button(LANG_MAP[lang]["trans_btn"], key="lang_btn", on_click=toggle_lang, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"<div class=\"title-style\">{LANG_MAP[lang]["title1"]}</div>", unsafe_allow_html=True)

# Select League & Date
st.markdown(f"<p style=\"color:#aaa; margin-left:15px;\">{LANG_MAP[lang]["sel_league"]}</p>", unsafe_allow_html=True)
league_keys = list(LEAGUE_CODES.keys())
league = st.selectbox("L", league_keys, index=1, label_visibility="collapsed")

st.markdown(f"<p style=\"color:#aaa; margin-left:15px; margin-top:15px;\">{LANG_MAP[lang]["sel_date"]}</p>", unsafe_allow_html=True)
date_option = st.radio("Date Option", LANG_MAP[lang]["date_opts"], horizontal=True, label_visibility="collapsed")
sel_date = st.date_input("D", value=today_mm, min_value=today_mm, label_visibility="collapsed")

# Check Matches Now
st.markdown("<div class=\"check-btn-wrapper\">", unsafe_allow_html=True)
check_click = st.button(LANG_MAP[lang]["btn_check"], key="check_btn", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

if check_click:
    st.session_state.check_performed = True
    progress_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.01)
        progress_bar.progress(percent_complete + 1)
    
    with st.spinner("Checking Matches..."):
        try:
            l_code = LEAGUE_CODES[league]
            table_cache_key = f"table_v2_{l_code}_{sel_date}_{date_option}"
            cached_table = get_disk_cache(table_cache_key)

            if cached_table:
                st.session_state.display_matches = cached_table["matches"]
                st.session_state.h_teams = cached_table["h_teams"]
                st.session_state.a_teams = cached_table["a_teams"]
            else:
                football_data_token = st.secrets["api_keys"]["FOOTBALL_DATA_KEY"]
                api_sports_token = st.secrets["api_keys"]["API_SPORTS_KEY"]

                if date_option == LANG_MAP[lang]["date_opts"][1]:
                    d_from, d_to = today_mm, today_mm + datetime.timedelta(days=1)
                elif date_option == LANG_MAP[lang]["date_opts"][2]:
                    d_from, d_to = today_mm, today_mm + datetime.timedelta(days=2)
                else:
                    d_from = d_to = sel_date

                d_from_api = d_from - datetime.timedelta(days=1)
                d_to_api = d_to + datetime.timedelta(days=1)

                all_matches = []
                h_set, a_set = set(), set()

                # Fetch from Football-Data.org
                if l_code == "ALL":
                    target_codes = ",".join([v for k, v in LEAGUE_CODES.items() if v != "ALL"])
                    url_football_data = f"https://api.football-data.org/v4/matches?competitions={target_codes}&dateFrom={d_from_api}&dateTo={d_to_api}"
                else:
                    url_football_data = f"https://api.football-data.org/v4/competitions/{l_code}/matches?dateFrom={d_from_api}&dateTo={d_to_api}"
                
                headers_football_data = {"X-Auth-Token": football_data_token}
                response_football_data = requests.get(url_football_data, headers=headers_football_data)
                data_football_data = response_football_data.json()
                matches_football_data = data_football_data.get("matches", [])

                for m in matches_football_data:
                    if m["status"] in ["SCHEDULED", "TIMED"]:
                        utc_dt = datetime.datetime.strptime(m["utcDate"], "%Y-%m-%dT%H:%M:%SZ")
                        mm_dt = utc_dt + datetime.timedelta(hours=6, minutes=30)
                        
                        if d_from <= mm_dt.date() <= d_to:
                            home_team_name = m["homeTeam"]["name"]
                            away_team_name = m["awayTeam"]["name"]
                            league_display_name = LEAGUE_NAME_MAP.get(m["competition"]["name"], m["competition"]["name"])

                            all_matches.append({
                                "datetime": mm_dt.strftime("%d/%m %H:%M"),
                                "home": home_team_name,
                                "away": away_team_name,
                                "league": league_display_name,
                                "h_logo": m["homeTeam"].get("crest", ""),
                                "a_logo": m["awayTeam"].get("crest", ""),
                                "utc_str": m["utcDate"],
                                "home_team_id_fd": m["homeTeam"]["id"],
                                "away_team_id_fd": m["awayTeam"]["id"],
                                "home_team_id_api_sports": get_team_id(league_display_name, home_team_name, "API-Sports"),
                                "away_team_id_api_sports": get_team_id(league_display_name, away_team_name, "API-Sports")
                            })
                            h_set.add(home_team_name)
                            a_set.add(away_team_name)
                
                st.session_state.display_matches = all_matches
                st.session_state.h_teams = ["Select Team"] + sorted(list(h_set)) if h_set else ["No matches found"]
                st.session_state.a_teams = ["Select Team"] + sorted(list(a_set)) if a_set else ["No matches found"]
                
                cache_expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=59)
                set_disk_cache(table_cache_key, {
                    "matches": st.session_state.display_matches,
                    "h_teams": st.session_state.h_teams,
                    "a_teams": st.session_state.a_teams
                }, expiry_dt=cache_expiry)
            else:
                st.session_state.h_teams = ["No matches found"]
                st.session_state.a_teams = ["No matches found"]
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Display Matches Table
if st.session_state.display_matches:
    grouped_matches = {}
    for match in st.session_state.display_matches:
        grouped_matches.setdefault(match["league"], []).append(match)
    
    for l_title, matches_list in grouped_matches.items():
        st.markdown(f"<div style=\"color:#FFD700; font-weight:bold; margin: 15px 0 5px 15px; border-bottom: 1px solid #333;\">🏆 {l_title}</div>", unsafe_allow_html=True)
        for idx, m in enumerate(matches_list, 1):
            st.markdown(f"""
                <div class=\"match-row\" style=\"height: auto; padding: 15px 10px;\">
                    <div class=\"col-no\">#{idx}</div>
                    <div class=\"col-time\" style=\"font-size: 11px;\">📅 {m["datetime"]}</div>
                    <div class=\"col-team\" style=\"display: flex; flex-direction: column; align-items: center; text-align: center;\">
                        <img src=\"{m["h_logo"]}\" width=\"30\" style=\"margin-bottom:5px;\">
                        <div>{m["home"]}</div>
                    </div>
                    <div class=\"col-vs\">VS</div>
                    <div class=\"col-team\" style=\"display: flex; flex-direction: column; align-items: center; text-align: center;\">
                        <img src=\"{m["a_logo"]}\" width=\"30\" style=\"margin-bottom:5px;\">
                        <div>{m["away"]}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# Prediction Section
if st.session_state.check_performed and not st.session_state.display_matches:
    st.warning(LANG_MAP[lang]["no_fixture"])
elif st.session_state.check_performed and st.session_state.display_matches:
    st.markdown(f"<div class=\"title-style\">{LANG_MAP[lang]["title2"]}</div>", unsafe_allow_html=True)
    
    col_home, col_away = st.columns(2)
    with col_home:
        home_team = st.selectbox(LANG_MAP[lang]["home"], st.session_state.h_teams, key="home_team_select")
    with col_away:
        away_team = st.selectbox(LANG_MAP[lang]["away"], st.session_state.a_teams, key="away_team_select")

    if home_team != "Select Team" and away_team != "Select Team":
        selected_match = None
        for match in st.session_state.display_matches:
            if match["home"] == home_team and match["away"] == away_team:
                selected_match = match
                break

        if selected_match:
            st.markdown(f"""
                <div class=\"match-row\" style=\"height: auto; padding: 15px 10px; background-color: #222; border-radius: 10px; margin-top: 20px;\">
                    <div class=\"col-time\" style=\"font-size: 11px;\">📅 {selected_match["datetime"]}</div>
                    <div class=\"col-team\" style=\"display: flex; flex-direction: column; align-items: center; text-align: center;\">
                        <img src=\"{selected_match["h_logo"]}\" width=\"30\" style=\"margin-bottom:5px;\">
                        <div>{selected_match["home"]}</div>
                    </div>
                    <div class=\"col-vs\">VS</div>
                    <div class=\"col-team\" style=\"display: flex; flex-direction: column; align-items: center; text-align: center;\">
                        <img src=\"{selected_match["a_logo"]}\" width=\"30\" style=\"margin-bottom:5px;\">
                        <div>{selected_match["away"]}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div class=\"check-btn-wrapper\">", unsafe_allow_html=True)
            gen_click = st.button(LANG_MAP[lang]["btn_gen"], key="gen_btn", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            if gen_click:
                with st.spinner("Generating Prediction..."):
                    # Placeholder for prediction logic
                    st.write("Prediction for", home_team, "vs", away_team, "will be generated here.")
                    st.write("Football-Data Home ID:", selected_match.get("home_team_id_fd"))
                    st.write("Football-Data Away ID:", selected_match.get("away_team_id_fd"))
                    st.write("API-Sports Home ID:", selected_match.get("home_team_id_api_sports"))
                    st.write("API-Sports Away ID:", selected_match.get("away_team_id_api_sports"))

        else:
            st.warning(LANG_MAP[lang]["no_match"])
    else:
        st.info("Please select both home and away teams to generate predictions.")
                    
