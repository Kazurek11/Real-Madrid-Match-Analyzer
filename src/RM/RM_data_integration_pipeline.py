"""
RM_data_integration_pipeline.py - Real Madrid Data Integration & Analytics Pipeline

Kompleksowy system przetwarzania i integracji danych dotyczących meczów i zawodników Realu Madryt.
Moduł implementuje zaawansowany pipeline do wczytywania, przetwarzania, dopasowywania i agregowania
danych z różnych źródeł, umożliwiając prowadzenie szczegółowych analiz statystycznych
zarówno na poziomie zespołu, jak i poszczególnych zawodników.

Główne funkcjonalności:
1. Wczytywanie i konsolidacja danych zawodników z wielu plików Excel
2. Wczytywanie i integracja danych meczowych z wielu sezonów
3. Standaryzacja nazw drużyn i harmonizacja formatów danych
4. Dopasowanie rekordów graczy do konkretnych meczów na podstawie dat
5. Przypisanie unikalnych identyfikatorów drużyn i meczów do wszystkich rekordów
6. Agregacja statystyk zawodników do poziomu drużyny dla każdego meczu
7. Generowanie spójnego zbioru danych z zagregowanymi statystykami meczowymi
8. Zapis przetworzonych danych do pliku CSV

Moduł wykorzystuje zaawansowane metody przetwarzania danych z biblioteki pandas
oraz własne narzędzia do standaryzacji i łączenia danych, zapewniając wysoką
jakość oraz spójność wyjściowych zbiorów danych.

"""

import pandas as pd
import numpy as np
import os
import sys
import traceback
from datetime import datetime
from .RM_players_analyzer import RealMadridPlayersAnalyzer

current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from helpers.logger import info, error, debug, warning
from helpers.file_utils import FileUtils
from data_processing.merge_all_season_data import DataMerger
from data_processing.data_processor import DataProcessor
from data_processing.const_variable import *
from data_processing.get_RM_matches import RealMadridMatches


