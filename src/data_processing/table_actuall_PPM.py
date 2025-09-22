"""
Moduł obliczania dynamicznych statystyk PPM dla plików sezonowych LaLiga.

Ten skrypt dodaje do każdego pliku sezonowego kolumny PPM_H oraz PPM_A,
czyli punkty na mecz gospodarza i gościa liczone DYNAMICZNIE przed każdym meczem.
PPM jest obliczane na podstawie dotychczasowych wyników drużyn w bieżącym sezonie.

Moduł umożliwia:
- Przetwarzanie wielu plików sezonowych jednocześnie
- Obliczanie aktualnych punktów na mecz dla każdej drużyny
- Aktualizację plików CSV z danymi sezonowymi
"""

import os
import pandas as pd
import sys

current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from helpers.file_utils import FileUtils
from helpers.logger import info, warning, error, set_level, debug
from data_processing.data_processor import DataProcessor
# Import stałych z modułu const_variable
from data_processing.const_variable import SEASON_FILES # SEASON_DATES, SEASON_YEARS, SEASON_ID_TO_NAME

set_level("INFO")

class SeasonPPMCalculator:
    """
    Klasa odpowiedzialna za obliczanie punktów na mecz (PPM) dla gospodarza i gościa w plikach sezonowych.
    
    Klasa umożliwia obliczenie i dodanie do pliku sezonowego dwóch kolumn:
    - PPM_H: punkty na mecz zespołu gospodarzy przed danym meczem
    - PPM_A: punkty na mecz zespołu gości przed danym meczem
    
    PPM jest obliczane jako stosunek dotychczas zdobytych punktów do liczby rozegranych meczów.
    Dla każdego meczu w pliku, PPM jest obliczane na podstawie wyników wcześniejszych meczów,
    co daje dynamiczny obraz formy drużyn tuż przed każdym meczem.
    
    Attributes:
        file_path (str): Ścieżka do pliku CSV z danymi sezonu
        data_frame (pd.DataFrame): DataFrame z danymi sezonu
        team_points (dict): Słownik z punktami zdobytymi przez każdą drużynę
        team_matches_played (dict): Słownik z liczbą meczów rozegranych przez każdą drużynę
        ppm_home_team (list): Lista z PPM gospodarza dla każdego meczu
        ppm_away_team (list): Lista z PPM gościa dla każdego meczu
        file_utils (FileUtils): Instancja klasy pomocniczej do operacji na plikach
    """

    def __init__(self, file_path: str):
        """
        Inicjalizuje obiekt SeasonPPMCalculator.
        
        Args:
            file_path (str): Ścieżka do pliku CSV z danymi sezonu
        """
        self.file_path = file_path
        self.data_frame = None
        self.team_points: dict[int, int] = {}
        self.team_matches_played: dict[int, int] = {}
        self.ppm_home_team: list[float] = []
        self.ppm_away_team: list[float] = []
        self.file_utils = FileUtils()
        self.data_processor = DataProcessor(os.path.dirname(os.path.dirname(file_path)))

    def prepare_data(self) -> bool:
        """
        Przygotowuje dane przed obliczaniem PPM - standaryzuje nazwy drużyn i dodaje brakujące ID.
        
        Metoda standaryzuje nazwy drużyn według określonego słownika mapowań,
        a następnie dodaje identyfikatory drużyn (home_team_id i away_team_id) jeśli ich brakuje.
        
        Returns:
            bool: True jeśli dane zostały pomyślnie przygotowane, False w przypadku błędu
        """
        # Wczytaj dane
        df = self.file_utils.load_csv_safe(self.file_path)
        if df is None:
            error(f"Nie udało się wczytać pliku: {self.file_path}")
            return False
            
        # Sprawdź czy kolumny home_team i away_team istnieją
        if 'home_team' not in df.columns or 'away_team' not in df.columns:
            error(f"Brak kolumn home_team lub away_team w pliku {self.file_path}")
            return False
            
        # Standaryzuj nazwy drużyn
        _, df = self.data_processor.standardize_team_names(data=df)
        if df is None:
            error(f"Błąd podczas standaryzacji nazw drużyn w pliku {self.file_path}")
            return False
            
        # Sprawdź czy potrzeba dodać kolumny ID
        needs_id_columns = ('home_team_id' not in df.columns) or ('away_team_id' not in df.columns)
        
        if needs_id_columns:
            info(f"Dodawanie kolumn ID drużyn do pliku {self.file_path}")
            df = self.data_processor.add_team_ids_to_dataframe(df)
            if df is None:
                error(f"Błąd podczas dodawania ID drużyn do pliku {self.file_path}")
                return False
                
            # Zapisz plik z nowymi kolumnami
            success = self.file_utils.save_csv_safe(df, self.file_path, index=False)
            if not success:
                error(f"Nie udało się zapisać pliku z dodanymi ID drużyn: {self.file_path}")
                return False
            
            info(f"Zaktualizowano plik {self.file_path} - dodano kolumny ID drużyn")
        
        return True

    def load_data(self) -> bool:
        """
        Wczytuje dane z pliku CSV i weryfikuje obecność wymaganych kolumn.
        
        Metoda najpierw przygotowuje dane (standaryzacja nazw, dodanie ID), a następnie
        wczytuje plik CSV i sprawdza, czy zawiera wszystkie niezbędne kolumny
        do obliczenia PPM. Wymagane kolumny to: 'round', 'home_team_id', 'away_team_id',
        'home_goals', 'away_goals'.
        
        Returns:
            bool: True jeśli plik został poprawnie wczytany i zawiera wszystkie wymagane kolumny,
                  False w przeciwnym razie
        """
        # Przygotuj dane - standaryzuj nazwy i dodaj ID jeśli potrzeba
        if not self.prepare_data():
            return False
            
        # Wczytaj zaktualizowany plik
        self.data_frame = self.file_utils.load_csv_safe(self.file_path)
        if self.data_frame is None:
            error(f"Nie udało się wczytać pliku po przygotowaniu: {self.file_path}")
            return False
            
        # Sprawdź wymagane kolumny
        required_columns = ['round', 'home_team_id', 'away_team_id', 'home_goals', 'away_goals']
        for column in required_columns:
            if column not in self.data_frame.columns:
                error(f"Brak wymaganej kolumny '{column}' w pliku {self.file_path}")
                return False
                
        return True

    def calculate_ppm(self) -> None:
        """
        Oblicza punkty na mecz (PPM) dla gospodarza i gościa w każdym meczu.
        
        Metoda sortuje mecze według kolejki (i ewentualnie daty, jeśli jest dostępna),
        a następnie iteruje po meczach w kolejności chronologicznej. Dla każdego meczu:
        1. Oblicza PPM dla gospodarza i gościa na podstawie dotychczasowych wyników
        2. Aktualizuje liczbę rozegranych meczów przez obie drużyny
        3. Aktualizuje liczbę punktów zdobytych przez obie drużyny (3 za zwycięstwo, 1 za remis)
        
        Po zakończeniu iteracji, metoda dodaje obliczone wartości PPM jako nowe kolumny
        'PPM_H' i 'PPM_A' do DataFrame data_frame.
        
        Notes:
            - Dla drużyny, która nie rozegrała jeszcze żadnego meczu, PPM wynosi 0.0
            - PPM jest zaokrąglane do 3 miejsc po przecinku
            - Metoda pomija aktualizację punktów dla meczów bez znanego wyniku (NaN)
            - Drużyny są identyfikowane za pomocą ich identyfikatorów (home_team_id, away_team_id)
        """
        sort_columns = ['round']
        if 'match_date' in self.data_frame.columns:
            sort_columns.append('match_date')
        self.data_frame = self.data_frame.sort_values(by=sort_columns).reset_index(drop=True)

        for _, match_row in self.data_frame.iterrows():
            home_team_id = match_row['home_team_id']
            away_team_id = match_row['away_team_id']

            home_points = self.team_points.get(home_team_id, 0)
            home_matches = self.team_matches_played.get(home_team_id, 0)
            away_points = self.team_points.get(away_team_id, 0)
            away_matches = self.team_matches_played.get(away_team_id, 0)

            self.ppm_home_team.append(round(home_points / home_matches, 3) if home_matches > 0 else 0.0)
            self.ppm_away_team.append(round(away_points / away_matches, 3) if away_matches > 0 else 0.0)

            self.team_matches_played[home_team_id] = home_matches + 1
            self.team_matches_played[away_team_id] = away_matches + 1

            if pd.isna(match_row['home_goals']) or pd.isna(match_row['away_goals']):
                continue
            home_goals = int(match_row['home_goals'])
            away_goals = int(match_row['away_goals'])
            if home_goals > away_goals:
                self.team_points[home_team_id] = home_points + 3
                self.team_points[away_team_id] = away_points
            elif home_goals < away_goals:
                self.team_points[home_team_id] = home_points
                self.team_points[away_team_id] = away_points + 3
            else:
                self.team_points[home_team_id] = home_points + 1
                self.team_points[away_team_id] = away_points + 1

        self.data_frame['PPM_H'] = self.ppm_home_team
        self.data_frame['PPM_A'] = self.ppm_away_team

    def save(self) -> bool:
        """
        Zapisuje zaktualizowany DataFrame z kolumnami PPM do oryginalnego pliku CSV.
        
        Metoda wykorzystuje funkcję save_csv_safe z klasy FileUtils do bezpiecznego
        zapisania danych do pliku CSV. Po pomyślnym zapisie, informacja jest logowana.
        
        Returns:
            bool: True jeśli zapis się powiódł, False w przypadku błędu
            
        Notes:
            - Metoda nadpisuje oryginalny plik z dodatkowymi kolumnami PPM_H i PPM_A
            - Indeksy DataFrame nie są zapisywane do pliku (index=False)
        """
        success = self.file_utils.save_csv_safe(self.data_frame, self.file_path, index=False)
        if success:
            info(f"Zaktualizowano plik: {self.file_path} (dodano PPM_H, PPM_A)")
        return success

