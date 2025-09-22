"""
Moduł generowania tabel ligowych na podstawie danych meczowych LaLiga. Pomaga on sprawdzać komplementarność danych.

Ten skrypt tworzy tabele ligowe na podstawie plików CSV zawierających wyniki meczów.
Umożliwia generowanie tabel dla konkretnych przedziałów czasowych, analizę formy drużyn
oraz zapisywanie wyników do plików CSV.

Funkcjonalności:
- Przetwarzanie plików CSV z wynikami meczów z różnych sezonów (2021-2025)
- Obliczanie statystyk dla każdej drużyny: punkty, gole, bilans bramkowy
- Generowanie osobne zestawienia dla meczów domowych i wyjazdowych
- Tworzenie rankingów "all-time" łączące dane z wielu sezonów
- Zapisywanie wyników do plików CSV w folderze "results"
- Analizowanie formy drużyn na podstawie ostatnich 5 meczów
"""
import pandas as pd
import os
import datetime as dt
import re
import sys
from .table_actuall_PPM import SeasonPPMCalculator
from typing import Dict, List, Union, Any
from data_processing.const_variable import SEASON_FILES, SEASON_DATES, SEASON_YEARS, SEASON_ID_TO_NAME
current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from helpers.logger import info, debug, warning, error, critical, set_level
from helpers.file_utils import FileUtils
from RM.RM_rivals import Rival

set_level("INFO")

# # -------------------------------------------------------------------------
# # Stałe dotyczące sezonów - używane w table_actuall_PPM.py i table_league.py
# # -------------------------------------------------------------------------
# SEASON_FILES: List[str] = [
#     "mecze_rywala_19_20.csv",
#     "mecze_rywala_20_21.csv",
#     "mecze_rywala_21_22.csv",
#     "mecze_rywala_22_23.csv",
#     "mecze_rywala_23_24.csv",
#     "mecze_rywala_24_25.csv"
# ]

# # Lista dat początku i końca sezonów (format: ["YYYY-MM-DD", "YYYY-MM-DD"])
# SEASON_DATES: List[List[str]] = [
#     ["2019-08-16", "2020-07-19"],
#     ["2020-09-12", "2021-05-23"],
#     ["2021-08-13", "2022-05-22"],
#     ["2022-08-12", "2023-06-04"],
#     ["2023-08-11", "2024-05-26"],
#     ["2024-08-16", "2025-03-16"]
# ]

# # Identyfikatory lat sezonowych (format: "19_20" oznacza sezon 2019/2020)
# SEASON_YEARS: List[str] = ["19_20", "20_21", "21_22", "22_23", "23_24", "24_25"]

# # -------------------------------------------------------------------------
# # Mapowanie między identyfikatorami sezonów a ich pełnymi nazwami
# # -------------------------------------------------------------------------
# SEASON_ID_TO_NAME: Dict[str, str] = {
#     "19_20": "Sezon 2019/2020",
#     "20_21": "Sezon 2020/2021",
#     "21_22": "Sezon 2021/2022",
#     "22_23": "Sezon 2022/2023",
#     "23_24": "Sezon 2023/2024",
#     "24_25": "Sezon 2024/2025"
# }

def create_team_stats_template():
    """
    Tworzy szablon statystyk drużyny z wartościami początkowymi.
    
    Funkcja zwraca nowy słownik zawierający pola statystyk drużyny z zerowymi wartościami.
    Używanie szablonu zapobiega problemom z referencjami, które mogłyby wystąpić przy
    wielokrotnym używaniu tego samego słownika.
    
    Returns:
        dict: Słownik zawierający początkowe wartości statystyk drużyny:
            - matches: liczba rozegranych meczów
            - wins: liczba zwycięstw
            - draws: liczba remisów
            - losses: liczba porażek
            - goals_scored: liczba strzelonych goli
            - goals_conceded: liczba straconych goli
            - points: zdobyte punkty
            - home_matches: liczba meczów jako gospodarz
            - away_matches: liczba meczów jako gość
    """
    return {'matches': 0, 'wins': 0, 'draws': 0, 'losses': 0,
            'goals_scored': 0, 'goals_conceded': 0, 'points': 0,
            'home_matches': 0, 'away_matches': 0}

