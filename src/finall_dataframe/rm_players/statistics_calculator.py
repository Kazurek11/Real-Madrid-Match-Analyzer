import pandas as pd
import os
import sys

current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from helpers.logger import info, error, debug, warning

class StatisticsCalculator:
    """Klasa obliczająca różne statystyki zawodników"""
    
    def __init__(self, data_loader, season_manager, player_manager):
        """
        Inicjalizuje kalkulator statystyk zawodników.
        
        Args:
            data_loader: Dostawca danych z meczów i statystyk
            season_manager: Manager sezonów do określania dat
            player_manager: Manager zawodników do obsługi danych personalnych
            
        Notes:
            - Inicjalizuje dostęp do przefiltrowanych i oryginalnych danych
            - Przechowuje cache dla zoptymalizowanego dostępu
            - Automatycznie konfiguruje źródła danych
        """
        self.data_loader = data_loader
        self.season_manager = season_manager
        self.player_manager = player_manager
        
        self._dates_without_season = set()
        self._combined_data = None
        
        self._initialize_data_access()
    
    def _initialize_data_access(self):
        """
        Inicjalizuje dostęp do wszystkich źródeł danych.
        
        Notes:
            - Preferuje przefiltrowane dane nad oryginalnymi
            - Zapewnia fallback do oryginalnych danych
            - Ustawia atrybuty dla szybkiego dostępu
        """
        self.individual = self.data_loader.individual
        self.matches = self.data_loader.matches
        self.old_matches = self.data_loader.old_matches
        
        if hasattr(self.data_loader, 'filtered_individual') and not self.data_loader.filtered_individual.empty:
            self.filtered_individual = self.data_loader.filtered_individual
        else:
            self.filtered_individual = self.individual
            
        if hasattr(self.data_loader, 'filtered_matches') and not self.data_loader.filtered_matches.empty:
            self.filtered_matches = self.data_loader.filtered_matches
        else:
            self.filtered_matches = self.matches
    
    def get_player_rating(self, player_id, match_date, number_of_matches=1):
        """
        Pobiera średnią ocenę zawodnika z ostatnich N meczów.
        
        Args:
            player_id (int): ID zawodnika
            match_date (str/datetime): Data meczu jako punkt odniesienia
            number_of_matches (int): Liczba ostatnich meczów do uwzględnienia
            
        Returns:
            float: Średnia ocena z ostatnich N meczów lub 0
            
        Notes:
            - Preferuje kolumnę 'rating' nad 'editor_rating'
            - Uwzględnia tylko mecze z is_value > 0 jeśli kolumna istnieje
            - Używa ogólnej średniej jako fallback
        """
        try:
            player_name = self.player_manager.get_player_name(player_id)
            if not player_name:
                return 0
                
            data = self.filtered_individual[self.filtered_individual['player_name'] == player_name]
            
            if data.empty:
                return 0
            
            match_date_dt = pd.to_datetime(match_date)
            last_n_matches = data[data['match_date'] < match_date_dt].sort_values(
                by='match_date', ascending=False).head(number_of_matches)
            
            if not last_n_matches.empty:
                if 'is_value' in last_n_matches.columns:
                    valid_matches = last_n_matches[last_n_matches['is_value'] > 0]
                    if not valid_matches.empty:
                        if 'rating' in valid_matches.columns:
                            return valid_matches['rating'].mean()
                        elif 'editor_rating' in valid_matches.columns:
                            return valid_matches['editor_rating'].mean()
                else:
                    if 'rating' in last_n_matches.columns:
                        return last_n_matches['rating'].mean()
                    elif 'editor_rating' in last_n_matches.columns:
                        return last_n_matches['editor_rating'].mean()
            
            if 'is_value' in data.columns:
                valid_all_matches = data[data['is_value'] > 0]
            else:
                valid_all_matches = data
                
            if not valid_all_matches.empty:
                if 'rating' in valid_all_matches.columns:
                    return valid_all_matches['rating'].mean()
                elif 'editor_rating' in valid_all_matches.columns:
                    return valid_all_matches['editor_rating'].mean()
            
            return 0
        except Exception as e:
            error(f"Błąd podczas pobierania oceny dla zawodnika {player_id}: {str(e)}")
            return 0
    
    def is_player_in_previous_season(self, player_id, match_date, min_minutes=200):
        """
        Sprawdza czy zawodnik grał w poprzednim sezonie.
        
        Args:
            player_id (int): ID zawodnika
            match_date (str/datetime): Data meczu jako punkt odniesienia
            min_minutes (int): Minimalna liczba minut do uznania za aktywnego
            
        Returns:
            bool: True jeśli zawodnik grał wystarczająco w poprzednim sezonie
            
        Notes:
            - Używa oryginalnych danych (nie przefiltrowanych)
            - Sprawdza sumę minut w poprzednim sezonie
            - Zwraca False dla pierwszego sezonu
        """
        try:
            player_name = self.player_manager.get_player_name(player_id)
            if not player_name:
                return False
            
            season = self.season_manager.get_season(match_date)
            if not season:
                return False
                
            prev_season = self.season_manager.get_previous_season(season)
            if not prev_season or prev_season is True:
                return False
                
            prev_season_data = self.individual[
                (self.individual['player_name'] == player_name) &
                (self.individual['match_date'] >= prev_season["start_date"]) & 
                (self.individual['match_date'] <= prev_season["end_date"])
            ]
            
            if prev_season_data.empty:
                return False
                
            if 'player_min' not in prev_season_data.columns:
                return False
                
            total_minutes = prev_season_data["player_min"].sum()
            return total_minutes >= min_minutes
        except Exception as e:
            error(f"Błąd podczas sprawdzania obecności zawodnika w poprzednim sezonie: {str(e)}")
            return False
    
    def get_last_season_rating(self, player_id, match_date):
        """
        Pobiera średnią ocenę zawodnika z poprzedniego sezonu.
        
        Args:
            player_id (int): ID zawodnika
            match_date (str/datetime): Data meczu jako punkt odniesienia
            
        Returns:
            float: Średnia ocena z poprzedniego sezonu lub 0
            
        Notes:
            - Dla pierwszego sezonu używa starych danych
            - Sprawdza aktywność zawodnika w poprzednim sezonie
            - Fallback do średniej sezonowej jeśli brak danych zawodnika
        """
        try:
            player_name = self.player_manager.get_player_name(player_id)
            if not player_name:
                return 0
                
            season = self.season_manager.get_season(match_date)
            if not season:
                date_str = pd.to_datetime(match_date).strftime('%Y-%m-%d')
                if date_str not in self._dates_without_season:
                    self._dates_without_season.add(date_str)
                    debug(f"Nie znaleziono sezonu dla daty {date_str}")
                return 0
                
            prev_season = self.season_manager.get_previous_season(season)
            if prev_season is True or prev_season is None:
                return self._get_old_data_rating(player_id)
                
            if self.is_player_in_previous_season(player_id, match_date):
                prev_season_data = self.individual[
                    (self.individual['player_name'] == player_name) & 
                    (self.individual['match_date'] >= prev_season["start_date"]) & 
                    (self.individual['match_date'] <= prev_season["end_date"])
                ]
                
                if not prev_season_data.empty:
                    if 'is_value' in prev_season_data.columns:
                        valid_data = prev_season_data[prev_season_data['is_value'] == 1]
                        if not valid_data.empty and 'editor_rating' in valid_data.columns:
                            return valid_data['editor_rating'].mean()
                    elif 'editor_rating' in prev_season_data.columns:
                        return prev_season_data['editor_rating'].mean()
            
            return self._get_avg_season_rating(prev_season)
        except Exception as e:
            error(f"Błąd podczas pobierania oceny z poprzedniego sezonu: {str(e)}")
            return 0
    
    def _get_old_data_rating(self, player_id):
        """
        Pobiera ocenę zawodnika ze starych danych.
        
        Args:
            player_id (int): ID zawodnika
            
        Returns:
            float: Średnia ocena ze starych danych lub 0
        """
        try:
            player_name = self.player_manager.get_player_name(player_id)
            if not player_name or self.old_matches.empty:
                return 0
                
            player_data = self.old_matches[self.old_matches['player_name'] == player_name]
            
            if player_data.empty:
                return 0
                
            if 'is_value' in player_data.columns and 'editor_rating' in player_data.columns:
                valid_data = player_data[player_data['is_value'] > 0]
                if not valid_data.empty:
                    return valid_data['editor_rating'].mean()
            elif 'editor_rating' in player_data.columns:
                return player_data['editor_rating'].mean()
                
            return 0
        except Exception as e:
            error(f"Błąd podczas pobierania starszych danych: {str(e)}")
            return 0
    
    def _get_avg_season_rating(self, season):
        """
        Oblicza średnią ocenę dla całego sezonu.
        
        Args:
            season (dict): Słownik z informacjami o sezonie
            
        Returns:
            float: Średnia ocena sezonu lub 0
        """
        try:
            if not season or not isinstance(season, dict):
                return 0
                
            season_matches = self.matches[
                (self.matches['match_date'] >= season["start_date"]) & 
                (self.matches['match_date'] <= season["end_date"])
            ]
            
            if season_matches.empty:
                return 0
                
            if 'editor_rating' in season_matches.columns:
                return season_matches['editor_rating'].mean()
            else:
                return 0
        except Exception as e:
            error(f"Błąd podczas pobierania średniej oceny sezonu: {str(e)}")
            return 0
    
    def get_player_win_ratio(self, player_id, match_date):
        """
        Oblicza procent zwycięstw zawodnika w meczach pierwszej drużyny.
        
        Args:
            player_id (int): ID zawodnika
            match_date (str/datetime): Data meczu jako punkt odniesienia
            
        Returns:
            float: Procent zwycięstw (0-100) lub 0
            
        Notes:
            - Uwzględnia tylko mecze pierwszej drużyny (is_first_squad = 1)
            - Sprawdza wynik Real Madryt (team_id = 1)
            - Oblicza na podstawie meczów przed podaną datą
        """
        try:
            player_name = self.player_manager.get_player_name(player_id)
            if not player_name:
                return 0
                
            if self.filtered_individual.empty:
                debug("Brak przefiltrowanych danych indywidualnych")
                return 0
                
            if 'player_name' not in self.filtered_individual.columns:
                debug(f"Kolumna 'player_name' nie istnieje. Dostępne: {self.filtered_individual.columns.tolist()[:5]}...")
                return 0
            
            player_matches = self.filtered_individual[
                (self.filtered_individual['player_name'] == player_name) & 
                (self.filtered_individual['match_date'] < pd.to_datetime(match_date))
            ]
            
            if 'is_first_squad' in player_matches.columns:
                player_matches = player_matches[player_matches['is_first_squad'] == 1]
            
            if player_matches.empty:
                return 0
                
            required_columns = ['home_team_id', 'away_team_id', 'home_goals', 'away_goals']
            for col in required_columns:
                if col not in player_matches.columns:
                    debug(f"Brak wymaganej kolumny: {col}")
                    return 0
                    
            win_matches = player_matches[
                ((player_matches['home_team_id'] == 1) & (player_matches['home_goals'] > player_matches['away_goals'])) |
                ((player_matches['away_team_id'] == 1) & (player_matches['away_goals'] > player_matches['home_goals']))
            ]
            
            if win_matches.empty:
                return 0
                
            win_ratio = len(win_matches) / len(player_matches) * 100
            return win_ratio
        except Exception as e:
            error(f"Błąd podczas obliczania win_ratio dla zawodnika {player_id}: {str(e)}")
            return 0
    
    def _get_combined_player_data(self):
        """
        Łączy aktualne i historyczne dane o zawodnikach.
        
        Returns:
            dict: Słownik z kluczami 'matches' i 'players' zawierający DataFrame
            
        Notes:
            - Używa cache dla optymalizacji
            - Preferuje przefiltrowane dane
            - Zwraca puste DataFrame w przypadku błędu
        """
        if self._combined_data is not None:
            return self._combined_data
        
        try:
            matches = self.filtered_matches
            individual = self.filtered_individual
            
            if matches.empty or individual.empty:
                debug("Jedno ze źródeł danych jest puste")
                return {'matches': pd.DataFrame(), 'players': pd.DataFrame()}
                
            debug(f"Połączono {len(matches)} rekordów meczowych i {len(individual)} rekordów indywidualnych")
            
            self._combined_data = {
                'matches': matches,
                'players': individual
            }
            
            return self._combined_data
        except Exception as e:
            error(f"Błąd podczas łączenia danych: {str(e)}")
            return {'matches': pd.DataFrame(), 'players': pd.DataFrame()}
    
    def get_player_per90_stats(self, player_id, match_date):
        """
        Oblicza statystyki zawodnika na 90 minut gry.
        
        Args:
            player_id (int): ID zawodnika
            match_date (str/datetime): Data meczu jako punkt odniesienia
            
        Returns:
            dict: Słownik ze statystykami G90, A90, KP90
            
        Notes:
            - Używa danych przed podaną datą
            - Fallback do starych danych i zawodników na tej samej pozycji
            - Zwraca domyślne wartości (0) jeśli brak danych
        """
        try:
            player_name = self.player_manager.get_player_name(player_id)
            if not player_name:
                return self._get_default_stats()
                
            player_data = self.individual[self.individual['player_name'] == player_name]
            
            if not player_data.empty:
                match_date_dt = pd.to_datetime(match_date)
                player_data_before = player_data[player_data['match_date'] < match_date_dt]
                
                if not player_data_before.empty:
                    return self._calculate_stats_from_dataset(player_data_before)
                    
            if not self.old_matches.empty:
                player_matches = self.old_matches[self.old_matches['player_name'] == player_name]
                if not player_matches.empty:
                    return self._calculate_stats_from_dataset(player_matches)
                
            player_position = self.player_manager.get_player_position(player_id)
            if player_position:
                similar_players = self.player_manager.get_same_position_players(player_position, player_name)
                if similar_players:
                    position_data = self.individual[self.individual['player_name'].isin(similar_players)]
                    if not position_data.empty:
                        return self._calculate_stats_from_dataset(position_data)
            
            return self._get_default_stats()
        except Exception as e:
            error(f"Błąd podczas obliczania statystyk na 90 minut dla zawodnika {player_id}: {str(e)}")
            return self._get_default_stats()
    
    def _get_default_stats(self):
        """
        Zwraca domyślne statystyki zawodnika.
        
        Returns:
            dict: Słownik z zerowymi wartościami statystyk
        """
        return {
            'RM_PX_G90': 0,
            'RM_PX_A90': 0,
            'RM_PX_KP90': 0
        }
    
    def _calculate_stats_from_dataset(self, dataset):
        """
        Oblicza statystyki na 90 minut z zestawu danych.
        
        Args:
            dataset (pd.DataFrame): Dane meczowe zawodnika
            
        Returns:
            dict: Słownik ze statystykami na 90 minut
            
        Notes:
            - Wymaga kolumn: goals, assists, key_passes, player_min
            - Zwraca domyślne wartości jeśli brak wymaganych kolumn
        """
        if dataset.empty:
            return self._get_default_stats()
            
        required_cols = ['goals', 'assists', 'key_passes', 'player_min']
        missing_cols = [col for col in required_cols if col not in dataset.columns]
        
        if missing_cols:
            debug(f"Brak wymaganych kolumn: {', '.join(missing_cols)}")
            return self._get_default_stats()
                
        total_minutes = dataset['player_min'].sum()
        
        if total_minutes == 0:
            return self._get_default_stats()
            
        goals = dataset['goals'].sum()
        assists = dataset['assists'].sum()
        key_passes = dataset['key_passes'].sum()
        
        return {
            'RM_PX_G90': (goals * 90) / total_minutes,
            'RM_PX_A90': (assists * 90) / total_minutes,
            'RM_PX_KP90': (key_passes * 90) / total_minutes
        }
    
    def get_player_stat(self, player_id, match_date, stat_type):
        """
        Pobiera konkretną statystykę zawodnika.
        
        Args:
            player_id (int): ID zawodnika
            match_date (str/datetime): Data meczu
            stat_type (str): Typ statystyki ("G90", "A90", "KP90")
            
        Returns:
            float: Wartość statystyki lub 0
        """
        try:
            stats = self.get_player_per90_stats(player_id, match_date)
            
            if not isinstance(stats, dict):
                return 0
            
            if stat_type == "G90" and "RM_PX_G90" in stats:
                return stats['RM_PX_G90']
            elif stat_type == "A90" and "RM_PX_A90" in stats:
                return stats['RM_PX_A90']
            elif stat_type == "KP90" and "RM_PX_KP90" in stats:
                return stats['RM_PX_KP90']
                    
            return 0
        except Exception as e:
            error(f"Błąd w get_player_stat dla zawodnika {player_id}: {str(e)}")
            return 0