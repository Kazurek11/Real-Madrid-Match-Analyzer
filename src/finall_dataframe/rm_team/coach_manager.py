import pandas as pd
from helpers.logger import error


class CoachManager:
    """Klasa zarządzająca danymi trenerów Real Madryt"""
    
    def __init__(self, coach_data):
        """
        Inicjalizuje manager trenerów z danymi trenerskimi.
        
        Args:
            coach_data (pd.DataFrame): DataFrame z danymi trenerów zawierający kolumny:
                                     coach_id, coach_name, start_date, end_date
        """
        self.coach_data = coach_data
    
    def get_coach_id_by_date(self, match_date):
        """
        Zwraca ID trenera Real Madryt aktywnego w określonej dacie.
        
        Args:
            match_date (str/datetime): Data meczu
            
        Returns:
            int/None: ID trenera lub None jeśli nie znaleziono
            
        Notes:
            - Sprawdza przedział start_date <= match_date <= end_date
            - Zwraca pierwszego pasującego trenera
        """
        matching_coaches = self.coach_data[
            (self.coach_data['start_date'] <= match_date) & 
            (self.coach_data['end_date'] >= match_date)
        ]
        if matching_coaches.empty:
            return None
        return matching_coaches['coach_id'].iloc[0]
    
    def get_coach_id_by_name(self, coach_name):
        """
        Zwraca ID trenera na podstawie nazwy.
        
        Args:
            coach_name (str): Nazwa trenera
            
        Returns:
            int/None: ID trenera lub None jeśli nie znaleziono
        """
        matching_coaches = self.coach_data[self.coach_data['coach_name'] == coach_name]
        if matching_coaches.empty:
            return None
        return matching_coaches['coach_id'].iloc[0]
    
    def get_coach_name_by_id(self, coach_id):
        """
        Zwraca nazwę trenera na podstawie ID.
        
        Args:
            coach_id (int): ID trenera
            
        Returns:
            str/None: Nazwa trenera lub None jeśli nie znaleziono
        """
        matching_coaches = self.coach_data[self.coach_data['coach_id'] == coach_id]
        if matching_coaches.empty:
            return None
        return matching_coaches['coach_name'].iloc[0]
    
    def validate_coach_exists(self, coach_id):
        """
        Sprawdza czy trener istnieje w bazie danych.
        
        Args:
            coach_id (int): ID trenera do sprawdzenia
            
        Returns:
            bool: True jeśli trener istnieje, False w przeciwnym razie
            
        Notes:
            - Loguje błąd jeśli trener nie istnieje
        """
        check = self.coach_data[self.coach_data['coach_id'] == coach_id]
        if check.empty:
            error(f"UWAGA: Trener o ID {coach_id} nie istnieje w bazie danych!")
            return False
        return True