import numpy as np
import pandas as pd
from finall_dataframe.rm_team.season_calculator import get_all_opp_matches
from helpers.logger import error

def calculate_OP_G_SCO_ALL(opponent_id, match_date, season_manager):
    """
    Oblicza łączne gole strzelone przez przeciwnika w sezonie.
    
    Funkcja analizuje wszystkie mecze przeciwnika od początku poprzedniego sezonu
    do daty konkretnego meczu i sumuje wszystkie gole strzelone przez tę drużynę.
    Uwzględnia mecze domowe i wyjazdowe przeciwnika.
    
    Args:
        opponent_id (int): ID drużyny przeciwnika w bazie danych
        match_date (str/datetime): Data meczu, do której obliczamy statystyki
        season_manager (SeasonManager): Obiekt zarządzający sezonami i datami
        
    Returns:
        int/float: Łączna liczba goli strzelonych przez przeciwnika w sezonie.
                  Zwraca 0 dla pierwszego sezonu lub braku meczów,
                  np.nan w przypadku błędu lub braku danych
    
    Notes:
        - Uwzględnia tylko mecze od początku poprzedniego sezonu do daty meczu
        - Dla pierwszego sezonu (brak poprzedniego) zwraca 0
        - Automatycznie konwertuje daty na format datetime64[ns]
        - Sumuje gole z meczów domowych (home_goals) i wyjazdowych (away_goals)
        - Używa logowania błędów przez moduł helpers.logger
        
    Examples:
        >>> goals = calculate_OP_G_SCO_ALL(15, "2023-03-15", season_manager)
        >>> print(f"Gole strzelone: {goals}")
        45
    """
    try:
        current_season = season_manager.get_season(match_date)
        previous_season = season_manager.get_previous_season(current_season)
        
        if previous_season is True:
            return 0
            
        opp_matches = get_all_opp_matches(opponent_id)
        if opp_matches is None:
            return np.nan
            
        if opp_matches['match_date'].dtype != 'datetime64[ns]':
            opp_matches['match_date'] = pd.to_datetime(opp_matches['match_date'], errors='coerce')
        
        filtered_matches = opp_matches[
            (opp_matches['match_date'] >= previous_season["start_date"]) & 
            (opp_matches['match_date'] < match_date)
        ]
        
        if len(filtered_matches) == 0:
            return 0
        
        home_games = filtered_matches[filtered_matches['home_team_id'] == opponent_id]
        away_games = filtered_matches[filtered_matches['away_team_id'] == opponent_id]
        
        goals_scored = home_games['home_goals'].sum() + away_games['away_goals'].sum()
        return goals_scored
        
    except Exception as e:
        error(f"Błąd przy obliczaniu goli strzelonych dla przeciwnika {opponent_id}: {str(e)}")
        return np.nan

def calculate_OP_G_CON_ALL(opponent_id, match_date, season_manager):
    """
    Oblicza łączne gole stracone przez przeciwnika w sezonie.
    
    Funkcja analizuje wszystkie mecze przeciwnika od początku poprzedniego sezonu
    do daty konkretnego meczu i sumuje wszystkie gole stracone przez tę drużynę.
    Uwzględnia mecze domowe i wyjazdowe przeciwnika.
    
    Args:
        opponent_id (int): ID drużyny przeciwnika w bazie danych
        match_date (str/datetime): Data meczu, do której obliczamy statystyki
        season_manager (SeasonManager): Obiekt zarządzający sezonami i datami
        
    Returns:
        int/float: Łączna liczba goli straconych przez przeciwnika w sezonie.
                  Zwraca 0 dla pierwszego sezonu lub braku meczów,
                  np.nan w przypadku błędu lub braku danych
    
    Notes:
        - Uwzględnia tylko mecze od początku poprzedniego sezonu do daty meczu
        - Dla pierwszego sezonu (brak poprzedniego) zwraca 0
        - Automatycznie konwertuje daty na format datetime64[ns]
        - Sumuje gole stracone w meczach domowych (away_goals) i wyjazdowych (home_goals)
        - Logika: w meczu domowym przeciwnik traci away_goals, w wyjazdowym home_goals
        
    Examples:
        >>> goals_conceded = calculate_OP_G_CON_ALL(15, "2023-03-15", season_manager)
        >>> print(f"Gole stracone: {goals_conceded}")
        32
    """
    try:
        current_season = season_manager.get_season(match_date)
        previous_season = season_manager.get_previous_season(current_season)
        
        if previous_season is True:
            return 0
            
        opp_matches = get_all_opp_matches(opponent_id)
        if opp_matches is None:
            return np.nan
            
        if opp_matches['match_date'].dtype != 'datetime64[ns]':
            opp_matches['match_date'] = pd.to_datetime(opp_matches['match_date'], errors='coerce')
        
        filtered_matches = opp_matches[
            (opp_matches['match_date'] >= previous_season["start_date"]) & 
            (opp_matches['match_date'] < match_date)
        ]
        
        if len(filtered_matches) == 0:
            return 0
        
        home_games = filtered_matches[filtered_matches['home_team_id'] == opponent_id]
        away_games = filtered_matches[filtered_matches['away_team_id'] == opponent_id]
        
        goals_conceded = home_games['away_goals'].sum() + away_games['home_goals'].sum()
        return goals_conceded
        
    except Exception as e:
        error(f"Błąd przy obliczaniu goli straconych dla przeciwnika {opponent_id}: {str(e)}")
        return np.nan

