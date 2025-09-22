"""
Kalkulator statystyk sezonowych dla drużyn La Liga.

Moduł oblicza średnie punktów na mecz oraz wydajność przeciwko drużynom
różnych poziomów na podstawie ich PPM (punktów na mecz).
Obsługuje zarówno Real Madryt jak i inne drużyny La Liga.
"""

import numpy as np
import pandas as pd
import os
from helpers.logger import info, error
from helpers.file_utils import FileUtils
from .config import WIN_POINTS, DRAW_POINTS, TOP_TIER_MIN_PPM, MID_TIER_MIN_PPM, MID_TIER_MAX_PPM, LOW_TIER_MAX_PPM

def get_all_opp_matches(team_id):
    """
    Pobiera wszystkie mecze określonej drużyny z bazy danych.
    
    Args:
        team_id (int): ID drużyny
        
    Returns:
        pd.DataFrame/None: DataFrame z meczami lub None jeśli brak danych
        
    Notes:
        - Zwraca mecze gdzie drużyna występuje jako gospodarz lub gość
        - Loguje błąd jeśli brak meczów dla podanego ID
        - Używa pliku all_matches.csv z połączonymi danymi sezonowymi
    """
    all_matches = FileUtils.load_csv_safe(os.path.join(FileUtils.get_project_root(),"Data","Mecze", "all_season", "merged_matches", "all_matches.csv"))
    team_matches = all_matches[
        (all_matches['home_team_id'] == team_id) | 
        (all_matches['away_team_id'] == team_id)
    ]
    if team_matches.empty:
        error(f"Brak meczów dla drużyny o ID {team_id}. Sprawdź poprawność team_id.")
        return None
    return team_matches

