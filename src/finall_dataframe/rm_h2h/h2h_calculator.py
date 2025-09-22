"""
Kalkulatory statystyk Head-to-Head między Real Madryt a przeciwnikami.

Ten moduł zawiera funkcje do obliczania statystyk bezpośrednich starć
między Real Madryt a przeciwnikami, obejmujące wyniki, bilans bramkowy
oraz średnie punkty na mecz z różnych okresów czasowych.
"""

import pandas as pd
import numpy as np
from helpers.logger import warning
from finall_dataframe.rm_team.config import WIN_POINTS, DRAW_POINTS
from .config import REAL_MADRID_ID
from .validators import validate_h2h_dataframe

def get_h2h_matches(df, opp_id, match_date, last_n=None):
    """
    Pobiera mecze bezpośrednie między Real Madryt a przeciwnikiem przed określoną datą.
    
    Args:
        df (pd.DataFrame): DataFrame z danymi meczów zawierający kolumny:
            - match_date: Data meczu
            - home_team_id: ID drużyny gospodarzy
            - away_team_id: ID drużyny gości
            - home_goals: Bramki gospodarzy
            - away_goals: Bramki gości
        opp_id (int): ID drużyny przeciwnika do analizy H2H
        match_date (str/datetime): Data graniczna - pobiera mecze sprzed tej daty
        last_n (int, optional): Liczba ostatnich meczów do pobrania.
                               Jeśli None, pobiera wszystkie mecze H2H
        
    Returns:
        pd.DataFrame or None: DataFrame z meczami H2H posortowanymi od najnowszych.
                             Zwraca None jeśli brak meczów lub błąd walidacji.
        
    Process:
        1. Waliduje format DataFrame pod kątem wymaganych kolumn
        2. Filtruje mecze gdzie Real Madryt grał przeciwko opp_id przed match_date
        3. Sortuje mecze od najnowszych do najstarszych
        4. Ogranicza do last_n meczów jeśli parametr podany
        
    Notes:
        - Real Madryt może być gospodarzem lub gościem
        - Uwzględnia tylko mecze przed podaną datą (wykluczając aktualny mecz)
        - Loguje ostrzeżenie jeśli brak meczów H2H
        - Używa REAL_MADRID_ID z konfiguracji (standardowo ID=1)
        
    Example:
        >>> df = load_match_data()
        >>> h2h = get_h2h_matches(df, opp_id=3, match_date='2023-10-15', last_n=5)
        >>> print(f"Znaleziono {len(h2h)} meczów H2H")
    """
    if not validate_h2h_dataframe(df):
        return None
    
    h2h_matches = df[
        (df['match_date'] < pd.to_datetime(match_date)) & 
        (((df['home_team_id'] == REAL_MADRID_ID) & (df['away_team_id'] == opp_id)) |
         ((df['home_team_id'] == opp_id) & (df['away_team_id'] == REAL_MADRID_ID)))
    ]
    
    if h2h_matches.empty:
        warning(f"Brak meczów H2H między RM a drużyną {opp_id} przed {match_date}")
        return None
    
    h2h_matches = h2h_matches.sort_values('match_date', ascending=False)
    
    if last_n:
        h2h_matches = h2h_matches.head(last_n)
    
    return h2h_matches