def calculate_OP_G_SCO_G_CON_RAT(opponent_id, match_date, season_manager):
    """
    Oblicza stosunek goli strzelonych do straconych przez przeciwnika w sezonie.
    
    Funkcja wykorzystuje wcześniej obliczone gole strzelone i stracone przez przeciwnika
    do wyliczenia wskaźnika skuteczności ofensywnej względem defensywnej.
    Wyższy wskaźnik oznacza lepszą skuteczność ofensywną względem defensywy.
    
    Args:
        opponent_id (int): ID drużyny przeciwnika w bazie danych
        match_date (str/datetime): Data meczu, do której obliczamy statystyki
        season_manager (SeasonManager): Obiekt zarządzający sezonami i datami
        
    Returns:
        float: Stosunek goli strzelonych do straconych.
              Zwraca liczbę goli strzelonych jeśli nie stracono żadnego gola,
              0 jeśli nie strzelono ani nie stracono goli,
              np.nan w przypadku błędu
    
    Notes:
        - Wykorzystuje funkcje calculate_OP_G_SCO_ALL i calculate_OP_G_CON_ALL
        - W przypadku 0 straconych goli zwraca liczbę strzelonych (unika dzielenia przez 0)
        - Wskaźnik > 1.0 oznacza więcej goli strzelonych niż straconych
        - Wskaźnik < 1.0 oznacza więcej goli straconych niż strzelonych
        
    Examples:
        >>> ratio = calculate_OP_G_SCO_G_CON_RAT(15, "2023-03-15", season_manager)
        >>> print(f"Stosunek goli: {ratio:.2f}")
        1.41
    """
    try:
        goals_scored = calculate_OP_G_SCO_ALL(opponent_id, match_date, season_manager)
        goals_conceded = calculate_OP_G_CON_ALL(opponent_id, match_date, season_manager)
        
        if goals_conceded == 0:
            return goals_scored if goals_scored > 0 else 0
        
        return goals_scored / goals_conceded
        
    except Exception as e:
        error(f"Błąd przy obliczaniu stosunku goli dla przeciwnika {opponent_id}: {str(e)}")
        return np.nan

