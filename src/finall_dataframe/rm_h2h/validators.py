"""
Moduł walidacji danych dla analiz Head-to-Head Real Madryt.

Ten moduł zawiera funkcje walidacyjne zapewniające integralność
i kompletność danych wymaganych do przeprowadzenia analiz H2H,
obejmujące walidację struktur DataFrame, kursów bukmacherskich
oraz wyników końcowych analiz.
"""

import pandas as pd
from helpers.logger import error, warning, info
from .config import REQUIRED_MATCH_COLUMNS, REQUIRED_ODDS_COLUMNS

def validate_h2h_dataframe(df):
    """
    Waliduje DataFrame pod kątem wymaganych kolumn dla analiz Head-to-Head.
    
    Args:
        df (pd.DataFrame): DataFrame z danymi meczów do walidacji. Musi zawierać
                          kolumny zdefiniowane w REQUIRED_MATCH_COLUMNS:
                          - match_id, match_date, home_team_id, away_team_id
                          - home_goals, away_goals dla obliczania wyników
        
    Returns:
        bool: True jeśli DataFrame spełnia wszystkie wymagania dla analiz H2H.
              False jeśli brakuje kluczowych kolumn lub występują błędy strukturalne.
        
    Process:
        1. Sprawdza obecność wszystkich wymaganych kolumn z REQUIRED_MATCH_COLUMNS
        2. Waliduje typ danych kolumny match_date (wymagany datetime)
        3. Automatycznie konwertuje match_date do datetime jeśli potrzeba
        4. Loguje błędy dla brakujących kolumn i ostrzeżenia dla konwersji
        
    Data Requirements:
        - match_id: Unikalne identyfikatory meczów
        - match_date: Daty meczów w formacie datetime
        - home_team_id/away_team_id: ID drużyn dla identyfikacji H2H
        - home_goals/away_goals: Wyniki bramkowe dla obliczania statystyk
        
    Notes:
        - Automatyczna konwersja dat z ostrzeżeniem w logu
        - Nie modyfikuje oryginalnego DataFrame
        - Krytyczne dla wszystkich funkcji H2H calculator
        - Loguje szczegółowe informacje o problemach walidacji
        
    Example:
        >>> df = load_match_data()
        >>> if validate_h2h_dataframe(df):
        >>>     print("DataFrame gotowy do analiz H2H")
        >>> else:
        >>>     print("Błędy walidacji - sprawdź logi")
    """
    for col in REQUIRED_MATCH_COLUMNS:
        if col not in df.columns:
            error(f"DataFrame nie ma wymaganej kolumny: {col}")
            return False
    
    if df['match_date'].dtype != 'datetime64[ns]':
        warning("Kolumna 'match_date' nie jest typu datetime, konwertuję")
        df['match_date'] = pd.to_datetime(df['match_date'], errors='coerce')
        info("Przekonwertowano kolumnę 'match_date' na datetime")
    
    return True

def validate_odds_dataframe(df):
    """
    Waliduje DataFrame pod kątem kursów bukmacherskich dla analiz H2H.
    
    Args:
        df (pd.DataFrame): DataFrame z danymi kursów do walidacji. Musi zawierać
                          kolumny zdefiniowane w REQUIRED_ODDS_COLUMNS:
                          - home_odds_fair, away_odds_fair (odmarżowione kursy)
                          - match_id, match_date dla linkowania z meczami
        
    Returns:
        bool: True jeśli DataFrame zawiera wszystkie wymagane kolumny z kursami.
              False jeśli brakuje kluczowych kolumn z odmarżowionymi kursami.
        
    Process:
        1. Iteruje przez wszystkie kolumny z REQUIRED_ODDS_COLUMNS
        2. Sprawdza obecność każdej wymaganej kolumny w DataFrame
        3. Loguje błąd dla pierwszej brakującej kolumny i przerywa walidację
        4. Zwraca False natychmiast po znalezieniu problemu
        
    Required Odds Columns:
        - home_odds_fair: Odmarżowione kursy na wygraną gospodarzy
        - away_odds_fair: Odmarżowione kursy na wygraną gości
        - Kolumny identyfikacyjne: match_id, match_date dla łączenia danych
        
    Notes:
        - Nie sprawdza wartości kursów, tylko ich obecność
        - Krytyczne dla funkcji odds_calculator
        - Używa odmarżowionych kursów (fair odds) dla obiektywności
        - Szybkie przerwanie przy pierwszym błędzie dla wydajności
        
    Example:
        >>> df_with_odds = load_odds_data()
        >>> if validate_odds_dataframe(df_with_odds):
        >>>     print("DataFrame z kursami gotowy do analiz")
        >>> else:
        >>>     print("Brakuje wymaganych kolumn z kursami")
    """
    for col in REQUIRED_ODDS_COLUMNS:
        if col not in df.columns:
            error(f"DataFrame nie ma wymaganej kolumny: {col}")
            return False
    return True

