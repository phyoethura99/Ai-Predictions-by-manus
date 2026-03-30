import streamlit as st
import datetime
import requests
from google import genai
import time
import json
import os
import dateutil.parser

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
                expiry = datetime.datetime.fromisoformat(cache_data['expiry'])
                if datetime.datetime.now(datetime.timezone.utc) < expiry.replace(tzinfo=datetime.timezone.utc):
                    return cache_data['data']
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
            json.dump({'data': data, 'expiry': expiry_dt.isoformat()}, f)
    except Exception as e:
        st.sidebar.error(f"Cache Error: {str(e)}")

# Time Handling
now_mm = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=6, minutes=30)
today_mm = now_mm.date()

# Dictionary & Session State
if 'lang' not in st.session_state:
    st.session_state.lang = 'EN'
if 'h_teams' not in st.session_state:
    st.session_state.h_teams = ["Select Team"]
if 'a_teams' not in st.session_state:
    st.session_state.a_teams = ["Select Team"]
if 'display_matches' not in st.session_state:
    st.session_state.display_matches = []
if 'check_performed' not in st.session_state:
    st.session_state.check_performed = False

def toggle_lang():
    st.session_state.lang = 'MM' if st.session_state.lang == 'EN' else 'EN'

d = {
    'EN': {
        'title1': 'Predictions', 'sel_league': 'Select League', 'sel_date': 'Select Date',
        'btn_check': 'Check Matches Now', 'title2': 'Select Team',
        'home': 'HOME TEAM', 'away': 'AWAY TEAM', 'btn_gen': 'Generate Predictions',
        'trans_btn': 'မြန်မာဘာသာသို့ ပြောင်းရန်',
        'date_opts': ["Manual Date", "Within 24 Hours", "Within 48 Hours"],
        'ai_lang': 'English',
        'no_match': 'No match found between these teams! Please check the Match Table.',
        'no_fixture': 'No matches available for this date.'
    },
    'MM': {
        'title1': 'ပွဲကြိုခန့်မှန်းချက်များ', 'sel_league': 'လိဂ်ကို ရွေးချယ်ပါ', 'sel_date': 'ရက်စွဲကို ရွေးချယ်ပါ',
        'btn_check': 'ပွဲစဉ်များကို စစ်ဆေးမည်', 'title2': 'အသင်းကို ရွေးချယ်ပါ',
        'home': 'အိမ်ရှင်အသင်း', 'away': 'ဧည့်သည်အသင်း', 'btn_gen': 'ခန့်မှန်းချက် ထုတ်ယူမည်',
        'trans_btn': 'Switch to English',
        'date_opts': ["ရက်စွဲတပ်၍ရှာမည်", "၂၄ နာရီအတွင်း", "၄၈ နာရီအတွင်း"],
        'ai_lang': 'Burmese',
        'no_match': 'ရွေးထားသော ပွဲစဉ်မရှိပါ။ Match Table ကို ပြန်စစ်ပါ။',
        'no_fixture': 'ရွေးထားသော ရက်စွဲတွင် ပွဲစဉ်မရှိပါ။'
    }
}
lang = st.session_state.lang

league_codes = {
    "All Leagues": "ALL",
    "FIFA World Cup": "WC",
    "UEFA Champions League": "CL",
    "Bundesliga (Germany)": "BL1",
    "Eredivisie (Netherlands)": "DED",
    "Campeonato Brasileiro Série A (Brazil)": "BSA",
    "La Liga (Spain)": "PD",
    "Ligue 1 (France)": "FL1",
    "Championship (England)": "ELC",
    "Primeira Liga (Portugal)": "PPL",
    "European Championship": "EC",
    "Serie A (Italy)": "SA",
    "Premier League (England)": "PL"
}