class League_Table:
    """
    Klasa odpowiedzialna za tworzenie i zarządzanie tabelami ligowymi.
    
    Umożliwia tworzenie tabel ligowych na podstawie danych meczowych w określonym przedziale
    czasowym. Obsługuje różne sezony ligowe, wylicza statystyki drużyn, sortuje tabelę
    według punktów i różnicy bramek oraz zapisuje wyniki do plików CSV.
    
    Attributes:
        file_path_data (str): Ścieżka do pliku z danymi meczów
        date_from (str): Data początkowa zakresu w formacie YYYY-MM-DD
        date_until (str): Data końcowa zakresu w formacie YYYY-MM-DD
        table (pd.DataFrame): DataFrame zawierający obliczoną tabelę ligową
        file_utils (FileUtils): Instancja klasy pomocniczej do operacji na plikach
        project_root (str): Ścieżka do głównego katalogu projektu
        data (pd.DataFrame): Wczytane dane meczowe
        rival (Rival): Instancja klasy Rival, jeśli tabela jest powiązana z konkretnym rywalem
        rival_id (int): ID rywala, jeśli tabela jest powiązana z konkretnym rywalem
        rival_name (str): Nazwa rywala, jeśli tabela jest powiązana z konkretnym rywalem
    """
    
    def __init__(self, file_path_data, date_from, date_until, rival_id=None):
        """
        Inicjalizuje tabelę ligową.
        
        Args:
            file_path_data (str): Ścieżka do pliku z danymi meczów
            date_from (str): Data początkowa w formacie YYYY-MM-DD
            date_until (str): Data końcowa w formacie YYYY-MM-DD
            rival_id (int, optional): ID rywala, jeśli chcemy powiązać tabelę z konkretnym rywalem
            
        Notes:
            - Inicjalizuje instancję FileUtils do operacji na plikach
            - Wczytuje dane meczowe z podanego pliku
            - Jeśli podano rival_id, inicjalizuje powiązanie z tym rywalem
            - Błędy są logowane za pomocą modułu logger
        """
        self.file_path_data = file_path_data
        self.date_from = date_from
        self.date_until = date_until
        self.table = None
        
        self.file_utils = FileUtils()
        self.project_root = self.file_utils.get_project_root()
        self.data = self.file_utils.load_csv_safe(file_path_data)
        
        self.rival = None
        self.rival_id = None
        self.rival_name = None
        
        if rival_id is not None:
            try:
                self.rival = Rival(rival_id)
                self.rival_id = self.rival.id
                self.rival_name = self.rival.name
                debug(f"Powiązano tabelę z rywalem: {self.rival_name} (ID: {self.rival_id})")
            except Exception as e:
                warning(f"Nie udało się zainicjalizować rywala o ID {rival_id}: {str(e)}")
        
    def update_date(self):
        """
        Aktualizuje dane na podstawie podanego zakresu dat.
        
        Metoda filtruje wczytane dane, pozostawiając tylko mecze rozegrane w zakresie
        od self.date_from do self.date_until. Jeśli kolumna match_date nie istnieje
        w danych, operacja nie zostanie wykonana.
        
        Notes:
            - Kolumna match_date jest konwertowana na typ datetime
            - Mecze spoza zakresu dat są usuwane z DataFrame
            - Błędy są logowane za pomocą modułu logger
            - Jeśli kolumna match_date nie istnieje, wyświetlany jest komunikat błędu
        """
        if "match_date" not in self.data.columns:
            error(f'Brak kolumny "match_date" w pliku pod ścieżką {self.file_path_data}')
            return
        
        self.data["match_date"] = pd.to_datetime(self.data["match_date"])
        self.data = self.data[(self.data["match_date"] >= pd.to_datetime(self.date_from)) & 
                             (self.data["match_date"] <= pd.to_datetime(self.date_until))]
        debug(f"Zaktualizowano dane do zakresu dat {self.date_from} - {self.date_until}")
        
    def check_season(self):
        """
        Określa sezon na podstawie zakresu dat self.date_from i self.date_until.
        
        Metoda porównuje podany zakres dat z predefiniowanymi datami sezonów zdefiniowanymi
        w stałych SEASON_DATES i zwraca identyfikator sezonu, jeśli zakres mieści się w którymś z sezonów.
        
        Returns:
            str: Identyfikator sezonu (np. "20_21", "21_22") lub None, gdy nie znaleziono pasującego sezonu
        """
        from datetime import datetime
        
        try:
            date_from = datetime.strptime(self.date_from, "%Y-%m-%d")
            date_until = datetime.strptime(self.date_until, "%Y-%m-%d")
        except ValueError as e:
            error(f"Nieprawidłowy format daty: {str(e)}")
            return None
        
        count = None
        for i, season in enumerate(SEASON_DATES):
            season_start = datetime.strptime(season[0], "%Y-%m-%d")
            season_end = datetime.strptime(season[1], "%Y-%m-%d")
            
            if date_from >= season_start and date_until <= season_end:
                count = i
                break
        
        if count is not None:
            return SEASON_YEARS[count]
        
        # Extract season from file_path_data if date range doesn't match any predefined season
        if hasattr(self, 'file_path_data') and self.file_path_data:
            file_name = os.path.basename(self.file_path_data)
            # Improved regex pattern to match various season formats in filenames
            season_match = re.search(r'(\d{2})_(\d{2})', file_name)
            if season_match:
                season_id = f"{season_match.group(1)}_{season_match.group(2)}"
                debug(f"Wyodrębniono sezon {season_id} z nazwy pliku {file_name}")
                return season_id
        
        warning(f"Nie znaleziono sezonu dla zakresu dat {self.date_from} - {self.date_until}")
        return None
            
    def reorder_columns(self):
        """
        Zmienia kolejność kolumn w tabeli na standardowy układ.
        
        Metoda reorganizuje kolumny w tabeli ligowej według predefiniowanego porządku,
        co zapewnia spójny układ danych we wszystkich generowanych tabelach. Kolumny,
        które nie są zdefiniowane w porządku standardowym, są dodawane na końcu.
        
        Returns:
            pd.DataFrame: DataFrame z uporządkowanymi kolumnami lub None, jeśli tabela nie została jeszcze obliczona
            
        Notes:
            - Jeśli tabela nie została jeszcze obliczona (self.table is None), zwracane jest None
            - Metoda nie usuwa żadnych kolumn, tylko zmienia ich kolejność
            - Kolumny, których nie ma w predefiniowanej liście, są umieszczane na końcu tabeli
            - Informacja o zmianie kolejności kolumn jest logowana
        """
        if self.table is None:
            warning("Tabela nie została jeszcze obliczona")
            return None
            
        desired_order = [
            'position', 'team_id', 'team_name', 'matches', 
            'home_matches', 'away_matches', 'wins', 'draws', 
            'losses', 'goals_scored', 'goals_conceded', 
            'goals_difference', 'points'
        ]
        
        available_columns = [col for col in desired_order if col in self.table.columns]
        other_columns = [col for col in self.table.columns if col not in desired_order]
        
        self.table = self.table[available_columns + other_columns]
        debug("Zmieniono kolejność kolumn w tabeli")
        
        return self.table           
        
    def calculate_table_for_two_dates(self):
        """
        Oblicza tabelę ligową dla zakresu dat od self.date_from do self.date_until.
        
        Metoda analizuje wszystkie mecze w podanym zakresie dat, oblicza statystyki dla każdej
        drużyny (punkty, gole, zwycięstwa, itd.) i tworzy posortowaną tabelę ligową.
        Tabela jest sortowana według punktów, różnicy bramek i liczby strzelonych goli.
        
        Returns:
            pd.DataFrame: Obliczona tabela ligowa jako DataFrame
            
        Notes:
            - Metoda przetwarza każdy mecz i aktualizuje statystyki obu drużyn
            - Tabela jest sortowana w kolejności: punkty (malejąco), różnica bramek (malejąco), 
              strzelone gole (malejąco)
            - Drużyny są identyfikowane przez ich ID, a nazwy są dodawane jeśli dostępne
            - Tabela zawiera kolumny: pozycja, ID drużyny, nazwa drużyny, mecze, zwycięstwa,
              remisy, porażki, strzelone gole, stracone gole, różnica bramek, punkty
            - Tabela jest zapisywana jako atrybut klasy (self.table)
        """
        debug(f"Rozpoczęcie obliczania tabeli dla danych ram czasowych od {self.date_from} do {self.date_until}")
        
        teams_stats = {}
        team_names = {}
        
        for _, match in self.data.iterrows():
            home_team = match['home_team_id']
            away_team = match['away_team_id']
            
            if 'home_team' in match and not pd.isna(match['home_team']):
                team_names[home_team] = match['home_team']
            if 'away_team' in match and not pd.isna(match['away_team']):
                team_names[away_team] = match['away_team']
            
            if home_team not in teams_stats:
                teams_stats[home_team] = create_team_stats_template()
            if away_team not in teams_stats:
                teams_stats[away_team] = create_team_stats_template()
            
            teams_stats[home_team]['matches'] += 1
            teams_stats[away_team]['matches'] += 1
            
            teams_stats[home_team]['home_matches'] += 1
            teams_stats[away_team]['away_matches'] += 1
            
            home_goals = match['home_goals']
            away_goals = match['away_goals']
            teams_stats[home_team]['goals_scored'] += home_goals
            teams_stats[home_team]['goals_conceded'] += away_goals
            teams_stats[away_team]['goals_scored'] += away_goals
            teams_stats[away_team]['goals_conceded'] += home_goals
            
            if home_goals > away_goals:
                teams_stats[home_team]['wins'] += 1
                teams_stats[home_team]['points'] += 3
                teams_stats[away_team]['losses'] += 1
            elif home_goals < away_goals:
                teams_stats[away_team]['wins'] += 1
                teams_stats[away_team]['points'] += 3
                teams_stats[home_team]['losses'] += 1
            else:
                teams_stats[home_team]['draws'] += 1
                teams_stats[home_team]['points'] += 1
                teams_stats[away_team]['draws'] += 1
                teams_stats[away_team]['points'] += 1
        
        table = pd.DataFrame.from_dict(teams_stats, orient='index')
        
        table['goals_difference'] = table['goals_scored'] - table['goals_conceded']
        
        if self.rival_id is not None:
            table['team_id'] = self.rival_id
            table['team_name'] = self.rival_name
            
        table = table.sort_values(by=['points', 'goals_difference', 'goals_scored'], 
                                 ascending=[False, False, False])
              
        table.reset_index(inplace=True)
        table.rename(columns={'index': 'team_id'}, inplace=True)
        
        if team_names:
            table['team_name'] = table['team_id'].map(team_names)
        
        table.insert(0, 'position', range(1, len(table) + 1))
        
        self.table = table
        period = f"{self.date_from} do {self.date_until}"
        debug(f"Zakończono obliczanie tabeli dla okresu od {period}")
        
        return table
    
    def save_or_update_file(self):
        """
        Zapisuje obliczoną tabelę ligową do pliku CSV w folderze wynikowym.
        
        Metoda tworzy folder wynikowy, jeśli nie istnieje, generuje nazwę pliku na podstawie
        sezonu lub zakresu dat i zapisuje tabelę do pliku CSV. Przed zapisem kolumny
        są reorganizowane za pomocą metody reorder_columns.
        
        Returns:
            str: Ścieżka do zapisanego pliku CSV lub None w przypadku błędu
            
        Notes:
            - Jeśli tabela nie została jeszcze obliczona, metoda automatycznie wywołuje
              calculate_table_for_two_dates()
            - Nazwa pliku jest generowana na podstawie identyfikatora sezonu lub zakresu dat
            - Metoda używa FileUtils do bezpiecznego zapisywania plików i tworzenia katalogów
            - Informacje o zapisie i ewentualne błędy są logowane
            - W przypadku błędu zwracana jest wartość None
        """
        if self.table is None:
            info("Tabela nie została jeszcze obliczona, obliczam...")
            self.calculate_table_for_two_dates()
        
        self.reorder_columns()
        try:
            save_directory = os.path.join(self.project_root,"Data", "Results")
            if not self.file_utils.ensure_directory_exists(save_directory):
                save_directory = self.file_utils.get_results_directory()
            
            season_id = self.check_season()
            if season_id:
                season_str = str(season_id).replace('_', '')
                filename = f"LL_table{season_str}.csv"
            else:
                filename = f"LL_table_{str(self.date_from)}-{str(self.date_until)}.csv"
            
            file_path = os.path.join(save_directory, filename)
            debug(f"Próba zapisu do pliku: {file_path}")
            
            if self.file_utils.save_csv_safe(df=self.table, file_path=file_path):
                info(f"Tabela zapisana do pliku: {file_path}")
                return file_path
            else:
                error(f"Nie udało się zapisać tabeli do pliku: {file_path}")
                return None
                
        except Exception as e:
            critical(f"BŁĄD KRYTYCZNY podczas zapisywania tabeli: {str(e)}")
            return None
        
    def get_last_5_matches(self, team_id):
        """
        Zwraca 5 ostatnich meczów drużyny przed datą self.date_until.
        
        Metoda filtruje mecze danej drużyny, sortuje je według dat i zwraca 5 ostatnich
        spotkań rozegranych przed datą końcową self.date_until.
        
        Args:
            team_id (int): ID drużyny
            
        Returns:
            pd.DataFrame: DataFrame zawierający 5 ostatnich meczów drużyny lub pusty DataFrame
                          jeśli dane są niedostępne lub brak kolumny match_date
                          
        Notes:
            - Metoda zwraca mecze, w których drużyna występowała jako gospodarz lub gość
            - Mecze są sortowane według daty, od najnowszych do najstarszych
            - Jeśli brak kolumny match_date, zwracany jest pusty DataFrame
            - Jeśli drużyna rozegrała mniej niż 5 meczów, zwracane są wszystkie dostępne mecze
        """
        team_matches = self.data.copy()
        
        team_matches = team_matches[(team_matches["home_team_id"] == team_id) | 
                                  (team_matches["away_team_id"] == team_id)]
        
        if "match_date" in team_matches.columns:
            team_matches["match_date"] = pd.to_datetime(team_matches["match_date"])
            
            team_matches = team_matches[team_matches["match_date"] <= pd.to_datetime(self.date_until)]
            
            team_matches = team_matches.sort_values(by="match_date", ascending=False)
            
            return team_matches.head(5)
        else:
            warning("Brak kolumny match_date w danych. Nie można analizować ostatnich meczów.")
            return pd.DataFrame()
        
    def check_form_team(self, team_id):
        """
        Analizuje formę drużyny na podstawie ostatnich 5 meczów od self.date_until.
        
        Metoda oblicza różne wskaźniki formy drużyny na podstawie jej ostatnich 5 meczów:
        średnie kursy, średnie gole strzelone i stracone, średnią różnicę bramek,
        średnią pozycję rywali oraz średnią zdobywanych punktów na mecz.
        
        Args:
            team_id (int): ID drużyny do analizy
                
        Returns:
            pd.DataFrame: DataFrame zawierający jeden wiersz ze statystykami formy drużyny:
                - OP_ODD_W_L5: Średni kurs na wygraną z ostatnich 5 meczów
                - OP_ODD_L_L5: Średni kurs na porażkę z ostatnich 5 meczów
                - OP_G_SCO_L5: Średnia goli zdobytych w ostatnich 5 meczach
                - OP_G_CON_L5: Średnia goli straconych w ostatnich 5 meczach
                - OP_GDIF_L5: Średnia różnica bramek w ostatnich 5 meczach
                - OP_OPP_POS_L5: Średnia pozycja rywali w ostatnich 5 meczach
                - OP_PPM_L5: Średnia punktów na mecz w ostatnich 5 meczach
                
        Notes:
            - Jeśli drużyna nie rozegrała żadnego meczu, zwracany jest DataFrame z zerami
            - Wartości są zaokrąglane do 3 miejsc po przecinku
            - Dla meczów u siebie i na wyjeździe stosowane są odpowiednie kolumny kursów i PPM
            - Jeśli brak danych o kursach lub PPM, są one pomijane w obliczeniach
        """
        last_matches = self.get_last_5_matches(team_id=team_id)
        
        if last_matches.empty:
            warning(f"Brak ostatnich meczów dla drużyny ID={team_id}")
            return pd.DataFrame({
                'team_id': [team_id],
                'OP_ODD_W_L5': [0.000],
                'OP_ODD_L_L5': [0.000],
                'OP_G_SCO_L5': [0.000],
                'OP_G_CON_L5': [0.000],
                'OP_GDIF_L5': [0.000],
                'OP_OPP_POS_L5': [0.000],
                'OP_PPM_L5': [0.000]
            })
        
        goals_scored = 0
        goals_conceded = 0
        points = 0
        opponent_positions = []
        win_odds_sum = 0
        loss_odds_sum = 0
        matches_count = len(last_matches)
        
        for _, match in last_matches.iterrows():
            is_home = match['home_team_id'] == team_id
            
            if is_home:
                team_goals = match['home_goals']
                opponent_goals = match['away_goals']
                
                if 'PPM_A' in match and not pd.isna(match['PPM_A']):
                    opponent_positions.append(match['PPM_A'])
                
                if 'home_odds_fair' in match and 'away_odds_fair' in match:
                    win_odds_sum += match['home_odds_fair']
                    loss_odds_sum += match['away_odds_fair']
            else:
                team_goals = match['away_goals']
                opponent_goals = match['home_goals']
                
                if 'PPM_H' in match and not pd.isna(match['PPM_H']):
                    opponent_positions.append(match['PPM_H'])
                
                if 'away_odds_fair' in match and 'home_odds_fair' in match:
                    win_odds_sum += match['away_odds_fair']
                    loss_odds_sum += match['home_odds_fair']
            
            goals_scored += team_goals
            goals_conceded += opponent_goals
            
            if team_goals > opponent_goals:
                points += 3
            elif team_goals == opponent_goals:
                points += 1
        
        avg_goals_scored = round(goals_scored / matches_count, 3) if matches_count > 0 else 0
        avg_goals_conceded = round(goals_conceded / matches_count, 3) if matches_count > 0 else 0
        avg_goal_difference = round(avg_goals_scored - avg_goals_conceded, 3)
        avg_points = round(points / matches_count, 3) if matches_count > 0 else 0
        avg_win_odds = round(win_odds_sum / matches_count, 3) if matches_count > 0 else 0
        avg_loss_odds = round(loss_odds_sum / matches_count, 3) if matches_count > 0 else 0
        
        avg_opponent_position = 0
        if opponent_positions:
            avg_opponent_position = round(sum(opponent_positions) / len(opponent_positions), 3)
        
        result_df = pd.DataFrame({
            'team_id': [team_id],
            'OP_ODD_W_L5': [avg_win_odds],
            'OP_ODD_L_L5': [avg_loss_odds],
            'OP_G_SCO_L5': [avg_goals_scored],
            'OP_G_CON_L5': [avg_goals_conceded],
            'OP_GDIF_L5': [avg_goal_difference],
            'OP_OPP_POS_L5': [avg_opponent_position],
            'OP_PPM_L5': [avg_points]
        })
        
        return result_df
       
