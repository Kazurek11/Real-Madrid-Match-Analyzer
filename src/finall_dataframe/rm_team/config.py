"""
Konfiguracja modułu analizy drużyny Real Madryt.

Ten moduł zawiera wszystkie stałe używane w analizie statystyk drużynowych,
ocen trenerów i wydajności przeciwko różnym typom przeciwników.
"""

# ===== KONFIGURACJA KOLUMN OCEN =====
# Wybór między ocenami redaktorów (EDI) a użytkowników (USR)
RM_COACH_RATING = 'RM_coach_rating_EDI'  # Alternatywa: RM_coach_rating_US
RM_TEAM_RATING = 'RM_team_rating_EDI'    # Alternatywa: RM_team_rating_USR
OPP_RATING = 'rival_rating_EDI'          # Alternatywa: rival_rating_USR

# ===== DEFINICJA KOLUMN WYJŚCIOWYCH =====
# Kompletna lista kolumn dodawanych do DataFrame z analizą drużynową
COLUMNS_TO_ADD = [
    # Dane trenera
    'RM_C_ID',          # ID trenera Realu Madryt
    'RM_C_RT_PS',       # Średnia ocen trenera w poprzednim sezonie
    'RM_C_FORM5',       # Średnia ocen trenera z ostatnich 5 meczów
    
    # Statystyki ofensywne/defensywne (ostatnie 5 meczów)
    'RM_G_SCO_L5',      # Średnia goli zdobytych przez Real w ostatnich 5 meczach
    'RM_G_CON_L5',      # Średnia goli straconych przez Real w ostatnich 5 meczach
    'RM_GDIF_L5',       # Średnia różnica bramek Realu w ostatnich 5 meczach
    
    # Wydajność punktowa
    'RM_PPM_L5',        # Średnia punktów na mecz Realu z ostatnich 5 meczów
    'RM_PPM_SEA',       # Średnia punktów na mecz Realu w sezonie
    'RM_OPP_PPM_L5',    # Średnia punktów na mecz rywali Realu z ostatnich 5 meczów
    
    # Wydajność przeciwko różnym poziomom drużyn
    'RM_GPM_VS_TOP',    # Średnia goli na mecz Realu z drużynami TOP
    'RM_PPM_VS_TOP',    # Średnia punktów na mecz Realu z drużynami TOP
    'RM_GPM_VS_MID',    # Średnia goli na mecz Realu z drużynami MID
    'RM_PPM_VS_MID',    # Średnia punktów na mecz Realu z drużynami MID
    'RM_GPM_VS_LOW',    # Średnia goli na mecz Realu z drużynami LOW
    'RM_PPM_VS_LOW',    # Średnia punktów na mecz Realu z drużynami LOW
]

# ===== SYSTEM PUNKTOWY =====
# Standardowy system punktów La Liga
WIN_POINTS = 3      # Punkty za zwycięstwo
DRAW_POINTS = 1     # Punkty za remis (0 za porażkę)

# ===== KLASYFIKACJA DRUŻYN =====
# Progi punktów na mecz (PPM) do kategoryzacji przeciwników
TOP_TIER_MIN_PPM = 1.9      # Drużyny TOP: PPM >= 1.9
MID_TIER_MIN_PPM = 1.2      # Drużyny MID: 1.2 <= PPM < 1.9  
MID_TIER_MAX_PPM = 1.9      # Górna granica dla drużyn MID
LOW_TIER_MAX_PPM = 1.2      # Drużyny LOW: PPM < 1.2

# ===== DANE SPECJALNE =====
# Rezerwowane dla przyszłych rozszerzeń lub specjalnych konfiguracji
SPECIAL_DATA = ""

# ===== DOKUMENTACJA UŻYCIA =====
"""
Przykład kategoryzacji drużyn na podstawie PPM:
- TOP: Real Madrid, Barcelona, Atletico (PPM >= 1.9)
- MID: Valencia, Sevilla, Real Sociedad (1.2 <= PPM < 1.9)
- LOW: Drużyny walczące o utrzymanie (PPM < 1.2)

Kolumny są generowane dla każdego meczu Realu Madryt i zawierają:
1. Informacje o trenerze i jego formie
2. Statystyki ofensywne/defensywne z ostatnich meczów
3. Wydajność punktową w różnych kontekstach
4. Specjalistyczne metryki przeciwko różnym poziomom przeciwników
"""