class RM_merge_and_edit:
    """
    Klasa zapewniająca kompleksowy proces integracji i analizy danych graczy oraz meczów Realu Madryt.
    
    Implementuje pełny proces ETL (Extract, Transform, Load) dla danych piłkarskich,
    od wczytania surowych danych z plików źródłowych, przez ich przetworzenie i dopasowanie,
    aż po agregację i eksport końcowego zbioru danych analitycznych.
    
    Atrybuty:
        file_utils (FileUtils): Narzędzia do operacji na plikach i ścieżkach.
        rm_analyzer (RealMadridPlayersAnalyzer): Analizator danych zawodników.
        data_merger (DataMerger): Narzędzie do łączenia danych z wielu sezonów.
        data_processor (DataProcessor): Procesor danych do operacji standaryzujących.
        RM_player_data (pd.DataFrame): Dane zawodników Realu Madryt.
        RM_match_data (pd.DataFrame): Dane meczów Realu Madryt.
        dates_of_madrid_match (list): Lista dat meczów Realu Madryt.
        update_RM_player_data (pd.DataFrame): Przefiltrowane dane zawodników po dopasowaniu.
        coach_data (pd.DataFrame): Oceny ogolne trenera,drużyny przeciwnej i stylu gry RM.
    
    Notes:
        - Klasa jest zaprojektowana z myślą o automatycznym przetwarzaniu danych, minimalizując
          potrzebę ręcznej ingerencji w proces
        - Wszystkie kluczowe operacje są dokładnie logowane za pomocą modułu logger
        - W przypadku wystąpienia błędów na dowolnym etapie, informacje diagnostyczne
          są zapisywane do logów
    """
    def __init__(self):
        """
        Inicjalizuje klasę RM_merge_and_edit i wczytuje wszystkie niezbędne dane źródłowe.
        
        Proces inicjalizacji obejmuje:
        1. Utworzenie instancji klas pomocniczych
        2. Wczytanie i przetworzenie danych zawodników z plików Excel
        3. Wczytanie i przetworzenie danych meczowych z wielu sezonów
        
        Notes:
            - Proces jest wykonywany sekwencyjnie, najpierw wczytywane są dane graczy,
              a następnie dane meczów
            - W przypadku niepowodzenia wczytywania plików, odpowiednie atrybuty
              są inicjalizowane pustymi DataFrame
            - Cały proces jest szczegółowo logowany
        """
        self.file_utils = FileUtils()
        self.rm_analyzer = RealMadridPlayersAnalyzer()
        self.data_merger = DataMerger()
        self.data_processor = DataProcessor(os.path.join(self.file_utils.get_project_root(), "Data"))
        self.coach_data = self.coach_teamstyle_rival_data()
        info("Inicjalizacja: Wczytywanie plików Excel z danymi graczy...")
        if not self.rm_analyzer.load_excel_files():
            error("Nie udało się wczytać plików Excel z danymi graczy!")
            self.RM_player_data = pd.DataFrame()
        else:
            info("Inicjalizacja: Przetwarzanie danych graczy...")
            self.RM_player_data = self.rm_analyzer.merge_and_process_data()
        
        info("Inicjalizacja: Wczytywanie danych sezonów...")
        seasons_loaded = self.data_merger.load_all_seasons()
        
        if not seasons_loaded:
            error("Nie udało się wczytać danych sezonów!")
            self.RM_match_data = pd.DataFrame()
        else:
            info("Inicjalizacja: Wczytywanie danych meczów Realu Madryt...")
            rm_matches = RealMadridMatches(self.data_merger.all_matches)
            self.RM_match_data = rm_matches.get_real_madrid_matches()
        
        self.dates_of_madrid_match = None
        self.update_RM_player_data = None
    def coach_teamstyle_rival_data(self) -> pd.DataFrame:
        """
        Wczytuje, przetwarza i łączy dane dotyczące ocen trenerów i drużyn z plików Excel.
        
        Metoda wczytuje dane z dwóch źródeł - najnowszego pliku Excel z 2025 roku oraz
        archiwalnego pliku z latami 2019-2024. Następnie standaryzuje nazwy kolumn,
        łączy oba zbiory danych, usuwa niepotrzebne kolumny (m.in. dane opisowe i oceny
        sędziów) oraz przetwarza kolumnę z datami na format datetime.
        
        Returns:
            pd.DataFrame: DataFrame zawierający połączone i przetworzone dane o ocenach
                         trenerów i drużyn lub pusty DataFrame w przypadku błędu
        
        Raises:
            Exception: Wyjątek złapany i zalogowany w przypadku problemów z wczytywaniem
                      plików lub przetwarzaniem danych
                      
        Notes:
            - Wykorzystuje FileUtils.load_excel_safe do bezpiecznego wczytywania plików Excel
            - Standaryzuje nazwy kolumn z dwóch różnych formatów źródłowych
            - Usuwa kolumny z ocenami sędziów, średnimi ocenami piłkarzy oraz danymi opisowymi
            - Usuwa wiersze z brakującymi wartościami
            - Konwertuje kolumnę match_date na format datetime
        """
        try:
            info("Wczytywanie danych o trenerach i ocenach drużynowych...")
            
            data_1 = FileUtils.load_excel_safe(
                os.path.join(FileUtils.get_project_root(), "Data", "Excele", "oceny_pilkarzy2_2025.xlsx"), 
                sheet_name="mecze_20250319"
            )
            info(f"Wczytano dane z mecze_20250319, liczba wierszy: {len(data_1) if data_1 is not None else 0}")
            
            data_2 = FileUtils.load_excel_safe(
                os.path.join(FileUtils.get_project_root(), "Data", "Excele", "real_players_match_19-24.xlsx"), 
                sheet_name="mecze20240911"
            )
            info(f"Wczytano dane z mecze20240911, liczba wierszy: {len(data_2) if data_2 is not None else 0}")
            
            if data_1 is None and data_2 is None:
                error("Nie udało się wczytać żadnych danych z plików Excel")
                return pd.DataFrame()
            
            if data_1 is not None:
                info("Przetwarzanie danych z pliku 2025...")
                data_1.rename(columns={
                    'name': 'home_team',
                    'name.1': 'away_team',
                    'editor_madrid_manager_rating': 'RM_coach_rating_EDI',
                    'avg_madrid_manager_rating': 'RM_coach_rating_USR',
                    'editor_madrid_team_rating': 'RM_team_rating_EDI',
                    'avg_madrid_team_rating': 'RM_team_rating_USR',
                    'editor_opposing_team_rating': 'rival_rating_EDI',
                    'avg_opposing_team_rating': 'rival_rating_USR',
                    'editor_referee_rating': 'referee_rating_EDI',
                    'avg_referee_rating': 'referee_rating_USR'
                }, inplace=True)
            
            if data_2 is not None:
                info("Przetwarzanie danych z pliku 2019-2024...")
                data_2.rename(columns={
                    'data': 'match_date',
                    'gospodarz': 'home_team',
                    'gość': 'away_team',
                    'bramki [gosp]': 'home_goals',
                    'bramki [gość]': 'away_goals',
                    'trener [red.]': 'RM_coach_rating_EDI',
                    'trener [userzy]': 'RM_coach_rating_USR',
                    'Real [red.]': 'RM_team_rating_EDI',
                    'Real [userzy]': 'RM_team_rating_USR',
                    'rywal [red.]': 'rival_rating_EDI',
                    'rywal [userzy]': 'rival_rating_USR',
                    'sędzia [red.]': 'referee_rating_EDI',
                    'sędzia [userzy]': 'referee_rating_USR'
                }, inplace=True)
            
            info("Łączenie danych z obu plików...")
            frames = []
            if data_1 is not None:
                frames.append(data_1)
            if data_2 is not None:
                frames.append(data_2)
                
            result = pd.concat(frames)
            info(f"Po połączeniu, liczba wierszy: {len(result)}")
            
            info("Usuwanie niepotrzebnych kolumn...")
            columns_to_drop = [
                'avg_all_players_rating', 'editor_all_players_rating', 'madrid_manager_description',
                'referee_description', 'śr. piłkarzy [red.]', 'śr. piłkarzy [userzy]',
                'trener [opis]', 'sędzia [opis]', 'referee_rating_USR', 'referee_rating_EDI'
            ]
            
            existing_columns = [col for col in columns_to_drop if col in result.columns]
            if existing_columns:
                result.drop(columns=existing_columns, inplace=True)
                info(f"Usunięto kolumny: {existing_columns}")
            
            initial_rows = len(result)
            result.dropna(inplace=True)
            info(f"Usunięto {initial_rows - len(result)} wierszy z brakującymi wartościami")
            
            if 'match_date' in result.columns:
                info("Konwersja kolumny 'match_date' na format datetime...")
                result['match_date'] = pd.to_datetime(result['match_date'], errors='coerce')
                
                if result['match_date'].isna().any():
                    warning(f"Wykryto {result['match_date'].isna().sum()} nieprawidłowych dat")
                    result = result.dropna(subset=['match_date'])
                    info(f"Po usunięciu nieprawidłowych dat pozostało {len(result)} wierszy")
            
            info(f"Zakończono przetwarzanie danych o trenerach i ocenach drużyn. Wynikowy DataFrame zawiera {len(result)} wierszy i {len(result.columns)} kolumn")
            return result
            
        except Exception as e:
            error(f"Błąd podczas wczytywania i przetwarzania danych o trenerach: {str(e)}")
            error(traceback.format_exc())
            return pd.DataFrame()
    def append_team_id(self):
        """
        Dodaje identyfikatory drużyn do danych zawodników.
        
        Metoda wykorzystuje data_processor do przypisania odpowiednich identyfikatorów drużyn
        do wszystkich rekordów zawodników. Identyfikatory te są niezbędne do późniejszego
        łączenia danych z innymi zbiorami oraz do analizy.
        
        Returns:
            None
            
        Notes:
            - Operacja modyfikuje bezpośrednio atrybut RM_player_data
            - Wykorzystywana jest funkcjonalność add_team_ids_to_dataframe z DataProcessor
        """
        self.RM_player_data = self.data_processor.add_team_ids_to_dataframe(self.RM_player_data)
    
    def _get_dates_of_madrid_match(self):
        """
        Pobiera i przetwarza daty meczów Realu Madryt z dataframe RM_match_data.
        
        Metoda zapewnia, że wszystkie daty są prawidłowo sformatowane jako obiekt datetime,
        co jest krytyczne dla poprawnego dopasowania rekordów graczy do meczów.
        
        Returns:
            list: Lista przetworzonych dat meczów Realu Madryt
            
        Notes:
            - Metoda sprawdza czy kolumna match_date istnieje w RM_match_data
            - W razie potrzeby dokonuje konwersji dat do formatu datetime
            - Usuwa rekordy z nieprawidłowymi datami (NaT)
            - Wyniki pośrednie są zapisywane w atrybucie dates_of_madrid_match
            - Wszystkie problemy są szczegółowo logowane
        """
        if "match_date" not in self.RM_match_data.columns:
            error("Kolumna 'match_date' nie istnieje w pliku 'self.RM_match_data'.")
            return []
        
        if not pd.api.types.is_datetime64_any_dtype(self.RM_match_data["match_date"]):
            info("Konwersja kolumny match_date w RM_match_data na format datetime")
            try:
                self.RM_match_data["match_date"] = pd.to_datetime(self.RM_match_data["match_date"], errors='coerce')
                
                if self.RM_match_data["match_date"].isna().any():
                    warning(f"Usunięto {self.RM_match_data['match_date'].isna().sum()} rekordów z nieprawidłowymi datami")
                    self.RM_match_data = self.RM_match_data.dropna(subset=["match_date"])
            except Exception as e:
                error(f"Błąd podczas konwersji dat w RM_match_data: {str(e)}")
                return []
        
        self.dates_of_madrid_match = self.RM_match_data["match_date"].tolist()
        return self.dates_of_madrid_match
            
    def _choose_the_same_event(self):
        """
        Filtruje dane graczy, zachowując tylko rekordy odpowiadające datom meczów Realu Madryt.
        
        Metoda wykonuje kluczowy etap integracji danych - zapewnia, że analizujemy tylko rekordy
        zawodników z dni, w których odbywały się mecze Realu Madryt, eliminując nieistotne dane.
        
        Returns:
            None
            
        Notes:
            - Metoda tworzy kopię danych graczy, aby uniknąć modyfikacji oryginalnego DataFrame
            - Wykonuje standaryzację nazw drużyn w obu zbiorach danych
            - Konwertuje i waliduje daty w obu zbiorach
            - Filtruje dane graczy, pozostawiając tylko rekordy z datami meczów
            - Wyniki są zapisywane w atrybucie update_RM_player_data
            - Szczegółowe informacje o liczbie dopasowanych rekordów są logowane
        """
        if self.RM_player_data is None or self.RM_match_data is None:
            error("Brak danych do przetworzenia")
            return
        
        data = self.RM_player_data.copy()
        
        updated, data = self.data_processor.standardize_team_names(data)
        
        updated, self.RM_match_data = self.data_processor.standardize_team_names(self.RM_match_data.copy())
        
        if "match_date" not in data.columns:
            error("Kolumna 'match_date' nie istnieje w RM_player_data")
            return
        
        if not pd.api.types.is_datetime64_any_dtype(data["match_date"]):
            info("Konwersja kolumny match_date w RM_player_data na format datetime")
            try:
                data["match_date"] = pd.to_datetime(data["match_date"], errors='coerce')
                
                if data["match_date"].isna().any():
                    warning(f"Usunięto {data['match_date'].isna().sum()} rekordów z nieprawidłowymi datami")
                    data = data.dropna(subset=["match_date"])
            except Exception as e:
                error(f"Błąd podczas konwersji dat w RM_player_data: {str(e)}")
                return
        
        match_dates = self._get_dates_of_madrid_match()
        
        filtered_data = data[data["match_date"].isin(match_dates)]
        
        self.update_RM_player_data = filtered_data
        info(f"Wybrano {len(filtered_data)} rekordów pasujących do dat meczów z {len(data)} dostępnych")
        info(f"Zakres dat: {filtered_data['match_date'].min()} - {filtered_data['match_date'].max()}")
        
    def _match_coach_data_by_date(self):
        """
        Dopasowuje dane trenera do odpowiednich meczów Realu Madryt, implementując zaawansowany
        mechanizm dopasowania rekordów na podstawie dat i drużyn z pełną diagnostyką procesu.
        
        Proces dopasowania obejmuje następujące etapy:
        
        1. WALIDACJA WSTĘPNA:
            - Sprawdzenie istnienia i niepustości zbiorów danych trenera i meczów
            - Wczesne przerwanie wykonania przy braku wymaganych danych
        
        2. STANDARYZACJA NAZW DRUŻYN:
            - Ujednolicenie nazw wszystkich drużyn w danych trenera
            - Przekształcenie różnych wariantów zapisu (np. "Real Madryt" → "Real Madrid CF")
            - Zapewnienie spójności nazewnictwa między zbiorami danych
        
        3. DODAWANIE IDENTYFIKATORÓW DRUŻYN:
            - Wzbogacenie danych trenera o identyfikatory liczbowe drużyn
            - Przypisanie każdej drużynie jednoznacznego ID zgodnego z bazą referencyjną
            - Umożliwienie łączenia zbiorów danych na podstawie ID zamiast nazw tekstowych
        
        4. NORMALIZACJA DAT:
            - Konwersja formatów dat w obu zbiorach do wspólnego standardu
            - Usunięcie komponentu czasowego z dat (normalizacja do poziomu dnia)
            - Zapewnienie precyzyjnego dopasowania meczów bez zależności od godziny
        
        5. ANALIZA DIAGNOSTYCZNA ZBIORÓW:
            - Raportowanie dostępnych kolumn w obu zbiorach
            - Porównanie liczby unikalnych dat i ich zakresów
            - Wczesne wykrywanie problemów z zakresami czasowymi danych
        
        6. ŁĄCZENIE DANYCH:
            - Połączenie danych meczów i trenera na podstawie trzech kluczy: daty, gospodarza i gościa
            - Zachowanie wszystkich rekordów meczów (połączenie typu left join)
            - Utworzenie jednolitego zbioru zawierającego ID meczu oraz oceny trenera
        
        7. EKSTRAKCJA KOLUMN:
            - Wybór tylko niezbędnych kolumn związanych z ocenami trenera i drużyn
            - Dynamiczny wybór dostępnych kolumn ocen (EDI/USR dla trenera, drużyny RM i rywala)
            - Utworzenie nowego, uproszczonego DataFrame z najistotniejszymi danymi
        
        8. ANALIZA REZULTATÓW:
            - Obliczenie liczby meczów z poprawnie dopasowanymi danymi trenera
            - Szczegółowa diagnostyka niedopasowanych meczów
            - Identyfikacja potencjalnych dopasowań na podstawie samej daty
            - Ostrzeżenia o niekompletnych dopasowaniach z pełnym raportowaniem
        
        9. AKTUALIZACJA DANYCH:
            - Przypisanie przetworzonych danych trenera do atrybutu klasy
            - Gotowość do dalszego przetwarzania w kolejnych etapach pipeline'u
        
        Returns:
            None: Funkcja modyfikuje atrybut self.coach_data, przypisując mu przefiltrowane
                    i dopasowane dane z ocenami trenera i drużyn.
        
        Raises:
            Wyjątki są przechwytywane wewnętrznie i zapisywane do logów, 
            funkcja nie propaguje błędów dalej.
        
        Dependencies:
            - DataProcessor: Do standaryzacji nazw drużyn i dodawania identyfikatorów
            - pandas: Do operacji na DataFrame i łączenia zbiorów danych
            - logger: Do szczegółowego raportowania każdego kroku procesu
        
        Notes:
            Funkcja stosuje konserwatywne podejście do dopasowania danych, unikając automatycznego
            przypisywania danych w przypadku niejednoznaczności, aby zapobiec przekłamaniom.
            W przypadku niedopasowania, szczegółowa diagnostyka pomaga zidentyfikować problem.
        """
        if self.coach_data is None or self.coach_data.empty or self.RM_match_data is None or self.RM_match_data.empty:
            error("Brak danych trenera lub meczów do dopasowania")
            return
        
        info("Rozpoczęcie dopasowywania danych trenera do meczów Realu Madryt...")
        
        info("Standaryzacja nazw drużyn w danych trenera...")
        updated, standardized_coach_data = self.data_processor.standardize_team_names(self.coach_data)
        if updated:
            self.coach_data = standardized_coach_data
            info("Zaktualizowano nazwy drużyn w danych trenera")
        else:
            info("Nazwy drużyn w danych trenera są już zgodne ze standardem lub brak kolumn do aktualizacji")
        
        info("Dodawanie identyfikatorów drużyn do danych trenera...")
        if "home_team" in self.coach_data.columns and "away_team" in self.coach_data.columns:
            self.coach_data = self.data_processor.add_team_ids_to_dataframe(self.coach_data)
            info("Dodano identyfikatory drużyn do danych trenera")
        else:
            warning("Brak wymaganych kolumn home_team i/lub away_team w danych trenera")
            return
        
        coach_data = self.coach_data.copy()
        match_data = self.RM_match_data.copy()
        
        if self.RM_match_data.index.name == "match_id":
            match_data = match_data.reset_index()
        
        if not pd.api.types.is_datetime64_any_dtype(match_data["match_date"]):
            match_data["match_date"] = pd.to_datetime(match_data["match_date"], errors='coerce')
        
        if not pd.api.types.is_datetime64_any_dtype(coach_data["match_date"]):
            coach_data["match_date"] = pd.to_datetime(coach_data["match_date"], errors='coerce')
        
        match_data["match_date"] = match_data["match_date"].dt.normalize()
        coach_data["match_date"] = coach_data["match_date"].dt.normalize()
        
        info(f"Kolumny w danych meczów: {', '.join(match_data.columns.tolist())}")
        info(f"Kolumny w danych trenera: {', '.join(coach_data.columns.tolist())}")
        
        match_unique_dates = match_data["match_date"].nunique()
        coach_unique_dates = coach_data["match_date"].nunique()
        info(f"Unikalne daty: {match_unique_dates} w meczach, {coach_unique_dates} w danych trenera")
        
        match_date_range = f"{match_data['match_date'].min()} - {match_data['match_date'].max()}"
        coach_date_range = f"{coach_data['match_date'].min()} - {coach_data['match_date'].max()}"
        info(f"Zakres dat meczów: {match_date_range}")
        info(f"Zakres dat trenera: {coach_date_range}")
        
        initial_rows = len(coach_data)
        info(f"Początkowa liczba rekordów danych trenera: {initial_rows}")
        
        merged_data = pd.merge(
            match_data,
            coach_data,
            on=["match_date", "home_team", "away_team"],
            how="left"
        )
        
        coach_columns = [
            "match_id", "RM_coach_rating_EDI", "RM_coach_rating_USR", 
            "RM_team_rating_EDI", "RM_team_rating_USR", 
            "rival_rating_EDI", "rival_rating_USR"
        ]
        
        available_columns = ["match_id"] + [col for col in coach_columns[1:] if col in merged_data.columns]
        
        if len(available_columns) <= 1:
            warning("Brak kolumn z ocenami trenera w danych po dopasowaniu")
            return
        
        filtered_coach_data = merged_data[available_columns].copy()
        
        matched_records = filtered_coach_data.dropna(subset=available_columns[1:], how='all').shape[0]
        match_count = len(match_data)
        
        info(f"Dopasowano dane trenera dla {matched_records} z {match_count} meczów Realu Madryt")
        
        if matched_records < match_count:
            warning(f"Dla {match_count - matched_records} meczów nie znaleziono danych trenera")
            
            missing_mask = filtered_coach_data[available_columns[1:]].isna().all(axis=1)
            missing_matches = filtered_coach_data[missing_mask]
            
            if not missing_matches.empty:
                missing_match_ids = missing_matches["match_id"].tolist()
                match_info = match_data[match_data["match_id"].isin(missing_match_ids)]
                match_info = match_info[["match_id", "match_date", "home_team", "away_team", 
                                        "home_team_id", "away_team_id"]].head(5)
                warning(f"Przykładowe mecze bez danych trenera:\n{match_info}")
                
                missing_dates = match_info["match_date"].tolist()
                potential_matches = coach_data[coach_data["match_date"].isin(missing_dates)]
                
                if not potential_matches.empty:
                    warning(f"Dla informacji: znaleziono {len(potential_matches)} potencjalne dopasowania po samej dacie")
                    warning("Te dane NIE zostały automatycznie przypisane, aby uniknąć przekłamań")
        
        self.coach_data = filtered_coach_data
        info("Zakończono dopasowanie danych trenera do meczów Realu Madryt")
    def _match_by_date(self):
        """
        Przypisuje identyfikatory meczów do rekordów graczy na podstawie zgodności dat.
        
        Ta kluczowa metoda łączy dane graczy z danymi meczów, zapewniając że każdy
        rekord zawodnika zostaje skojarzony z odpowiednim meczem. Mechanizm dopasowania
        opiera się na zgodności dat, z dokładnością do dnia.
        
        Returns:
            None
            
        Notes:
            - Metoda tworzy kopię danych meczowych, aby uniknąć modyfikacji oryginału
            - Normalizuje formaty dat w obu zbiorach danych do wspólnego standardu
            - Wyodrębnia tylko część datową (bez czasu) dla precyzyjnego dopasowania
            - Tworzy mapowanie między datami a identyfikatorami meczów
            - Dla każdej grupy rekordów graczy z tą samą datą przypisuje odpowiedni identyfikator meczu
            - Konwertuje kolumnę match_id na typ liczbowy
            - Szczegółowo raportuje liczbę dopasowanych rekordów i problematycznych przypadków
            - Bezpośrednio modyfikuje atrybut update_RM_player_data
        """
        if self.update_RM_player_data is None or self.RM_match_data is None:
            error("Brak danych do dopasowania")
            return
        
        match_data = self.RM_match_data.copy()
        if self.RM_match_data.index.name == "match_id":
            match_data = match_data.reset_index()
        
        if not pd.api.types.is_datetime64_any_dtype(match_data["match_date"]):
            match_data["match_date"] = pd.to_datetime(match_data["match_date"], errors='coerce')
        
        if not pd.api.types.is_datetime64_any_dtype(self.update_RM_player_data["match_date"]):
            self.update_RM_player_data["match_date"] = pd.to_datetime(self.update_RM_player_data["match_date"], errors='coerce')
        
        match_data["match_date_only"] = match_data["match_date"].dt.date
        self.update_RM_player_data["match_date_only"] = self.update_RM_player_data["match_date"].dt.date
        
        if "match_id" not in self.update_RM_player_data.columns:
            self.update_RM_player_data["match_id"] = None
        
        date_match_mapping = {}
        for _, row in match_data.iterrows():
            date = row["match_date_only"] 
            date_match_mapping[date] = row["match_id"]
        
        player_date_groups = self.update_RM_player_data.groupby("match_date_only")
        
        matches_assigned = 0
        
        for date, group_indices in player_date_groups.groups.items():
            if date in date_match_mapping:
                self.update_RM_player_data.loc[group_indices, "match_id"] = date_match_mapping[date]
                matches_assigned += 1
        
        if "match_id" in self.update_RM_player_data.columns and not self.update_RM_player_data["match_id"].isna().all():
            self.update_RM_player_data["match_id"] = pd.to_numeric(self.update_RM_player_data["match_id"], errors='coerce')
        
        missing_ids = self.update_RM_player_data["match_id"].isna().sum()
        info(f"Przypisano ID dla {matches_assigned} unikalnych dat meczów")
        if missing_ids > 0:
            warning(f"{missing_ids} rekordów pozostało bez przypisanego match_id")
    
    def prepare_match_stats(self):
        """
        Przygotowuje kompleksowy zbiór danych z zagregowanymi statystykami meczowymi i danymi trenerskimi.
        
        Ta metoda stanowi finalny etap przetwarzania danych, agregując statystyki
        poszczególnych zawodników do poziomu całego zespołu dla każdego meczu oraz
        dołączając dane o ocenach trenera i stylu gry drużyny.
        Wynikowy DataFrame zawiera jeden wiersz na mecz z pełnymi statystykami zespołowymi.
        
        Returns:
            pd.DataFrame: DataFrame z zagregowanymi statystykami meczowymi, ocenami trenera 
                         i drużyn, z match_id jako indeksem
            
        Notes:
            - Metoda sprawdza dostępność niezbędnych danych i kolumn przed rozpoczęciem przetwarzania
            - Dynamicznie określa dostępne kolumny do agregacji
            - Dla różnych typów statystyk stosuje odpowiednie funkcje agregujące:
              * Suma dla wartości kumulatywnych (strzały, podania, faule itd.)
              * Średnia dla ocen (editor_rating, user_rating)
              * Maksimum dla czasu trwania meczu
            - Łączy statystyki zespołowe z podstawowymi danymi o meczach
            - Dołącza dane ocen trenera, stylu gry i ocen drużyny przeciwnej
            - Oblicza dodatkowe wskaźniki, np. liczbę ocenionych zawodników
            - Zaokrągla wartości numeryczne dla lepszej czytelności
            - Sortuje wyniki według dat meczów (od najnowszych)
            - Szczegółowo raportuje liczbę przetworzonych meczów i kolumn
        """
        if self.update_RM_player_data is None or self.update_RM_player_data.empty:
            error("Brak danych graczy do przetworzenia")
            return None
            
        if "match_id" not in self.update_RM_player_data.columns:
            error("Brak kolumny match_id w danych graczy")
            return None
        
        info("Agregowanie statystyk drużynowych z danych graczy...")
        
        sum_columns = ["total_shots", "shots_on_target", "key_passes", "fouls", "fouled", "goals", "assists"]
        mean_columns = ["editor_rating", "user_rating"]
        
        available_sum_columns = [col for col in sum_columns if col in self.update_RM_player_data.columns]
        available_mean_columns = [col for col in mean_columns if col in self.update_RM_player_data.columns]
        
        agg_dict = {}
        for col in available_sum_columns:
            agg_dict[col] = 'sum'
        for col in available_mean_columns:
            agg_dict[col] = 'mean'
        
        if "player_min" in self.update_RM_player_data.columns:
            agg_dict["player_min"] = 'max'
        
        match_stats = self.update_RM_player_data.groupby("match_id").agg(agg_dict)
        
        if "player_min" in match_stats.columns:
            match_stats.rename(columns={"player_min": "match_duration [min]"}, inplace=True)
        
        info("Łączenie z danymi meczów...")
        
        match_data = self.RM_match_data.copy()
        if self.RM_match_data.index.name == "match_id":
            match_data = match_data.reset_index()
        
        match_columns = [
            "match_id", "round", "match_date", "home_team_id", "away_team_id", 
            "home_team", "away_team", "score", "result", "home_goals", "away_goals", 
            "home_odds", "draw_odds", "away_odds", "home_position", "away_position", 
            "season", "is_home", "real_result", "home_odds_fair", "draw_odds_fair", 
            "away_odds_fair", "PPM_H", "PPM_A"
        ]
        
        match_columns = [col for col in match_columns if col in match_data.columns]
        
        final_data = pd.merge(match_data[match_columns], match_stats, 
                             left_on="match_id", right_index=True, how="left")
        
        try:
            debug_info = self.update_RM_player_data["is_value"].value_counts()
            info(f"Wartości w kolumnie is_value: {debug_info}")
            
            self.update_RM_player_data["is_value_numeric"] = pd.to_numeric(
                self.update_RM_player_data["is_value"], 
                errors='coerce'
            )
            
            rated_players = self.update_RM_player_data[
                self.update_RM_player_data["is_value_numeric"] == 1
            ]
            is_value_count = rated_players.groupby("match_id").size()
            info(f"Zliczono oceny dla {len(is_value_count)} meczów")
            
            match_id_to_count = is_value_count.to_dict()
            final_data["player_rated_count"] = final_data["match_id"].map(match_id_to_count)
            
            if final_data["player_rated_count"].isna().any():
                missing_count = final_data["player_rated_count"].isna().sum()
                info(f"Brak danych o liczbie ocenionych graczy dla {missing_count} meczów - uzupełniam zerami")
                final_data["player_rated_count"] = final_data["player_rated_count"].fillna(0).astype(int)
        except Exception as e:
            error(f"Błąd podczas liczenia ocenionych graczy: {str(e)}")
            final_data["player_rated_count"] = 0
        
        if "is_value" in final_data.columns:
            final_data.drop(columns=["is_value"], inplace=True)
        
        if hasattr(self, 'coach_data') and not self.coach_data.empty and "match_id" in self.coach_data.columns:
            info("Dołączanie danych trenera i ocen zespołów...")
            
            coach_columns = [
                "RM_coach_rating_EDI", "RM_coach_rating_USR", 
                "RM_team_rating_EDI", "RM_team_rating_USR", 
                "rival_rating_EDI", "rival_rating_USR"
            ]
            
            available_columns = [col for col in coach_columns if col in self.coach_data.columns]
            
            if available_columns:
                self.coach_data["match_id"] = pd.to_numeric(self.coach_data["match_id"], errors='coerce')
                
                coach_duplicates = self.coach_data.duplicated(subset=["match_id"], keep=False)
                if coach_duplicates.any():
                    dup_count = coach_duplicates.sum()
                    info(f"Wykryto {dup_count} rekordów z duplikującymi się match_id w danych trenera")
                    
                    coach_data_agg = self.coach_data.groupby("match_id")[available_columns].mean().reset_index()
                    coach_data_for_merge = coach_data_agg
                else:
                    coach_data_for_merge = self.coach_data[["match_id"] + available_columns].copy()
                
                final_data = pd.merge(
                    final_data, 
                    coach_data_for_merge,
                    on="match_id",
                    how="left",
                    validate="1:1"
                )
                
                info(f"Dołączono {len(available_columns)} kolumn z danymi trenera i ocen zespołów")
                missing_coach_records = final_data[available_columns[0]].isna().sum() if available_columns else 0
                
                if missing_coach_records > 0:
                    warning(f"Dla {missing_coach_records} meczów brak danych trenera/zespołu")
                else:
                    info("Wszystkie mecze mają przypisane dane trenera i zespołu")
        
        
        final_data = self.data_processor.round_numeric_columns(final_data, decimals=3)
        final_data.sort_values(by="match_date", ascending=False, inplace=True)
        
        info(f"Przygotowano kompleksowy DataFrame z {len(final_data)} meczami i {len(final_data.columns)} kolumnami")
        
        return final_data
    
    def get_players_data(self):
        """
        Zwraca DataFrame z podstawowymi danymi graczy, w tym ID graczy i ich nazwiska.
        
        Metoda ekstrahuje unikalną listę graczy z przetworzonych danych,
        zapewniając mapowanie między nazwiskami a identyfikatorami.
        
        Returns:
            pd.DataFrame: DataFrame zawierający kolumny 'player_id' i 'player_name'
                         lub None w przypadku braku danych.
        """
        if not hasattr(self, 'merged_data') or self.merged_data is None or self.merged_data.empty:
            warning("Brak dostępnych danych graczy")
            return None
            
        try:
            player_names = self.merged_data["player_name"].unique()
            player_ids = range(1, len(player_names) + 1)
            
            players_df = pd.DataFrame({
                "player_id": player_ids,
                "player_name": player_names
            })
            
            info(f"Wygenerowano dane dla {len(players_df)} graczy")
            return players_df
        except Exception as e:
            error(f"Błąd podczas generowania danych graczy: {str(e)}")
            return None
        
    @staticmethod
    def save_individual_players_data(processor, output_path=None):
        """
        Zapisuje dane indywidualnych graczy do pliku CSV z określoną kolejnością kolumn,
        uzupełniając brakujące identyfikatory wszystkich drużyn na podstawie danych z pliku rywale.csv.
        
        Args:
            processor (RM_merge_and_edit): Instancja klasy procesora danych z przetworzonymi danymi graczy
            output_path (str, optional): Ścieżka docelowa pliku. Jeśli nie podano, używa domyślnej lokalizacji
        
        Returns:
            bool: True jeśli zapis zakończył się sukcesem, False w przeciwnym wypadku
        """
        try:
            info("Zapisywanie danych indywidualnych graczy z przypisanymi meczami...")
            
            if processor.update_RM_player_data is None or processor.update_RM_player_data.empty:
                warning("Brak danych indywidualnych graczy do zapisania")
                return False
                
            if "player_id" not in processor.update_RM_player_data.columns:
                info("Brak kolumny player_id w danych graczy")
                try:
                    name_mapping = {}
                    players_data = processor.rm_analyzer.get_players_data()
                    if players_data is not None and 'player_name' in players_data and 'player_id' in players_data:
                        name_mapping = dict(zip(players_data['player_name'], players_data['player_id']))
                    
                    processor.update_RM_player_data["player_id"] = processor.update_RM_player_data["player_name"].map(name_mapping)
                except Exception as e:
                    warning(f"Nie można przypisać identyfikatorów graczy: {str(e)}")
            
            if output_path is None:
                players_output_file = os.path.join(FileUtils.get_project_root(), "Data", "Real", "RM_individual_stats.csv")
            else:
                players_output_file = output_path
                    
            total_players = len(processor.update_RM_player_data)
            players_with_match_id = processor.update_RM_player_data["match_id"].notna().sum()
            players_without_match_id = processor.update_RM_player_data["match_id"].isna().sum()
            
            info(f"Przygotowywanie do zapisu danych {total_players} graczy:")
            info(f"  - {players_with_match_id} graczy z przypisanym ID meczu")
            if players_without_match_id > 0:
                warning(f"  - {players_without_match_id} graczy bez przypisanego ID meczu")
            
            player_data = processor.update_RM_player_data.copy()
            
            teams_mapping_path = os.path.join(FileUtils.get_project_root(), "Data", "Mecze", "id_nazwa", "rywale.csv")
            teams_mapping = None
            
            try:
                teams_mapping = pd.read_csv(teams_mapping_path)
                info(f"Wczytano mapowanie drużyn z {teams_mapping_path}: {len(teams_mapping)} drużyn")
                
                name_to_id = dict(zip(teams_mapping['team_name'], teams_mapping['team_id']))
                
                info(f"Utworzono mapowanie dla {len(name_to_id)} drużyn")
            except Exception as e:
                warning(f"Nie można wczytać mapowania drużyn: {str(e)}")
                teams_mapping = None
            
            if teams_mapping is not None:
                home_missing_mask = (
                    player_data["home_team_id"].isna() | 
                    (player_data["home_team_id"] == "") | 
                    (player_data["home_team_id"] == 0)
                )
                
                if home_missing_mask.any():
                    for team_name, team_id in name_to_id.items():
                        team_rows = home_missing_mask & (player_data["home_team"] == team_name)
                        if team_rows.any():
                            player_data.loc[team_rows, "home_team_id"] = team_id
                            info(f"Uzupełniono home_team_id={team_id} dla '{team_name}': {team_rows.sum()} rekordów")
                    
                    still_missing = player_data["home_team_id"].isna().sum()
                    if still_missing > 0:
                        warning(f"Nie udało się uzupełnić home_team_id dla {still_missing} rekordów")
                        missing_teams = player_data.loc[player_data["home_team_id"].isna(), "home_team"].unique()
                        warning(f"Drużyny bez mapowania: {', '.join(str(t) for t in missing_teams)}")
                
                away_missing_mask = (
                    player_data["away_team_id"].isna() | 
                    (player_data["away_team_id"] == "") | 
                    (player_data["away_team_id"] == 0)
                )
                
                if away_missing_mask.any():
                    for team_name, team_id in name_to_id.items():
                        team_rows = away_missing_mask & (player_data["away_team"] == team_name) 
                        if team_rows.any():
                            player_data.loc[team_rows, "away_team_id"] = team_id
                            info(f"Uzupełniono away_team_id={team_id} dla '{team_name}': {team_rows.sum()} rekordów")
                    
                    still_missing = player_data["away_team_id"].isna().sum()
                    if still_missing > 0:
                        warning(f"Nie udało się uzupełnić away_team_id dla {still_missing} rekordów")
                        missing_teams = player_data.loc[player_data["away_team_id"].isna(), "away_team"].unique()
                        warning(f"Drużyny bez mapowania: {', '.join(str(t) for t in missing_teams)}")
            
            sorted_player_data = player_data.sort_values(
                by=["match_date", "match_id", "is_first_squad", "player_min"], 
                ascending=[True, True, False, False]
            )
            
            all_columns = sorted_player_data.columns.tolist()
            ordered_columns = []
            
            priority_columns = ["match_id", "match_date", "home_team_id", "away_team_id"]
            for col in priority_columns:
                if col in all_columns:
                    ordered_columns.append(col)
                    all_columns.remove(col)
            
            ordered_columns.extend(all_columns)
            
            reordered_data = sorted_player_data[ordered_columns]
            reordered_data.sort_values("match_date", ascending=True, inplace=True)
            
            success = FileUtils.save_csv_safe(df=reordered_data, file_path=players_output_file, index=False)
            
            if success:
                info(f"Zapisano dane indywidualne graczy do pliku: {players_output_file}")
                info(f"Liczba zapisanych rekordów graczy: {total_players}")
                info(f"Liczba kolumn: {len(reordered_data.columns)}")
                info(f"Zakres dat zapisanych danych: {reordered_data['match_date'].min()} - {reordered_data['match_date'].max()}")
                info(f"Pierwszych 6 kolumn w pliku: {', '.join(ordered_columns[:6])}")
                return True
            else:
                error(f"Nie udało się zapisać danych graczy do pliku: {players_output_file}")
                return False
                
        except Exception as e:
            error(f"Wystąpił błąd podczas zapisywania danych indywidualnych graczy: {str(e)}")
            error(traceback.format_exc())
            return False
