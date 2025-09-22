"""
Moduł ładowania danych dla analizy Head-to-Head Real Madryt.

Ten moduł odpowiada za wczytywanie i przygotowanie danych meczowych
wymaganych do obliczania statystyk historycznych starć między 
Real Madryt a przeciwnikami w La Liga.
"""

import os
import pandas as pd
from helpers.file_utils import FileUtils
from helpers.logger import info, error, warning

class H2HDataLoader:
    """
    Ładowarka danych meczowych dla analizy Head-to-Head.
    
    Odpowiada za wczytywanie i walidację podstawowych źródeł danych
    wymaganych do obliczania statystyk historycznych starć Real Madryt
    z przeciwnikami La Liga.
    
    Attributes:
        rm_matches (pd.DataFrame): Mecze Real Madryt z pełnymi statystykami
        opp_matches (pd.DataFrame): Wszystkie mecze La Liga dla kontekstu przeciwników
        
    Data Sources:
        - RM_all_matches_stats.csv: Kompletne dane meczowe Real Madryt
        - all_matches.csv: Wszystkie mecze La Liga dla analizy przeciwników
    """
    
    def __init__(self):
        """
        Inicjalizuje ładowarkę danych H2H.
        
        Przygotowuje atrybuty do przechowywania danych meczowych
        bez ich automatycznego ładowania.
        """
        self.rm_matches = None
        self.opp_matches = None
    
    def load_data(self):
        """
        Ładuje wszystkie wymagane dane meczowe dla analizy Head-to-Head.
        
        Returns:
            tuple: (rm_matches_df, opp_matches_df) zawierające:
                - rm_matches_df (pd.DataFrame): Mecze Real Madryt z kolumnami:
                    * match_id: Unikalny identyfikator meczu
                    * match_date: Data meczu w formacie datetime
                    * home_team_id: ID drużyny gospodarzy
                    * away_team_id: ID drużyny gości
                    * rm_goals: Bramki zdobyte przez Real Madryt
                    * opponent_goals: Bramki zdobyte przez przeciwnika
                    * result: Wynik meczu (W/D/L)
                    * odds_rm_win: Kursy bukmacherskie na zwycięstwo RM
                
                - opp_matches_df (pd.DataFrame): Wszystkie mecze La Liga z kolumnami:
                    * match_id: Identyfikator meczu
                    * match_date: Data meczu
                    * home_team_id: ID gospodarzy
                    * away_team_id: ID gości
                    * season: Sezon rozgrywkowy
        
        Raises:
            FileNotFoundError: Gdy nie można znaleźć wymaganych plików CSV
            ValueError: Gdy dane są uszkodzone lub niepełne
            
        Process:
            1. Określa ścieżki do folderów z danymi (Data/Real i Data/Mecze)
            2. Ładuje RM_all_matches_stats.csv z pełnymi danymi Real Madryt
            3. Ładuje all_matches.csv z meczami wszystkich drużyn La Liga
            4. Konwertuje kolumny dat do formatu datetime dla spójności
            5. Waliduje kompletność kluczowych kolumn
            6. Przechowuje dane w atrybutach klasy dla dalszego użycia
            
        Notes:
            - Dane Real Madryt są krytyczne dla analizy H2H
            - Dane przeciwników służą do kontekstu i walidacji
            - Automatycznie konwertuje daty do pd.datetime
            - Loguje informacje o załadowanych danych
            - Przechowuje dane w pamięci dla wydajności
            
        Example:
            >>> loader = H2HDataLoader()
            >>> rm_data, opp_data = loader.load_data()
            >>> print(f"Załadowano {len(rm_data)} meczów RM")
        """
        info("Rozpoczynam ładowanie danych dla analizy H2H")
        
        rm_path = os.path.join(FileUtils.get_project_root(), 'Data', 'Real')
        opp_path = os.path.join(FileUtils.get_project_root(), 'Data', 'Mecze', 'all_season', 'merged_matches')
        
        try:
            rm_file_path = os.path.join(rm_path, 'RM_all_matches_stats.csv')
            self.rm_matches = FileUtils.load_csv_safe(rm_file_path)
            
            if self.rm_matches is None or len(self.rm_matches) == 0:
                raise ValueError("Nie udało się załadować danych meczowych Real Madryt")
            
            self.rm_matches['match_date'] = pd.to_datetime(self.rm_matches['match_date'])
            info(f"✓ Załadowano {len(self.rm_matches)} meczów Real Madryt")
            
        except Exception as e:
            error(f"Krytyczny błąd przy ładowaniu danych Real Madryt: {str(e)}")
            raise
        
        try:
            opp_file_path = os.path.join(opp_path, 'all_matches.csv')
            self.opp_matches = FileUtils.load_csv_safe(opp_file_path)
            
            if self.opp_matches is not None and len(self.opp_matches) > 0:
                self.opp_matches['match_date'] = pd.to_datetime(self.opp_matches['match_date'])
                info(f"✓ Załadowano {len(self.opp_matches)} meczów przeciwników")
            else:
                warning("Brak danych przeciwników - ograniczona analiza kontekstowa")
                
        except Exception as e:
            warning(f"Nie można załadować danych przeciwników: {str(e)}")
            self.opp_matches = None
        
        info("Zakończono ładowanie danych dla analizy H2H")
        return self.rm_matches, self.opp_matches