league_name_map = {
    "FIFA World Cup": "FIFA World Cup",
    "UEFA Champions League": "UEFA Champions League",
    "Bundesliga": "Bundesliga (Germany)",
    "Eredivisie": "Eredivisie (Netherlands)",
    "Campeonato Brasileiro Série A": "Campeonato Brasileiro Série A (Brazil)",
    "Primera Division": "La Liga (Spain)",
    "Ligue 1": "Ligue 1 (France)",
    "Championship": "Championship (England)",
    "Primeira Liga": "Primeira Liga (Portugal)",
    "European Championship": "European Championship",
    "Serie A": "Serie A (Italy)",
    "Premier League": "Premier League (England)"
}

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Language Toggle
col_space, col_lang = st.columns([7, 3])
with col_lang:
    st.markdown('<div class="lang-wrapper">', unsafe_allow_html=True)
    st.button(d[lang]["trans_btn"], key="lang_btn", on_click=toggle_lang, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div class="title-style">{d[lang]["title1"]}</div>', unsafe_allow_html=True)

# Select League & Date
st.markdown(f'<p style="color:#aaa; margin-left:15px;">{d[lang]["sel_league"]}</p>', unsafe_allow_html=True)
league_keys = list(league_codes.keys())
league = st.selectbox("L", league_keys, index=1, label_visibility="collapsed")

st.markdown(f'<p style="color:#aaa; margin-left:15px; margin-top:15px;">{d[lang]["sel_date"]}</p>', unsafe_allow_html=True)
date_option = st.radio("Date Option", d[lang]['date_opts'], horizontal=True, label_visibility="collapsed")
sel_date = st.date_input("D", value=today_mm, min_value=today_mm, label_visibility="collapsed")

# Check Matches Now
st.markdown('<div class="check-btn-wrapper">', unsafe_allow_html=True)
check_click = st.button(d[lang]["btn_check"], key="check_btn", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if check_click:
    st.session_state.check_performed = True
    progress_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.01)
        progress_bar.progress(percent_complete + 1)
    
    with st.spinner('Checking Matches...'):
        try:
            l_code = league_codes[league]
            table_cache_key = f"table_v2_{l_code}_{sel_date}_{date_option}"
            cached_table = get_disk_cache(table_cache_key)

            if cached_table:
                st.session_state.display_matches = cached_table['matches']
                st.session_state.h_teams = cached_table['h_teams']
                st.session_state.a_teams = cached_table['a_teams']
            else:
                token = st.secrets["api_keys"]["FOOTBALL_DATA_KEY"]
                if date_option == d[lang]['date_opts'][1]:
                    d_from, d_to = today_mm, today_mm + datetime.timedelta(days=1)
                elif date_option == d[lang]['date_opts'][2]:
                    d_from, d_to = today_mm, today_mm + datetime.timedelta(days=2)
                else:
                    d_from = d_to = sel_date

                d_from_api = d_from - datetime.timedelta(days=1)
                d_to_api = d_to + datetime.timedelta(days=1)

                if l_code == "ALL":
                    target_codes = ",".join([v for k, v in league_codes.items() if v != "ALL"])
                    url = f"https://api.football-data.org/v4/matches?competitions={target_codes}&dateFrom={d_from_api}&dateTo={d_to_api}"
                else:
                    url = f"https://api.football-data.org/v4/competitions/{l_code}/matches?dateFrom={d_from_api}&dateTo={d_to_api}"
                
                headers = {'X-Auth-Token': token}
                response = requests.get(url, headers=headers)
                data = response.json()
                matches = data.get('matches', [])
                
                st.session_state.display_matches = [] 
                if matches:
                    h_set, a_set = set(), set()
                    for m in matches:
                        if m['status'] in ['SCHEDULED', 'TIMED']:
                            utc_dt = datetime.datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
                            mm_dt = utc_dt + datetime.timedelta(hours=6, minutes=30)
                            
                            if d_from <= mm_dt.date() <= d_to:
                                h, a = m['homeTeam']['name'], m['awayTeam']['name']
                                h_logo = m['homeTeam'].get('crest', '')
                                a_logo = m['awayTeam'].get('crest', '')
                                l_display = league_name_map.get(m['competition']['name'], m['competition']['name'])
                                dt_str = mm_dt.strftime("%d/%m %H:%M")
                                h_set.add(h)
                                a_set.add(a)
                                st.session_state.display_matches.append({
                                    'datetime': dt_str, 'home': h, 'away': a, 'league': l_display,
                                    'h_logo': h_logo, 'a_logo': a_logo, 'utc_str': m['utcDate']
                                })
                    
                    st.session_state.h_teams = ["Select Team"] + sorted(list(h_set)) if h_set else ["No matches found"]
                    st.session_state.a_teams = ["Select Team"] + sorted(list(a_set)) if a_set else ["No matches found"]
                    
                    cache_expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=59)
                    set_disk_cache(table_cache_key, {
                        'matches': st.session_state.display_matches,
                        'h_teams': st.session_state.h_teams,
                        'a_teams': st.session_state.a_teams
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
        grouped_matches.setdefault(match['league'], []).append(match)
    
    for l_title, matches_list in grouped_matches.items():
        st.markdown(f'<div style="color:#FFD700; font-weight:bold; margin: 15px 0 5px 15px; border-bottom: 1px solid #333;">🏆 {l_title}</div>', unsafe_allow_html=True)
        for idx, m in enumerate(matches_list, 1):
            st.markdown(f"""
                <div class="match-row" style="height: auto; padding: 15px 10px;">
                    <div class="col-no">#{idx}</div>
                    <div class="col-time" style="font-size: 11px;">📅 {m['datetime']}</div>
                    <div class="col-team" style="display: flex; flex-direction: column; align-items: center; text-align: center;">
                        <img src="{m['h_logo']}" width="30" style="margin-bottom:5px;">
                        <div>{m['home']}</div>
                    </div>
                    <div class="col-vs">VS</div>
                    <div class="col-team" style="display: flex; flex-direction: column; align-items: center; text-align: center;">
                        <img src="{m['a_logo']}" width="30" style="margin-bottom:5px;">
                        <div>{m['away']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
elif st.session_state.check_performed:
    st.markdown(f"""
        <div style="background-color:rgba(255,0,0,0.1); padding:20px; border-radius:10px; border:1px solid #ff4b4b; text-align:center; margin:20px;">
            <h3 style="color:#ff4b4b; margin:0;">⚠️ Warning</h3>
            <p style="color:white; font-size:18px; margin-top:10px;">{d[lang]['no_fixture']}</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="title-style" style="font-size:45px; margin-top:20px;">{d[lang]["title2"]}</div>', unsafe_allow_html=True)

# --- Helper: API-Sports Data Fetching ---
def get_api_sports_stats(h_team, a_team, match_date):
    api_key = st.secrets["api_keys"]["API_SPORTS_KEY"]
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': api_key}
    MAJOR_LEAGUE_IDS = {'Premier League': 39, 'La Liga': 140, 'Serie A': 135, 'Bundesliga': 78, 'Ligue 1': 61}
    
    try:
        time.sleep(2)
        search_url = f"https://v3.football.api-sports.io/fixtures?date={match_date}"
        res = requests.get(search_url, headers=headers, timeout=15).json()
        
        fixture_obj = None
        if 'response' in res and res['response']:
            for f in res['response']:
                f_home = f['teams']['home']['name'].lower()
                f_away = f['teams']['away']['name'].lower()
                if (h_team.lower() in f_home or f_home in h_team.lower()) and (a_team.lower() in f_away or f_away in a_team.lower()):
                    fixture_obj = f
                    break
        
        if not fixture_obj: raise Exception("Fixture not found")
        f_id = fixture_obj['fixture']['id']
        h_real_id = fixture_obj['teams']['home']['id']
        a_real_id = fixture_obj['teams']['away']['id']
        league_id = fixture_obj['league']['id']
        season = fixture_obj['league']['season']

        standings_data = ""
        s_res = requests.get(f"https://v3.football.api-sports.io/standings?league={league_id}&season={season}", headers=headers, timeout=10).json()
        if s_res.get('response') and s_res['response']:
            for group in s_res['response'][0]['league']['standings']:
                for rank in group:
                    if int(rank['team']['id']) in [int(h_real_id), int(a_real_id)]:
                        standings_data += f"[{s_res['response'][0]['league']['name']}] {rank['team']['name']}: Rank {rank['rank']} (Pts: {rank['points']}, Form: {rank.get('form', 'N/A')}). "

        pred_res = requests.get(f"https://v3.football.api-sports.io/predictions?fixture={f_id}", headers=headers, timeout=10).json()
        inj_res = requests.get(f"https://v3.football.api-sports.io/injuries?fixture={f_id}", headers=headers, timeout=10).json()
        h_l10 = requests.get(f"https://v3.football.api-sports.io/fixtures?team={h_real_id}&last=10&status=FT", headers=headers, timeout=10).json()
        a_l10 = requests.get(f"https://v3.football.api-sports.io/fixtures?team={a_real_id}&last=10&status=FT", headers=headers, timeout=10).json()
        
        h_next = requests.get(f"https://v3.football.api-sports.io/fixtures?team={h_real_id}&next=2", headers=headers, timeout=10).json()
        a_next = requests.get(f"https://v3.football.api-sports.io/fixtures?team={a_real_id}&next=2", headers=headers, timeout=10).json()

        return {
            'analysis': pred_res.get('response', [None])[0],
            'injuries': inj_res.get('response', []),
            'standings': standings_data if standings_data else "No Standings Found",
            'h_last_10': h_l10.get('response', []),
            'a_last_10': a_l10.get('response', []),
            'h_schedule': h_next.get('response', []),
            'a_schedule': a_next.get('response', []),
            'h_id': h_real_id, 'a_id': a_real_id,
            'league_name': fixture_obj['league']['name']
        }
    except Exception as e:
        st.error(f"API-Sports Error: {str(e)}")
        return None

# --- Helper: AI Response ---
def get_gemini_response(prompt):
    ai_key = st.secrets["gemini_keys"]["GEMINI_KEY"]
    try:
        client = genai.Client(api_key=ai_key)
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt,
            config={'temperature': 0}
        )
        return response.text
    except Exception as e:
        st.error(f"Gemini AI Error: {str(e)}")
        return "⚠️ AI Service Busy. Please try again later."

# Home vs Away Section
c1, cvs, c2 = st.columns([2, 1, 2])
with c1:
    st.markdown(f'<p style="color:white; text-align:center; font-weight:900; font-size:12px;">{d[lang]["home"]}</p>', unsafe_allow_html=True)
    h_team = st.selectbox("H", st.session_state.h_teams, key="h", label_visibility="collapsed")
with cvs:
    st.markdown('<div style="display: flex; justify-content: center; align-items: center; height: 100%;"><div class="vs-ball">vs</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<p style="color:white; text-align:center; font-weight:900; font-size:12px;">{d[lang]["away"]}</p>', unsafe_allow_html=True)
    a_team = st.selectbox("A", st.session_state.a_teams, key="a", label_visibility="collapsed")

st.markdown('<div class="gen-btn-wrapper">', unsafe_allow_html=True)
gen_click = st.button(d[lang]["btn_gen"], key="gen_btn", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if gen_click:
    if h_team and a_team and h_team not in ["Select Team", "No matches found"]:
        match_obj = next((m for m in st.session_state.display_matches if m['home'] == h_team and m['away'] == a_team), None)
        if match_obj:
            progress_bar = st.progress(0)
            for percent_complete in range(100):
                time.sleep(0.01)
                progress_bar.progress(percent_complete + 1)
                
            with st.spinner('AI is analyzing real-time data from API...'):
                cache_key = f"pred_final_v12_{h_team}_{a_team}_{today_mm}"
                cached_result = get_disk_cache(cache_key)

                if cached_result:
                    st.markdown(cached_result, unsafe_allow_html=True)
                else:
                    real_data = get_api_sports_stats(h_team, a_team, today_mm.isoformat())
                    if real_data:
                        injury_list = [f"{i['player']['name']} ({i['player']['reason']})" for i in real_data.get('injuries', [])]
                        stats_context = f"""
                        [SOURCE: API-SPORTS VERIFIED DATA]
                        - Match: {h_team} vs {a_team}
                        - Tournament: {real_data['league_name']}
                        - STANDINGS: {real_data['standings']}
                        - INJURIES: {', '.join(injury_list) if injury_list else 'None'}
                        """
                        prompt = f"""
                        SYSTEM: Professional Tactical Analyst.
                        {stats_context}
                        Respond in BURMESE (Unicode).
                        FORMAT:
                        # သုံးသပ်ချက်
                        **{h_team} ခြေစွမ်း**
                        **{a_team} ခြေစွမ်း**
                        **နည်းဗျူဟာပိုင်း**
                        ### **Summarize Table**
                        | Category | Prediction |
                        | :--- | :--- |
                        | Winner | [မြန်မာလို] |
                        | Score | [Result] |
                        # **🏆 အကျိုးအကြောင်းခိုင်လုံဆုံးရွေးချယ်မှု: [ရလဒ်]**
                        """
                        response_text = get_gemini_response(prompt)
                        final_output = f'<div style="background:#0c0c0c; padding:20px; border-radius:15px; border:1px solid #39FF14; color:white;">{response_text}</div>'
                        set_disk_cache(cache_key, final_output)
                        st.markdown(final_output, unsafe_allow_html=True)
    else:
        st.warning("Please select teams first!")