def calculate_h2h_stats(df, opp_id, match_date, last_n=5):
    """
    Oblicza kompleksowe statystyki Head-to-Head z ostatnich meczów między RM a przeciwnikiem.
    
    Args:
        df (pd.DataFrame): DataFrame z danymi meczów z wymaganymi kolumnami
        opp_id (int): ID drużyny przeciwnika
        match_date (str/datetime): Data graniczna meczu
        last_n (int): Liczba ostatnich meczów H2H do analizy (domyślnie 5)
        
    Returns:
        dict or None: Słownik ze statystykami H2H zawierający:
            - win_ratio (float): Procent wygranych Real Madryt (0.0-1.0)
            - points_per_match (float): Średnie punkty RM na mecz (0-3 punkty)
            - goals_balance (int): Różnica bramkowa RM vs przeciwnik
            
        Zwraca None jeśli brak meczów H2H do analizy.
        
    Process:
        1. Pobiera ostatnie mecze H2H używając get_h2h_matches()
        2. Zlicza wygrane Real Madryt u siebie i na wyjeździe
        3. Zlicza remisy między drużynami
        4. Oblicza procent wygranych i średnie punkty na mecz
        5. Kalkuluje bilans bramkowy (bramki RM - bramki przeciwnika)
        
    Calculation Details:
        - Win Ratio: (wygrane_u_siebie + wygrane_na_wyjeździe) / total_mecze
        - Points Per Match: (wygrane * 3 + remisy * 1) / total_mecze
        - Goals Balance: suma_bramek_RM - suma_bramek_przeciwnika
        
    Notes:
        - Używa WIN_POINTS=3 i DRAW_POINTS=1 z konfiguracji
        - Obsługuje Real Madryt jako gospodarza i gościa
        - Wszystkie wartości zwracane jako float/int dla spójności
        
    Example:
        >>> stats = calculate_h2h_stats(df, opp_id=3, match_date='2023-10-15', last_n=5)
        >>> if stats:
        >>>     print(f"RM wygrywa {stats['win_ratio']:.1%} meczów H2H")
        >>>     print(f"Średnio {stats['points_per_match']:.2f} punktów na mecz")
    """
    h2h_matches = get_h2h_matches(df, opp_id, match_date, last_n)
    
    if h2h_matches is None or h2h_matches.empty:
        return None
    
    rm_home_wins = len(h2h_matches[
        (h2h_matches['home_team_id'] == REAL_MADRID_ID) & 
        (h2h_matches['home_goals'] > h2h_matches['away_goals'])
    ])
    
    rm_away_wins = len(h2h_matches[
        (h2h_matches['away_team_id'] == REAL_MADRID_ID) & 
        (h2h_matches['away_goals'] > h2h_matches['home_goals'])
    ])
    
    draws = len(h2h_matches[
        h2h_matches['home_goals'] == h2h_matches['away_goals']
    ])
    
    total_matches = len(h2h_matches)
    total_wins = rm_home_wins + rm_away_wins
    
    win_ratio = total_wins / total_matches
    points_per_match = (total_wins * WIN_POINTS + draws * DRAW_POINTS) / total_matches
    
    rm_goals = (
        h2h_matches[h2h_matches['home_team_id'] == REAL_MADRID_ID]['home_goals'].sum() +
        h2h_matches[h2h_matches['away_team_id'] == REAL_MADRID_ID]['away_goals'].sum()
    )
    
    opp_goals = (
        h2h_matches[h2h_matches['home_team_id'] == REAL_MADRID_ID]['away_goals'].sum() +
        h2h_matches[h2h_matches['away_team_id'] == REAL_MADRID_ID]['home_goals'].sum()
    )
    
    goals_balance = rm_goals - opp_goals
    
    return {
        'win_ratio': win_ratio,
        'points_per_match': points_per_match,
        'goals_balance': goals_balance
    }