def main() -> None:
    """
    Główna funkcja programu, aktualizuje pliki sezonowe o kolumny PPM_H i PPM_A.
    
    Funkcja wykonuje następujące kroki:
    1. Inicjalizuje FileUtils i określa ścieżki do katalogu sezonów
    2. Sprawdza czy katalog z plikami sezonów istnieje, tworzy go jeśli nie
    3. Iteruje po zdefiniowanej liście plików sezonowych (SEASON_FILES)
    4. Dla każdego istniejącego pliku sezonu:
       a. Inicjalizuje SeasonPPMCalculator
       b. Wczytuje dane
       c. Oblicza PPM dla wszystkich meczów
       d. Zapisuje zaktualizowane dane do pliku
       
    Notes:
        - Informacje o postępie są logowane za pomocą modułu logger
        - Pliki, które nie istnieją, są pomijane z odpowiednim ostrzeżeniem
        - Obsługa błędów jest realizowana przez metody klasy SeasonPPMCalculator
    """
    info("=== ROZPOCZĘCIE AKTUALIZACJI PPM W PLIKACH SEZONÓW ===")
    
    file_utils = FileUtils()
    
    project_root = file_utils.get_project_root()
    debug(f"Katalog główny projektu: {project_root}")
    
    seasons_dir = os.path.join(project_root, "Data", "Mecze", "all_season")
    debug(f"Katalog z plikami sezonów: {seasons_dir}")
    
    if not os.path.exists(seasons_dir):
        warning(f"Katalog {seasons_dir} nie istnieje!")
        if file_utils.ensure_directory_exists(seasons_dir):
            info(f"Utworzono katalog {seasons_dir}")
        else:
            error(f"Nie można utworzyć katalogu {seasons_dir}")
            return

    for season_filename in SEASON_FILES:
        season_file_path = os.path.join(seasons_dir, season_filename)
        debug(f"Sprawdzanie pliku: {season_file_path}")
        
        if not os.path.exists(season_file_path):
            warning(f"Plik {season_file_path} nie istnieje. Pomijam.")
            continue
            
        calculator = SeasonPPMCalculator(season_file_path)
        if calculator.load_data():
            calculator.calculate_ppm()
            calculator.save()
            
    info("=== ZAKOŃCZONO AKTUALIZACJĘ PPM W PLIKACH SEZONÓW ===")

if __name__ == "__main__":
    main()