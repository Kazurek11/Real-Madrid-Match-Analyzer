"""
Moduł do przetwarzania i analizy historycznych danych piłkarzy Realu Madryt.

Ten moduł umożliwia wczytanie, przefiltrowanie, przetworzenie i zapisanie historycznych
danych statystycznych piłkarzy Realu Madryt z różnych sezonów. Służy jako kluczowy
komponent w procesie przygotowania danych treningowych do modeli analitycznych
i predykcyjnych.

Główne funkcje modułu:
1. Wczytanie historycznych danych piłkarzy z plików Excel
2. Filtrowanie danych według dat granicznych (pełne dane vs dane z ocenami edytora)
3. Przygotowanie i czyszczenie zestawów danych
4. Mapowanie i standaryzacja nazw drużyn zgodnie ze słownikiem mapowań
5. Dodawanie identyfikatorów drużyn na podstawie ich nazw
6. Filtrowanie drużyn nieobecnych w pliku mapowania ID
7. Zapisanie przetworzonych danych w ustrukturyzowanym formacie CSV

Zastosowanie:
Dane wyjściowe tego modułu są wykorzystywane do:
- Wyciągnięcia średnich statystyk historycznych piłkarzy
- Określenia form zawodników przed określonymi meczami
- Analizy trendów wydajności zawodników w czasie
- Trenowania modeli prognostycznych dla przyszłych występów
- Uzupełniania brakujących danych w aktualnych zestawach danych

Moduł zapisuje dwa kluczowe pliki:
- 'RM_old_complete_data.csv': Pełne dane od określonej daty kompletności z mapowaniem ID drużyn
- 'RM_old_editor_data.csv': Dane z ocenami edytora, potencjalnie z szerszego zakresu dat, z mapowaniem ID drużyn

Przykłady użycia:
    # Podstawowe użycie z domyślnymi parametrami
    processor = RM_old_Data()
    processor.process_and_save_data()
    
    # Użycie z niestandardowymi datami granicznymi
    processor = RM_old_Data(
        date="2021-01-01", 
        complete_data_date="2020-06-01"
    )
    processor.process_and_save_data("ścieżka/do/katalogu/wyjściowego")
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
from data_processing.const_variable import SEASON_DATES
class RM_old_Data:
    """
    Klasa do przetwarzania historycznych danych piłkarzy Realu Madryt.
    
    Ta klasa umożliwia wczytanie, przetworzenie i zapisanie danych historycznych
    z dwóch różnych zakresów dat w celu utworzenia bazy dla analizy wcześniejszych
    występów zawodników. Dane te są kluczowe dla analizy form piłkarzy, trendów
    wydajności i jako czynniki predykcyjne w modelach statystycznych.
    
    Główne zadania klasy:
    - Wczytanie danych historycznych z plików Excel
    - Filtrowanie według dat granicznych i wartości ocen edytora
    - Przetwarzanie danych z zachowaniem ich integralności
    - Standaryzacja nazw drużyn i dodawanie identyfikatorów drużyn
    - Filtrowanie drużyn nieobecnych w pliku mapowania ID
    - Zapisywanie zestawów danych w ustrukturyzowanym formacie CSV
    
    Atrybuty:
        date (datetime): Data graniczna - pierwszy mecz do analizy w projekcie
        complete_data_date (datetime): Data od której wszystkie dane są kompletne 
        rm_analyzer (RealMadridPlayersAnalyzer): Obiekt analizatora danych piłkarzy
        data_processor (DataProcessor): Procesor do standaryzacji nazw drużyn i dodawania ID
        df_history (pd.DataFrame): Wczytane dane historyczne
        complete_df (pd.DataFrame): Przefiltrowane dane kompletne
        editor_df (pd.DataFrame): Dane z oceną edytora
        
    Notes:
        - Obiekt wymaga dostępu do plików Excel z danymi historycznymi
        - Działanie opiera się na klasie RealMadridPlayersAnalyzer do wczytywania danych
        - Do standaryzacji nazw drużyn i dodawania ID wykorzystuje klasę DataProcessor
        - Proces przetwarzania tworzy dwa osobne pliki CSV o różnej zawartości
        - Do prawidłowego działania wymaga poprawnej struktury katalogów projektu
    """
    
    def __init__(self, date=None, complete_data_date=None):
        """
        Inicjalizacja klasy przetwarzającej historyczne dane Realu Madryt.
        
        Args:
            date (str lub datetime, optional): Data graniczna do analizy.
                Domyślnie używa pierwszej daty z SEASON_DATES.
            complete_data_date (str lub datetime, optional): Data od której dane są 
                kompletne. Domyślnie "2020-01-04".
        """
        self.date = pd.to_datetime(date) if date else pd.to_datetime(SEASON_DATES[0][1])
        self.complete_data_date = pd.to_datetime(complete_data_date) if complete_data_date else pd.to_datetime("2020-01-04")
        
        self.rm_analyzer = None
        self.data_processor = None
        self.df_history = None
        self.complete_df = None
        self.editor_df = None
        
        info(f"Zainicjowano obiekt RM_old_Data z datą graniczną: {self.date}")
        info(f"Data kompletnych danych: {self.complete_data_date}")
    
    def initialize_analyzer(self):
        """
        Inicjalizuje analizator danych piłkarzy Realu Madryt.
        
        Tworzy instancję klasy RealMadridPlayersAnalyzer, która jest niezbędna
        do wczytywania i wstępnego przetwarzania danych z plików Excel. Metoda
        obsługuje wszelkie wyjątki, które mogą wystąpić podczas inicjalizacji.
        
        Args:
            Brak
            
        Returns:
            bool: True jeśli inicjalizacja się powiodła, False w przeciwnym razie
            
        Notes:
            - Metoda jest wywoływana automatycznie przez load_data() jeśli analizator nie istnieje
            - W przypadku błędu szczegółowe informacje są zapisywane w logach
            - Sukces jest wymagany do dalszego przetwarzania danych
        """
        try:
            self.rm_analyzer = RealMadridPlayersAnalyzer()
            if self.rm_analyzer is None:
                error("Nie udało się utworzyć instancji RealMadridPlayersAnalyzer")
                return False
            info("Poprawnie zainicjalizowano analizator danych")
            return True
        except Exception as e:
            error(f"Wystąpił błąd podczas inicjalizacji analizatora: {str(e)}")
            error(traceback.format_exc())
            return False

    def initialize_data_processor(self):
        """
        Inicjalizuje procesor danych do standaryzacji nazw drużyn i dodawania ID.
        
        Tworzy instancję klasy DataProcessor, która jest używana do normalizacji nazw drużyn
        i dodawania identyfikatorów drużyn na podstawie ich nazw. Metoda obsługuje 
        wszelkie wyjątki, które mogą wystąpić podczas inicjalizacji.
        
        Args:
            Brak
            
        Returns:
            bool: True jeśli inicjalizacja się powiodła, False w przeciwnym razie
            
        Notes:
            - Metoda jest wywoływana automatycznie przez process_team_names_and_ids() 
              jeśli procesor nie istnieje
            - W przypadku błędu szczegółowe informacje są zapisywane w logach
            - Wczytuje szablon mapowania ID drużyn dla późniejszego użycia
        """
        try:
            file_utils = FileUtils()
            project_root = file_utils.get_project_root()
            self.data_processor = DataProcessor(project_root)
            
            if not self.data_processor.load_team_id_template():
                warning("Nie można załadować szablonu ID drużyn. Mapowanie ID może być niekompletne.")
            
            info("Poprawnie zainicjalizowano procesor danych")
            return True
        except Exception as e:
            error(f"Wystąpił błąd podczas inicjalizacji procesora danych: {str(e)}")
            error(traceback.format_exc())
            return False
    
    def load_data(self):
        """
        Wczytuje dane historyczne z plików Excel za pomocą analizatora.
        """
        if not self.rm_analyzer:
            if not self.initialize_analyzer():
                return False
        
        try:
            if hasattr(self.rm_analyzer, 'df_2019v2024') and not self.rm_analyzer.df_2019v2024.empty:
                self.df_history = self.rm_analyzer.df_2019v2024.copy()
                info(f"Dane zostały już wczytane, liczba wierszy: {len(self.df_history)}")
            else:
                success = self.rm_analyzer.load_excel_files()
                if success and hasattr(self.rm_analyzer, 'df_2019v2024') and not self.rm_analyzer.df_2019v2024.empty:
                    self.df_history = self.rm_analyzer.df_2019v2024.copy()
                    info(f"Dane zostały wczytane, liczba wierszy: {len(self.df_history)}")
                else:
                    error("Nie udało się wczytać danych z lat 2019-2024")
                    return False
            
            self.df_history["match_date"] = pd.to_datetime(self.df_history["match_date"], errors='coerce')
            
            before_filter = len(self.df_history)
            
            self.df_history = self.df_history[self.df_history["match_date"] < self.date]
            info(f"Po filtrowaniu według daty pozostało {len(self.df_history)} z {before_filter} wierszy")
            
            ratings_count = self.df_history["editor_rating"].notna().sum()
            info(f"Liczba wierszy z oceną edytora: {ratings_count} ({ratings_count/len(self.df_history)*100:.1f}% danych)")
            
            if ratings_count == 0:
                warning("Brak ocen edytora po filtrowaniu według daty. Pomijam filtrowanie według ocen edytora.")
            else:
                before_rating_filter = len(self.df_history)
                self.df_history = self.df_history[self.df_history["editor_rating"].notna()]
                info(f"Po filtrowaniu według ocen edytora pozostało {len(self.df_history)} z {before_rating_filter} wierszy")
            
            return True
        except Exception as e:
            error(f"Wystąpił błąd podczas wczytywania danych: {str(e)}")
            error(traceback.format_exc())
            return False
    
    def process_team_names_and_ids(self, df):
        """
        Przetwarza nazwy drużyn i dodaje ich identyfikatory do DataFrame.
        
        Wykorzystuje DataProcessor do standaryzacji nazw drużyn zgodnie z ustalonym 
        słownikiem mapowań oraz do dodania identyfikatorów drużyn na podstawie ich nazw.
        Dodatkowo usuwa wiersze z drużynami, które nie są wymienione w pliku mapowania.
        
        Args:
            df (pd.DataFrame): DataFrame do przetworzenia
            
        Returns:
            pd.DataFrame: Przetworzony DataFrame z ustandaryzowanymi nazwami drużyn
                         i dodanymi identyfikatorami lub oryginalny DataFrame w przypadku błędu
                         
        Notes:
            - Inicjalizuje DataProcessor, jeśli nie istnieje
            - Wykonuje standaryzację nazw drużyn dla kolumn zawierających nazwy drużyn
            - Usuwa wiersze z drużynami nieobecnymi w pliku mapowania ID
            - Dodaje identyfikatory drużyn na podstawie ich nazw
            - Nie modyfikuje oryginalnego DataFrame w przypadku błędu
            - Loguje informacje o procesie i ewentualnych błędach
        """
        if df is None or df.empty:
            warning("Brak danych do przetworzenia nazw drużyn i ID")
            return df
            
        if not self.data_processor:
            if not self.initialize_data_processor():
                warning("Nie można zainicjalizować procesora danych. Nazwy drużyn i ID nie będą przetworzone.")
                return df
                
        try:
            info("Standaryzacja nazw drużyn...")
            updated, standardized_df = self.data_processor.standardize_team_names(data=df)
            
            if not updated or standardized_df is None:
                info("Brak zmian w nazwach drużyn lub błąd podczas standaryzacji.")
                standardized_df = df.copy()
            
            if not hasattr(self.data_processor, 'name_to_id') or not self.data_processor.name_to_id:
                if not self.data_processor.load_team_id_template():
                    warning("Nie można załadować szablonu ID drużyn. Filtrowanie drużyn może być niemożliwe.")
                    return standardized_df
            
            team_columns = ["team_name", "opponent_name", "home_team", "away_team"]
            filter_columns = [col for col in team_columns if col in standardized_df.columns]
            
            if filter_columns:
                valid_teams = set(self.data_processor.name_to_id.keys())
                
                rows_before = len(standardized_df)
                
                filtered_df = standardized_df.copy()
                
                for col in filter_columns:
                    mask = filtered_df[col].isin(valid_teams)
                    filtered_df = filtered_df[mask]
                    if len(filtered_df) < rows_before:
                        info(f"Usunięto {rows_before - len(filtered_df)} wierszy z drużynami nieobecnymi w pliku mapowania ID dla kolumny {col}")
                        rows_before = len(filtered_df)
                
                if filtered_df.empty:
                    warning("Po filtrowaniu drużyn nie pozostały żadne wiersze. Sprawdź mapowanie drużyn.")
                    return standardized_df
                
                standardized_df = filtered_df
            else:
                info("Brak kolumn z nazwami drużyn do filtrowania.")
            
            info("Dodawanie identyfikatorów drużyn...")
            team_columns = ["team_name", "opponent_name", "home_team", "away_team"]
            has_team_columns = any(col in standardized_df.columns for col in team_columns)
            
            if has_team_columns:
                result_df = self.data_processor.add_team_ids_to_dataframe(standardized_df)
                if result_df is not None:
                    info("Dodano identyfikatory drużyn do DataFrame")
                    return result_df
                else:
                    warning("Nie udało się dodać identyfikatorów drużyn")
            else:
                info("W DataFrame brak kolumn z nazwami drużyn do mapowania ID")
            
            return standardized_df
            
        except Exception as e:
            error(f"Wystąpił błąd podczas przetwarzania nazw drużyn i ID: {str(e)}")
            error(traceback.format_exc())
            return df
    
    def filter_data_by_date(self, df, date):
        """
        Filtruje DataFrame według daty.
        
        Tworzy kopię DataFrame zawierającą tylko wiersze, których data
        meczu jest większa lub równa podanej dacie granicznej. Jest to
        metoda pomocnicza wykorzystywana przez inne funkcje klasy.
        
        Args:
            df (pd.DataFrame): DataFrame do filtrowania
            date (datetime): Data graniczna do filtrowania (>= date)
            
        Returns:
            pd.DataFrame: Przefiltrowany DataFrame zawierający tylko mecze od podanej daty
            
        Notes:
            - Funkcja zachowuje się bezpiecznie, zwracając pusty DataFrame dla pustych danych wejściowych
            - Tworzy kopię danych wejściowych, aby uniknąć modyfikacji oryginalnego DataFrame
            - Zakłada istnienie kolumny 'match_date' w formacie datetime
            - Loguje informacje o liczbie wierszy po filtrowaniu dla celów diagnostycznych
        """
        if df is None or df.empty:
            warning("Brak danych do filtrowania")
            return pd.DataFrame()
        
        filtered_df = df[df["match_date"] >= date].copy()
        info(f"Po filtrowaniu według daty {date} pozostało {len(filtered_df)} wierszy")
        return filtered_df
    
    def prepare_complete_data(self):
        """
        Przygotowuje zestaw danych z okresu, gdy wszystkie kolumny są kompletne.
        
        Filtruje dane historyczne według daty granicznej kompletności (complete_data_date),
        resetuje indeksy, usuwa niepotrzebne kolumny i uzupełnia brakujące wartości.
        Ten zestaw danych zawiera tylko rekordy od daty, od której wszystkie kolumny
        są uzupełnione.
        
        Args:
            Brak
            
        Returns:
            pd.DataFrame: DataFrame z kompletnymi danymi od daty określonej jako complete_data_date
            
        Notes:
            - Wymaga wcześniejszego wywołania load_data()
            - Automatycznie filtruje dane według daty kompletności
            - Usuwa kolumnę "player_description" jako niepotrzebną do analizy
            - Wypełnia pozostałe brakujące wartości zerami
            - Zapisuje wyniki w atrybucie complete_df instancji
            - Loguje liczbę przygotowanych wierszy danych
            - W przypadku braku danych zwraca pusty DataFrame
        """
        if self.df_history is None:
            warning("Brak wczytanych danych historycznych")
            return pd.DataFrame()
            
        self.complete_df = self.filter_data_by_date(self.df_history, self.complete_data_date)
        
        self.complete_df.reset_index(drop=True, inplace=True)
        self.complete_df.index = self.complete_df.index + 1
        self.complete_df.drop(columns=["player_description"], inplace=True, errors='ignore')
        self.complete_df.fillna(0, inplace=True)
        
        info(f"Przygotowano zestaw kompletnych danych, liczba wierszy: {len(self.complete_df)}")
        return self.complete_df
    
    def prepare_editor_data(self):
        """
        Przygotowuje zestaw danych z uzupełnionymi ocenami edytora.
        
        Filtruje dane historyczne, zostawiając tylko wiersze z poprawnymi
        ocenami edytora, niezależnie od daty meczu. Ten zestaw danych
        może potencjalnie zawierać mecze z szerszego zakresu dat niż zestaw
        kompletnych danych, ale wszystkie będą miały oceny edytora.
        
        Args:
            Brak
            
        Returns:
            pd.DataFrame: DataFrame z danymi zawierającymi oceny edytora
            
        Notes:
            - Wymaga wcześniejszego wywołania load_data()
            - Filtruje tylko wiersze z poprawnie uzupełnionymi ocenami edytora
            - Zarówno wartości NaN jak i ciąg "NaN" są traktowane jako brakujące dane
            - Usuwa kolumnę "player_description" jako niepotrzebną do analizy
            - Uzupełnia brakujące wartości w kolumnach numerycznych zerami
            - Zapisuje wyniki w atrybucie editor_df instancji
            - Loguje liczbę przygotowanych wierszy danych
            - W przypadku braku danych zwraca pusty DataFrame
        """
        if self.df_history is None:
            warning("Brak wczytanych danych historycznych")
            return pd.DataFrame()
            
        self.editor_df = self.df_history[
            self.df_history["editor_rating"].notna() & 
            (self.df_history["editor_rating"] != "NaN")
        ].copy()
        
        self.editor_df.reset_index(drop=True, inplace=True)
        self.editor_df.index = self.editor_df.index + 1
        self.editor_df.drop(columns=["player_description"], inplace=True, errors='ignore')
        
        numeric_columns = self.editor_df.select_dtypes(include=['number']).columns
        self.editor_df[numeric_columns] = self.editor_df[numeric_columns].fillna(0)
        
        info(f"Przygotowano zestaw danych z ocenami edytora, liczba wierszy: {len(self.editor_df)}")
        return self.editor_df
    
    def save_data_to_file(self, df, file_name, output_dir=None):
        """
        Zapisuje DataFrame do pliku CSV w określonej lokalizacji.
        
        Zapisuje przygotowany zestaw danych do pliku CSV w określonej lokalizacji,
        wykorzystując bezpieczną metodę zapisu z klasy FileUtils. Metoda automatycznie
        tworzy katalogi, jeśli nie istnieją, i obsługuje potencjalne błędy.
        
        Args:
            df (pd.DataFrame): DataFrame do zapisania
            file_name (str): Nazwa pliku wynikowego (np. "RM_old_complete_data.csv")
            output_dir (str, optional): Katalog docelowy. Jeśli None, używa domyślnej ścieżki:
                "{project_root}/Data/Real/Old/"
            
        Returns:
            bool: True jeśli zapis się powiódł, False w przeciwnym razie
            
        Notes:
            - Bezpiecznie obsługuje przypadki pustych DataFrame
            - Automatycznie tworzy katalogi w ścieżce, jeśli nie istnieją
            - Używa FileUtils.save_csv_safe do bezpiecznego zapisu
            - Nie zapisuje indeksu w pliku CSV
            - Loguje szczegółowe informacje o zapisanym pliku
            - W przypadku błędu zapisuje szczegółowe informacje diagnostyczne
            - Jeśli nie podano output_dir, używa domyślnej ścieżki projektu
        """
        if df is None or df.empty:
            warning(f"Brak danych do zapisania dla pliku {file_name}")
            return False
            
        try:
            if output_dir is None:
                output_path = os.path.join(FileUtils.get_project_root(), "Data", "Real", "Old", file_name)
            else:
                output_path = os.path.join(output_dir, file_name)
                
            success = FileUtils.save_csv_safe(
                df=df,
                file_path=output_path,
                index=False
            )
            
            if success:
                info(f"Zapisano dane do pliku: {output_path}")
                info(f"Liczba zapisanych wierszy: {len(df)}")
                info(f"Liczba kolumn: {len(df.columns)}")
                return True
            else:
                error(f"Nie udało się zapisać danych do pliku: {output_path}")
                return False
                
        except Exception as e:
            error(f"Wystąpił błąd podczas zapisywania pliku {file_name}: {str(e)}")
            error(traceback.format_exc())
            return False
    
    def process_and_save_data(self, output_dir=None):
        """
        Przetwarza dane i zapisuje je do plików w określonym katalogu.
        
        Wykonuje pełny proces przetwarzania danych historycznych: wczytanie,
        przygotowanie dwóch różnych zestawów danych, standaryzację nazw drużyn,
        dodanie identyfikatorów drużyn i zapisanie ich do plików CSV.
        Jest to główna metoda klasy, która koordynuje cały proces przetwarzania.
        
        Ta metoda wykonuje sekwencyjnie:
        1. Wczytanie danych historycznych
        2. Przygotowanie zestawu kompletnych danych
        3. Przygotowanie zestawu danych z ocenami edytora
        4. Standaryzację nazw drużyn w obu zestawach danych
        5. Filtrowanie drużyn nieobecnych w pliku mapowania ID
        6. Dodanie identyfikatorów drużyn na podstawie ich nazw
        7. Zapisanie obu zestawów do plików CSV
        
        Args:
            output_dir (str, optional): Katalog docelowy dla plików wynikowych.
                Jeśli None, używa domyślnej ścieżki: "{project_root}/Data/Real/Old/"
                
        Returns:
            bool: True jeśli wszystkie operacje się powiodły, False jeśli wystąpiły błędy
            
        Notes:
            - Jest to główna metoda wykonawcza klasy
            - Wykonuje sekwencyjnie wszystkie etapy przetwarzania
            - Przerywa proces w przypadku błędu wczytywania danych
            - Zapisuje dwa pliki: "RM_old_complete_data.csv" i "RM_old_editor_data.csv"
            - Zwraca True tylko jeśli oba pliki zostały pomyślnie zapisane
            - Loguje szczegółowe informacje o każdym etapie procesu
            - W przypadku błędu zapisuje pełny traceback do logów
        """
        try:
            info("Rozpoczęto przetwarzanie historycznych danych Realu Madryt")
            
            if not self.load_data():
                error("Nie udało się wczytać danych. Przerwano przetwarzanie.")
                return False
                
            complete_data = self.prepare_complete_data()
            
            info("Standaryzacja nazw drużyn, filtrowanie nieznanych drużyn i dodawanie ID w danych kompletnych...")
            complete_data_processed = self.process_team_names_and_ids(complete_data)
            
            complete_saved = self.save_data_to_file(
                complete_data_processed, 
                "RM_old_complete_data.csv", 
                output_dir
            )
            
            editor_data = self.prepare_editor_data()
            
            info("Standaryzacja nazw drużyn, filtrowanie nieznanych drużyn i dodawanie ID w danych z ocenami edytora...")
            editor_data_processed = self.process_team_names_and_ids(editor_data)
            
            editor_saved = self.save_data_to_file(
                editor_data_processed, 
                "RM_old_editor_data.csv", 
                output_dir
            )
            
            if complete_saved and editor_saved:
                info("Przetwarzanie zakończone sukcesem. Zapisano oba pliki danych z mapowaniem nazw drużyn i ID.")
                return True
            else:
                warning("Przetwarzanie zakończone z ostrzeżeniami. Sprawdź logi.")
                return False
                
        except Exception as e:
            error(f"Wystąpił nieoczekiwany błąd podczas przetwarzania danych: {str(e)}")
            error(traceback.format_exc())
            return False


def main():
    """
    Funkcja główna do uruchamiania przetwarzania danych historycznych.
    
    Tworzy instancję klasy RM_old_Data z domyślnymi parametrami i wykonuje
    pełny proces przetwarzania i zapisywania danych. Dodatkowo wykorzystuje
    DataProcessor do standaryzacji nazw drużyn, filtrowania nieistniejących drużyn
    i dodawania identyfikatorów drużyn do wygenerowanych plików. Obsługuje
    wszelkie wyjątki, które mogą wystąpić podczas procesu.
    
    Główne etapy wykonywane przez funkcję:
    1. Utworzenie instancji RM_old_Data z domyślnymi parametrami
    2. Wczytanie, przetworzenie i przygotowanie danych historycznych
    3. Standaryzacja nazw drużyn zgodnie ze słownikiem mapowań
    4. Filtrowanie drużyn nieobecnych w pliku mapowania ID (np. Manchester City)
    5. Dodanie identyfikatorów drużyn na podstawie ich nazw
    6. Zapisanie dwóch plików danych: kompletnych i z ocenami edytora
    
    Args:
        Brak
        
    Returns:
        None
        
    Notes:
        - Funkcja jest wywoływana, gdy skrypt jest uruchamiany bezpośrednio
        - Używa domyślnych parametrów dla dat granicznych
        - Wykorzystuje DataProcessor do przetwarzania nazw drużyn i ID
        - Loguje informacje o sukcesie lub błędach wykonania
        - Filtruje drużyny nieobecne w pliku rywale.csv (np. Manchester City)
        - W przypadku błędu zapisuje pełny traceback do logów
        
    Przykład:
        # Uruchomienie z linii poleceń
        python RM_old_data.py
    """
    try:
        info("=== ROZPOCZĘCIE PRZETWARZANIA HISTORYCZNYCH DANYCH REALU MADRYT ===")
        
        file_utils = FileUtils()
        project_root = file_utils.get_project_root()
        
        info("Inicjalizacja procesora danych...")
        data_processor = DataProcessor(project_root)
        
        if not data_processor.load_team_id_template():
            warning("Nie można załadować mapowań ID drużyn. Upewnij się, że plik rywale.csv istnieje.")
        else:
            info(f"Wczytano mapowania dla {len(data_processor.name_to_id)} drużyn")
        
        info("Inicjalizacja procesora danych historycznych Realu Madryt...")
        processor = RM_old_Data(date=SEASON_DATES[0][1],)
        
        info("Rozpoczęcie pełnego procesu przetwarzania danych...")
        success = processor.process_and_save_data()
        
        info("Walidacja danych po zapisie...")
        if success and processor.initialize_data_processor():
            old_data_path = os.path.join(project_root, "Data", "Real", "Old")
            
            for file_name in ["RM_old_complete_data.csv", "RM_old_editor_data.csv"]:
                file_path = os.path.join(old_data_path, file_name)
                
                if os.path.exists(file_path):
                    info(f"Sprawdzanie spójności ID w pliku: {file_name}")
                    errors = processor.data_processor.validate_team_ids_in_file(file_path)
                    
                    if errors:
                        warning(f"Znaleziono {len(errors)} błędów ID w pliku {file_name}")
                        for idx, err_msg in errors[:5]:
                            warning(f"  - Wiersz {idx+2}: {err_msg}")
                        if len(errors) > 5:
                            warning(f"  ... oraz {len(errors) - 5} innych błędów")
                    else:
                        info(f"Plik {file_name} ma poprawne ID drużyn")
        
        if success:
            info("=== PROGRAM ZAKOŃCZONY SUKCESEM ===")
            info("Dane zostały przetworzone i zapisane w plikach CSV")
            info("Wszystkie drużyny mają odpowiednie identyfikatory z pliku rywale.csv")
            info("Drużyny nieobecne w pliku mapowania (np. Manchester City) zostały usunięte")
        else:
            error("=== PROGRAM ZAKOŃCZONY Z BŁĘDAMI ===")
            
    except Exception as e:
        error(f"Wystąpił nieoczekiwany błąd: {str(e)}")
        error(traceback.format_exc())
        error("=== PROGRAM ZAKOŃCZONY Z BŁĘDEM KRYTYCZNYM ===")


if __name__ == "__main__":
    main()