def main():
    """
    Funkcja główna realizująca pełen cykl przetwarzania danych dla Realu Madryt.
    
    Funkcja koordynuje sekwencyjne wykonanie wszystkich etapów przetwarzania danych:
    od wczytania źródłowych plików, przez przetwarzanie i dopasowywanie danych,
    aż po finalne generowanie i zapis zagregowanych statystyk meczowych.
    
    Notes:
        - Funkcja implementuje pełną obsługę wyjątków, aby zapewnić stabilne działanie
        - Wszystkie krytyczne etapy są szczegółowo logowane
        - Mierzy i raportuje całkowity czas wykonania operacji
        - W przypadku wystąpienia błędów na dowolnym etapie, szczegółowe informacje
          diagnostyczne są zapisywane do logów
    """
    try:
        info("===== ROZPOCZĘCIE PRZETWARZANIA DANYCH REALU MADRYT =====")
        start_time = datetime.now()
        
        processor = RM_merge_and_edit()
        
        if processor.RM_player_data.empty:
            error("Nie udało się wczytać danych graczy. Sprawdź pliki Excel.")
            return
        
        if processor.RM_match_data is None or processor.RM_match_data.empty:
            error("Nie udało się wczytać danych meczów. Sprawdź pliki sezonów.")
            return
        
        info(f"Wczytano dane graczy: {len(processor.RM_player_data)} rekordów")
        info(f"Wczytano dane meczów: {len(processor.RM_match_data)} rekordów")
        
        info("Krok 1: Dodawanie identyfikatorów drużyn do danych graczy...")
        processor.append_team_id()
        
        info("Krok 2: Wybieranie rekordów graczy z pasującymi datami meczów...")
        processor._choose_the_same_event()
        
        info("Krok 3: Przypisywanie identyfikatorów meczów do danych graczy...")
        processor._match_by_date()
        
        info("Krok 4: Przypisywanie identyfikatorów meczów do danych trenera...")
        processor._match_coach_data_by_date()
        
        info("Krok 5: Przygotowanie zagregowanych statystyk meczowych...")
        match_stats = processor.prepare_match_stats()
        
        if match_stats is None or match_stats.empty:
            error("Nie udało się wygenerować statystyk meczowych!")
            return
            
        output_file = os.path.join(FileUtils.get_project_root(), "Data", "Real", "RM_all_matches_stats.csv")
        FileUtils.save_csv_safe(df=match_stats, file_path=output_file, index=False, 
                              sort_by="match_date", ascending=True)    
        info(f"Zapisano statystyki meczowe do pliku: {output_file}")
        info(f"Liczba zapisanych meczów: {len(match_stats)}")
        info(f"Liczba kolumn: {len(match_stats.columns)}")
        
        info("Krok 6: Zapisywanie danych indywidualnych graczy z przypisanymi meczami...")
        RM_merge_and_edit.save_individual_players_data(processor)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        info(f"===== ZAKOŃCZONO PRZETWARZANIE DANYCH (czas: {execution_time:.2f} s) =====")
        
    except Exception as e:
        error(f"Wystąpił błąd podczas przetwarzania danych: {str(e)}")
        error(traceback.format_exc())
if __name__ == "__main__":
    main()