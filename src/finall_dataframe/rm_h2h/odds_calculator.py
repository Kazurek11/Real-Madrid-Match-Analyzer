import pandas as pd
from helpers.logger import error
from .config import REAL_MADRID_ID
from .validators import validate_odds_dataframe

def get_rm_odds(df, match_id, opp_id, match_date):
    """
    Pobiera odmarżowiony kurs na zwycięstwo Real Madryt z konkretnego meczu H2H.
    
    Args:
        df (pd.DataFrame): DataFrame z danymi meczów i kursami zawierający kolumny:
            - match_id: Unikalny identyfikator meczu
            - match_date: Data meczu
            - home_team_id: ID drużyny gospodarzy
            - away_team_id: ID drużyny gości
            - home_odds_fair: Odmarżowiony kurs na wygraną gospodarzy
            - away_odds_fair: Odmarżowiony kurs na wygraną gości
        match_id (int): ID konkretnego meczu do analizy
        opp_id (int): ID drużyny przeciwnika w meczu H2H
        match_date (str/datetime): Data meczu dla weryfikacji
        
    Returns:
        float or None: Odmarżowiony kurs na zwycięstwo Real Madryt w tym meczu.
                      Zwraca None jeśli brak danych lub błąd walidacji.
        
    Process:
        1. Waliduje format DataFrame pod kątem wymaganych kolumn z kursami
        2. Znajduje konkretny mecz po match_id, dacie i uczestnikach
        3. Identyfikuje czy Real Madryt grał u siebie czy na wyjeździe
        4. Zwraca odpowiedni odmarżowiony kurs (home_odds_fair lub away_odds_fair)
        
    Fair Odds (Kursy Odmarżowione):
        - Kursy oczyszczone z marży bukmachera dla dokładniejszej analizy
        - Lepiej odzwierciedlają rzeczywiste prawdopodobieństwo wygranej
        - Eliminują wpływ różnic w marżach między bukmacherami
        - Kluczowe dla obiektywnej analizy siły zespołów
        
    Notes:
        - Real Madryt może być gospodarzem (home_odds_fair) lub gościem (away_odds_fair)
        - Używa REAL_MADRID_ID z konfiguracji (standardowo ID=1)
        - Loguje błąd jeśli nie znajdzie meczu o podanych parametrach
        - Waliduje completeness danych przed przetwarzaniem
        
    Example:
        >>> df = load_match_data_with_odds()
        >>> odds = get_rm_odds(df, match_id=12345, opp_id=3, match_date='2023-10-15')
        >>> if odds:
        >>>     probability = 1 / odds
        >>>     print(f"Odmarżowiony kurs RM: {odds:.2f} (prawdopodobieństwo: {probability:.1%})")
    """
    if not validate_odds_dataframe(df):
        return None
    
    match_data = df[
        (df['match_id'] == match_id) & 
        (df['match_date'] == pd.to_datetime(match_date)) & 
        (((df['home_team_id'] == REAL_MADRID_ID) & (df['away_team_id'] == opp_id)) |
         ((df['home_team_id'] == opp_id) & (df['away_team_id'] == REAL_MADRID_ID)))
    ]
    
    if match_data.empty:
        error(f"Brak danych dla meczu ID {match_id} między RM a drużyną {opp_id} w dniu {match_date}")
        return None
    
    if match_data['home_team_id'].iloc[0] == REAL_MADRID_ID:
        return match_data['home_odds'].iloc[0]
    else:
        return match_data['away_odds'].iloc[0]