def calculate_OP_ODD_W_L5(opponent_id, match_date):
    """
    Oblicza średni kurs na wygraną przeciwnika z ostatnich 5 meczów.
    
    Funkcja analizuje ostatnie 5 meczów przeciwnika przed daną datą i oblicza
    średni kurs bukmacherski na wygraną tej drużyny. Uwzględnia kursy z meczów
    domowych i wyjazdowych.
    
    Args:
        opponent_id (int): ID drużyny przeciwnika w bazie danych
        match_date (str/datetime): Data meczu, przed którą szukamy ostatnich 5 meczów
        
    Returns:
        float: Średni kurs na wygraną przeciwnika z ostatnich 5 meczów.
              Zwraca np.nan jeśli brak danych, meczów lub kursów
    
    Notes:
        - Wymaga kolumn 'home_odds' i 'away_odds' w danych meczowych
        - Uwzględnia tylko mecze przed podaną datą
        - Sortuje mecze chronologicznie i bierze ostatnie 5
        - Dla meczów domowych używa 'home_odds', dla wyjazdowych 'away_odds'
        - Automatycznie pomija wartości NaN przy obliczaniu średniej
        
    Examples:
        >>> odds = calculate_OP_ODD_W_L5(15, "2023-03-15")
        >>> print(f"Średni kurs na wygraną: {odds:.2f}")
        2.15
    """
    try:
        opp_matches = get_all_opp_matches(opponent_id)
        if opp_matches is None:
            return np.nan
            
        # Sprawdź czy kolumny z kursami istnieją
        if 'home_odds' not in opp_matches.columns or 'away_odds' not in opp_matches.columns:
            return np.nan
        
        filtered_matches = opp_matches[opp_matches['match_date'] < match_date].sort_values('match_date').tail(5)
        
        if len(filtered_matches) == 0:
            return np.nan
        
        home_games = filtered_matches[filtered_matches['home_team_id'] == opponent_id]
        away_games = filtered_matches[filtered_matches['away_team_id'] == opponent_id]
        
        win_odds = []
        if not home_games.empty:
            win_odds.extend(home_games['home_odds'].dropna().tolist())
        if not away_games.empty:
            win_odds.extend(away_games['away_odds'].dropna().tolist())
        
        return np.mean(win_odds) if win_odds else np.nan
        
    except Exception as e:
        error(f"Błąd przy obliczaniu kursów na wygraną dla przeciwnika {opponent_id}: {str(e)}")
        return np.nan

def calculate_OP_ODD_L_L5(opponent_id, match_date):
    """
    Oblicza średni kurs na porażkę przeciwnika z ostatnich 5 meczów.
    
    Funkcja analizuje ostatnie 5 meczów przeciwnika przed daną datą i oblicza
    średni kurs bukmacherski na porażkę tej drużyny. Uwzględnia kursy z meczów
    domowych i wyjazdowych, gdzie porażka oznacza wygraną przeciwnej drużyny.
    
    Args:
        opponent_id (int): ID drużyny przeciwnika w bazie danych
        match_date (str/datetime): Data meczu, przed którą szukamy ostatnich 5 meczów
        
    Returns:
        float: Średni kurs na porażkę przeciwnika z ostatnich 5 meczów.
              Zwraca np.nan jeśli brak danych, meczów lub kursów
    
    Notes:
        - Wymaga kolumn 'home_odds' i 'away_odds' w danych meczowych
        - Uwzględnia tylko mecze przed podaną datą
        - Sortuje mecze chronologicznie i bierze ostatnie 5
        - Dla meczów domowych przeciwnika używa 'away_odds' (porażka = wygrana gościa)
        - Dla meczów wyjazdowych przeciwnika używa 'home_odds' (porażka = wygrana gospodarza)
        - Automatycznie pomija wartości NaN przy obliczaniu średniej
        
    Examples:
        >>> loss_odds = calculate_OP_ODD_L_L5(15, "2023-03-15")
        >>> print(f"Średni kurs na porażkę: {loss_odds:.2f}")
        1.85
    """
    try:
        opp_matches = get_all_opp_matches(opponent_id)
        if opp_matches is None:
            return np.nan
            
        # Sprawdź czy kolumny z kursami istnieją
        if 'home_odds' not in opp_matches.columns or 'away_odds' not in opp_matches.columns:
            return np.nan
        
        filtered_matches = opp_matches[opp_matches['match_date'] < match_date].sort_values('match_date').tail(5)
        
        if len(filtered_matches) == 0:
            return np.nan
        
        home_games = filtered_matches[filtered_matches['home_team_id'] == opponent_id]
        away_games = filtered_matches[filtered_matches['away_team_id'] == opponent_id]
        
        loss_odds = []
        if not home_games.empty:
            loss_odds.extend(home_games['away_odds'].dropna().tolist())
        if not away_games.empty:
            loss_odds.extend(away_games['home_odds'].dropna().tolist())
        
        return np.mean(loss_odds) if loss_odds else np.nan
        
    except Exception as e:
        error(f"Błąd przy obliczaniu kursów na porażkę dla przeciwnika {opponent_id}: {str(e)}")
        return np.nan
    