def check_project_structure():
    """
    Sprawdza strukturę projektu i wyświetla diagnostykę.
    
    Funkcja weryfikuje istnienie kluczowych katalogów projektu, ich dostępność
    i zawartość. W przypadku braku wymaganych katalogów, próbuje je utworzyć.
    Wyniki diagnostyki są logowane za pomocą modułu logger.
    
    Returns:
        None
        
    Notes:
        - Funkcja sprawdza katalogi: Data, Data/Mecze, Data/Mecze/all_season, results
        - Dla każdego katalogu sprawdzane są: istnienie, uprawnienia do zapisu, zawartość
        - Jeśli katalog nie istnieje, podejmowana jest próba jego utworzenia
        - Wszystkie informacje i błędy są logowane za pomocą modułu logger
    """
    file_utils = FileUtils()
    
    project_root = file_utils.get_project_root()
    
    info("\n=== DIAGNOSTYKA STRUKTURY PROJEKTU ===")
    info(f"Katalog główny projektu: {project_root}")
    
    data_dir = os.path.join(project_root, "Data")
    mecze_dir = os.path.join(data_dir, "Mecze")
    all_season_dir = os.path.join(mecze_dir, "all_season")
    results_dir = file_utils.get_results_directory() or os.path.join(project_root, "results")
    
    dirs_to_check = [
        (data_dir, "Data"),
        (mecze_dir, "Data/Mecze"),
        (all_season_dir, "Data/Mecze/all_season"),
        (results_dir, "results")
    ]
    
    for dir_path, dir_name in dirs_to_check:
        if os.path.exists(dir_path):
            info(f"Katalog {dir_name} istnieje")
            
            if os.path.isdir(dir_path):
                if os.access(dir_path, os.W_OK):
                    info(f"Masz uprawnienia do zapisu w {dir_name}")
                else:
                    warning(f"BRAK uprawnień do zapisu w {dir_name}")
                
                try:
                    contents = os.listdir(dir_path)
                    if contents:
                        info(f"Katalog zawiera {len(contents)} elementów")
                    else:
                        warning(f"  ! Katalog {dir_name} jest pusty")
                except Exception as e:
                    error(f"Problem podczas sprawdzania zawartości katalogu {dir_name}: {str(e)}")
            else:
                error(f"{dir_name} nie jest katalogiem!")
        else:
            warning(f"Katalog {dir_name} NIE istnieje")
            
            if file_utils.ensure_directory_exists(dir_path):
                info(f"Utworzono katalog {dir_name}")
            else:
                error(f"Nie można utworzyć katalogu {dir_name}")
    
    info("======================================\n")

