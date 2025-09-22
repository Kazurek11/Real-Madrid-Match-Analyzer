"""
Moduł agregacji danych meczów LaLiga

Ten skrypt łączy dane meczowe z wielu sezonów LaLiga w jeden zbiór danych.
Zapewnia spójność kolumn i formatów danych w połączonym zbiorze.
"""
import pandas as pd
import os
import re
import numpy as np
import sys
from typing import List, Optional, Tuple
current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
from data_processing.const_variable import COLUMN_MATCHES

from helpers.logger import info, debug, warning, error, critical, set_level
from helpers.file_utils import FileUtils

file_utils = FileUtils()
project_root = file_utils.get_project_root()
sys.path.append(project_root)

pd.set_option('future.no_silent_downcasting', True)

class DataMerger:
    """
    Klasa odpowiedzialna za łączenie i przetwarzanie danych meczów z różnych sezonów LaLiga.
    
    Umożliwia agregację danych meczowych z wielu plików źródłowych, wykonuje standaryzację formatu,
    dodaje identyfikatory meczów oraz zapewnia spójność kolumn w połączonych danych.
    
    Klasa zapewnia funkcjonalności:
    - Sprawdzanie zgodności kolumn w plikach źródłowych
    - Pobieranie i przetwarzanie plików sezonowych
    - Ekstrahowanie identyfikatorów sezonów z nazw plików
    - Łączenie danych z wielu sezonów w jeden spójny zbiór
    - Przydzielanie unikalnych identyfikatorów meczom
    - Zapisywanie wynikowych zbiorów danych
    """

    def __init__(self, file_name: str = "all_matches.csv"):
        """
        Inicjalizuje obiekt DataMerger, ustawia ścieżki oraz przygotowuje szablon kolumn.
        
        Args:
            file_name (str, optional): Nazwa pliku wynikowego. Domyślnie "all_matches.csv".
        """
        self.help = FileUtils()
        self.project_root = self.help.get_project_root()
        self.data_dir = os.path.join(self.project_root, "Data", "Mecze", "all_season")
        self.folder_name = "merged_matches"
        self.file_name = file_name
        self.output_path = os.path.join(self.data_dir, self.folder_name, self.file_name)
        
        debug(f"Katalog główny projektu: {self.project_root}")
        debug(f"Docelowa ścieżka do katalogu z danymi: {self.data_dir}")
        debug(f"Docelowa ścieżka do pliku wynikowego: {self.output_path}")
        
        self.all_matches = None
        self.column = self.columns_template_data()

    def columns_template_data(self):
        """
        Zwraca listę nazw kolumn oczekiwanych w plikach z danymi meczowymi.
        
        Returns:
            list: Lista nazw kolumn wymaganych w plikach z danymi meczowymi
        """
        return COLUMN_MATCHES

    def create_all_season_folder(self):
        """
        Tworzy folder wynikowy na dane połączone ze wszystkich sezonów, jeśli nie istnieje.
        
        Returns:
            str: Ścieżka do utworzonego lub istniejącego katalogu
        """
        return self.help.get_results_directory(base_path=self.data_dir, name_of_directory=self.folder_name)

    def get_season_files(self, pattern: str = "mecze_rywala_" or "rival_matches") -> List[str]:
        """
        Pobiera listę plików CSV z danymi meczów sezonowych z katalogu all_season.
        
        Args:
            pattern (str, optional): Wzorzec nazw plików do wyszukania. 
                Domyślnie "mecze_rywala_" lub "rival_matches".
        
        Returns:
            List[str]: Lista pełnych ścieżek do znalezionych plików CSV
        """
        try:
            all_files = self.help.get_all_files_from_directory(self.data_dir)
            if not all_files:
                warning(f"Nie znaleziono plików pasujących do wzorca {pattern}*.csv")
            else:
                debug(f"Znaleziono pliki: {', '.join([os.path.basename(f) for f in all_files])}")
            return all_files
        except Exception as e:
            error(f"Błąd podczas wyszukiwania plików: {str(e)}")
            return []

    def extract_season_id(self, file_path: str) -> str:
        """
        Wyciąga identyfikator sezonu z nazwy pliku i konwertuje na pełny format, np. '2020-2021'.
        
        Args:
            file_path (str): Ścieżka do pliku, z którego ma zostać wyekstrahowany identyfikator sezonu
            
        Returns:
            str: Identyfikator sezonu w formacie "YYYY-YYYY" lub pusty ciąg znaków w przypadku błędu
        """
        try:
            file_name = os.path.basename(file_path)
            pattern = r'_(\d{2})_(\d{2})\.'
            match = re.search(pattern, file_name)
            if match:
                first_year = match.group(1)
                second_year = match.group(2)
                full_first_year = f"20{first_year}"
                full_second_year = f"20{second_year}"
                return f"{full_first_year}-{full_second_year}"
            else:
                season_id = file_name.split('_')[-1].replace('.csv', '')
                if len(season_id) == 5:
                    first_year = season_id[:2]
                    second_year = season_id[3:]
                    return f"20{first_year}-20{second_year}"
                warning(f"Nie można dopasować wzorca sezonu w pliku {file_path}")
                return ""
        except Exception as e:
            warning(f"Nie można określić sezonu z pliku {file_path}: {str(e)}")
            return ""

    def check_columns_in_file(self, file_path: str) -> Tuple[bool, set, set]:
        """
        Sprawdza, czy plik ma zgodne kolumny z szablonem.
        
        Args:
            file_path (str): Ścieżka do pliku CSV, który ma zostać sprawdzony
            
        Returns:
            Tuple[bool, set, set]: Krotka zawierająca:
                - bool: True jeśli plik ma wszystkie wymagane kolumny, False w przeciwnym przypadku
                - set: Zbiór brakujących kolumn
                - set: Zbiór nadmiarowych kolumn
        """
        df = self.help.load_csv_safe(file_path)
        if df is None:
            warning(f"Nie można wczytać pliku: {file_path}")
            return False, set(), set()
        file_columns = set(df.columns)
        template_columns = set(self.column)
        missing = template_columns - file_columns
        extra = file_columns - template_columns
        if missing:
            warning(f"Plik {file_path} NIE MA kolumn: {missing}")
        if extra:
            warning(f"Plik {file_path} MA NADMIAROWE kolumny: {extra}")
        return len(missing) == 0, missing, extra

    def check_and_fix_columns(self, file_path: str) -> bool:
        """
        Sprawdza i naprawia brakujące kolumny w pliku CSV.
        
        Args:
            file_path (str): Ścieżka do pliku CSV do sprawdzenia i naprawy
            
        Returns:
            bool: True jeśli plik został pomyślnie naprawiony lub nie wymaga naprawy,
                  False w przypadku błędu
        """
        df = self.help.load_csv_safe(file_path)
        if df is None:
            warning(f"Nie można wczytać pliku: {file_path}")
            return False
            
        ok, missing, _ = self.check_columns_in_file(file_path)
        if ok:
            return True
            
        if 'score' in missing and 'home_goals' in df.columns and 'away_goals' in df.columns:
            df = self.add_score_column(df)
            missing.remove('score')
            
        if 'result' in missing and 'home_goals' in df.columns and 'away_goals' in df.columns:
            df = self.add_result_column(df)
            missing.remove('result')
            
        for col in missing:
            df[col] = np.nan
            info(f"Dodano pustą kolumnę '{col}' do pliku {os.path.basename(file_path)}")
            
        success = self.help.save_csv_safe(df, file_path, index=False)
        if success:
            info(f"Naprawiono plik {os.path.basename(file_path)}, dodając brakujące kolumny")
        else:
            error(f"Nie udało się zapisać naprawionego pliku {file_path}")
            
        return success

    def check_all_column(self) -> bool:
        """
        Sprawdza i naprawia kolumny we wszystkich plikach CSV.
        
        Returns:
            bool: True jeśli wszystkie pliki mają zgodne kolumny (po naprawach),
                  False jeśli któregoś pliku nie da się naprawić
        """
        season_files = self.get_season_files()
        all_ok = True
        
        for file_path in season_files:
            if not self.check_and_fix_columns(file_path):
                all_ok = False
                
        if all_ok:
            info("Wszystkie pliki mają zgodne kolumny z szablonem (po naprawach).")
        else:
            warning("Niektórych plików nie udało się naprawić.")
            
        return all_ok

    def prepare_season_dataframe(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Wczytuje plik sezonu, dodaje kolumnę 'season' i przetwarza dane.
        
        Args:
            file_path (str): Ścieżka do pliku CSV zawierającego dane jednego sezonu
            
        Returns:
            Optional[pd.DataFrame]: DataFrame z przetworzonymi danymi sezonu lub None w przypadku błędu
        """
        season_df = self.help.load_csv_safe(file_path)
        if season_df is None:
            return None
            
        if 'score' not in season_df.columns:
            season_df = self.add_score_column(season_df)
            
        if 'result' not in season_df.columns:
            season_df = self.add_result_column(season_df)
        
        season_id = self.extract_season_id(file_path)
        season_df["season"] = season_id
        
        if "result" in season_df.columns and season_df["result"].dtype == 'object':
            if season_df["result"].isin(["H", "A", "D"]).any():
                result_temp = season_df["result"].replace({"H": 1, "A": 2, "D": 0})
                season_df["result"] = result_temp.astype("Int64")
        
        season_df = self.reorder_columns(season_df)
        return season_df

    def concat_all_seasons(self, dfs: list) -> pd.DataFrame:
        """
        Łączy listę DataFrame'ów w jeden DataFrame.
        
        Args:
            dfs (list): Lista DataFrame'ów z danymi poszczególnych sezonów
            
        Returns:
            pd.DataFrame: Połączony DataFrame zawierający dane ze wszystkich sezonów
        """
        info("Łączenie danych z wszystkich sezonów...")
        combined_df = pd.concat(dfs, ignore_index=True)
        
        ordered_df = self.reorder_columns(combined_df)
        
        return ordered_df

    def check_nan_value(self, df: pd.DataFrame) -> None:
        """
        Sprawdza i wypisuje, czy w DataFrame występują wartości NaN.
        
        Args:
            df (pd.DataFrame): DataFrame do sprawdzenia
        """
        nan_cols = df.columns[df.isna().any()].tolist()
        if nan_cols:
            warning(f"DataFrame zawiera NaN w kolumnach: {nan_cols}")
        else:
            info("Brak wartości NaN w DataFrame.")
            
    def add_score_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Dodaje kolumnę 'score' w formacie 'home_goals:away_goals'.
        
        Args:
            df (pd.DataFrame): DataFrame, do którego ma zostać dodana kolumna 'score'
            
        Returns:
            pd.DataFrame: DataFrame z dodaną kolumną 'score' (jeśli to możliwe)
        """
        if df is None:
            return df
            
        if 'home_goals' in df.columns and 'away_goals' in df.columns:
            home_goals_formatted = df['home_goals'].fillna('').astype(str)
            away_goals_formatted = df['away_goals'].fillna('').astype(str)
            
            home_goals_formatted = home_goals_formatted.apply(
                lambda x: str(int(float(x))) if x and x != 'nan' and '.' in x else x)
            away_goals_formatted = away_goals_formatted.apply(
                lambda x: str(int(float(x))) if x and x != 'nan' and '.' in x else x)
            
            df['score'] = home_goals_formatted + ':' + away_goals_formatted
            
            df.loc[(df['score'] == ':') | (df['score'] == 'nan:nan'), 'score'] = np.nan
            
            info(f"Dodano kolumnę 'score' na podstawie 'home_goals' i 'away_goals'")
        else:
            warning(f"Nie można utworzyć kolumny 'score' - brak kolumn 'home_goals' lub 'away_goals'")
        
        return df

    def add_result_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Dodaje kolumnę 'result' z wartościami H, D, A zależnymi od wyniku meczu.
        
        Args:
            df (pd.DataFrame): DataFrame, do którego ma zostać dodana kolumna 'result'
            
        Returns:
            pd.DataFrame: DataFrame z dodaną kolumną 'result' (jeśli to możliwe)
        """
        if df is None:
            return df
            
        if 'home_goals' in df.columns and 'away_goals' in df.columns:
            home_win_mask = df['home_goals'] > df['away_goals']
            draw_mask = df['home_goals'] == df['away_goals']
            away_win_mask = df['home_goals'] < df['away_goals']
            
            df.loc[home_win_mask, 'result'] = 'H'
            df.loc[draw_mask, 'result'] = 'D'
            df.loc[away_win_mask, 'result'] = 'A'
            
            info(f"Dodano kolumnę 'result' na podstawie 'home_goals' i 'away_goals'")
        else:
            warning(f"Nie można utworzyć kolumny 'result' - brak kolumn 'home_goals' lub 'away_goals'")
    
        return df
    
    def set_match_ids(self) -> Optional[pd.DataFrame]:
        """
        Ustawia identyfikatory meczów, gdzie mecze Realu Madryt otrzymują ID od 1 do N,
        a pozostałe mecze od 1000 wzwyż.
        
        Returns:
            Optional[pd.DataFrame]: Zaktualizowany DataFrame z kolumną match_id lub None w przypadku błędu
        """
        if self.all_matches is None:
            error("Brak danych. Najpierw wczytaj pliki z sezonami.")
            return None
        try:
            df = self.all_matches.copy()
            
            real_madrid_id = 1
            real_madrid_name = "Real Madrid CF"
            
            is_real_madrid_match = (
                (df["home_team_id"] == real_madrid_id) | 
                (df["away_team_id"] == real_madrid_id)
            )
            
            real_madrid_matches_count = is_real_madrid_match.sum()
            
            if "match_id" not in df.columns:
                df["match_id"] = np.nan
            
            df.loc[is_real_madrid_match, "match_id"] = np.arange(1, real_madrid_matches_count + 1)
            
            df.loc[~is_real_madrid_match, "match_id"] = np.arange(1000, 1000 + len(df) - real_madrid_matches_count)
            
            df["match_id"] = df["match_id"].astype('Int64')
            
            self.all_matches = df
            info(f"Ustawiono ID od 1 do {real_madrid_matches_count} dla {real_madrid_matches_count} meczów Realu Madryt.")
            info(f"Ustawiono ID od 1000 do {1000 + len(df) - real_madrid_matches_count - 1} dla {len(df) - real_madrid_matches_count} pozostałych meczów.")
            
            return df
        except Exception as e:
            error(f"Błąd podczas ustawiania ID meczów: {str(e)}")
            return None

    def save_with_match_id_as_index(self, df: pd.DataFrame, path: str) -> bool:
        """
        Zapisuje DataFrame do pliku CSV, ustawiając match_id jako indeks.
        
        Args:
            df (pd.DataFrame): DataFrame do zapisania
            path (str): Ścieżka do pliku, w którym dane mają zostać zapisane
            
        Returns:
            bool: True jeśli operacja zapisu się powiodła, False w przeciwnym przypadku
        """
        try:
            if "match_id" not in df.columns:
                warning(f"Brak kolumny match_id w DataFrame. Nie można ustawić jako indeks.")
                return self.help.save_csv_safe(df=df, file_path=path, index=False)
            
            df = self.reorder_columns(df)
            
            df_to_save = df.set_index("match_id")
            result = self.help.save_csv_safe(df=df_to_save, file_path=path, index=True)
            
            info(f"Zapisano plik {path} z {len(df_to_save)} wierszami i indeksem match_id.")
            return result
        except Exception as e:
            error(f"Błąd podczas zapisywania pliku {path}: {str(e)}")
            return False

    def process_and_save_data(self) -> Tuple[bool, pd.DataFrame]:
        """
        Wykonuje pełny workflow przetwarzania danych i zapisuje wyniki.
        
        Returns:
            Tuple[bool, pd.DataFrame]: Krotka zawierająca:
                - bool: True jeśli operacja się powiodła, False w przypadku błędu
                - pd.DataFrame: DataFrame z wszystkimi meczami lub None w przypadku błędu
        """
        try:
            self.check_all_column()
    
            season_files = self.get_season_files()
            processed_seasons = []
            for file_path in season_files:
                season_df = self.prepare_season_dataframe(file_path)
                if season_df is not None:
                    processed_seasons.append(season_df)
            if not processed_seasons:
                error("Nie udało się przetworzyć żadnych plików.")
                return False, None
    
            all_matches = self.concat_all_seasons(processed_seasons)
            self.all_matches = all_matches
    
            self.check_nan_value(self.all_matches)
    
            if self.set_match_ids() is None:
                return False, None
            
            self.all_matches = self.reorder_columns(self.all_matches)

            output_dir = os.path.join(self.data_dir, self.folder_name)
            self.help.ensure_directory_exists(output_dir)
            
            all_matches_path = os.path.join(output_dir, "all_matches.csv")
            
            status_all_matches = self.save_with_match_id_as_index(self.all_matches, all_matches_path)
            
            if status_all_matches:
                info(f"Zapisano plik {all_matches_path} z {len(self.all_matches)} wierszami.")
            else:
                warning("Wystąpiły problemy podczas zapisywania pliku.")
    
            return status_all_matches, self.all_matches
    
        except Exception as e:
            error(f"Błąd podczas przetwarzania danych: {str(e)}")
            return False, None

    def load_all_seasons(self) -> bool:
        """
        Wczytuje wszystkie dane sezonów niezbędne do dalszej analizy bez zapisywania do pliku CSV.
        
        Returns:
            bool: True jeśli operacja się powiodła, False w przypadku błędu
        """
        try:
            info("Wczytywanie danych wszystkich sezonów...")
            
            self.check_all_column()
            
            season_files = self.get_season_files()
            if not season_files:
                error("Nie znaleziono plików z danymi sezonów.")
                return False
                
            processed_seasons = []
            for file_path in season_files:
                info(f"Wczytywanie pliku: {os.path.basename(file_path)}")
                season_df = self.prepare_season_dataframe(file_path)
                if season_df is not None:
                    processed_seasons.append(season_df)
            
            if not processed_seasons:
                error("Nie udało się przetworzyć żadnych plików.")
                return False
                
            self.all_matches = self.concat_all_seasons(processed_seasons)
            info(f"Połączono dane z {len(processed_seasons)} sezonów, łącznie {len(self.all_matches)} meczów.")
            
            self.check_nan_value(self.all_matches)
            
            if self.set_match_ids() is None:
                error("Nie udało się ustawić ID meczów.")
                return False
                
            info("Pomyślnie wczytano wszystkie dane sezonów.")
            return True
            
        except Exception as e:
            error(f"Błąd podczas wczytywania danych sezonów: {str(e)}")
            return False
    
    def reorder_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Reorganizuje kolumny DataFrame zgodnie z kolejnością zdefiniowaną w COLUMN_MATCHES.
        
        Args:
            df (pd.DataFrame): DataFrame, którego kolumny mają zostać zreorganizowane
            
        Returns:
            pd.DataFrame: DataFrame z zreorganizowanymi kolumnami
        """
        if df is None:
            return df
            
        template_cols = [col for col in self.column if col in df.columns]
        
        extra_cols = [col for col in df.columns if col not in self.column]
        
        new_order = template_cols + extra_cols
        
        return df[new_order]