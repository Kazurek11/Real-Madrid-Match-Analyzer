"""
Moduł przechowujący stałe używane w różnych częściach systemu.

Ten plik zawiera zdefiniowane stałe używane w wielu modułach, co pozwala
na centralne zarządzanie wartościami i uniknięcie duplikacji kodu.
"""

from typing import Dict, List, Tuple, Union
from datetime import date

# -------------------------------------------------------------------------
# Stałe dotyczące drużyn - używane w data_processor.py
# -------------------------------------------------------------------------
TEAM_NAMES_MAPPING: Dict[str, List[str]] = {
    'Real Madrid CF': ['Real Madrid', 'Real Madryt', 'Real Madrid CF', 'Madrid'],
    'FC Barcelona': ['Barcelona', 'FC Barcelona', 'Barca', 'Barça'],
    'Atletico Madrid': ["Atlético Madryt",'Atletico Madrid', 'Atlético Madrid', 'Atletico', 'Atlético','Atl. Madrid'],
    'Athletic Club': ['Athletic Bilbao', 'Athletic Club', 'Athletic','Ath Bilbao'],
    'Sevilla FC': ['Sevilla', 'Sevilla FC'],
    'Valencia CF': ['Valencia', 'Valencia CF'],
    'Villarreal CF': ['Villarreal', 'Villarreal CF'],
    'Real Sociedad': ['Real Sociedad', 'RSSS'],
    'Real Betis': ['Real Betis', 'Betis'],
    'RC Celta': ['Celta Vigo', 'RC Celta', 'Celta'],
    'CA Osasuna': ['Osasuna', 'CA Osasuna'],
    'RCD Mallorca': ['Mallorca', 'RCD Mallorca'],
    'RCD Espanyol': ['Espanyol', 'RCD Espanyol'],
    'Getafe CF': ['Getafe', 'Getafe CF'],
    'Elche CF': ['Elche', 'Elche CF'],
    'Granada CF': ['Granada', 'Granada CF'],
    'Rayo Vallecano': ['Rayo Vallecano', 'Rayo'],
    'Cádiz CF': ['Cadiz CF', 'Cádiz CF', 'Cadiz', 'Cádiz'],
    'Deportivo Alaves': ['Alaves', 'Deportivo Alavés', 'Alavés'],
    'Levante UD': ['Levante', 'Levante UD'],
    'UD Las Palmas': ['Las Palmas', 'UD Las Palmas'],
    'CD Leganes': ['Leganes', 'CD Leganes','Leganés','CD Leganés'],
    'SD Huesca': ['Huesca'],
    'SD Eibar':['Eibar'],
    'Girona FC':['Girona',"Girona FC","Girona CF"],
    'Real Valladolid': ['Valladolid', 'Real Valladolid'],
    'UD Almeria': ['UD Almería', 'Almeria','UD Almería']
}

# -------------------------------------------------------------------------
# Stałe dotyczące kolumn danych - używane w merge_all_season_data.py
# -------------------------------------------------------------------------
COLUMN_MATCHES: List[str] = [
    'round', 'match_date', 'home_team_id', 'away_team_id', 'home_team', 'away_team',
    'score', 'result', 'home_goals', 'away_goals', 'home_odds', 'draw_odds',
    'away_odds', 'home_odds_fair', 'draw_odds_fair', 'away_odds_fair', 'PPM_H', 'PPM_A'
]

# -------------------------------------------------------------------------
# Stałe dotyczące sezonów - używane w table_actuall_PPM.py i table_league.py
# -------------------------------------------------------------------------
SEASON_FILES: List[str] = [
    "mecze_rywala_19_20.csv",
    "mecze_rywala_20_21.csv",
    "mecze_rywala_21_22.csv",
    "mecze_rywala_22_23.csv",
    "mecze_rywala_23_24.csv",
    "mecze_rywala_24_25.csv"
]

# Lista dat początku i końca sezonów (format: ["YYYY-MM-DD", "YYYY-MM-DD"])
SEASON_DATES: List[List[str]] = [
    ["2019-08-16", "2020-07-19"],
    ["2020-09-12", "2021-05-23"],
    ["2021-08-13", "2022-05-22"],
    ["2022-08-12", "2023-06-04"],
    ["2023-08-11", "2024-05-26"],
    ["2024-08-16", "2025-03-16"]
]

# Identyfikatory lat sezonowych (format: "19_20" oznacza sezon 2019/2020)
SEASON_YEARS: List[str] = ["19_20", "20_21", "21_22", "22_23", "23_24", "24_25"]

# -------------------------------------------------------------------------
# Mapowanie między identyfikatorami sezonów a ich pełnymi nazwami
# -------------------------------------------------------------------------
SEASON_ID_TO_NAME: Dict[str, str] = {
    "19_20": "Sezon 2019/2020",
    "20_21": "Sezon 2020/2021",
    "21_22": "Sezon 2021/2022",
    "22_23": "Sezon 2022/2023",
    "23_24": "Sezon 2023/2024",
    "24_25": "Sezon 2024/2025"
}