class SeasonCalculator:
    """
    Kalkulator statystyk sezonowych dla drużyn La Liga.
    
    Oblicza średnie punktów na mecz, goli oraz wydajność przeciwko
    drużynom różnych poziomów (TOP/MID/LOW) na podstawie ich PPM.
    Obsługuje specjalne przypadki dla Real Madryt oraz uniwersalne
    obliczenia dla pozostałych drużyn.
    """
    
    def __init__(self, rm_matches, season_manager, team_id):
        """
        Inicjalizuje kalkulator statystyk sezonowych.
        
        Args:
            rm_matches (pd.DataFrame): Dane meczów Real Madryt z kolumnami specyficznymi
            season_manager: Manager sezonów do określania dat rozpoczęcia/zakończenia
            team_id (int): ID drużyny do analizy
            
        Notes:
            - team_id=1 oznacza Real Madryt (używa rm_matches i kolumny 'real_result')
            - Inne team_id używają danych ze wszystkich meczów via get_all_opp_matches()
            - rm_matches zawiera preprocessowane dane specifyczne dla RM
        """
        self.rm_matches = rm_matches
        self.season_manager = season_manager
        self.team_id = team_id
    
    def calculate_team_points_per_match_season(self, match_date):
        """
        Oblicza średnią punktów na mecz drużyny w poprzednim sezonie.
        
        Args:
            match_date (str/datetime): Data meczu jako punkt odniesienia
            
        Returns:
            float/int: Średnia punktów na mecz lub 0 jeśli brak danych
            
        Notes:
            - Dla Real Madryt (ID=1) używa kolumny 'real_result' (1=wygrana, 0.5=remis, 0=porażka)
            - Dla innych drużyn oblicza na podstawie porównania home_goals vs away_goals
            - Zwraca 0 dla pierwszego sezonu (brak poprzedniego sezonu)
            - Filtruje mecze od początku poprzedniego sezonu do match_date (wyłącznie)
            - Uwzględnia 3 punkty za wygraną, 1 punkt za remis, 0 za porażkę
        """
        current_season = self.season_manager.get_season(match_date)
        previous_season = self.season_manager.get_previous_season(current_season)
        
        if self.team_id != 1:
            info(f"Obliczamy statystyki dla drużyny o ID {self.team_id}")
            opp_matches = get_all_opp_matches(self.team_id)
            if opp_matches is None:
                return None
            if opp_matches['match_date'].dtype != 'datetime64[ns]':
                opp_matches['match_date'] = pd.to_datetime(opp_matches['match_date'], errors='coerce')
            
            if previous_season is True:
                info(f"Brak wcześniejszego sezonu dla daty {match_date} (pierwszy sezon)")
                return 0
                
            filtered_matches = opp_matches[
                (opp_matches['match_date'] >= previous_season["start_date"]) & 
                (opp_matches['match_date'] < match_date)
            ]
            if len(filtered_matches) == 0:
                return np.nan
            
            home_games = filtered_matches[filtered_matches['home_team_id'] == self.team_id] 
            away_games = filtered_matches[filtered_matches['away_team_id'] == self.team_id]
            
            home_wins = len(home_games[home_games['home_goals'] > home_games['away_goals']])
            away_wins = len(away_games[away_games['away_goals'] > away_games['home_goals']])
            home_draws = len(home_games[home_games['home_goals'] == home_games['away_goals']])
            away_draws = len(away_games[away_games['away_goals'] == away_games['home_goals']])
            
            total_wins = home_wins + away_wins
            total_draws = home_draws + away_draws
            total_points = (total_wins * WIN_POINTS) + (total_draws * DRAW_POINTS)
            
            return total_points / len(filtered_matches)
        
        if previous_season is True:
            info(f"Brak wcześniejszego sezonu dla daty {match_date} (pierwszy sezon)")
            return 0
        elif not isinstance(previous_season, dict) or "start_date" not in previous_season:
            error(f"Nieprawidłowe dane o sezonie dla daty {match_date}")
            return 0
        
        filtered_matches = self.rm_matches[
            (self.rm_matches['match_date'] >= previous_season["start_date"]) & 
            (self.rm_matches['match_date'] < match_date)
        ]
        
        if len(filtered_matches) == 0:
            return np.nan
        
        try:
            total_points = (
                (filtered_matches[filtered_matches['real_result'] == 1].shape[0] * WIN_POINTS) + 
                (filtered_matches[filtered_matches['real_result'] == 0.5].shape[0] * DRAW_POINTS)
            )
            
            return total_points / len(filtered_matches)
        except Exception as e:
            error(f"Błąd przy obliczaniu punktów na mecz w sezonie: {str(e)}")
            return False
    
    def calculate_team_stats_against_tier(self, match_date, min_ppm, max_ppm=None):
        """
        Oblicza statystyki drużyny przeciwko przeciwnikom o określonym poziomie PPM.
        
        Args:
            match_date (str/datetime): Data meczu jako punkt odniesienia
            min_ppm (float): Minimalna wartość PPM przeciwnika dla kategorii
            max_ppm (float, optional): Maksymalna wartość PPM przeciwnika (None = bez limitu)
            
        Returns:
            tuple: (średnia_goli_na_mecz, średnia_punktów_na_mecz) lub (False, False) przy błędzie
            
        Notes:
            - Filtruje przeciwników na podstawie ich PPM (Points Per Match)
            - PPM_H = PPM gospodarza, PPM_A = PPM gościa
            - Jeśli max_ppm=None, uwzględnia wszystkich powyżej min_ppm
            - Zwraca (np.nan, np.nan) jeśli brak meczów w kategorii
            - Dla RM używa kolumn 'goals' i 'real_result'
            - Dla innych drużyn oblicza gole i punkty na podstawie home/away_goals
            - Specjalny przypadek dla pierwszego sezonu (2019-2020)
        """
        current_season = self.season_manager.get_season(match_date)
        previous_season = self.season_manager.get_previous_season(current_season)
        
        if self.team_id != 1:
            opp_matches = get_all_opp_matches(self.team_id)
            if opp_matches is None:
                return False, False
            if opp_matches['match_date'].dtype != 'datetime64[ns]':
                opp_matches['match_date'] = pd.to_datetime(opp_matches['match_date'], errors='coerce')
            
            if previous_season is True:
                info(f"Specjalny przypadek dla sezonu 2019-2020. Data meczu: {match_date}")
                filtered_matches = opp_matches[
                    (opp_matches['match_date'] >= pd.to_datetime("2019-08-01")) & 
                    (opp_matches['match_date'] < match_date)
                ]
            else:
                filtered_matches = opp_matches[
                    (opp_matches['match_date'] < match_date) & 
                    (opp_matches['match_date'] >= previous_season["start_date"])
                ]
            
            if max_ppm is None:
                tier_matches = filtered_matches[
                    ((filtered_matches['home_team_id'] == self.team_id) & (filtered_matches['PPM_A'] > min_ppm)) |
                    ((filtered_matches['away_team_id'] == self.team_id) & (filtered_matches['PPM_H'] > min_ppm))
                ]
            else:
                tier_matches = filtered_matches[
                    ((filtered_matches['home_team_id'] == self.team_id) & 
                     (filtered_matches['PPM_A'] >= min_ppm) & (filtered_matches['PPM_A'] <= max_ppm)) |
                    ((filtered_matches['away_team_id'] == self.team_id) & 
                     (filtered_matches['PPM_H'] >= min_ppm) & (filtered_matches['PPM_H'] <= max_ppm))
                ]
            
            if len(tier_matches) == 0:
                return np.nan, np.nan
            
            home_games = tier_matches[tier_matches['home_team_id'] == self.team_id]
            away_games = tier_matches[tier_matches['away_team_id'] == self.team_id]
            
            if home_games.empty and away_games.empty:
                info(f"Brak meczów dla drużyny o ID {self.team_id} w danym okresie.")
                return np.nan, np.nan
            
            try:
                goals_scored = home_games['home_goals'].sum() + away_games['away_goals'].sum()
                
                home_wins = len(home_games[home_games['home_goals'] > home_games['away_goals']])
                away_wins = len(away_games[away_games['away_goals'] > away_games['home_goals']])
                home_draws = len(home_games[home_games['home_goals'] == home_games['away_goals']])
                away_draws = len(away_games[away_games['away_goals'] == away_games['home_goals']])
                
                total_wins = home_wins + away_wins
                total_draws = home_draws + away_draws
                total_points = (total_wins * WIN_POINTS) + (total_draws * DRAW_POINTS)
                
                avg_goals = goals_scored / len(tier_matches)
                avg_points = total_points / len(tier_matches)
                return avg_goals, avg_points
            
            except Exception as e:
                error(f"Błąd przy obliczaniu statystyk przeciwko drużynom: {str(e)}")
                return False, False
        
        if previous_season is True:
            info(f"Specjalny przypadek dla sezonu 2019-2020. Data meczu: {match_date}")
            return False, False
        elif not isinstance(previous_season, dict) or "start_date" not in previous_season:
            error(f"Nieprawidłowe dane o sezonie dla daty {match_date}")
            return False, False
            
        filtered_matches = self.rm_matches[
            (self.rm_matches['match_date'] < match_date) & 
            (self.rm_matches['match_date'] > previous_season["start_date"])
        ]
        
        if max_ppm is None:
            tier_matches = filtered_matches[
                (filtered_matches['PPM_H'] > min_ppm) | 
                (filtered_matches['PPM_A'] > min_ppm)
            ]
        else:
            tier_matches = filtered_matches[
                ((filtered_matches['PPM_H'] >= min_ppm) & (filtered_matches['PPM_H'] <= max_ppm)) | 
                ((filtered_matches['PPM_A'] >= min_ppm) & (filtered_matches['PPM_A'] <= max_ppm))
            ]
        
        if len(tier_matches) == 0:
            return np.nan, np.nan
        
        try:
            goals_scored = tier_matches['goals'].sum()
            
            points = (
                (tier_matches[tier_matches['real_result'] == 1].shape[0] * WIN_POINTS) + 
                (tier_matches[tier_matches['real_result'] == 0.5].shape[0] * DRAW_POINTS)
            )
            
            avg_goals = goals_scored / len(tier_matches)
            avg_points = points / len(tier_matches)
            return avg_goals, avg_points
            
        except Exception as e:
            error(f"Błąd przy obliczaniu statystyk przeciwko drużynom: {str(e)}")
            return False, False
    
    def calculate_team_goals_against_top(self, match_date):
        """
        Oblicza średnią goli na mecz przeciwko drużynom TOP tier.
        
        Args:
            match_date (str/datetime): Data meczu jako punkt odniesienia
            
        Returns:
            float: Średnia goli na mecz przeciwko drużynom TOP (PPM >= 1.9)
            
        Notes:
            - TOP tier: drużyny z PPM >= 1.9 (silne drużyny)
            - Uwzględnia tylko mecze z poprzedniego sezonu przed match_date
        """
        avg_goals, _ = self.calculate_team_stats_against_tier(match_date, TOP_TIER_MIN_PPM)
        return avg_goals
    
    def calculate_team_points_against_top(self, match_date):
        """
        Oblicza średnią punktów na mecz przeciwko drużynom TOP tier.
        
        Args:
            match_date (str/datetime): Data meczu jako punkt odniesienia
            
        Returns:
            float: Średnia punktów na mecz przeciwko drużynom TOP (PPM >= 1.9)
            
        Notes:
            - TOP tier: drużyny z PPM >= 1.9 (silne drużyny)
            - Uwzględnia tylko mecze z poprzedniego sezonu przed match_date
        """
        _, avg_points = self.calculate_team_stats_against_tier(match_date, TOP_TIER_MIN_PPM)
        return avg_points
    
    def calculate_team_goals_against_mid(self, match_date):
        """
        Oblicza średnią goli na mecz przeciwko drużynom MID tier.
        
        Args:
            match_date (str/datetime): Data meczu jako punkt odniesienia
            
        Returns:
            float: Średnia goli na mecz przeciwko drużynom MID (1.2 <= PPM < 1.9)
            
        Notes:
            - MID tier: drużyny ze średnim PPM między 1.2 a 1.9
            - Uwzględnia tylko mecze z poprzedniego sezonu przed match_date
        """
        avg_goals, _ = self.calculate_team_stats_against_tier(match_date, MID_TIER_MIN_PPM, MID_TIER_MAX_PPM)
        return avg_goals
    
    def calculate_team_points_against_mid(self, match_date):
        """
        Oblicza średnią punktów na mecz przeciwko drużynom MID tier.
        
        Args:
            match_date (str/datetime): Data meczu jako punkt odniesienia
            
        Returns:
            float: Średnia punktów na mecz przeciwko drużynom MID (1.2 <= PPM < 1.9)
            
        Notes:
            - MID tier: drużyny ze średnim PPM między 1.2 a 1.9
            - Uwzględnia tylko mecze z poprzedniego sezonu przed match_date
        """
        _, avg_points = self.calculate_team_stats_against_tier(match_date, MID_TIER_MIN_PPM, MID_TIER_MAX_PPM)
        return avg_points
    
    def calculate_team_goals_against_low(self, match_date):
        """
        Oblicza średnią goli na mecz przeciwko drużynom LOW tier.
        
        Args:
            match_date (str/datetime): Data meczu jako punkt odniesienia
            
        Returns:
            float: Średnia goli na mecz przeciwko drużynom LOW (PPM < 1.2)
            
        Notes:
            - LOW tier: drużyny z niskim PPM poniżej 1.2 (słabe drużyny)
            - Uwzględnia tylko mecze z poprzedniego sezonu przed match_date
        """
        avg_goals, _ = self.calculate_team_stats_against_tier(match_date, 0, LOW_TIER_MAX_PPM)
        return avg_goals
    
    def calculate_team_points_against_low(self, match_date):
        """
        Oblicza średnią punktów na mecz przeciwko drużynom LOW tier.
        
        Args:
            match_date (str/datetime): Data meczu jako punkt odniesienia
            
        Returns:
            float: Średnia punktów na mecz przeciwko drużynom LOW (PPM < 1.2)
            
        Notes:
            - LOW tier: drużyny z niskim PPM poniżej 1.2 (słabe drużyny)
            - Uwzględnia tylko mecze z poprzedniego sezonu przed match_date
        """
        _, avg_points = self.calculate_team_stats_against_tier(match_date, 0, LOW_TIER_MAX_PPM)
        return avg_points