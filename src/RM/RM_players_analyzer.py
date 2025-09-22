"""
RM_players_analyzer.py - Moduł do analizy danych piłkarzy Realu Madryt.

Ten skrypt przetwarza dane z plików Excel zawierających statystyki meczowe piłkarzy
Realu Madryt, wykonuje analizę ich występów, ocen i czasu gry oraz generuje 
podsumowanie w postaci plików CSV.

Funkcjonalności:
- Wczytywanie i łączenie danych z wielu plików Excel (sezony 2019-2025)
- Kategoryzacja meczów na rozgrywki La Liga, Liga Mistrzów i inne
- Obliczanie czasu gry zawodników w różnych sezonach i rozgrywkach  
- Analizowanie ocen zawodników przyznawanych przez użytkowników i edytorów
- Śledzenie informacji o kontuzjach i dostępności zawodników
- Generowanie profili zawodników z przypisaniem pozycji boiskowych
- Eksport przetworzonych danych do plików CSV
"""
DATE = "2020-01-01" # ZACZYNAMY FILTROWANIE SPOTKAŃ OD 2020 ROKU
import pandas as pd
import numpy as np
import os
import sys
import traceback
from datetime import datetime
from typing import Dict, List, Tuple, Set, Optional

current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from helpers.logger import info, error, debug, warning, critical
from helpers.file_utils import FileUtils

pd.set_option('display.max_seq_items', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 80)
pd.set_option('display.min_rows', 10)
pd.set_option('display.precision', 2)
pd.set_option('display.max_colwidth', 30)
pd.set_option('future.no_silent_downcasting', True)


