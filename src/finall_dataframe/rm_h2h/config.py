"""
Konfiguracja modułu Head-to-Head.
"""

# Kolumny Head-to-Head do dodania w analizie
H2H_COLUMNS = [
    'H2H_RM_W_L5',      # Procent wygranych Real Madryt w ostatnich 5 meczach H2H
    'H2H_RM_GDIF_L5',   # Różnica bramkowa Real Madryt w ostatnich 5 meczach H2H  
    'H2H_PPM_L5',       # Średnie punkty na mecz Real w ostatnich 5 meczach H2H
    'H2H_PPM',          # Średnie punkty na mecz Real we wszystkich meczach H2H
    'H2H_EXISTS',       # Czy istnieją wcześniejsze mecze H2H (0=nie, 1=tak)
    'RM_ODD_W'          # Odmarżowiony kurs na zwycięstwo Real Madryt
]

# Kolumny wymagane w danych meczowych
REQUIRED_MATCH_COLUMNS = ['match_date', 'home_team_id', 'away_team_id', 'home_goals', 'away_goals']

# Kolumny wymagane dla kursów
REQUIRED_ODDS_COLUMNS = ['match_id', 'home_team_id', 'away_team_id', 'home_odds_fair', 'away_odds_fair']

# ID Real Madryt
REAL_MADRID_ID = 1