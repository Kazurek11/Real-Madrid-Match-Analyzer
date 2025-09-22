"""
Kalkulator statystyk drużynowych i trenerskich.

Moduł oblicza średnie ocen trenerów, statystyki ofensywne/defensywne
oraz wydajność punktową dla Real Madryt i przeciwników na podstawie
ostatnich meczów i poprzednich sezonów.
"""

import pandas as pd
import numpy as np
from helpers.logger import info, error, warning
from data_processing.const_variable import SEASON_DATES
from finall_dataframe.rm_team.config import RM_COACH_RATING, WIN_POINTS, DRAW_POINTS
from finall_dataframe.rm_team.utils import check_type_in_dataframe, check_NaN_column_in_RM_matches


class StatsCalculator:
    """
    Kalkulator statystyk drużynowych i trenerskich.
    
    Oblicza średnie ocen trenerów, statystyki meczowe oraz wydajność
    przeciwko różnym typom przeciwników na podstawie danych historycznych.
    Obsługuje zarówno Real Madryt jak i drużyny przeciwników.
    
    Attributes:
        rm_matches (pd.DataFrame): Dane meczów Real Madryt z preprocessowanymi kolumnami
        opp_matches (pd.DataFrame): Dane wszystkich meczów La Liga
        season_manager: Manager do zarządzania datami sezonów
    """
    
    def __init__(self, rm_matches, opp_matches, season_manager):
        """
        Inicjalizuje kalkulator statystyk.
        
        Args:
            rm_matches (pd.DataFrame): Dane meczów Real Madryt z kolumnami specyficznymi
            opp_matches (pd.DataFrame): Dane wszystkich meczów La Liga
            season_manager: Manager sezonów do określania dat rozpoczęcia/zakończenia
            
        Notes:
            - rm_matches zawiera preprocessowane dane z kolumnami 'real_result', 'goals'
            - opp_matches zawiera surowe dane wszystkich drużyn z home/away_goals
            - season_manager zapewnia funkcje get_season() i get_previous_season()
        """
        self.rm_matches = rm_matches
        self.opp_matches = opp_matches
        self.season_manager = season_manager
    
    def calculate_coach_rating_last_season(self, coach_id, match_date):
        """
        Oblicza średnią ocenę trenera z poprzedniego sezonu.
        
        Args:
            coach_id (int): ID trenera (nieużywane w obecnej implementacji)
            match_date (str/datetime): Data meczu jako punkt odniesienia
            
        Returns:
            float/np.nan: Średnia ocena trenera lub NaN jeśli brak danych
            
        Notes:
            - Dla pierwszego sezonu używa danych z SEASON_DATES[0]
            - Filtruje mecze z niepustymi ocenami trenera (RM_COACH_RATING)
            - Zwraca NaN jeśli brak ocen w poprzednim sezonie
            - Konwertuje daty do datetime64[ns] jeśli potrzeba
            - Loguje informacje o liczbie meczów i średniej ocenie
        """
        current_season = self.season_manager.get_season(match_date)
        previous_season = self.season_manager.get_previous_season(current_season)
        
        if previous_season is True:
            info(f"Brak wcześniejszego sezonu dla daty {match_date} (pierwszy sezon)")
            first_season_matches = self.rm_matches[
                (self.rm_matches['match_date'] >= SEASON_DATES[0][0]) & 
                (self.rm_matches['match_date'] <= SEASON_DATES[0][1])
            ]
            valid_matches = first_season_matches[first_season_matches[RM_COACH_RATING].notna()]
            
            if valid_matches.empty:
                info(f"Brak ocen trenera w pierwszym sezonie dla daty {match_date}")
                return np.nan
                
            coach_rating_avg = valid_matches[RM_COACH_RATING].mean()
            info(f"Średnia ocena trenera z {len(valid_matches)} meczów: {coach_rating_avg}")
            return coach_rating_avg
            
        elif not isinstance(previous_season, dict) or "start_date" not in previous_season:
            error(f"Invalid previous season data for match date {match_date}")
            return np.nan
        
        if not check_type_in_dataframe(self.rm_matches, 'match_date', 'datetime64[ns]'):
            self.rm_matches['match_date'] = pd.to_datetime(self.rm_matches['match_date'], errors='coerce')
        
        previous_season_matches = self.rm_matches[
            (self.rm_matches['match_date'] > previous_season["start_date"]) & 
            (self.rm_matches['match_date'] < previous_season["end_date"])
        ]
        
        valid_matches = previous_season_matches[previous_season_matches[RM_COACH_RATING].notna()]
        
        if valid_matches.empty:
            info(f"Brak ocen trenera w poprzednim sezonie dla daty {match_date}")
            return np.nan
            
        coach_rating_avg = valid_matches[RM_COACH_RATING].mean()
        info(f"Średnia ocena trenera z {len(valid_matches)} meczów poprzedniego sezonu: {coach_rating_avg}")
        return coach_rating_avg
    
    def calculate_coach_rating_last_5(self, match_date):
        """
        Oblicza średnią ocenę trenera z ostatnich 5 meczów.
        
        Args:
            match_date (str/datetime): Data meczu jako punkt odniesienia
            
        Returns:
            float/False: Średnia ocena trenera z ostatnich 5 meczów lub False/0 przy błędzie
            
        Notes:
            - Filtruje mecze przed match_date
            - Sortuje malejąco po dacie i bierze pierwsze 5 meczów
            - Sprawdza poprawność danych przez check_NaN_column_in_RM_matches
            - Zwraca 0 jeśli brak meczów
            - Używa kolumny RM_COACH_RATING do obliczeń
        """
        filtered_matches = self.rm_matches[self.rm_matches['match_date'] < match_date]
        sorted_matches = filtered_matches.sort_values('match_date', ascending=False)
        last_5_matches = sorted_matches.head(5)
        
        if len(last_5_matches) == 0:
            return np.nan
        
        if not check_NaN_column_in_RM_matches(last_5_matches):
            return False
        
        try:
            sum_of_coach_rating = last_5_matches[RM_COACH_RATING].sum()
            return sum_of_coach_rating / len(last_5_matches)
        except Exception as e:
            error(f"Błąd przy obliczaniu oceny trenera z ostatnich 5 meczów: {str(e)}")
            return False
    
    def calculate_last_5_stats(self, match_date, team_id, matches_count=5):
        """
        Oblicza statystyki z ostatnich X meczów dla określonej drużyny.
        
        Args:
            match_date (str/datetime): Data meczu jako punkt odniesienia
            team_id (int): ID drużyny (1 dla Real Madryt, inne dla przeciwników)
            matches_count (int): Liczba ostatnich meczów do analizy (domyślnie 5)
            
        Returns:
            dict/False: Słownik ze statystykami lub False przy błędzie
            
        Notes:
            - Dla team_id=1 używa _calculate_real_madrid_last_5()
            - Dla innych team_id używa _calculate_opponent_last_5()
            - Zwracany słownik zawiera klucze z prefiksem RM_ lub OP_
            - Statystyki obejmują: gole strzelone/stracone, różnicę bramek, PPM, PPM przeciwników
        """
        if team_id == 1:
            return self._calculate_real_madrid_last_5(match_date, matches_count)
        else:
            return self._calculate_opponent_last_5(match_date, team_id, matches_count)
    
    def _calculate_real_madrid_last_5(self, match_date, matches_count):
        """
        Oblicza statystyki ostatnich meczów dla Real Madryt.
        
        Args:
            match_date (str/datetime): Data meczu jako punkt odniesienia
            matches_count (int): Liczba ostatnich meczów do analizy
            
        Returns:
            dict/False: Słownik ze statystykami RM lub False przy błędzie
            
        Notes:
            - Używa kolumn specyficznych dla RM: 'goals', 'real_result'
            - Oblicza gole stracone na podstawie home/away_goals przeciwników
            - Punkty na podstawie real_result (1=wygrana, 0.5=remis, 0=porażka)
            - PPM przeciwników z kolumn PPM_H/PPM_A
            - Zwraca średnie wartości podzielone przez liczbę meczów
            - Klucze: RM_G_SCO_L5, RM_G_CON_L5, RM_GDIF_L5, RM_PPM_L5, RM_OPP_PPM_L5
        """
        info(f"Obliczam statystyki ostatnich {matches_count} meczów dla Realu Madryt przed {match_date}")
        
        filtered_matches = self.rm_matches[self.rm_matches['match_date'] < match_date]
        sorted_matches = filtered_matches.sort_values('match_date', ascending=False)
        last_matches = sorted_matches.head(matches_count)
        
        if len(last_matches) == 0:
            warning(f"Brak meczów dla Realu Madryt przed datą {match_date}")
            return False
            
        if not check_NaN_column_in_RM_matches(last_matches):
            error(f"Znaleziono wartości NaN w danych dla Realu Madryt")
            return False
        
        try:
            matches_count = len(last_matches)
            rm_goals = last_matches['goals'].sum()
            
            rm_conceded_goals = (
                last_matches[last_matches['home_team_id'] == 1]['away_goals'].sum() + 
                last_matches[last_matches['away_team_id'] == 1]['home_goals'].sum()
            )
            
            rm_difference = rm_goals - rm_conceded_goals
            
            rm_points = (
                (last_matches[last_matches['real_result'] == 1].shape[0] * WIN_POINTS) + 
                (last_matches[last_matches['real_result'] == 0.5].shape[0] * DRAW_POINTS)
            )
            
            rm_opp_ppm = (
                last_matches[last_matches['home_team_id'] == 1]['PPM_A'].sum() + 
                last_matches[last_matches['away_team_id'] == 1]['PPM_H'].sum()
            )
            
            info(f"Pomyślnie obliczono statystyki dla Realu Madryt")
            return {
                'RM_G_SCO_L5': rm_goals / matches_count,
                'RM_G_CON_L5': rm_conceded_goals / matches_count,
                'RM_GDIF_L5': rm_difference / matches_count,
                'RM_PPM_L5': rm_points / matches_count,
                'RM_OPP_PPM_L5': rm_opp_ppm / matches_count
            }
            
        except Exception as e:
            error(f"Wystąpił błąd podczas obliczania statystyk dla Realu Madryt: {str(e)}")
            return False
    
    def _calculate_opponent_last_5(self, match_date, team_id, matches_count):
        """
        Oblicza statystyki ostatnich meczów dla drużyny przeciwnika.
        
        Args:
            match_date (str/datetime): Data meczu jako punkt odniesienia
            team_id (int): ID drużyny przeciwnika
            matches_count (int): Liczba ostatnich meczów do analizy
            
        Returns:
            dict/np.nan: Słownik ze statystykami przeciwnika lub np.nan przy błędzie
            
        Notes:
            - Używa danych opp_matches z wszystkimi meczami La Liga
            - Filtruje mecze gdzie team_id występuje jako gospodarz lub gość
            - Oblicza gole na podstawie home_goals/away_goals w zależności od roli
            - Punkty na podstawie porównania wyników home_goals vs away_goals
            - PPM przeciwników drużyny z kolumn PPM_H/PPM_A
            - Klucze: OP_G_SCO_L5, OP_G_CON_L5, OP_GDIF_L5, OP_PPM_L5, OP_OPP_PPM_L5
        """
        info(f"Obliczam statystyki ostatnich {matches_count} meczów dla zespołu ID={team_id} przed {match_date}")
        
        try:
            filtered_matches = self.opp_matches[
                (self.opp_matches['match_date'] < match_date) & 
                ((self.opp_matches['home_team_id'] == team_id) | (self.opp_matches['away_team_id'] == team_id))
            ]
            sorted_matches = filtered_matches.sort_values('match_date', ascending=False)
            last_matches = sorted_matches.head(matches_count)
            
            if len(last_matches) == 0:
                warning(f"Brak meczów dla zespołu ID={team_id} przed datą {match_date}")
                return np.nan
                
            if not check_NaN_column_in_RM_matches(last_matches):
                error(f"Znaleziono wartości NaN w danych dla zespołu ID={team_id}")
                return np.nan
            
            matches_count = len(last_matches)
            
            opp_goals = (
                last_matches[last_matches['home_team_id'] == team_id]['home_goals'].sum() + 
                last_matches[last_matches['away_team_id'] == team_id]['away_goals'].sum()
            )
            
            opp_conceded_goals = (
                last_matches[last_matches['home_team_id'] == team_id]['away_goals'].sum() + 
                last_matches[last_matches['away_team_id'] == team_id]['home_goals'].sum()
            )
            
            opp_difference = opp_goals - opp_conceded_goals
            
            home_wins = last_matches[
                (last_matches["home_team_id"] == team_id) & 
                (last_matches["home_goals"] > last_matches["away_goals"])
            ].shape[0]
            
            away_wins = last_matches[
                (last_matches["away_team_id"] == team_id) & 
                (last_matches["away_goals"] > last_matches["home_goals"])
            ].shape[0]
            
            draws = last_matches[
                last_matches["home_goals"] == last_matches["away_goals"]
            ].shape[0]
            
            opp_points = (home_wins + away_wins) * WIN_POINTS + draws * DRAW_POINTS
            
            point_per_match_of_rivalas_rival = (
                last_matches[last_matches['home_team_id'] == team_id]['PPM_A'].sum() + 
                last_matches[last_matches['away_team_id'] == team_id]['PPM_H'].sum()
            )
            
            info(f"Pomyślnie obliczono statystyki dla zespołu ID={team_id}")
            return {
                'OP_G_SCO_L5': opp_goals / matches_count,
                'OP_G_CON_L5': opp_conceded_goals / matches_count,
                'OP_GDIF_L5': opp_difference / matches_count,
                'OP_PPM_L5': opp_points / matches_count,
                'OP_OPP_PPM_L5': point_per_match_of_rivalas_rival / matches_count
            }
            
        except Exception as e:
            error(f"Wystąpił błąd podczas obliczania statystyk dla zespołu ID={team_id}: {str(e)}")
            return False