class RealMadridPlayersAnalyzer:
    """
    Klasa do analizy danych piłkarzy Realu Madryt.
    
    Przetwarza dane z plików Excel zawierających statystyki meczowe, generuje 
    kompleksowe profile zawodników z uwzględnieniem występów w różnych rozgrywkach,
    oblicza czas gry i średnie oceny w poszczególnych sezonach oraz zapisuje 
    wyniki do plików CSV.
    
    Attributes:
        file_utils (FileUtils): Instancja klasy pomocniczej do operacji na plikach
        project_root (str): Ścieżka do głównego katalogu projektu
        excel_path_2025 (str): Ścieżka do pliku Excel z ocenami na sezon 2024/2025
        excel_path_2019_2024 (str): Ścieżka do pliku Excel z ocenami z lat 2019-2024
        output_dir (str): Ścieżka do katalogu wynikowego
        df_2025 (pd.DataFrame): DataFrame z danymi z sezonu 2024/2025
        df_2019v2024 (pd.DataFrame): DataFrame z danymi z sezonów 2019-2024
        all_data (pd.DataFrame): Połączone dane ze wszystkich sezonów
        LL_matches (pd.DataFrame): DataFrame z meczami La Liga
        CL_matches (pd.DataFrame): DataFrame z meczami Ligi Mistrzów
        other_matches (pd.DataFrame): DataFrame z pozostałymi meczami
        real_player_csv (pd.DataFrame): DataFrame z profilami zawodników
        season_names (List[str]): Lista identyfikatorów sezonów
        injured_players (List[str]): Lista kontuzjowanych zawodników
    """

    def __init__(self):
        """
        Inicjalizuje analizator danych piłkarzy Realu Madryt.
        
        Metoda inicjalizuje wszystkie wymagane atrybuty, tworzy ścieżki do plików
        źródłowych i katalogów wynikowych oraz przygotowuje puste DataFrame'y do
        późniejszego wypełnienia danymi.
        
        Notes:
            - Tworzy katalogu wynikowe jeśli nie istnieją
            - Definiuje listę sezonów od 20_21 do 24_25
            - Inicjalizuje listę kontuzjowanych zawodników
        """
        self.file_utils = FileUtils()
        self.project_root = self.file_utils.get_project_root()
        
        self.excel_path_2025 = os.path.join(self.project_root, "Data", "Excele", "oceny_pilkarzy2_2025.xlsx")
        self.excel_path_2019_2024 = os.path.join(self.project_root, "Data", "Excele", "real_players_match_19-24.xlsx")
        
        self.output_dir = os.path.join(self.project_root, "Data", "Real")
        self.file_utils.ensure_directory_exists(self.output_dir)
        
        self.df_2025 = pd.DataFrame()
        self.df_2019v2024 = pd.DataFrame()
        self.all_data = pd.DataFrame()
        self.LL_matches = pd.DataFrame()
        self.CL_matches = pd.DataFrame()
        self.other_matches = pd.DataFrame()
        self.real_player_csv = pd.DataFrame()
        
        self.season_names = ["19_20","20_21", "21_22", "22_23", "23_24", "24_25"]
        self.injured_players = self.search_injured_player()
    
    def validate_dataframe(self, df: pd.DataFrame, required_columns: List[str], name: str) -> bool:
        """
        Sprawdza czy DataFrame ma wymagane kolumny.
        
        Metoda weryfikuje czy podany DataFrame zawiera wszystkie kolumny niezbędne 
        do przeprowadzenia analizy. Jeśli brakuje wymaganych kolumn, loguje
        szczegółowe informacje o braku.
        
        Args:
            df (pd.DataFrame): DataFrame do sprawdzenia
            required_columns (List[str]): Lista wymaganych kolumn
            name (str): Nazwa DataFrame (używana w komunikatach logowania)
        
        Returns:
            bool: True jeśli wszystkie wymagane kolumny istnieją, False w przeciwnym przypadku
            
        Notes:
            - Sprawdza czy DataFrame nie jest pusty
            - Identyfikuje i loguje brakujące kolumny
            - W przypadku błędów używa modułu logger
        """
        if df is None or df.empty:
            error(f"DataFrame {name} jest pusty!")
            return False
            
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error(f"Brakujące kolumny w {name}: {missing_columns}")
            error(f"Dostępne kolumny: {df.columns.tolist()}")
            return False
        return True
    
    def check_file_exists(self, path: str, description: str) -> bool:
        """
        Sprawdza czy plik istnieje i zwraca informację.
        
        Metoda weryfikuje istnienie pliku pod podaną ścieżką i loguje informację
        o jego dostępności.
        
        Args:
            path (str): Ścieżka do pliku
            description (str): Opis pliku (używany w komunikatach logowania)
        
        Returns:
            bool: True jeśli plik istnieje, False w przeciwnym przypadku
            
        Notes:
            - Wynik weryfikacji jest zapisywany do dziennika za pomocą funkcji info()
        """
        exists = os.path.exists(path)
        info(f"{description} istnieje: {exists}")
        return exists
    
    def load_excel_files(self) -> bool:
        """
        Wczytuje dane z plików Excel.
        
        Metoda próbuje wczytać dane z plików Excel zawierających statystyki piłkarzy.
        Sprawdza dostępność plików i w przypadku ich braku, wyświetla ostrzeżenia.
        W przypadku problemów ze znalezieniem arkuszy, próbuje znaleźć alternatywne
        arkusze.
        """
        try:
            file_2025_exists = self.check_file_exists(self.excel_path_2025, "Plik 2025")
            file_2019_2024_exists = self.check_file_exists(self.excel_path_2019_2024, "Plik 2019-2024")
            
            if not file_2025_exists and not file_2019_2024_exists:
                warning("Żaden z plików źródłowych nie istnieje. Nie można kontynuować.")
                return False
            
            if file_2025_exists:
                try:
                    excel_2025 = pd.ExcelFile(self.excel_path_2025)
                    info(f"Arkusze w pliku 2025: {excel_2025.sheet_names}")
                    
                    if "pikarze_20250319" not in excel_2025.sheet_names:
                        warning(f"Arkusz 'pikarze_20250319' nie istnieje w pliku 2025")
                        available_sheets = [s for s in excel_2025.sheet_names if 'pikarze' in s.lower() or 'pilkarze' in s.lower()]
                        if available_sheets:
                            warning(f"Próba użycia alternatywnego arkusza: {available_sheets[0]}")
                            sheet_name_2025 = available_sheets[0]
                        else:
                            sheet_name_2025 = excel_2025.sheet_names[0]
                            warning(f"Używam pierwszego dostępnego arkusza: {sheet_name_2025}")
                    else:
                        sheet_name_2025 = "pikarze_20250319"
                    
                    self.df_2025 = self.file_utils.load_excel_safe(self.excel_path_2025, sheet_name=sheet_name_2025)
                    
                    if self.df_2025 is not None and 'match_date' in self.df_2025.columns:
                        self.df_2025['match_date'] = pd.to_datetime(self.df_2025['match_date'], errors='coerce')
                        info(f"Wczytano dane z 2025, liczba wierszy: {len(self.df_2025)}")
                except Exception as e:
                    error(f"Błąd podczas wczytywania danych 2025: {str(e)}")
            
            if file_2019_2024_exists:
                try:
                    excel_2019_2024 = pd.ExcelFile(self.excel_path_2019_2024)
                    info(f"Arkusze w pliku 2019-2024: {excel_2019_2024.sheet_names}")
                    
                    if "pilkarze20240528" not in excel_2019_2024.sheet_names:
                        warning(f"Arkusz 'pilkarze20240528' nie istnieje w pliku 2019-2024")
                        available_sheets = [s for s in excel_2019_2024.sheet_names if 'pikarze' in s.lower() or 'pilkarze' in s.lower()]
                        if available_sheets:
                            warning(f"Próba użycia alternatywnego arkusza: {available_sheets[0]}")
                            sheet_name_2019_2024 = available_sheets[0]
                        else:
                            sheet_name_2019_2024 = excel_2019_2024.sheet_names[0]
                            warning(f"Używam pierwszego dostępnego arkusza: {sheet_name_2019_2024}")
                    else:
                        sheet_name_2019_2024 = "pilkarze20240528"
                    
                    self.df_2019v2024 = self.file_utils.load_excel_safe(self.excel_path_2019_2024, 
                                                                      sheet_name=sheet_name_2019_2024)
                    
                    if self.df_2019v2024 is not None and 'match_date' in self.df_2019v2024.columns:
                        self.df_2019v2024['match_date'] = pd.to_datetime(self.df_2019v2024['match_date'], errors='coerce')
                        info(f"Wczytano dane z 2019-2024, liczba wierszy: {len(self.df_2019v2024)}")
                except Exception as e:
                    error(f"Błąd podczas wczytywania danych 2019-2024: {str(e)}")
            
            if (self.df_2025 is None or self.df_2025.empty) and (self.df_2019v2024 is None or self.df_2019v2024.empty):
                error("Nie udało się wczytać żadnych danych.")
                return False
                
            return True
            
        except Exception as e:
            error(f"Błąd podczas wczytywania plików Excel: {str(e)}")
            error(traceback.format_exc())
            return False
    
    def merge_and_process_data(self) -> pd.DataFrame:
        """
        Łączy i przetwarza dane z różnych plików.
        
        Metoda analizuje strukturę wczytanych DataFrame'ów, weryfikuje obecność
        wymaganych kolumn, łączy dane z różnych źródeł, a następnie dokonuje
        niezbędnych przekształceń (np. konwersja dat, wypełnianie brakujących wartości).
        
        Returns:
            pd.DataFrame: Przetworzony DataFrame z danymi o meczach lub pusty DataFrame
                          w przypadku błędu
                          
        Notes:
            - Sprawdza zgodność struktur DataFrame'ów przed połączeniem
            - Filtruje dane od poczatyku 2020 roku
            - Sortuje wyniki według daty meczu
            - Usuwa niepotrzebne kolumny i wypełnia brakujące wartości
            - Loguje szczegółowe informacje o procesie i błędach
        """
        try:
            info("\nKolumny w df_2025:")
            info(str(self.df_2025.columns.tolist()))
            info("\nKolumny w df_2019v2024:")
            info(str(self.df_2019v2024.columns.tolist()))
            info("\nSprawdzamy czy nazwy kolumn się zgadzają")
            
            required_columns = [
                "match_date", "home_team", "away_team", "home_goals", "away_goals",
                "player_name", "player_min", "is_first_squad", "goals", "assists", 
                "total_shots", "shots_on_target", "user_rating", "editor_rating"
            ]
            
            valid_df_2025 = self.validate_dataframe(self.df_2025, required_columns, "df_2025") if not self.df_2025.empty else False
            valid_df_2019v2024 = self.validate_dataframe(self.df_2019v2024, required_columns, "df_2019v2024") if not self.df_2019v2024.empty else False
            
            result_df = pd.DataFrame()
            
            if not self.df_2025.empty and not self.df_2019v2024.empty and self.df_2025.columns.equals(self.df_2019v2024.columns):
                result_df = pd.concat([self.df_2019v2024, self.df_2025], ignore_index=True)
                info(f"\nPo połączeniu, liczba wierszy w all_data: {len(result_df)}")
                
                if "player_description" in result_df.columns:
                    result_df = result_df.drop(["player_description"], axis=1)
                    info("Usunięto kolumnę 'player_description'")
                
                result_df.fillna(0, inplace=True)
            elif not self.df_2025.empty and not self.df_2019v2024.empty:
                error("Nazwy kolumn w plikach się nie zgadzają. Próba łączenia na wspólnych kolumnach.")
                common_columns = list(set(self.df_2025.columns) & set(self.df_2019v2024.columns))
                if len(common_columns) >= len(required_columns):
                    warning(f"Próba połączenia na podstawie {len(common_columns)} wspólnych kolumn")
                    result_df = pd.concat([
                        self.df_2019v2024[common_columns], 
                        self.df_2025[common_columns]
                    ], ignore_index=True)
                    info(f"Połączono dane używając {len(common_columns)} wspólnych kolumn. Wierszy: {len(result_df)}")
                else:
                    error("Za mało wspólnych kolumn, aby bezpiecznie połączyć dane")
                    return pd.DataFrame()
            elif not self.df_2025.empty:
                warning("Używam tylko danych z 2025 (dane 2019-2024 są niedostępne)")
                result_df = self.df_2025.copy()
            elif not self.df_2019v2024.empty:
                warning("Używam tylko danych z 2019-2024 (dane 2025 są niedostępne)")
                result_df = self.df_2019v2024.copy()
            else:
                error("Brak dostępnych danych - nie można kontynuować analizy")
                return pd.DataFrame()
                
            if "match_date" not in result_df.columns:
                error("Kolumna 'match_date' nie istnieje w danych!")
                error(f"Dostępne kolumny: {result_df.columns.tolist()}")
                return pd.DataFrame()
            
            if not pd.api.types.is_datetime64_any_dtype(result_df["match_date"]):
                result_df["match_date"] = pd.to_datetime(result_df["match_date"], errors='coerce')
                invalid_dates = result_df["match_date"].isna()
                if invalid_dates.any():
                    warning(f"Usunięto {invalid_dates.sum()} wierszy z nieprawidłowymi datami")
                    result_df = result_df[~invalid_dates]
            
            info(f"\nZakres dat w danych przed filtrowaniem:")
            info(f"Najwcześniejsza data: {result_df['match_date'].min()}")
            info(f"Najpóźniejsza data: {result_df['match_date'].max()}")
            info(f"Liczba wierszy przed filtrowaniem: {len(result_df)}")
            
            filter_date = pd.to_datetime(DATE) # DATA OD KTOREJ ZACZYNAMY FILTROWANIE 
            result_df = result_df[result_df["match_date"] >= filter_date]
            
            info(f"\nZakres dat po filtrowaniu:")
            info(f"Najwcześniejsza data: {result_df['match_date'].min()}")
            info(f"Najpóźniejsza data: {result_df['match_date'].max()}")
            info(f"Liczba wierszy po filtrowaniu: {len(result_df)}")
            
            result_df.sort_values(by='match_date', inplace=True, ascending=False)
            result_df.reset_index(drop=True, inplace=True)
            
            info("Zwracam DataFrame z danymi o meczach Realu")
            return result_df
            
        except Exception as e:
            error(f"Błąd podczas łączenia i przetwarzania danych: {str(e)}")
            error(traceback.format_exc())
            return pd.DataFrame()
        
    def search_injured_player(self) -> List[str]:
        """Pobiera i kategoryzuje aktualnie kontuzjowanych graczy z pliku CSV.
        
        Funkcja wczytuje dane z pliku RM_players.csv i filtruje je, aby znaleźć zawodników,
        którzy są aktualnie w drużynie (actual_player == 1), ale są niedostępni 
        (current_availability == 0) z powodu kontuzji lub innych przyczyn.
        
        Returns:
            List[str]: Lista nazwisk kontuzjowanych/niedostępnych zawodników.
            
        Raises:
            FileNotFoundError: Gdy plik CSV nie istnieje.
            ValueError: Gdy dane w pliku CSV mają nieprawidłowy format.
            
        Notes:
            - Używa metody load_csv_safe z klasy FileUtils do bezpiecznego wczytania pliku
            - Filtruje tylko graczy którzy są w aktualnym składzie (actual_player == 1)
            - Zwraca tylko tych graczy, którzy są obecnie niedostępni (current_availability == 0)
            - W przypadku problemów z wczytaniem pliku, FileUtils.load_csv_safe obsłuży błędy
            - Jeśli plik istnieje ale nie zawiera wymaganych kolumn, zwraca pustą listę
        """
        try:
            data_path = os.path.join(self.file_utils.get_project_root(), "Data", "Real", "RM_players.csv")
            data = self.file_utils.load_csv_safe(data_path)
            
            if data is not None and "actual_player" in data.columns and "current_availability" in data.columns:
                filtered_data = data[(data["actual_player"] == 1) & (data["current_availability"] == 0)]
                if "player_name" in filtered_data.columns:
                    return filtered_data["player_name"].to_list()
                    
            return []
        except Exception as e:
            error(f"Błąd podczas wyszukiwania kontuzjowanych graczy: {str(e)}")
            return []
        
    def categorize_teams(self) -> bool:
        """
        Dzieli mecze na kategorie (La Liga, Liga Mistrzów, inne).
        
        Metoda kategoryzuje mecze na podstawie nazw drużyn, przypisując je do jednej
        z trzech kategorii: La Liga, Liga Mistrzów lub inne rozgrywki. Tworzy osobne
        DataFrame'y dla każdej kategorii i dodaje kolumnę z oznaczeniem typu rozgrywek.
        
        Returns:
            bool: True jeśli operacja się powiodła, False w przypadku błędu
            
        Notes:
            - Wczytuje listę rywali z La Liga z pliku CSV
            - Identyfikuje drużyny z Ligi Mistrzów przez wykluczenie
            - Dodaje kolumnę 'competition_category' z oznaczeniem rozgrywek
            - Loguje liczby meczów w poszczególnych kategoriach
        """
        try:
            rivals_path = os.path.join(self.project_root, "Data", "Mecze", "id_nazwa", "rywale_polskie_nazwy.csv")
            
            rivals = pd.read_csv(rivals_path)
            rivals_la_liga = rivals["nazwa_rywala"].to_list()
            rivals_la_liga = rivals_la_liga[1:]
            
            rivals_all = pd.concat([self.all_data["home_team"], self.all_data["away_team"]]).unique().tolist()
            
            other_teams = [
                'Real Madryt',
                'CD Alcoyano',
                'CD Minera',
                'CP Cacereño',
                'Al-Ahly SC',
                'Al-Hilal SFC',
                'Arandina CF',
                'FC Pachuca'
            ]
            
            rivalas_CL = list(set(rivals_all) - set(rivals_la_liga))
            rivalas_CL = [team for team in rivalas_CL if team not in other_teams]
            
            other_teams = other_teams[1:]
            
            self.LL_matches = self.all_data[
                (self.all_data["home_team"].isin(rivals_la_liga)) | (self.all_data["away_team"].isin(rivals_la_liga))
            ]
            
            self.CL_matches = self.all_data[
                (self.all_data["home_team"].isin(rivalas_CL)) | (self.all_data["away_team"].isin(rivalas_CL))
            ]
            
            self.other_matches = self.all_data[
                ~self.all_data.index.isin(self.LL_matches.index) & ~self.all_data.index.isin(self.CL_matches.index)
            ]
            
            self.LL_matches = self.LL_matches.assign(competition_category="Premier Spain Team")
            self.CL_matches = self.CL_matches.assign(competition_category="Champions League")
            self.other_matches = self.other_matches.assign(competition_category="Other")
            
            info(f"Liczba meczów w La Liga: {len(self.LL_matches)}")
            info(f"Liczba meczów w Lidze Mistrzów: {len(self.CL_matches)}")
            info(f"Liczba meczów w innych rozgrywkach: {len(self.other_matches)}")
            
            return True
            
        except Exception as e:
            error(f"Błąd podczas kategoryzacji drużyn: {str(e)}")
            error(traceback.format_exc())
            return False
        
    def name_to_id(self,name) -> bool:
        """Funkcja na podstawie nazwiska piłkarza pobiera jego ID z pliku CSV.
        Args: name (str): Nazwisko piłkarza
        Returns: bool: True jeśli ID zostało znalezione, False w przeciwnym przypadku

        Notes:
            - Używa metody load_csv_safe z klasy FileUtils do bezpiecznego wczytania pliku
            - Sprawdza czy kolumna 'player_name' istnieje w DataFrame
            - Zwraca ID zawodnika lub False jeśli nie znaleziono
        """
        try:
            data_path = os.path.join(self.file_utils.get_project_root(), "Data", "Real", "RM_players.csv")
            data = self.file_utils.load_csv_safe(data_path)
            
            if data is not None and "player_name" in data.columns:
                player_id = data.loc[data["player_name"] == name, "player_id"]
                if not player_id.empty:
                    return player_id.values[0]
                    
            return False
        except Exception as e:
            error(f"Błąd podczas wyszukiwania ID zawodnika: {str(e)}")
            return False
        
    def prepare_player_profiles(self) -> bool:
        """
        Tworzy profile zawodników z pozycjami i ID.
        
        Metoda tworzy kompleksowe profile zawodników na podstawie unikalnych nazwisk
        z danych meczowych. Przypisuje każdemu zawodnikowi unikalny identyfikator oraz
        jedną lub więcej pozycji boiskowych na podstawie predefiniowanych list.
        
        Returns:
            bool: True jeśli operacja się powiodła, False w przypadku błędu
            
        Notes:
            - Tworzy DataFrame z unikalnymi zawodnikami i przypisuje im ID
            - Definiuje listy zawodników dla każdej pozycji boiskowej
            - Jeden zawodnik może mieć przypisanych wiele pozycji
            - Loguje informacje o liczbie utworzonych profili
        """
        try:
            players_LL = list(self.LL_matches["player_name"].unique())
            
            self.real_player_csv = pd.DataFrame({
                "player_name": players_LL,
                "player_id": range(1, len(players_LL)+1)
            })
            
            player_positions = {}
            
            goalkeepers = ["Courtois", "Kepa", "Yáñez", "Łunin"]
            left_back = ["Fran García", "Mendy", "Marcelo", "Miguel Gutiérrez", "Camavinga"]
            right_back = ["Carvajal", "Odriozola", "Lucas Vázquez", "Marvin", "Sergio Santos", "Nacho"]
            center_back = ["Lorenzo","Jacobo Ramón","Chust","Asencio", "Nacho", "Gila", "Rüdiger", "Tchouaméni", "Alaba", "Vallejo", "Varane", "Ramos", "Militão"]
            def_midfilder = ["Chema","Tchouaméni", "Kroos", "Blanco", "Camavinga", "Valverde", "Casemiro"]
            midfilder = ["Arribas","Nico Paz","Mario Martín","Chema","Isco", "Tchouaméni", "Kroos", "Blanco", "Camavinga", "Valverde", "Casemiro", "Modrić", "Ceballos", "Bellingham", "Arda Güler"]
            ofensive_midfilder = ["Arribas","Ødegaard","Isco", "Bellingham", "Arda Güler", "Modrić","Nico Paz"]
            right_winger = ["Peter","Asensio", "Rodrygo", "Valverde", "Arda Güler", "Brahim", "Mbappé","Bale"]
            left_winger = ["Vinícius", "Mbappé", "Hazard", "Rodrygo"]
            striker = ["Álvaro","Mariano","Endrick", "Mbappé", "Borja Mayoral", "Vinícius", "Jović", "Benzema","Latasa","Gonzalo","Hugo Duro","Joselu"]
            
            def add_position(player_list, position):
                for player in player_list:
                    if player not in player_positions:
                        player_positions[player] = []
                    if position not in player_positions[player]:
                        player_positions[player].append(position)
            
            add_position(goalkeepers, "GK")
            add_position(left_back, "LB")
            add_position(right_back, "RB")
            add_position(center_back, "CB")
            add_position(def_midfilder, "DM")
            add_position(midfilder, "CM")
            add_position(ofensive_midfilder, "CAM")
            add_position(right_winger, "RW")
            add_position(left_winger, "LW")
            add_position(striker, "ST")
            
            positions_df = pd.Series(player_positions).reset_index()
            positions_df.columns = ['player_name', 'player_position']
            
            self.real_player_csv = self.real_player_csv.drop('player_position', axis=1, errors='ignore')
            self.real_player_csv = self.real_player_csv.merge(positions_df, on='player_name', how='outer')
            
            self.real_player_csv["player_id"] = range(1, len(self.real_player_csv) + 1)
            
            info(f"Utworzono profile dla {len(self.real_player_csv)} zawodników")
            return True
            
        except Exception as e:
            error(f"Błąd podczas przygotowania profili zawodników: {str(e)}")
            error(traceback.format_exc())
            return False
    
    def create_season_splits(self) -> Tuple[Dict, Dict]:
        """
        Tworzy podziały danych na sezony dla La Liga i Champions League.
        
        Metoda dzieli dane meczowe na poszczególne sezony dla rozgrywek La Liga i Ligi Mistrzów,
        tworząc słowniki z DataFrame'ami dla każdego sezonu. Filtrowanie odbywa się na podstawie
        dat rozpoczęcia i zakończenia każdego sezonu.
        
        Returns:
            Tuple[Dict, Dict]: Słowniki DataFrame'ów dla każdego sezonu (La Liga, Champions League)
                              lub puste słowniki w przypadku błędu
                              
        Notes:
            - Definiuje dokładne daty granic dla każdego sezonu
            - Tworzy osobne słowniki dla meczów La Liga i Champions League
            - Loguje informacje o liczbie meczów w każdym sezonie i rozgrywkach
        """
        try:
            season_LL_dataframes = {
                "19_20": self.LL_matches[(self.LL_matches["match_date"] <= "2020-09-19" ) & (self.LL_matches["match_date"] >= "2020-01-01")],
                "20_21": self.LL_matches[(self.LL_matches["match_date"] <= "2021-05-22") & (self.LL_matches["match_date"] >= "2020-09-20")],
                "21_22": self.LL_matches[(self.LL_matches["match_date"] <= "2022-05-20") & (self.LL_matches["match_date"] >= "2021-08-14")],
                "22_23": self.LL_matches[(self.LL_matches["match_date"] <= "2023-06-23") & (self.LL_matches["match_date"] >= "2022-08-14")],
                "23_24": self.LL_matches[(self.LL_matches["match_date"] <= "2024-05-25") & (self.LL_matches["match_date"] >= "2023-08-12")],
                "24_25": self.LL_matches[self.LL_matches["match_date"] >= "2024-08-18"]
            }
            
            season_CL_dataframes = {
                "19_20": self.LL_matches[(self.LL_matches["match_date"] <= "2021-05-22") & (self.LL_matches["match_date"] >= "2020-09-20")],
                "20_21": self.CL_matches[(self.CL_matches["match_date"] <= "2021-05-22") & (self.CL_matches["match_date"] >= "2020-09-20")],
                "21_22": self.CL_matches[(self.CL_matches["match_date"] <= "2022-05-28") & (self.CL_matches["match_date"] >= "2021-08-14")],
                "22_23": self.CL_matches[(self.CL_matches["match_date"] <= "2023-06-23") & (self.CL_matches["match_date"] >= "2022-08-14")],
                "23_24": self.CL_matches[(self.CL_matches["match_date"] <= "2024-06-01") & (self.CL_matches["match_date"] >= "2023-08-12")],
                "24_25": self.CL_matches[self.CL_matches["match_date"] >= "2024-08-18"]
            }
            
            for season in self.season_names:
                info(f"Sezon {season} - La Liga: {len(season_LL_dataframes[season])} meczów, Champions League: {len(season_CL_dataframes[season])} meczów")
                
            return season_LL_dataframes, season_CL_dataframes
            
        except Exception as e:
            error(f"Błąd podczas podziału na sezony: {str(e)}")
            error(traceback.format_exc())
            return {}, {}
    
    def calculate_playing_time(self, season_LL_dataframes: Dict, season_CL_dataframes: Dict) -> bool:
        """
        Oblicza czas gry dla zawodników w różnych sezonach i rozgrywkach.
        
        Metoda sumuje minuty gry dla każdego zawodnika w poszczególnych sezonach
        i rozgrywkach (La Liga, Champions League) oraz tworzy podsumowanie łącznego
        czasu gry. Wyniki są zapisywane jako nowe kolumny w DataFrame'ie real_player_csv.
        
        Args:
            season_LL_dataframes (Dict): Słownik DataFrame'ów dla sezonów La Liga
            season_CL_dataframes (Dict): Słownik DataFrame'ów dla sezonów Champions League
            
        Returns:
            bool: True jeśli operacja się powiodła, False w przypadku błędu
            
        Notes:
            - Tworzy kolumny z czasem gry dla każdego sezonu i każdej rozgrywki
            - Sumuje minuty gry dla każdego zawodnika w każdej kategorii
            - Weryfikuje poprawność obliczeń przez porównanie sum
            - Zastępuje wartości NaN zerami dla wszystkich kolumn czasu
        """
        try:
            for season in self.season_names:
                for comp in ["cl", "la_liga", "all"]:
                    col_name = f"playing_time_{season}_{comp}"
                    if col_name not in self.real_player_csv.columns:
                        self.real_player_csv[col_name] = 0
            
            self.real_player_csv["all_playing_time"] = 0
            
            season_data = {season: {"cl": {}, "la_liga": {}, "all": {}} for season in self.season_names}
            
            for i, season_name in enumerate(self.season_names):
                players_in_cl = season_CL_dataframes[season_name]["player_name"].unique()
                for player in players_in_cl:
                    cl_minutes = season_CL_dataframes[season_name].loc[
                        season_CL_dataframes[season_name]["player_name"] == player, "player_min"
                    ].sum()
                    season_data[season_name]["cl"][player] = cl_minutes
                    season_data[season_name]["all"][player] = cl_minutes
                
                players_in_la_liga = season_LL_dataframes[season_name]["player_name"].unique()
                for player in players_in_la_liga:
                    la_liga_minutes = season_LL_dataframes[season_name].loc[
                        season_LL_dataframes[season_name]["player_name"] == player, "player_min"
                    ].sum()
                    season_data[season_name]["la_liga"][player] = la_liga_minutes
                    
                    if player in season_data[season_name]["all"]:
                        season_data[season_name]["all"][player] += la_liga_minutes
                    else:
                        season_data[season_name]["all"][player] = la_liga_minutes
            
            for season in self.season_names:
                for player, minutes in season_data[season]["cl"].items():
                    mask = self.real_player_csv["player_name"] == player
                    if any(mask):
                        self.real_player_csv.loc[mask, f"playing_time_{season}_cl"] = minutes
                
                for player, minutes in season_data[season]["la_liga"].items():
                    mask = self.real_player_csv["player_name"] == player
                    if any(mask):
                        self.real_player_csv.loc[mask, f"playing_time_{season}_la_liga"] = minutes
                
                for player, minutes in season_data[season]["all"].items():
                    mask = self.real_player_csv["player_name"] == player
                    if any(mask):
                        self.real_player_csv.loc[mask, f"playing_time_{season}_all"] = minutes
                        current_total = self.real_player_csv.loc[mask, "all_playing_time"].values[0]
                        if pd.isna(current_total):
                            current_total = 0
                        self.real_player_csv.loc[mask, "all_playing_time"] = current_total + minutes
            
            time_columns = [col for col in self.real_player_csv.columns if 'playing_time' in col or col == 'all_playing_time']
            for col in time_columns:
                self.real_player_csv[col] = self.real_player_csv[col].fillna(0)
            
            info("Weryfikacja sum czasu gry dla zawodników:")
            for player in self.real_player_csv["player_name"].unique():
                mask = self.real_player_csv["player_name"] == player
                all_seasons_minutes = 0
                
                for season in self.season_names:
                    all_minutes_col = f"playing_time_{season}_all"
                    if all_minutes_col in self.real_player_csv.columns:
                        season_minutes = self.real_player_csv.loc[mask, all_minutes_col].values[0]
                        if not pd.isna(season_minutes):
                            all_seasons_minutes += float(season_minutes)
                
                current_all = self.real_player_csv.loc[mask, "all_playing_time"].values[0]
                if not pd.isna(current_all) and abs(current_all - all_seasons_minutes) > 1:
                    warning(f"Różnica dla {player}: Suma sezonów: {all_seasons_minutes}, all_playing_time: {current_all}")
                    self.real_player_csv.loc[mask, "all_playing_time"] = all_seasons_minutes
            
            info("\nPodsumowanie czasu gry dla pierwszych 5 zawodników:")
            for i, player in enumerate(self.real_player_csv["player_name"].unique()[:5]):
                seasons_played = []
                total_minutes = self.real_player_csv.loc[self.real_player_csv["player_name"] == player, "all_playing_time"].values[0]
                
                for season in self.season_names:
                    minutes = self.real_player_csv.loc[
                        self.real_player_csv["player_name"] == player, 
                        f"playing_time_{season}_all"
                    ].values[0]
                    if minutes > 0:
                        seasons_played.append(f"20{season[:2]}/20{season[3:]}")
                
                if total_minutes > 0:
                    info(f"{player}: {int(total_minutes)} minut w sezonach: {', '.join(seasons_played)}")
            
            return True
            
        except Exception as e:
            error(f"Błąd podczas obliczania czasu gry: {str(e)}")
            error(traceback.format_exc())
            return False
    
    def mark_seasons_played(self) -> bool:
        """
        Oznacza sezony, w których zawodnik brał udział.
        
        Metoda tworzy boolowskie oznaczenia dla każdego sezonu, wskazujące czy
        dany zawodnik występował w tym sezonie (w którejkolwiek z rozgrywek).
        Dodatkowo oblicza i zapisuje liczbę sezonów, w których każdy zawodnik grał.
        
        Returns:
            bool: True jeśli operacja się powiodła, False w przypadku błędu
            
        Notes:
            - Tworzy kolumny typu 'season_XX_YY' z wartościami 0/1 dla każdego sezonu
            - Sumuje liczbę sezonów z aktywnym udziałem zawodnika
            - Wartość 1 oznacza, że zawodnik grał w danym sezonie w La Liga lub Lidze Mistrzów
        """
        try:
            for season in range(len(self.season_names)):
                column_LL = f"playing_time_{self.season_names[season]}_la_liga"
                column_CL = f"playing_time_{self.season_names[season]}_cl"
                another_column_name = f"season_{self.season_names[season]}"
                
                self.real_player_csv[another_column_name] = np.where(
                    (self.real_player_csv[column_LL] > 0) | (self.real_player_csv[column_CL] > 0),
                    1,
                    0
                )
            
            season_columns = [f"season_{season}" for season in self.season_names]
            self.real_player_csv["seasons_played"] = self.real_player_csv[season_columns].sum(axis=1)
            
            info("Oznaczono sezony, w których zawodnicy brali udział")
            return True
            
        except Exception as e:
            error(f"Błąd podczas oznaczania sezonów: {str(e)}")
            error(traceback.format_exc())
            return False
    
    def calculate_player_ratings(self, season_LL_dataframes: Dict, season_CL_dataframes: Dict) -> bool:
        """
        Oblicza średnie oceny zawodników dla różnych sezonów i rozgrywek.
        
        Metoda oblicza średnie oceny zawodników (przyznawane przez edytorów i użytkowników)
        dla każdego sezonu i każdej kategorii rozgrywek. Dodatkowo tworzy łączne
        podsumowanie ocen dla wszystkich sezonów.
        
        Args:
            season_LL_dataframes (Dict): Słownik DataFrame'ów dla sezonów La Liga
            season_CL_dataframes (Dict): Słownik DataFrame'ów dla sezonów Champions League
            
        Returns:
            bool: True jeśli operacja się powiodła, False w przypadku błędu
            
        Notes:
            - Wylicza średnie oceny z pominięciem zerowych wartości
            - Tworzy osobne kolumny dla ocen edytorów i użytkowników
            - Rozróżnia między rozgrywkami La Liga i Ligi Mistrzów
            - Oblicza średnie oceny łącznie dla wszystkich sezonów
            - Zamienia wartości NaN na 0 dla czytelności
        """
        try:
            info("\nInicjalizacja kolumn ocen...")
            for season in self.season_names:
                for comp in ["la_liga", "cl"]:
                    for rater in ["editor", "users"]:
                        col_name = f"rating_{season}_{rater}_{comp}"
                        try:
                            if col_name in self.real_player_csv.columns:
                                self.real_player_csv[col_name] = self.real_player_csv[col_name].astype(float)
                            else:
                                self.real_player_csv[col_name] = 0.0
                        except Exception as e:
                            error(f"Błąd podczas konwersji kolumny {col_name}: {str(e)}")
            
            overall_columns = [
                "overall_rating_editor_la_liga", "overall_rating_editor_cl", 
                "overall_rating_users_la_liga", "overall_rating_users_cl"
            ]
            for col in overall_columns:
                try:
                    if col in self.real_player_csv.columns:
                        self.real_player_csv[col] = self.real_player_csv[col].astype(float)
                    else:
                        self.real_player_csv[col] = 0.0
                except Exception as e:
                    error(f"Błąd podczas inicjalizacji kolumny {col}: {str(e)}")
            
            info("\nPrzetwarzanie ocen dla wszystkich sezonów...")
            real_madrid_players = self.all_data["player_name"].unique()
            
            for i, season_name in enumerate(self.season_names):
                try:
                    season_ll = season_LL_dataframes[season_name]
                    
                    required_cols = ["user_rating", "editor_rating", "player_name"]
                    if not all(col in season_ll.columns for col in required_cols):
                        missing = [col for col in required_cols if col not in season_ll.columns]
                        warning(f"Brak kolumn {missing} w danych La Liga dla sezonu {season_name}, pomijam...")
                        continue
                        
                    for player in real_madrid_players:
                        try:
                            player_ll_ratings = season_ll[
                                (season_ll["user_rating"] != 0) & 
                                (season_ll["editor_rating"] != 0) & 
                                (season_ll["player_name"] == player)
                            ]
                            
                            mean_ll_users = player_ll_ratings["user_rating"].mean()
                            mean_ll_editor = player_ll_ratings["editor_rating"].mean()
                            
                            mask = self.real_player_csv["player_name"] == player
                            if any(mask) and not pd.isna(mean_ll_users):
                                self.real_player_csv.loc[mask, f"rating_{season_name}_users_la_liga"] = float(mean_ll_users)
                            if any(mask) and not pd.isna(mean_ll_editor):
                                self.real_player_csv.loc[mask, f"rating_{season_name}_editor_la_liga"] = float(mean_ll_editor)
                        except Exception as e:
                            error(f"Błąd podczas przetwarzania ocen La Liga dla zawodnika {player} w sezonie {season_name}: {str(e)}")
                    
                    season_cl = season_CL_dataframes[season_name]
                    
                    if not all(col in season_cl.columns for col in required_cols):
                        missing = [col for col in required_cols if col not in season_cl.columns]
                        warning(f"Brak kolumn {missing} w danych Champions League dla sezonu {season_name}, pomijam...")
                        continue
                        
                    for player in real_madrid_players:
                        try:
                            player_cl_ratings = season_cl[
                                (season_cl["user_rating"] != 0) & 
                                (season_cl["editor_rating"] != 0) & 
                                (season_cl["player_name"] == player)
                            ]
                            
                            mean_cl_users = player_cl_ratings["user_rating"].mean()
                            mean_cl_editor = player_cl_ratings["editor_rating"].mean()
                            
                            mask = self.real_player_csv["player_name"] == player
                            if any(mask) and not pd.isna(mean_cl_users):
                                self.real_player_csv.loc[mask, f"rating_{season_name}_users_cl"] = float(mean_cl_users)
                            if any(mask) and not pd.isna(mean_cl_editor):
                                self.real_player_csv.loc[mask, f"rating_{season_name}_editor_cl"] = float(mean_cl_editor)
                        except Exception as e:
                            error(f"Błąd podczas przetwarzania ocen Champions League dla zawodnika {player} w sezonie {season_name}: {str(e)}")
                except Exception as e:
                    error(f"Błąd podczas przetwarzania sezonu {season_name}: {str(e)}")
            
            self.real_player_csv = self.real_player_csv.fillna(0)
            
            info("\nObliczanie ogólnych rankingów...")
            for player in self.real_player_csv["player_name"].unique():
                try:
                    player_mask = self.real_player_csv["player_name"] == player
                    
                    editor_la_liga_ratings = []
                    for season in self.season_names:
                        try:
                            rating_col = f"rating_{season}_editor_la_liga"
                            if rating_col in self.real_player_csv.columns:
                                rating = self.real_player_csv.loc[player_mask, rating_col].values[0]
                                if rating > 0:
                                    editor_la_liga_ratings.append(rating)
                        except Exception as e:
                            error(f"Błąd podczas przetwarzania ocen edytorów La Liga dla {player} w sezonie {season}: {str(e)}")
                    
                    if editor_la_liga_ratings:
                        self.real_player_csv.loc[player_mask, "overall_rating_editor_la_liga"] = sum(editor_la_liga_ratings) / len(editor_la_liga_ratings)
                    
                    editor_cl_ratings = []
                    for season in self.season_names:
                        try:
                            rating_col = f"rating_{season}_editor_cl"
                            if rating_col in self.real_player_csv.columns:
                                rating = self.real_player_csv.loc[player_mask, rating_col].values[0]
                                if rating > 0:
                                    editor_cl_ratings.append(rating)
                        except Exception as e:
                            error(f"Błąd podczas przetwarzania ocen edytorów CL dla {player} w sezonie {season}: {str(e)}")
                    
                    if editor_cl_ratings:
                        self.real_player_csv.loc[player_mask, "overall_rating_editor_cl"] = sum(editor_cl_ratings) / len(editor_cl_ratings)
                    
                    users_la_liga_ratings = []
                    for season in self.season_names:
                        try:
                            rating_col = f"rating_{season}_users_la_liga"
                            if rating_col in self.real_player_csv.columns:
                                rating = self.real_player_csv.loc[player_mask, rating_col].values[0]
                                if rating > 0:
                                    users_la_liga_ratings.append(rating)
                        except Exception as e:
                            error(f"Błąd podczas przetwarzania ocen użytkowników La Liga dla {player} w sezonie {season}: {str(e)}")
                    
                    if users_la_liga_ratings:
                        self.real_player_csv.loc[player_mask, "overall_rating_users_la_liga"] = sum(users_la_liga_ratings) / len(users_la_liga_ratings)
                    
                    users_cl_ratings = []
                    for season in self.season_names:
                        try:
                            rating_col = f"rating_{season}_users_cl"
                            if rating_col in self.real_player_csv.columns:
                                rating = self.real_player_csv.loc[player_mask, rating_col].values[0]
                                if rating > 0:
                                    users_cl_ratings.append(rating)
                        except Exception as e:
                            error(f"Błąd podczas przetwarzania ocen użytkowników CL dla {player} w sezonie {season}: {str(e)}")
                    
                    if users_cl_ratings:
                        self.real_player_csv.loc[player_mask, "overall_rating_users_cl"] = sum(users_cl_ratings) / len(users_cl_ratings)
                except Exception as e:
                    error(f"Błąd podczas przetwarzania zawodnika {player}: {str(e)}")
            
            info("\nPodsumowanie ocen dla pierwszych 3 zawodników:")
            count = 0
            for player in self.real_player_csv["player_name"].unique():
                if count >= 3:
                    break
                
                ll_editor = self.real_player_csv.loc[self.real_player_csv["player_name"] == player, "overall_rating_editor_la_liga"].values[0]
                ll_users = self.real_player_csv.loc[self.real_player_csv["player_name"] == player, "overall_rating_users_la_liga"].values[0]
                cl_editor = self.real_player_csv.loc[self.real_player_csv["player_name"] == player, "overall_rating_editor_cl"].values[0]
                cl_users = self.real_player_csv.loc[self.real_player_csv["player_name"] == player, "overall_rating_users_cl"].values[0]
                
                if ll_editor > 0 or cl_editor > 0:
                    info(f"{player}:")
                    info(f"  La Liga - Edytorzy: {ll_editor:.2f}, Użytkownicy: {ll_users:.2f}")
                    info(f"  Champions League - Edytorzy: {cl_editor:.2f}, Użytkownicy: {cl_users:.2f}")
                    count += 1
            
            return True
            
        except Exception as e:
            error(f"Błąd podczas obliczania ocen zawodników: {str(e)}")
            error(traceback.format_exc())
            return False
    
    def mark_player_availability(self) -> bool:
        """
        Oznacza aktualnych i kontuzjowanych zawodników.
        
        Metoda dodaje do profili zawodników informacje o ich aktualnej dostępności
        i statusie w zespole. Oznacza aktualnych graczy oraz zawodników kontuzjowanych
        na podstawie predefiniowanej listy.
        
        Returns:
            bool: True jeśli operacja się powiodła, False w przypadku błędu
            
        Notes:
            - Tworzy kolumnę 'acctual_player' oznaczającą czy zawodnik jest aktywny w bieżącym sezonie
            - Tworzy kolumnę 'current_availability' informującą o dostępności zawodnika
            - Wartość 0 w 'current_availability' oznacza kontuzję lub brak w aktualnym składzie
            - Lista kontuzjowanych zawodników jest zdefiniowana jako atrybut klasy
        """
        try:
            self.real_player_csv["acctual_player"] = np.where(
                self.real_player_csv["playing_time_24_25_all"] > 0,
                1,
                0
            )
            
            self.real_player_csv["current_availability"] = 1
            
            self.real_player_csv["current_availability"] = np.where(
                self.real_player_csv["player_name"].isin(self.injured_players),
                0,
                self.real_player_csv["current_availability"]
            )
            
            self.real_player_csv["current_availability"] = np.where(
                self.real_player_csv["acctual_player"] == 0,
                0,
                self.real_player_csv["current_availability"]
            )
            
            info("Oznaczono aktualnych i kontuzjowanych zawodników")
            return True
            
        except Exception as e:
            error(f"Błąd podczas oznaczania dostępności zawodników: {str(e)}")
            error(traceback.format_exc())
            return False
    
    def save_results(self) -> bool:
        """
        Zapisuje przetworzone dane do plików CSV.
        
        Metoda zapisuje przetworzone dane zawodników do pliku CSV w katalogu
        wynikowym. Formatuje wartości liczbowe z dwoma miejscami po przecinku.
        
        Returns:
            bool: True jeśli operacja się powiodła, False w przypadku błędu
            
        Notes:
            - Zapisuje dane do pliku RM_players_stats.csv w katalogu output_dir
            - Używa formatu float_format="%.2f" dla czytelności numerów
            - Pomija indeksy podczas zapisu (index=False)
        """
        try:
            output_file = os.path.join(self.output_dir, "RM_players_stats.csv")
            self.real_player_csv.to_csv(output_file, index=False, float_format="%.2f")
            info(f"Zapisano statystyki zawodników do pliku: {output_file}")
            return True
            
        except Exception as e:
            error(f"Błąd podczas zapisywania wyników: {str(e)}")
            error(traceback.format_exc())
            return False
    
    def process_all(self) -> bool:
        """
        Wykonuje cały proces przetwarzania danych.
        
        Metoda realizuje kompletny proces analizy danych zawodników, wywołując
        sekwencyjnie wszystkie niezbędne metody klasy. Jeśli którykolwiek krok
        zakończy się niepowodzeniem, proces zostaje przerwany.
        
        Returns:
            bool: True jeśli cały proces zakończył się pomyślnie, False w przypadku błędu
            
        Notes:
            - Wykonuje wszystkie kroki analizy w odpowiedniej kolejności
            - Sprawdza wyniki każdego kroku i przerywa proces w razie błędu
            - Loguje informacje o rozpoczęciu i zakończeniu całego procesu
            - Używane metody: load_excel_files, merge_and_process_data, categorize_teams,
              prepare_player_profiles, create_season_splits, calculate_playing_time,
              mark_seasons_played, calculate_player_ratings, mark_player_availability, save_results
        """
        info("=== ROZPOCZĘCIE ANALIZY DANYCH PIŁKARZY REALU MADRYT ===")
        
        if not self.load_excel_files():
            error("Wczytywanie plików Excel nie powiodło się - przerywam przetwarzanie")
            return False
        
        merged_data = self.merge_and_process_data()
        if merged_data is None or merged_data.empty:
            error("Łączenie i przetwarzanie danych nie powiodło się - przerywam przetwarzanie")
            return False
        
        self.all_data = merged_data
        
        if not self.categorize_teams():
            error("Kategoryzacja drużyn nie powiodła się - przerywam przetwarzanie")
            return False
        
        if not self.prepare_player_profiles():
            error("Przygotowanie profili zawodników nie powiodło się - przerywam przetwarzanie")
            return False
        
        season_LL_dataframes, season_CL_dataframes = self.create_season_splits()
        if not season_LL_dataframes or not season_CL_dataframes:
            error("Podział na sezony nie powiódł się - przerywam przetwarzanie")
            return False
        
        if not self.calculate_playing_time(season_LL_dataframes, season_CL_dataframes):
            error("Obliczanie czasu gry nie powiodło się - przerywam przetwarzanie")
            return False
        
        if not self.mark_seasons_played():
            error("Oznaczanie sezonów nie powiodło się - przerywam przetwarzanie")
            return False
        
        if not self.calculate_player_ratings(season_LL_dataframes, season_CL_dataframes):
            error("Obliczanie ocen zawodników nie powiodło się - przerywam przetwarzanie")
            return False
        
        if not self.mark_player_availability():
            error("Oznaczanie dostępności zawodników nie powiodło się - przerywam przetwarzanie")
            return False
        
        if not self.save_results():
            error("Zapisywanie wyników nie powiodło się")
            return False
        
        info("=== ZAKOŃCZONO ANALIZĘ DANYCH PIŁKARZY REALU MADRYT ===")
        return True


def main():
    """
    Główna funkcja uruchamiająca przetwarzanie danych piłkarzy Realu Madryt.
    
    Funkcja tworzy instancję klasy RealMadridPlayersAnalyzer i uruchamia proces
    analizy. Na podstawie wyniku procesu wyświetla odpowiedni komunikat o statusie
    zakończenia programu.
    
    Notes:
        - Tworzy instancję analizatora
        - Wywołuje metodę process_all() wykonującą całą analizę
        - Wyświetla komunikat o powodzeniu lub niepowodzeniu programu
    """
    try:
        analyzer = RealMadridPlayersAnalyzer()
        success = analyzer.process_all()
        
        if success:
            info("Program zakończył pracę pomyślnie.")
            return 0
        else:
            error("Program zakończył pracę z błędami. Sprawdź logi, aby uzyskać więcej informacji.")
            return 1
    except Exception as e:
        critical(f"Wystąpił nieoczekiwany błąd: {str(e)}")
        critical(traceback.format_exc())
        return 2


if __name__ == "__main__":
    sys.exit(main())