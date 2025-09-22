"""
Moduł ładowania danych dla analizy przeciwników Real Madryt.

Ten moduł odpowiada za wczytywanie i przygotowanie danych meczowych
wymaganych do obliczania statystyk drużyn przeciwnych w meczach
przeciwko Real Madryt, włączając historyczne wyniki i formy zespołów.
"""

import pandas as pd
import os
from helpers.file_utils import FileUtils
from finall_dataframe.rm_team.analyzer import RealMadridTeamAnalyzer 
from helpers.logger import info, error, debug, warning

class DataLoader:
    """
    Ładowarka danych dla analizy statystyk przeciwników Real Madryt.
    
    Odpowiada za wczytywanie, synchronizację i przygotowanie wszystkich
    źródeł danych wymaganych do obliczania statystyk przeciwników, ich
    form, wydajności i trendów przed meczami z Real Madryt.
    
    Attributes:
        analyzer (RealMadridTeamAnalyzer): Analizator drużynowy Real Madryt używany jako punkt odniesienia
        
    Data Sources:
        - RM_all_matches_stats.csv: Mecze Real Madryt z pełnymi statystykami
        - all_matches.csv: Wszystkie mecze La Liga dla analizy przeciwników
        
    Process Flow:
        1. Wykorzystuje dane Real Madryt jako bazę do analizy
        2. Ładuje dodatkowe dane meczowe przeciwników
        3. Synchronizuje i przygotowuje struktury danych
        4. Dodaje kolumny dla statystyk przeciwników
    """
    
    def __init__(self):
        """
        Inicjalizuje ładowarkę danych dla analizy przeciwników.
        
        Tworzy instancję RealMadridTeamAnalyzer z predefiniowanym ID
        Real Madryt (team_id=1) jako punkt odniesienia dla analizy
        statystyk przeciwników.
        
        Notes:
            - Real Madryt ma standardowe ID=1 w systemie
            - Analizator RM służy jako źródło danych bazowych
            - Przygotowuje infrastrukturę do analizy przeciwników
        """
        self.analyzer = RealMadridTeamAnalyzer(team_id=1)
        info("DataLoader dla analizy przeciwników zainicjalizowany")
        
    def load_base_data(self):
        """
        Wczytuje i przygotowuje bazowe dane Real Madryt dla analizy przeciwników.
        
        Returns:
            tuple: Krotka zawierająca:
                - df (pd.DataFrame): DataFrame z danymi meczów Real Madryt zawierający:
                    * MATCH_ID: Unikalny identyfikator meczu
                    * M_DATE: Data meczu w formacie datetime
                    * OPPONENT_ID: ID drużyny przeciwnika
                    * HOME_AWAY: Czy Real grał u siebie czy na wyjeździe
                    * RESULT: Wynik meczu (W/D/L)
                    * Wszystkie kolumny ze statystykami drużynowymi RM
                    
                - first_date (pd.Timestamp): Najwcześniejsza data meczu w zbiorze,
                                           używana jako punkt startowy analizy
        
        Process:
            1. Uruchamia analizę drużynową Real Madryt
            2. Tworzy kopię DataFrame dla bezpieczeństwa danych
            3. Konwertuje kolumnę M_DATE do formatu datetime jeśli potrzeba
            4. Oblicza najwcześniejszą datę jako punkt referencyjny
            
        Notes:
            - Konwersja dat jest kluczowa dla późniejszych analiz czasowych
            - Pierwsza data służy do filtrowania meczów przeciwników
            - DataFrame zawiera kompletne statystyki drużynowe Real Madryt
            - Dane są przygotowane do rozszerzenia o statystyki przeciwników
            
        Example:
            >>> loader = DataLoader()
            >>> df, first_date = loader.load_base_data()
            >>> print(f"Mecze do analizy: {len(df)}")
            >>> print(f"Okres analizy od: {first_date}")
        """
        info("Rozpoczynam ładowanie bazowych danych Real Madryt")
        
        base_df = self.analyzer.analyze()
        prepared_df = base_df.copy()
        
        if prepared_df["M_DATE"].dtype == 'object':
            prepared_df["M_DATE"] = pd.to_datetime(prepared_df["M_DATE"], format="%Y-%m-%d")
            debug("Skonwertowano kolumnę M_DATE do formatu datetime")
        
        first_date = prepared_df["M_DATE"].min()
        
        info(f"Załadowano bazowe dane: {len(prepared_df)} meczów od {first_date}")
        return prepared_df, first_date
    
    def load_match_data(self):
        """
        Wczytuje kompletne dane meczowe Real Madryt i wszystkich drużyn La Liga.
        
        Returns:
            tuple: Krotka zawierająca:
                - rm_matches (pd.DataFrame): Mecze Real Madryt z kolumnami:
                    * match_id: Identyfikator meczu
                    * match_date: Data meczu
                    * home_team_id: ID drużyny gospodarzy
                    * away_team_id: ID drużyny gości
                    * rm_goals: Bramki Real Madryt
                    * opponent_goals: Bramki przeciwnika
                    * result: Wynik meczu
                    * odds_*: Kursy bukmacherskie
                    
                - opp_matches (pd.DataFrame): Wszystkie mecze La Liga z kolumnami:
                    * match_id: Identyfikator meczu
                    * match_date: Data meczu
                    * home_team_id: ID gospodarzy
                    * away_team_id: ID gości
                    * home_goals: Bramki gospodarzy
                    * away_goals: Bramki gości
                    * season: Sezon rozgrywkowy
        
        Data Sources:
            - Real Madrid: Data/Real/RM_all_matches_stats.csv
            - Wszystkie mecze: Data/Mecze/all_season/merged_matches/all_matches.csv
            
        Notes:
            - Używa FileUtils.load_csv_safe() dla bezpiecznego ładowania
            - Dane Real Madryt zawierają pełne statystyki meczowe
            - Dane przeciwników służą do analizy form i trendów
            - W przypadku błędu ładowania zwraca None dla problematycznego pliku
            - Pliki muszą istnieć w określonych lokalizacjach
            
        Raises:
            FileNotFoundError: Gdy nie można znaleźć wymaganych plików CSV
            
        Example:
            >>> loader = DataLoader()
            >>> rm_data, opp_data = loader.load_match_data()
            >>> print(f"Mecze RM: {len(rm_data)}")
            >>> print(f"Mecze La Liga: {len(opp_data)}")
        """
        info("Rozpoczynam ładowanie danych meczowych")
        
        rm_path = os.path.join(FileUtils.get_project_root(), 'Data', 'Real')
        opp_path = os.path.join(FileUtils.get_project_root(), 'Data', 'Mecze', 'all_season', 'merged_matches')
        
        try:
            rm_file_path = os.path.join(rm_path, 'RM_all_matches_stats.csv')
            rm_matches = FileUtils.load_csv_safe(rm_file_path)
            
            if rm_matches is None or len(rm_matches) == 0:
                error("Nie udało się wczytać danych meczowych Real Madryt")
                rm_matches = pd.DataFrame()
            else:
                info(f"Wczytano {len(rm_matches)} meczów Real Madryt")
                
        except Exception as e:
            error(f"Błąd przy ładowaniu danych Real Madryt: {str(e)}")
            rm_matches = pd.DataFrame()
        
        try:
            opp_file_path = os.path.join(opp_path, 'all_matches.csv')
            opp_matches = FileUtils.load_csv_safe(opp_file_path)
            
            if opp_matches is None or len(opp_matches) == 0:
                warning("Nie udało się wczytać danych przeciwników - ograniczona analiza")
                opp_matches = pd.DataFrame()
            else:
                info(f"✓ Wczytano {len(opp_matches)} meczów przeciwników")
                
        except Exception as e:
            warning(f"Błąd przy ładowaniu danych przeciwników: {str(e)}")
            opp_matches = pd.DataFrame()
        
        info("Zakończono ładowanie danych meczowych")
        return rm_matches, opp_matches
    
    def prepare_columns(self, df, columns_to_add):
        """
        Przygotowuje DataFrame dodając wymagane kolumny dla statystyk przeciwników.
        
        Args:
            df (pd.DataFrame): DataFrame bazowy do rozszerzenia
            columns_to_add (list): Lista nazw kolumn do dodania, np.:
                - OP_PPM_L5: Średnie punkty przeciwnika z ostatnich 5 meczów
                - OP_FORM_L5: Forma przeciwnika z ostatnich 5 meczów
                - OP_GPM_HOME: Średnie bramki przeciwnika u siebie
                - OP_GPM_AWAY: Średnie bramki przeciwnika na wyjeździe
                - OP_PPM_SEA: Średnie punkty przeciwnika w sezonie
                
        Returns:
            pd.DataFrame: DataFrame z dodanymi kolumnami zainicjalizowanymi wartościami pd.NA
            
        Notes:
            - Używa pd.NA jako wartość domyślną (lepsze od np.nan w pandas >= 1.0)
            - Nie nadpisuje istniejących kolumn jeśli już występują
            - Operacja modyfikuje oryginalny DataFrame (in-place)
            - Przygotowuje strukturę do późniejszego wypełnienia statystykami
            - Obsługuje gracefully przypadek pustej listy kolumn
            
        Process:
            1. Iteruje przez listę kolumn do dodania
            2. Sprawdza czy kolumna już istnieje w DataFrame
            3. Dodaje nową kolumnę z wartościami pd.NA jeśli nie istnieje
            4. Loguje liczbę dodanych kolumn
            
        Example:
            >>> loader = DataLoader()
            >>> df = pd.DataFrame({'MATCH_ID': [1, 2, 3]})
            >>> cols = ['OP_PPM_L5', 'OP_FORM_L5']
            >>> df_prepared = loader.prepare_columns(df, cols)
            >>> print(df_prepared.columns.tolist())
            ['MATCH_ID', 'OP_PPM_L5', 'OP_FORM_L5']
        """
        if not columns_to_add:
            debug("Brak kolumn do dodania")
            return df
            
        added_columns = 0
        
        for column in columns_to_add:
            if column not in df.columns:
                df[column] = pd.NA
                added_columns += 1
            else:
                debug(f"Kolumna {column} już istnieje - pomijam")
        
        info(f"Dodano {added_columns} nowych kolumn dla statystyk przeciwników")
        debug(f"Dodane kolumny: {[col for col in columns_to_add if col not in df.columns]}")
        
        return df
    
    def get_data_summary(self):
        """
        Zwraca podsumowanie stanu załadowanych danych.
        
        Returns:
            dict: Słownik z metrykami danych:
                - analyzer_status: Status analizatora Real Madryt
                - data_sources: Informacje o źródłach danych
                - loading_status: Status operacji ładowania
        """
        return {
            "analyzer_status": "initialized" if hasattr(self, 'analyzer') else "not_initialized",
            "data_sources": {
                "rm_data_path": "Data/Real/RM_all_matches_stats.csv",
                "opponents_data_path": "Data/Mecze/all_season/merged_matches/all_matches.csv"
            },
            "loading_capability": "ready"
        }