def calculate_h2h_overall_ppm(df, opp_id, match_date):
    """
    Oblicza średnie punkty Real Madryt na mecz ze wszystkich meczów H2H w historii.
    
    Args:
        df (pd.DataFrame): DataFrame z danymi meczów zawierający kompletną historię
        opp_id (int): ID drużyny przeciwnika do analizy
        match_date (str/datetime): Data graniczna - analizuje mecze sprzed tej daty
        
    Returns:
        float or None: Średnie punkty na mecz Real Madryt przeciwko temu przeciwnikowi
                      w całej dostępnej historii. Zwraca None jeśli brak meczów H2H.
        
    Process:
        1. Pobiera wszystkie mecze H2H z historii (bez ograniczenia last_n)
        2. Zlicza wszystkie wygrane Real Madryt u siebie i na wyjeździe
        3. Zlicza wszystkie remisy w historii starć
        4. Oblicza średnie punkty używając systemu punktowego La Liga
        
    Calculation:
        PPM = (total_wins * 3 + total_draws * 1) / total_matches_played
        
    Notes:
        - Różni się od calculate_h2h_stats() tym, że analizuje całą historię
        - Nie ma ograniczenia do ostatnich N meczów
        - Używa tego samego systemu punktowego co Liga (3-1-0)
        - Kluczowa metryka dla długoterminowej analizy H2H
        - Pomaga ocenić historyczną dominację nad przeciwnikiem
        
    Use Cases:
        - Porównanie z recent form (ostatnie 5 meczów)
        - Ocena długoterminowych trendów H2H
        - Analiza historycznej przewagi Real Madryt
        
    Example:
        >>> overall_ppm = calculate_h2h_overall_ppm(df, opp_id=3, match_date='2023-10-15')
        >>> if overall_ppm:
        >>>     print(f"RM średnio zdobywa {overall_ppm:.2f} punktów przeciwko tej drużynie")
        >>>     if overall_ppm > 2.0:
        >>>         print("Historyczna dominacja Real Madryt")
    """
    h2h_matches = get_h2h_matches(df, opp_id, match_date)
    
    if h2h_matches is None or h2h_matches.empty:
        return None
    
    rm_home_wins = len(h2h_matches[
        (h2h_matches['home_team_id'] == REAL_MADRID_ID) & 
        (h2h_matches['home_goals'] > h2h_matches['away_goals'])
    ])
    
    rm_away_wins = len(h2h_matches[
        (h2h_matches['away_team_id'] == REAL_MADRID_ID) & 
        (h2h_matches['away_goals'] > h2h_matches['home_goals'])
    ])
    
    draws = len(h2h_matches[
        h2h_matches['home_goals'] == h2h_matches['away_goals']
    ])
    
    total_matches = len(h2h_matches)
    total_wins = rm_home_wins + rm_away_wins
    
    return (total_wins * WIN_POINTS + draws * DRAW_POINTS) / total_matches

def is_playing_before(df, match_date, team_id):
    """
    Sprawdza, czy Real Madryt grał wcześniej z przeciwnikiem przed określoną datą.
    
    Funkcja weryfikuje czy istnieją jakiekolwiek mecze bezpośrednie między Real Madryt
    a przeciwnikiem w bazie danych przed podaną datą meczu. Jest używana do bezpiecznego
    wypełnienia wartości NaN w końcowym datasecie.
    
    Args:
        df (pd.DataFrame): DataFrame z danymi meczów zawierający kolumny:
            - match_date: Data meczu
            - home_team_id: ID drużyny gospodarzy  
            - away_team_id: ID drużyny gości
        match_date (str/datetime): Data graniczna - sprawdza mecze sprzed tej daty
        team_id (int): ID drużyny przeciwnika do sprawdzenia H2H z Real Madryt
        
    Returns:
        bool: True jeśli istnieje przynajmniej jeden mecz H2H przed podaną datą,
              False jeśli brak wcześniejszych meczów w bazie danych.
              
    Logic:
        - Wartość True (1) oznacza: istnieją mecze H2H w przeszłości w bazie
        - Wartość False (0) oznacza: brak wcześniejszych meczów H2H w bazie
        
    Usage in Dataset:
        Kolumna H2H_EXISTS w finalnym datasecie:
        - 0: Real Madryt wcześniej nie rozegrał z daną drużyną żadnego meczu
        - 1: Istnieją mecze w przeszłości w bazie danych przed określoną datą
        
    Notes:
        - Używa funkcji get_h2h_matches() do wyszukania historycznych meczów
        - Kluczowa dla bezpiecznego wypełniania NaN w statystykach H2H
        - Pozwala rozróżnić brak danych od braku historii meczów
        - Real Madryt może być gospodarzem lub gościem w sprawdzanych meczach
        
    Example:
        >>> df = load_match_data()
        >>> exists = is_playing_before(df, '2023-10-15', team_id=3)
        >>> if exists:
        >>>     print("Real Madryt ma historię meczów z tą drużyną")
        >>> else:
        >>>     print("Pierwszy mecz H2H z tą drużyną")
    """
    h2h_matches = get_h2h_matches(df, team_id, match_date)
    if h2h_matches is None or h2h_matches.empty:
        return False
    return True
        