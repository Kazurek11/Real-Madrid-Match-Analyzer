"""
Moduł ładowania danych dla analizy zawodników Real Madryt.

Ten moduł odpowiada za wczytywanie, walidację i wstępne przetwarzanie
wszystkich plików danych wymaganych do analizy statystyk zawodników
Real Madryt, włączając mecze, statystyki indywidualne i dane historyczne.
"""

import os
import pandas as pd
import sys

current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from helpers.logger import info, error, debug, warning
from helpers.file_utils import FileUtils

class DataLoader:
    """
    Ładowarka danych dla kompleksowej analizy zawodników Real Madryt.
    
    Odpowiada za wczytywanie, walidację i synchronizację wszystkich źródeł
    danych wymaganych do obliczania statystyk zawodników, form, ocen
    i wydajności w różnych okresach czasowych.
    
    Attributes:
        base_path (str): Ścieżka bazowa do katalogu z danymi
        real_path (str): Ścieżka do katalogu z danymi Real Madryt
        data_cache (dict): Pamięć podręczna wczytanych plików
        
        matches (pd.DataFrame): Statystyki meczowe Real Madryt
        individual (pd.DataFrame): Indywidualne statystyki zawodników
        players (pd.DataFrame): Podstawowe dane zawodników
        players_stats (pd.DataFrame): Zagregowane statystyki zawodników
        old_matches (pd.DataFrame): Historyczne dane meczowe
        all_matches (pd.DataFrame): Wszystkie mecze La Liga
        
        min_date_individual (pd.Timestamp): Najwcześniejsza data w danych indywidualnych
        min_date_matches (pd.Timestamp): Najwcześniejsza data w danych meczowych
        common_min_date (pd.Timestamp): Najwcześniejsza wspólna data obu zbiorów
        common_dates (set): Zbiór dat występujących w obu źródłach
        filtered_matches (pd.DataFrame): Mecze z datami wspólnymi
        filtered_individual (pd.DataFrame): Statystyki indywidualne z datami wspólnymi
        
    Data Sources:
        - RM_all_matches_stats.csv: Kompletne statystyki meczowe RM
        - RM_individual_stats.csv: Indywidualne występy zawodników
        - RM_players.csv: Podstawowe informacje o zawodnikach
        - RM_players_stats.csv: Zagregowane statystyki zawodników
        - RM_old_editor_data.csv: Historyczne dane meczowe
        - all_matches.csv: Kontekst meczów całej La Liga
    """
    
    def __init__(self, base_path=None):
        """
        Inicjalizuje ładowarkę danych dla analizy zawodników.
        
        Args:
            base_path (str, optional): Niestandardowa ścieżka do katalogu danych.
                                     Domyślnie używa Data/ w katalogu głównym projektu.
                        
        Notes:
            - Przygotowuje strukturę katalogów do wczytywania danych
            - Inicjalizuje pustą pamięć podręczną dla optymalizacji
            - Nie wczytuje danych automatycznie - wymaga wywołania load_all_data()
        """
        self.base_path = base_path if base_path else os.path.join(FileUtils.get_project_root(), "Data")
        self.real_path = os.path.join(self.base_path, "Real")
        self.data_cache = {}
        
    def load_csv(self, file_path):
        """
        Wczytuje pojedynczy plik CSV z pamięcią podręczną i obsługą błędów.
        
        Args:
            file_path (str): Pełna ścieżka do pliku CSV do wczytania
            
        Returns:
            pd.DataFrame: Wczytane dane w postaci DataFrame. W przypadku błędu
                         zwraca pusty DataFrame z odpowiednimi logami błędów.
            
        Notes:
            - Wykorzystuje pamięć podręczną dla optymalizacji wielokrotnych wywołań
            - Zawsze zwraca kopię danych aby uniknąć przypadkowych modyfikacji
            - Używa FileUtils.load_csv_safe dla bezpiecznego wczytywania
            - Loguje błędy bez przerywania wykonania programu
            
        Example:
            >>> loader = DataLoader()
            >>> matches_df = loader.load_csv("Data/Real/RM_all_matches_stats.csv")
        """
        if file_path in self.data_cache:
            return self.data_cache[file_path].copy()
            
        try:
            df = FileUtils.load_csv_safe(file_path).copy()
            self.data_cache[file_path] = df
            return df.copy()
        except Exception as e:
            error(f"Nie udało się wczytać pliku {file_path}: {e}")
            return pd.DataFrame()
    
    def load_all_data(self):
        """
        Wczytuje wszystkie wymagane pliki danych dla analizy zawodników.
        
        Returns:
            DataLoader: Referencję do bieżącego obiektu z wczytanymi danymi
            
        Process:
            1. Wczytuje 6 głównych plików CSV z danymi Real Madryt i La Liga
            2. Wykonuje wstępne przetwarzanie danych (daty, wartości null)
            3. Oblicza minimalne daty dla każdego zbioru danych
            4. Synchronizuje daty między zbiorami i tworzy przefiltrowane wersje
            5. Loguje podsumowanie wczytanych danych
            
        Data Files Loaded:
            - matches: Statystyki wszystkich meczów Real Madryt
            - individual: Indywidualne występy każdego zawodnika w każdym meczu
            - players: Podstawowe dane zawodników (ID, imię, pozycja)
            - players_stats: Zagregowane statystyki zawodników
            - old_matches: Historyczne dane meczowe dla kontekstu
            - all_matches: Wszystkie mecze La Liga dla analizy przeciwników
            
        Notes:
            - Automatycznie uruchamia preprocessing i synchronizację dat
            - Tworzy przefiltrowane wersje z tylko wspólnymi datami
            - Obsługuje błędy gracefully - puste DataFrame przy problemach
            - Wszystkie dane dostępne jako atrybuty po zakończeniu
            
        Raises:
            Nie podnosi wyjątków - błędy są logowane i zastępowane pustymi DataFrame
        """
        info("Rozpoczynam wczytywanie wszystkich danych dla analizy zawodników")
        
        self.matches = self.load_csv(os.path.join(self.real_path, "RM_all_matches_stats.csv"))
        self.individual = self.load_csv(os.path.join(self.real_path, "RM_individual_stats.csv"))
        self.players = self.load_csv(os.path.join(self.real_path, "RM_players.csv"))
        self.players_stats = self.load_csv(os.path.join(self.real_path, "RM_players_stats.csv"))
        self.old_matches = self.load_csv(os.path.join(self.real_path, "Old", "RM_old_editor_data.csv"))
        self.all_matches = self.load_csv(os.path.join(self.base_path, "Mecze", "all_season", "merged_matches", "all_matches.csv"))
        
        info(f"Wczytano pliki danych:")
        info(f"  - Mecze RM: {len(self.matches)} wierszy")
        info(f"  - Statystyki indywidualne: {len(self.individual)} wierszy") 
        info(f"  - Zawodnicy: {len(self.players)} wierszy")
        info(f"  - Statystyki zawodników: {len(self.players_stats)} wierszy")
        info(f"  - Historyczne mecze: {len(self.old_matches)} wierszy")
        info(f"  - Wszystkie mecze La Liga: {len(self.all_matches)} wierszy")
        
        self._preprocess_data()
        
        self.min_date_individual = self.individual["match_date"].min() if not self.individual.empty and "match_date" in self.individual.columns else pd.NaT
        self.min_date_matches = self.matches["match_date"].min() if not self.matches.empty and "match_date" in self.matches.columns else pd.NaT
        
        self._find_common_dates()
        
        info("Zakończono wczytywanie i przetwarzanie danych")
        return self
    
    def _find_common_dates(self):
        """
        Synchronizuje daty między zbiorami danych meczowych i indywidualnych.
        
        Process:
            1. Ekstraktuje unikalne daty z obu głównych zbiorów danych
            2. Znajduje przecięcie dat występujących w obu źródłach
            3. Określa najwcześniejszą wspólną datę jako punkt startowy analizy
            4. Tworzy przefiltrowane wersje danych zawierające tylko wspólne daty
            5. Loguje szczegółowe informacje o synchronizacji
            
        Creates:
            - common_dates (set): Zbiór dat w formacie YYYY-MM-DD wspólnych dla obu źródeł
            - common_min_date (pd.Timestamp): Najwcześniejsza data wspólna
            - filtered_matches (pd.DataFrame): Mecze tylko z wspólnymi datami
            - filtered_individual (pd.DataFrame): Statystyki indywidualne z wspólnymi datami
            
        Notes:
            - Kluczowe dla zapewnienia spójności analizy czasowej
            - Eliminuje mecze bez danych o zawodnikach i vice versa
            - Obsługuje przypadki braku wspólnych dat z odpowiednimi ostrzeżeniami
            - Format daty: YYYY-MM-DD dla porównań string-based
            
        Logging:
            - Informuje o liczbie znalezionych wspólnych dat
            - Pokazuje najwcześniejszą wspólną datę
            - Raportuje rozmiary przefiltrowanych zbiorów
            - Ostrzega o problemach z synchronizacją
        """
        try:
            if self.matches.empty or self.individual.empty:
                warning("Jeden z wymaganych zbiorów danych jest pusty - brak synchronizacji dat")
                self.common_min_date = None
                self.common_dates = set()
                self.filtered_matches = pd.DataFrame()
                self.filtered_individual = pd.DataFrame()
                return
                
            matches_dates = set(self.matches["match_date"].dt.strftime("%Y-%m-%d"))
            individual_dates = set(self.individual["match_date"].dt.strftime("%Y-%m-%d"))
            
            self.common_dates = matches_dates.intersection(individual_dates)
            
            if not self.common_dates:
                warning("Nie znaleziono wspólnych dat między zbiorami danych")
                self.common_min_date = None
                self.filtered_matches = pd.DataFrame()
                self.filtered_individual = pd.DataFrame()
                return
                
            self.common_min_date = pd.to_datetime(min(self.common_dates))
            
            self.filtered_matches = self.matches[
                self.matches["match_date"].dt.strftime("%Y-%m-%d").isin(self.common_dates)
            ].copy()
            self.filtered_individual = self.individual[
                self.individual["match_date"].dt.strftime("%Y-%m-%d").isin(self.common_dates)
            ].copy()
            
            info(f"Synchronizacja dat zakończona pomyślnie:")
            info(f"  - Wspólne daty: {len(self.common_dates)}")
            info(f"  - Najwcześniejsza wspólna data: {self.common_min_date}")
            info(f"  - Mecze po filtracji: {len(self.filtered_matches)} wierszy")
            info(f"  - Statystyki indywidualne po filtracji: {len(self.filtered_individual)} wierszy")
            
        except Exception as e:
            error(f"Błąd podczas synchronizacji dat: {str(e)}")
            import traceback
            error(traceback.format_exc())
            self.common_min_date = None
            self.common_dates = set()
            self.filtered_matches = pd.DataFrame()
            self.filtered_individual = pd.DataFrame()
    
    def _preprocess_data(self):
        """
        Wykonuje wstępne przetwarzanie i czyszczenie wczytanych danych.
        
        Process:
            1. Konwertuje kolumny 'match_date' do formatu pandas datetime
            2. Zastępuje wszystkie wartości NaN wartością 0 dla spójności obliczeń
            3. Zapewnia jednolity format danych we wszystkich zbiorach
            
        Applied To:
            - matches: Statystyki meczowe Real Madryt
            - individual: Indywidualne statystyki zawodników  
            - old_matches: Historyczne dane meczowe
            
        Notes:
            - Metoda prywatna wywoływana automatycznie przez load_all_data()
            - Kluczowa dla zapewnienia spójności formatów dat
            - Eliminuje problemy z obliczeniami na wartościach null
            - Modyfikuje dane in-place dla wydajności
            - Pomija zbiory bez kolumny 'match_date'
        """
        info("Rozpoczynam wstępne przetwarzanie danych")
        
        datasets_to_process = [
            ("matches", self.matches),
            ("individual", self.individual), 
            ("old_matches", self.old_matches)
        ]
        
        for name, df in datasets_to_process:
            if df.empty:
                warning(f"Zbiór {name} jest pusty - pomijam przetwarzanie")
                continue
                
            if 'match_date' in df.columns:
                df['match_date'] = pd.to_datetime(df['match_date'])
                debug(f"Skonwertowano daty w zbiorze {name}")
            
            if df.isnull().values.any():
                null_count = df.isnull().sum().sum()
                df.fillna(0, inplace=True)
                debug(f"Zastąpiono {null_count} wartości null w zbiorze {name}")
        
        info("Zakończono wstępne przetwarzanie danych")
    
    def get_data_summary(self):
        """
        Zwraca szczegółowe podsumowanie wczytanych i przetworzonych danych.
        
        Returns:
            dict: Słownik zawierający metryki wszystkich wczytanych zbiorów danych:
                - dataset_sizes: Rozmiary poszczególnych zbiorów
                - date_ranges: Zakresy dat dla zbiorów zawierających daty
                - common_data_info: Informacje o synchronizacji dat
                - data_quality: Metryki jakości danych
        """
        return {
            "dataset_sizes": {
                "matches": len(self.matches) if hasattr(self, 'matches') else 0,
                "individual": len(self.individual) if hasattr(self, 'individual') else 0,
                "players": len(self.players) if hasattr(self, 'players') else 0,
                "players_stats": len(self.players_stats) if hasattr(self, 'players_stats') else 0,
                "old_matches": len(self.old_matches) if hasattr(self, 'old_matches') else 0,
                "all_matches": len(self.all_matches) if hasattr(self, 'all_matches') else 0
            },
            "date_ranges": {
                "matches": (self.min_date_matches, self.matches['match_date'].max()) if hasattr(self, 'matches') and not self.matches.empty else None,
                "individual": (self.min_date_individual, self.individual['match_date'].max()) if hasattr(self, 'individual') and not self.individual.empty else None
            },
            "common_data_info": {
                "common_dates_count": len(self.common_dates) if hasattr(self, 'common_dates') else 0,
                "common_min_date": self.common_min_date if hasattr(self, 'common_min_date') else None,
                "filtered_matches_count": len(self.filtered_matches) if hasattr(self, 'filtered_matches') else 0,
                "filtered_individual_count": len(self.filtered_individual) if hasattr(self, 'filtered_individual') else 0
            }
        }