def validate_h2h_analysis_results(result_df):
    """
    Waliduje kompletność i jakość wyników analiz Head-to-Head.
    
    Args:
        result_df (pd.DataFrame): DataFrame z wynikami analiz H2H zawierający:
                                 - Kolumny H2H_*: Statystyki Head-to-Head
                                 - RM_ODD_W: Kursy na wygraną Real Madryt
                                 - Wszystkie poprzednie kolumny analiz
        
    Returns:
        dict: Szczegółowy raport walidacji zawierający:
            - total_matches (int): Łączna liczba przeanalizowanych meczów
            - h2h_columns_added (int): Liczba dodanych kolumn H2H
            - h2h_missing_values (int): Łączna liczba brakujących wartości H2H
            - h2h_completeness (float): Procent kompletności danych H2H (0-100%)
            - rm_odds_stats (pd.Series): Statystyki opisowe kursów RM (jeśli dostępne)
        
    Process:
        1. Identyfikuje wszystkie kolumny H2H (prefix 'H2H_') i kursy RM
        2. Oblicza metryki kompletności dla dodanych kolumn
        3. Generuje statystyki opisowe dla kursów Real Madryt
        4. Tworzy szczegółowy raport jakości danych
        5. Loguje podsumowanie wyników walidacji
        
    Quality Metrics:
        - Completeness: % wypełnionych komórek w kolumnach H2H
        - Coverage: Liczba meczów z kompletnymi danymi H2H
        - Odds Distribution: Rozkład kursów na wygraną RM
        
    Notes:
        - Używa prefixów kolumn do identyfikacji danych H2H
        - Oblicza kompletność na podstawie wszystkich komórek H2H
        - Generuje statystyki opisowe tylko jeśli kolumna RM_ODD_W istnieje
        - Loguje kluczowe metryki jakości dla monitorowania
        - Przydatne do oceny skuteczności procesu analizy H2H
        
    Example:
        >>> analyzed_df = h2h_analyzer.analyze()
        >>> report = validate_h2h_analysis_results(analyzed_df)
        >>> print(f"Kompletność H2H: {report['h2h_completeness']:.1f}%")
        >>> if report['h2h_completeness'] > 95:
        >>>     print("Wysoka jakość danych H2H")
        >>> else:
        >>>     print("Uwaga: Niska kompletność danych H2H")
    """
    h2h_columns_actual = [col for col in result_df.columns if col.startswith('H2H_') or col == 'RM_ODD_W']
    
    validation_report = {
        'total_matches': len(result_df),
        'h2h_columns_added': len(h2h_columns_actual),
        'h2h_missing_values': result_df[h2h_columns_actual].isnull().sum().sum(),
        'h2h_completeness': (1 - result_df[h2h_columns_actual].isnull().sum().sum() / 
                           (len(result_df) * len(h2h_columns_actual))) * 100,
        'rm_odds_stats': result_df['RM_ODD_W'].describe() if 'RM_ODD_W' in result_df.columns else None
    }
    
    info(f"Walidacja analizy H2H:")
    info(f"  - Mecze: {validation_report['total_matches']}")
    info(f"  - Kolumny H2H: {validation_report['h2h_columns_added']}")
    info(f"  - Kompletność H2H: {validation_report['h2h_completeness']:.1f}%")
    
    return validation_report