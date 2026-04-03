import streamlit as st
import datetime
import requests
from google import genai
import time
import json
import os
import dateutil.parser
from mapping import LANG_MAP, LEAGUE_CODES, LEAGUE_NAME_MAP, get_team_id, MAJOR_LEAGUE_IDS

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

# Session State
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

# --- UI Styling ---
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Main App ---

# Language toggle button
col_space, col_lang = st.columns([7, 3])
with col_lang:
    st.markdown("<div class=\"lang-wrapper\">", unsafe_allow_html=True)
    st.button(LANG_MAP[lang]["trans_btn"], key="lang_btn", on_click=toggle_lang, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f'<div class="title-style">{LANG_MAP[lang]["title1"]}</div>', unsafe_allow_html=True)

# Select League & Date
st.markdown(f'<p style="color:#aaa; margin-left:15px;">{LANG_MAP[lang]["sel_league"]}</p>', unsafe_allow_html=True)
league_keys = list(LEAGUE_CODES.keys())
league = st.selectbox("L", league_keys, index=1, label_visibility="collapsed")

st.markdown(f'<p style="color:#aaa; margin-left:15px; margin-top:15px;">{LANG_MAP[lang]["sel_date"]}</p>', unsafe_allow_html=True)
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
            l_code = LEAGUE_CODES[league]["fd_id"]
            table_cache_key = f"table_v2_{l_code}_{sel_date}_{date_option}"
            cached_table = get_disk_cache(table_cache_key)

            if cached_table:
                st.session_state.display_matches = cached_table["matches"]
                st.session_state.h_teams = cached_table["h_teams"]
                st.session_state.a_teams = cached_table["a_teams"]
            else:
                token = st.secrets["api_keys"]["FOOTBALL_DATA_KEY"]
                if date_option == LANG_MAP[lang]["date_opts"][1]:
                    d_from, d_to = today_mm, today_mm + datetime.timedelta(days=1)
                elif date_option == LANG_MAP[lang]["date_opts"][2]:
                    d_from, d_to = today_mm, today_mm + datetime.timedelta(days=2)
                else:
                    d_from = d_to = sel_date

                d_from_api = d_from - datetime.timedelta(days=1)
                d_to_api = d_to + datetime.timedelta(days=1)

                if l_code == "ALL":
                    target_codes = ",".join([v["fd_id"] for k, v in LEAGUE_CODES.items() if v["fd_id"] != "ALL"])
                    url = f"https://api.football-data.org/v4/matches?competitions={target_codes}&dateFrom={d_from_api.isoformat()}&dateTo={d_to_api.isoformat()}"
                else:
                    url = f"https://api.football-data.org/v4/competitions/{l_code}/matches?dateFrom={d_from_api.isoformat()}&dateTo={d_to_api.isoformat()}"
                
                headers = {"X-Auth-Token": token}
                response = requests.get(url, headers=headers)
                data = response.json()
                matches = data.get("matches", [])
                
                st.session_state.display_matches = [] 
                if matches:
                    h_set, a_set = set(), set()
                    for m in matches:
                        if m["status"] in ["SCHEDULED", "TIMED"]:
                            utc_dt = datetime.datetime.strptime(m["utcDate"], "%Y-%m-%dT%H:%M:%SZ")
                            mm_dt = utc_dt + datetime.timedelta(hours=6, minutes=30)
                            
                            if d_from <= mm_dt.date() <= d_to:
                                h, a = m["homeTeam"]["name"], m["awayTeam"]["name"]
                                h_logo = m["homeTeam"].get("crest", "")
                                a_logo = m["awayTeam"].get("crest", "")
                                l_display = LEAGUE_NAME_MAP.get(m["competition"]["name"], m["competition"]["name"])
                                dt_str = mm_dt.strftime("%d/%m %H:%M")
                                h_set.add(h)
                                a_set.add(a)
                                st.session_state.display_matches.append({
                                    "datetime": dt_str, "home": h, "away": a, "league": l_display,
                                    "h_logo": h_logo, "a_logo": a_logo, "utc_str": m["utcDate"],
                                    "home_team_id_fd": m["homeTeam"]["id"],
                                    "away_team_id_fd": m["awayTeam"]["id"],
                                    "home_team_id_api_sports": get_team_id(l_display, h, "API-Sports"),
                                    "away_team_id_api_sports": get_team_id(l_display, a, "API-Sports")
                                })
                    
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
        st.markdown(f'<div style="color:#FFD700; font-weight:bold; margin: 15px 0 5px 15px; border-bottom: 1px solid #333;">🏆 {l_title}</div>', unsafe_allow_html=True)
        for idx, m in enumerate(matches_list, 1):
            st.markdown(f'''
                <div class="match-row" style="height: auto; padding: 15px 10px;">
                    <div class="col-no">#{idx}</div>
                    <div class="col-time" style="font-size: 11px;">📅 {m["datetime"]}</div>
                    <div class="col-team" style="display: flex; flex-direction: column; align-items: center; text-align: center;">
                        <img src="{m["h_logo"]}" width="30" style="margin-bottom:5px;">
                        <div>{m["home"]}</div>
                    </div>
                    <div class="col-vs">VS</div>
                    <div class="col-team" style="display: flex; flex-direction: column; align-items: center; text-align: center;">
                        <img src="{m["a_logo"]}" width="30" style="margin-bottom:5px;">
                        <div>{m["away"]}</div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
elif st.session_state.check_performed:
    st.markdown(f'''
        <div style="background-color:rgba(255,0,0,0.1); padding:20px; border-radius:10px; border:1px solid #ff4b4b; text-align:center; margin:20px;">
            <h3 style="color:#ff4b4b; margin:0;">⚠️ Warning</h3>
            <p style="color:white; font-size:18px; margin-top:10px;">{LANG_MAP[lang]["no_fixture"]}</p>
        </div>
    ''', unsafe_allow_html=True)

st.markdown(f'<div class="title-style" style="font-size:45px; margin-top:20px;">{LANG_MAP[lang]["title2"]}</div>', unsafe_allow_html=True)

# --- Helper: API-Sports Data Fetching ---
def get_api_sports_stats(h_team, a_team, match_obj):
    api_key = st.secrets["api_keys"]["API_SPORTS_KEY"]
    headers = {"x-rapidapi-host": "v3.football.api-sports.io", "x-rapidapi-key": api_key}
    
    try:
        h_real_id = match_obj.get("home_team_id_api_sports")
        a_real_id = match_obj.get("away_team_id_api_sports")
        
        if not h_real_id or not a_real_id:
            raise Exception("API-Sports Team ID not found in mapping.")

        # Search for fixture using team IDs and date
        match_date = dateutil.parser.parse(match_obj["utc_str"]).date()
        search_url = f"https://v3.football.api-sports.io/fixtures?date={match_date.isoformat()}&team={h_real_id}"
        res = requests.get(search_url, headers=headers, timeout=15).json()
        
        fixture_obj = None
        if "response" in res and res["response"]:
            for f in res["response"]:
                if f["teams"]["home"]["id"] == h_real_id and f["teams"]["away"]["id"] == a_real_id:
                    fixture_obj = f
                    break
        
        if not fixture_obj: raise Exception("Fixture not found on API-Sports for the given date and teams.")
        
        f_id = fixture_obj["fixture"]["id"]
        league_id = fixture_obj["league"]["id"]
        season = fixture_obj["league"]["season"]

        standings_data = ""
        s_res = requests.get(f"https://v3.football.api-sports.io/standings?league={league_id}&season={season}", headers=headers, timeout=15).json()
        if "response" in s_res and s_res["response"]:
            for standing in s_res["response"][0]["league"]["standings"][0]:
                if standing["team"]["id"] == h_real_id:
                    standings_data += f"Home Team Rank: {standing['rank']}. Points: {standing['points']}. Form: {standing['form']}. Description: {standing['description'] if standing['description'] else 'N/A'}.\n"
                elif standing["team"]["id"] == a_real_id:
                    standings_data += f"Away Team Rank: {standing['rank']}. Points: {standing['points']}. Form: {standing['form']}. Description: {standing['description'] if standing['description'] else 'N/A'}.\n"
        
        injuries_data = ""
        i_res = requests.get(f"https://v3.football.api-sports.io/injuries?fixture={f_id}", headers=headers, timeout=15).json()
        if "response" in i_res and i_res["response"]:
            for injury in i_res["response"]:
                player_name = injury["player"]["name"]
                team_name = injury["team"]["name"]
                reason = injury["reason"]
                injuries_data += f"{team_name}: {player_name} - {reason}.\n"

        h2h_data = ""
        h2h_res = requests.get(f"https://v3.football.api-sports.io/fixtures/headtohead?h2h={h_real_id}-{a_real_id}", headers=headers, timeout=15).json()
        if "response" in h2h_res and h2h_res["response"]:
            for h2h_match in h2h_res["response"]:
                home_team_name = h2h_match["teams"]["home"]["name"]
                away_team_name = h2h_match["teams"]["away"]["name"]
                score_home = h2h_match["score"]["fulltime"]["home"]
                score_away = h2h_match["score"]["fulltime"]["away"]
                h2h_data += f"{home_team_name} {score_home}-{score_away} {away_team_name}\n"

        return standings_data, injuries_data, h2h_data

    except Exception as e:
        st.error(f"API-Sports Data Error: {str(e)}")
        return "", "", ""

# --- Helper: Gemini AI Prediction ---
def get_gemini_prediction(home_team, away_team, standings, injuries, h2h, ai_lang):
    genai.configure(api_key=st.secrets["api_keys"]["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-pro")

    prompt = f"""
    You are an AI football analyst. Analyze the following data to predict the outcome of the match between {home_team} and {away_team}.
    Provide a prediction, a confidence score (out of 100), and a brief explanation in {ai_lang}.

    Match: {home_team} vs {away_team}

    Standings Data:
    {standings if standings else "N/A"}

    Injuries Data:
    {injuries if injuries else "N/A"}

    Head-to-Head Data:
    {h2h if h2h else "N/A"}

    Prediction:
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini AI Error: {str(e)}"

# --- Part 2: Select Teams and Generate Prediction ---

if "display_matches" in st.session_state and st.session_state.display_matches:
    team_names = sorted(list(set([f["home"] for f in st.session_state.display_matches] + [f["away"] for f in st.session_state.display_matches])))
    home_team = st.selectbox(LANG_MAP[lang]["home"], team_names)
    away_team = st.selectbox(LANG_MAP[lang]["away"], team_names, index=min(1, len(team_names)-1) if len(team_names)>1 else 0)

    # Find the specific match
    selected_match = None
    for f in st.session_state.display_matches:
        if f["home"] == home_team and f["away"] == away_team:
            selected_match = f
            break

    if selected_match:
        st.markdown(f'''
        <div class="match-card">
            📅 {selected_match["datetime"]}<br><br>
            <span class="team-name">{home_team.upper()}</span>
            <span class="vs">VS</span>
            <span class="team-name">{away_team.upper()}</span>
        </div>
        ''', unsafe_allow_html=True)

        if st.button(LANG_MAP[lang]["btn_gen"]):
            with st.spinner("Generating prediction..."):
                # Get Team IDs using the mapping logic
                league_full_name = LEAGUE_NAME_MAP.get(selected_match["league"], selected_match["league"])
                
                fd_home_id = selected_match["home_team_id_fd"]
                fd_away_id = selected_match["away_team_id_fd"]

                as_home_id = get_team_id(league_full_name, home_team, "API-Sports")
                as_away_id = get_team_id(league_full_name, away_team, "API-Sports")

                st.write(f"**Football-Data Home ID:** {fd_home_id}")
                st.write(f"**Football-Data Away ID:** {fd_away_id}")
                st.write(f"**API-Sports Home ID:** {as_home_id}")
                st.write(f"**API-Sports Away ID:** {as_away_id}")

                standings, injuries, h2h = get_api_sports_stats(home_team, away_team, selected_match)
                prediction = get_gemini_prediction(home_team, away_team, standings, injuries, h2h, LANG_MAP[lang]["ai_lang"])
                st.success(prediction)

    else:
        st.error(LANG_MAP[lang]["no_match"])