def main() -> None:
    """
    Główna funkcja skryptu, przetwarza pliki sezonowe i dodaje kolumny PPM.

    Funkcja dla każdego pliku sezonowego:
    1. Standaryzuje nazwy drużyn w formacie zgodnym z mapowaniem
    2. Dodaje identyfikatory drużyn (home_team_id, away_team_id) na podstawie pliku mapowania
    3. Oblicza punkty na mecz (PPM) dla każdej drużyny przed każdym meczem
    4. Zapisuje zaktualizowane pliki z nowymi kolumnami PPM_H i PPM_A

    Returns:
        None
        
    Notes:
        - Pliki sezonowe są określone w stałej SEASON_FILES
        - Funkcja ignoruje pliki, które nie istnieją
        - Funkcja raportuje postęp i błędy za pomocą modułu logger
        - Każdy plik jest przetwarzany niezależnie, błędy w jednym pliku nie wpływają na przetwarzanie pozostałych
    """
    info("Rozpoczynam obliczanie statystyk PPM dla plików sezonowych...")
    
    file_utils = FileUtils()
    project_root = file_utils.get_project_root()
    
    # Katalog z plikami sezonowymi
    seasons_dir = os.path.join(project_root, "Data", "Mecze", "all_season")
    
    # Sprawdź istnienie katalogu
    if not os.path.exists(seasons_dir):
        error(f"Katalog z plikami sezonowymi nie istnieje: {seasons_dir}")
        return
        
    # Przetwórz każdy plik sezonowy
    for file_name in SEASON_FILES:
        # Dodaj rozszerzenie .csv jeśli nie ma
        if not file_name.endswith('.csv'):
            file_name = f"{file_name}.csv"
            
        file_path = os.path.join(seasons_dir, file_name)
        
        # Sprawdź czy plik istnieje
        if not os.path.exists(file_path):
            warning(f"Plik {file_name} nie istnieje w katalogu {seasons_dir}")
            continue
            
        # Wyodrębnij sezon z nazwy pliku - poprawiona wersja
        try:
            # Próba wyodrębnienia sezonu z nazwy pliku
            season_match = re.search(r'(\d{2})_(\d{2})', file_name)
            if season_match:
                season_start = int(season_match.group(1))
                season_end = int(season_match.group(2))
                info(f"Przetwarzanie sezonu 20{season_start}-20{season_end} z pliku {file_name}...")
                
                # Określ daty dla danego sezonu
                season_id = f"{season_start}_{season_end}"
                idx = SEASON_YEARS.index(season_id) if season_id in SEASON_YEARS else -1
                
                if idx >= 0 and idx < len(SEASON_DATES):
                    date_from = SEASON_DATES[idx][0]
                    date_until = SEASON_DATES[idx][1]
                    
                    # Utwórz tabelę ligową dla tego sezonu
                    info(f"Tworzenie tabeli ligowej dla sezonu 20{season_start}-20{season_end}...")
                    league_table = League_Table(file_path, date_from, date_until)
                    league_table.update_date()
                    league_table.calculate_table_for_two_dates()
                    saved_path = league_table.save_or_update_file()
                    
                    if saved_path:
                        info(f"Zapisano tabelę ligową dla sezonu 20{season_start}-20{season_end} do {saved_path}")
                    else:
                        error(f"Nie udało się zapisać tabeli ligowej dla sezonu 20{season_start}-20{season_end}")
            else:
                warning(f"Nie można wyodrębnić sezonu z nazwy pliku: {file_name}")
                info(f"Przetwarzanie pliku {file_name}...")
        except Exception as e:
            warning(f"Nie można wyodrębnić sezonu z nazwy pliku: {file_name} ({str(e)})")
            info(f"Przetwarzanie pliku {file_name}...")
        
        # Utwórz i uruchom kalkulator PPM dla pliku
        calculator = SeasonPPMCalculator(file_path)
        
        if calculator.load_data():
            # W metodzie load_data wykonywane są kroki:
            # 1. Standaryzacja nazw drużyn (prepare_data)
            # 2. Dodanie ID drużyn na podstawie rywale.csv (prepare_data)
            
            # Oblicz PPM dla każdego meczu
            calculator.calculate_ppm()
            
            # Zapisz zaktualizowany plik
            if calculator.save():
                info(f"Pomyślnie zaktualizowano plik: {file_name}")
            else:
                error(f"Nie udało się zapisać pliku: {file_name}")
        else:
            error(f"Nie udało się wczytać lub przygotować danych z pliku: {file_name}")
            
    info("Zakończono obliczanie statystyk PPM.")

if __name__ == "__main__":
    main()