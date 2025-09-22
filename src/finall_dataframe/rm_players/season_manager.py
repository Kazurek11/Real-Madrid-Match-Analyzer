import pandas as pd
import os
import sys  

current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from helpers.logger import info, error, debug, warning
from data_processing.const_variable import SEASON_DATES as SEASON

class SeasonManager:
    """Klasa zarządzająca informacjami o sezonach i wyszukiwaniem na podstawie dat"""
    
    def __init__(self):
        """
        Inicjalizuje manager sezonów z predefiniowanymi zakresami dat.
        
        Notes:
            - Definiuje 6 sezonów od 2019-2020 do 2024-2025
            - Konwertuje daty do formatu pandas datetime
            - Wykorzystuje stałe z SEASON_DATES
        """
        self.seasons = [
            {"name": "2019-2020", "start_date": pd.to_datetime(SEASON[0][0]), "end_date": pd.to_datetime(SEASON[0][1])},
            {"name": "2020-2021", "start_date": pd.to_datetime(SEASON[1][0]), "end_date": pd.to_datetime(SEASON[1][1])},
            {"name": "2021-2022", "start_date": pd.to_datetime(SEASON[2][0]), "end_date": pd.to_datetime(SEASON[2][1])},
            {"name": "2022-2023", "start_date": pd.to_datetime(SEASON[3][0]), "end_date": pd.to_datetime(SEASON[3][1])},
            {"name": "2023-2024", "start_date": pd.to_datetime(SEASON[4][0]), "end_date": pd.to_datetime(SEASON[4][1])},
            {"name": "2024-2025", "start_date": pd.to_datetime(SEASON[5][0]), "end_date": pd.to_datetime(SEASON[5][1])}
        ]
    
    def get_season_for_date(self, match_date):
        """
        Alias dla metody get_season zapewniający kompatybilność.
        
        Args:
            match_date (str/datetime): Data meczu
            
        Returns:
            dict/None: Informacje o sezonie lub None
        """
        return self.get_season(match_date)
    
    def get_season(self, match_date):
        """
        Określa sezon na podstawie podanej daty.
        
        Args:
            match_date (str/datetime): Data meczu do sprawdzenia
            
        Returns:
            dict/None: Słownik z kluczami 'name', 'start_date', 'end_date' lub None
            
        Notes:
            - Sprawdza wszystkie zdefiniowane sezony
            - Zwraca pierwszy pasujący sezon
            - Automatycznie konwertuje datę do pandas datetime
        """
        match_date = pd.to_datetime(match_date)
        for season in self.seasons:
            if season["start_date"] <= match_date <= season["end_date"]:
                return season
        return None
    
    def get_previous_season(self, season):
        """
        Zwraca informacje o poprzednim sezonie względem podanego.
        
        Args:
            season (dict): Słownik z informacjami o aktualnym sezonie
            
        Returns:
            dict/None/bool: Poprzedni sezon, None jeśli błąd, True dla pierwszego sezonu
            
        Notes:
            - Szuka sezonu po nazwie w liście sezonów
            - Zwraca True dla pierwszego sezonu (specjalny przypadek)
            - Loguje błąd jeśli nie znajdzie sezonu
        """
        if not season:
            return None
            
        try:
            current_index = next(i for i, s in enumerate(self.seasons) 
                                if s["name"] == season["name"])
        except StopIteration:
            error(f"Nie można znaleźć bieżącego sezonu '{season}' w liście sezonów.")
            return None   
            
        if current_index == 0:
            return True
            
        return self.seasons[current_index - 1]
    
    def get_season_name(self, match_date):
        """
        Pobiera nazwę sezonu dla określonej daty.
        
        Args:
            match_date (str/datetime): Data meczu
            
        Returns:
            str: Nazwa sezonu w formacie "YYYY-YYYY" lub pusty string
        """
        season = self.get_season(match_date)
        if not season:
            return ""
        return season["name"]
    
    def is_valid_season_date(self, match_date):
        """
        Sprawdza czy data mieści się w zakresie zdefiniowanych sezonów.
        
        Args:
            match_date (str/datetime): Data do sprawdzenia
            
        Returns:
            bool: True jeśli data należy do któregoś sezonu, False w przeciwnym razie
        """
        return self.get_season(match_date) is not None