LANG_MAP = {
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

LEAGUE_CODES = {
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

LEAGUE_NAME_MAP = {
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

TEAM_ID_MAP = {
    "Premier League (England)": {
        "Football-Data": {
            "Arsenal FC": 57,
            "Aston Villa FC": 58,
            "Chelsea FC": 61,
            "Everton FC": 62,
            "Fulham FC": 63,
            "Liverpool FC": 64,
            "Manchester City FC": 65,
            "Manchester United FC": 66,
            "Newcastle United FC": 67,
            "Sunderland AFC": 71,
            "Tottenham Hotspur FC": 73,
            "Wolverhampton Wanderers FC": 76,
            "Burnley FC": 328,
            "Leeds United FC": 341,
            "Nottingham Forest FC": 351,
            "Crystal Palace FC": 354,
            "Brighton & Hove Albion FC": 397,
            "Brentford FC": 402,
            "West Ham United FC": 563,
            "AFC Bournemouth": 1044
        },
        "API-Sports": {
            "Manchester United": 33,
            "Newcastle": 34,
            "Bournemouth": 35,
            "Fulham": 36,
            "Wolves": 39,
            "Liverpool": 40,
            "Arsenal": 42,
            "Burnley": 44,
            "Everton": 45,
            "Tottenham": 47,
            "West Ham": 48,
            "Chelsea": 49,
            "Manchester City": 50,
            "Brighton": 51,
            "Crystal Palace": 52,
            "Brentford": 55,
            "Sheffield Utd": 62,
            "Nottingham Forest": 65,
            "Aston Villa": 66,
            "Luton": 1359
        }
    },
    "La Liga (Spain)": {
        "Football-Data": {
            "Athletic Club": 77,
            "Club Atlético de Madrid": 78,
            "CA Osasuna": 79,
            "RCD Espanyol de Barcelona": 80,
            "FC Barcelona": 81,
            "Getafe CF": 82,
            "Real Madrid CF": 86,
            "Rayo Vallecano de Madrid": 87,
            "Levante UD": 88,
            "RCD Mallorca": 89,
            "Real Betis Balompié": 90,
            "Real Sociedad de Fútbol": 92,
            "Villarreal CF": 94,
            "Valencia CF": 95,
            "Deportivo Alavés": 263,
            "Elche CF": 285,
            "Girona FC": 298,
            "RC Celta de Vigo": 558,
            "Sevilla FC": 559,
            "Real Oviedo": 1048
        },
        "API-Sports": {
            "Barcelona": 529,
            "Atletico Madrid": 530,
            "Athletic Club": 531,
            "Valencia": 532,
            "Villarreal": 533,
            "Las Palmas": 534,
            "Sevilla": 536,
            "Celta Vigo": 538,
            "Real Madrid": 541,
            "Alaves": 542,
            "Real Betis": 543,
            "Getafe": 546,
            "Girona": 547,
            "Real Sociedad": 548,
            "Granada CF": 715,
            "Almeria": 723,
            "Cadiz": 724,
            "Osasuna": 727,
            "Rayo Vallecano": 728,
            "Mallorca": 798
        }
    },
    "Serie A (Italy)": {
        "Football-Data": {
            "AC Milan": 98,
            "ACF Fiorentina": 99,
            "AS Roma": 100,
            "Atalanta BC": 102,
            "Bologna FC 1909": 103,
            "Cagliari Calcio": 104,
            "Genoa CFC": 107,
            "FC Internazionale Milano": 108,
            "Juventus FC": 109,
            "SS Lazio": 110,
            "Parma Calcio 1913": 112,
            "SSC Napoli": 113,
            "Udinese Calcio": 115,
            "Hellas Verona FC": 450,
            "US Cremonese": 457,
            "US Sassuolo Calcio": 471,
            "AC Pisa 1909": 487,
            "Torino FC": 586,
            "US Lecce": 5890,
            "Como 1907": 7397
        },
        "API-Sports": {
            "Lazio": 487,
            "Sassuolo": 488,
            "AC Milan": 489,
            "Cagliari": 490,
            "Napoli": 492,
            "Udinese": 494,
            "Genoa": 495,
            "Juventus": 496,
            "AS Roma": 497,
            "Atalanta": 499,
            "Bologna": 500,
            "Fiorentina": 502,
            "Torino": 503,
            "Hellas Verona": 504,
            "Inter": 505,
            "Empoli": 511,
            "Frosinone": 512,
            "Salernitana": 514,
            "Lecce": 867,
            "Monza": 1579
        }
    },
    "Bundesliga (Germany)": {
        "Football-Data": {
            "1. FC Köln": 1,
            "TSG 1899 Hoffenheim": 2,
            "Bayer 04 Leverkusen": 3,
            "Borussia Dortmund": 4,
            "FC Bayern München": 5,
            "Hamburger SV": 7,
            "VfB Stuttgart": 10,
            "VfL Wolfsburg": 11,
            "SV Werder Bremen": 12,
            "1. FSV Mainz 05": 15,
            "FC Augsburg": 16,
            "SC Freiburg": 17,
            "Borussia Mönchengladbach": 18,
            "Eintracht Frankfurt": 19,
            "FC St. Pauli 1910": 20,
            "1. FC Union Berlin": 28,
            "1. FC Heidenheim 1846": 44,
            "RB Leipzig": 721
        },
        "API-Sports": {
            "Bayern München": 157,
            "Fortuna Düsseldorf": 158,
            "SC Freiburg": 160,
            "VfL Wolfsburg": 161,
            "Werder Bremen": 162,
            "Borussia Mönchengladbach": 163,
            "FSV Mainz 05": 164,
            "Borussia Dortmund": 165,
            "1899 Hoffenheim": 167,
            "Bayer Leverkusen": 168,
            "Eintracht Frankfurt": 169,
            "FC Augsburg": 170,
            "VfB Stuttgart": 172,
            "RB Leipzig": 173,
            "VfL Bochum": 176,
            "1. FC Heidenheim": 180,
            "SV Darmstadt 98": 181,
            "Union Berlin": 182,
            "1. FC Köln": 192
        }
    },
    "Ligue 1 (France)": {
        "Football-Data": {
            "Toulouse FC": 511,
            "Stade Brestois 29": 512,
            "Olympique de Marseille": 516,
            "AJ Auxerre": 519,
            "Lille OSC": 521,
            "OGC Nice": 522,
            "Olympique Lyonnais": 523,
            "Paris Saint-Germain FC": 524,
            "FC Lorient": 525,
            "Stade Rennais FC 1901": 529,
            "Angers SCO": 532,
            "Le Havre AC": 533,
            "FC Nantes": 543,
            "FC Metz": 545,
            "Racing Club de Lens": 546,
            "AS Monaco FC": 548,
            "RC Strasbourg Alsace": 576,
            "Paris FC": 1045
        },
        "API-Sports": {
            "Lille": 79,
            "Lyon": 80,
            "Marseille": 81,
            "Montpellier": 82,
            "Nantes": 83,
            "Nice": 84,
            "Paris Saint Germain": 85,
            "Monaco": 91,
            "Reims": 93,
            "Rennes": 94,
            "Strasbourg": 95,
            "Toulouse": 96,
            "Lorient": 97,
            "Clermont Foot": 99,
            "Stade Brestois 29": 106,
            "Le Havre": 111,
            "Metz": 112,
            "Lens": 116,
            "Saint Etienne": 1063
        }
    }
}

def get_team_id(league_full_name, team_name, api_source):
    """
    Retrieves the team ID for a given team name and API source, with safeguarded partial matching.
    """
    if league_full_name in TEAM_ID_MAP and api_source in TEAM_ID_MAP[league_full_name]:
        source_map = TEAM_ID_MAP[league_full_name][api_source]

        # Exact match
        if team_name in source_map:
            return source_map[team_name]

        # Safeguarded partial match (case-insensitive and checks for common abbreviations/variations)
        lower_team_name = team_name.lower()
        for mapped_name, team_id in source_map.items():
            if len(lower_team_name) > 4: # Added safeguard: only partial match if team name is longer than 4 characters
                if lower_team_name in mapped_name.lower() or mapped_name.lower() in lower_team_name:
                    # Add more sophisticated checks here if needed to prevent false positives
                    # For example, check for word boundaries or minimum length of match
                    return team_id
    return None
