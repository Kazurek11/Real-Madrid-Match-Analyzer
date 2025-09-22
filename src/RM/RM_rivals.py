"""
Skrypt do tworzenia struktury katalogów dla rywali Real Madryt.

Funkcjonalność:
- Wczytuje dane identyfikacyjne rywali z pliku CSV
- Tworzy unikalne katalogi dla każdej drużyny w formacie ID_NAZWA
- Katalogi są tworzone w głównej strukturze projektu
- Wykorzystuje zaawansowane logowanie do śledzenia operacji
- Zaimplementowano podejście obiektowe z klasami Rival i RivalManager
- Tworzy pliki z bezpośrednimi spotkaniami (head-to-head)
- Tworzy pliki z aktualną formą rywali (ostatnie 6 meczów)
"""

import pandas as pd
import os
from pathlib import Path
import sys
import importlib
from helpers.logger import info, debug, warning, error, critical, set_level
from helpers.file_utils import FileUtils
def real_data():
    current_file_path = os.path.dirname(os.path.abspath(__file__))
    parent_file = os.path.dirname(current_file_path)
    real_madrid_path = os.path.join(parent_file, "Data","Real","RM_matches.csv")
    return pd.read_csv(real_madrid_path)

set_level("INFO")
    
class Rival:
    """
    Klasa reprezentująca rywala Real Madryt.
    Przechowuje dane identyfikacyjne i ścieżkę do katalogu z danymi rywala.
    """
    _rivals_data = None
    
    def __init__(self, rival_id):
        """
        Inicjalizuje obiekt rywala.
        
        Args:
            rival_id (int): Identyfikator rywala
        """
        if Rival._rivals_data is None:
            self._load_rivals_data()
            
        rival_info = self._find_rival_by_id(rival_id)
        if not rival_info:
            raise ValueError(f"Nie znaleziono rywala o ID: {rival_id}")
            
        self.id = rival_id
        self.name = rival_info["team_name"]
        self.folder_path = None
        self.h2h_file_path_home = None
        self.h2h_file_path_away = None
        self.h2h_file_path = None
    
    @classmethod
    def _load_rivals_data(cls):
        """Ładuje dane wszystkich rywali z pliku CSV do pamięci podręcznej."""
        data_path = os.path.join(FileUtils.get_project_root(), "Data", "Mecze", "id_nazwa", "rywale.csv")
        cls._rivals_data = FileUtils.load_csv_safe(data_path)
        debug(f"Załadowano dane {len(cls._rivals_data)} rywali do pamięci podręcznej")
    
    @classmethod
    def refresh_data(cls):
        """Odświeża dane rywali z pliku."""
        cls._rivals_data = None
        cls._load_rivals_data()
        info("Odświeżono dane rywali")
    
    def _find_rival_by_id(self, rival_id):
        """Znajduje dane konkretnego rywala po ID."""
        matches = Rival._rivals_data[Rival._rivals_data["team_id"] == rival_id]
        if len(matches) > 0:
            return matches.iloc[0]
        return None
    
    def get_folder_name(self):
        """Zwraca nazwę folderu dla rywala w formacie ID_NAZWA."""
        return f"{self.id}_{self.name}"
        
    def create_folder(self, base_path):
        """
        Tworzy folder dla rywala w podanej ścieżce bazowej.
        
        Args:
            base_path (str): Ścieżka bazowa dla folderów rywali
            
        Returns:
            bool: True jeśli folder został utworzony lub już istnieje, False w przypadku błędu
        """
        folder_name = self.get_folder_name()
        full_path = os.path.join(base_path, folder_name)
        
        try:
            if os.path.exists(full_path):
                debug(f"Katalog dla rywala {self.name} już istnieje: {full_path}")
                self.folder_path = full_path
                return True
                
            os.makedirs(full_path, exist_ok=True)
            self.folder_path = full_path
            info(f"Utworzono katalog dla rywala: {folder_name}")
            return True
        except Exception as e:
            error(f"Błąd podczas tworzenia katalogu dla {self.name}: {str(e)}")
            return False
            
    def create_h2h_file(self):
        """
        Tworzy plik z historią meczów bezpośrednich (head-to-head) w folderze rywala.
        
        Returns:
            bool: True jeśli plik został utworzony, False w przypadku błędu
        """
        if not self.folder_path:
            warning(f"Nie można utworzyć pliku H2H dla {self.name} - brak ścieżki do folderu")
            return False
            
        try:
            self.h2h_file_path_home = os.path.join(self.folder_path, f"{self.name}_home_h2h.csv")
            self.h2h_file_path_away = os.path.join(self.folder_path, f"{self.name}_away_h2h.csv")
            self.h2h_file_path = os.path.join(self.folder_path, f"{self.name}_h2h.csv")
            df = real_data()
            
            real_home = df[df['away_team_id'] == self.id].sort_values(by=['date'])
            real_away = df[df['home_team_id'] == self.id].sort_values(by=['date'])
            real_overall = pd.concat([real_home, real_away]).sort_values(by=['date'])
            
            real_home.to_csv(self.h2h_file_path_home, index=False)
            real_away.to_csv(self.h2h_file_path_away, index=False)
            real_overall.to_csv(self.h2h_file_path, index=False)
            debug(f"Plik H2H dla {self.name} przygotowany do utworzenia: {self.h2h_file_path}")
            return True
        except Exception as e:
            error(f"Błąd podczas tworzenia pliku H2H dla {self.name}: {str(e)}")
            return False
    
    def create_form_file(self, file_path_sezonu=None):
        """
        Tworzy plik z aktualną formą rywala (6 ostatnich meczów).
        
        Args:
            file_path_sezonu (str, optional): Ścieżka do pliku CSV z danymi sezonu.
                                          Jeśli None, używa domyślnych danych.
        
        Returns:
            bool: True jeśli plik został utworzony, False w przypadku błędu
        """
        if not self.folder_path:
            warning(f"Nie można utworzyć pliku formy dla {self.name} - brak ścieżki do folderu")
            return False
            
        if self.id == 1:
            info(f"Pomijanie tworzenia pliku formy dla Real Madryt (ID=1)")
            return False
        
        try:
            form_file_path = os.path.join(self.folder_path, f"{self.name}_actual_form.csv")
            
            table_league = importlib.import_module('table_league')
            League_Table = getattr(table_league, 'League_Table')
            
            if file_path_sezonu is None:
                current_path = os.path.dirname(os.path.abspath(__file__))
                parent_dir = os.path.dirname(current_path)
                file_path_sezonu = os.path.join(parent_dir, "Data", "Mecze", "all_season", "all_season.csv")
            
            league_table = League_Table(file_path_to_season=file_path_sezonu, season_year='all')
            
            form_data = league_table.check_form_team(team_name=self.name, last_matches=6)
            
            if form_data is None:
                warning(f"Brak danych o formie dla drużyny {self.name}")
                return False
            
            if isinstance(form_data, dict):
                form_df = pd.DataFrame([form_data])
            else:
                form_df = form_data
                
            form_df.to_csv(form_file_path, index=False)
            info(f"Utworzono plik formy dla rywala: {self.name}")
            
            detailed_file_path = os.path.join(self.folder_path, f"{self.name}_last_matches.csv")
            
            team_id = self.id
            
            all_data = pd.read_csv(file_path_sezonu)
            max_round = all_data['round'].max() if 'round' in all_data.columns else 38
            
            detailed_stats = league_table.check_team_stats(
                team_id=team_id, 
                kolejka_do=max_round,
                file_path_sezonu=file_path_sezonu
            )
            
            if detailed_stats and 'match_details' in detailed_stats:
                detailed_stats['match_details'].to_csv(detailed_file_path, index=False)
                info(f"Utworzono plik ze szczegółami ostatnich meczów dla: {self.name}")
            
            return True
            
        except Exception as e:
            error(f"Błąd podczas tworzenia pliku formy dla {self.name}: {str(e)}")
            return False

        

class RivalManager:
    """
    Klasa zarządzająca rywalami Real Madryt.
    Odpowiada za wczytywanie danych, tworzenie obiektów Rival i zarządzanie katalogami.
    """
    def __init__(self):
        """Inicjalizuje menedżera rywali."""
        self.rivals = []
        self.base_path = None
        
    def load_rivals_data(self, file_path):
        """
        Wczytuje dane o rywalach z pliku CSV i tworzy obiekty Rival.
        
        Args:
            file_path (str): Ścieżka do pliku CSV z danymi rywali
            
        Returns:
            bool: True jeśli dane zostały wczytane poprawnie, False w przypadku błędu
        """
        if not os.path.exists(file_path):
            error(f"Nie znaleziono pliku z danymi rywali: {file_path}")
            return False
        
        try:
            info(f"Wczytywanie danych rywali z: {file_path}")
            data = pd.read_csv(file_path)
            
            for idx, row in data.iterrows():
                if row["id_rywala"] == 1 or row['id_rywala'] == '1':
                    info(f"Pomijanie Real Madryt (ID=1) jako rywala")
                    continue
                rival = Rival(row['id_rywala'], row['nazwa_rywala'])
                self.rivals.append(rival)
                
            debug(f"Wczytano dane {len(self.rivals)} rywali")
            return True
        except Exception as e:
            error(f"Błąd podczas wczytywania danych rywali: {str(e)}")
            return False
            
    def set_base_path(self, path):
        """Ustawia ścieżkę bazową dla folderów rywali."""
        self.base_path = path
        
        try:
            os.makedirs(self.base_path, exist_ok=True)
            debug(f"Katalog bazowy istnieje lub został utworzony: {self.base_path}")
            return True
        except Exception as e:
            critical(f"Nie można utworzyć katalogu bazowego {self.base_path}: {str(e)}")
            return False
            
    def create_all_folders(self):
        """
        Tworzy foldery dla wszystkich rywali.
        
        Returns:
            int: Liczba pomyślnie utworzonych folderów
        """
        if not self.base_path:
            error("Nie ustawiono katalogu bazowego dla folderów rywali")
            return 0
            
        if not self.rivals:
            warning("Brak danych rywali do przetworzenia")
            return 0
        
        folders_created = 0
        for rival in self.rivals:
            if rival.create_folder(self.base_path):
                folders_created += 1
        
        return folders_created
    
    def create_all_h2h_files(self):
        """
        Tworzy pliki z historią meczów bezpośrednich (H2H) dla wszystkich rywali.
        
        Returns:
            int: Liczba pomyślnie utworzonych plików H2H
        """
        if not self.rivals:
            warning("Brak danych rywali do przetworzenia")
            return 0
            
        files_created = 0
        for rival in self.rivals:
            if not rival.folder_path:
                warning(f"Brak folderu dla rywala {rival.name}, pomijanie tworzenia plików H2H")
                continue
                
            try:
                debug(f"Próba utworzenia plików H2H dla rywala: {rival.name}")
                if rival.create_h2h_file():
                    files_created += 1
                    info(f"Utworzono pliki H2H dla rywala: {rival.name}")
            except Exception as e:
                error(f"Błąd podczas tworzenia plików H2H dla rywala {rival.name}: {str(e)}")
        
        return files_created
    
    def create_all_form_files(self, file_path_sezonu=None):
        """
        Tworzy pliki z aktualną formą dla wszystkich rywali (poza Realem Madryt).
        
        Args:
            file_path_sezonu (str, optional): Ścieżka do pliku CSV z danymi sezonu.
        
        Returns:
            int: Liczba pomyślnie utworzonych plików formy
        """
        if not self.rivals:
            warning("Brak danych rywali do przetworzenia")
            return 0
            
        files_created = 0
        for rival in self.rivals:
            if not rival.folder_path:
                warning(f"Brak folderu dla rywala {rival.name}, pomijanie tworzenia pliku formy")
                continue
                
            if rival.id == 1:
                continue
                
            try:
                debug(f"Próba utworzenia pliku formy dla rywala: {rival.name}")
                if rival.create_form_file(file_path_sezonu):
                    files_created += 1
                    info(f"Utworzono pliki formy dla rywala: {rival.name}")
            except Exception as e:
                error(f"Błąd podczas tworzenia pliku formy dla rywala {rival.name}: {str(e)}")
        
        return files_created

def main():
    """
    Główna funkcja skryptu tworząca foldery dla wszystkich rywali,
    pliki z bezpośrednimi spotkaniami (H2H) oraz pliki z aktualną formą.
    """
    info("=== ROZPOCZĘCIE TWORZENIA KATALOGÓW I PLIKÓW RYWALI ===")
    
    try:
        current_path = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_path)
        rival_path = os.path.join(parent_dir, "Data", "Mecze", "id_nazwa", "rywale.csv")
        path_to_rival_folders = os.path.join(parent_dir, "Data", "Rywale")
        
        real_madrid_data_path = os.path.join(parent_dir, "Data", "Real", "real_madrid_all_matches.csv")
        if not os.path.exists(real_madrid_data_path):
            warning(f"Plik z danymi meczów Real Madryt nie istnieje: {real_madrid_data_path}")
            warning("Najpierw uruchom skrypt real_madrid_match.py, aby utworzyć ten plik")
            sys.exit(1)
        
        manager = RivalManager()
        
        info("Wczytywanie danych rywali...")
        if not manager.load_rivals_data(rival_path):
            error("Nie udało się wczytać danych rywali. Skrypt zostanie zakończony.")
            sys.exit(1)
        
        if not manager.set_base_path(path_to_rival_folders):
            error("Nie udało się utworzyć katalogu bazowego. Skrypt zostanie zakończony.")
            sys.exit(1)
        
        info("Tworzenie folderów dla rywali...")
        folders_created = manager.create_all_folders()
        info(f"Utworzono {folders_created} katalogów dla rywali")
        
        info("Tworzenie plików z meczami bezpośrednimi (H2H)...")
        files_created = manager.create_all_h2h_files()
        info(f"Utworzono pliki H2H dla {files_created} rywali")
        
        info("Tworzenie plików z aktualną formą rywali...")
        season_data_path = os.path.join(parent_dir, "Data", "Mecze", "all_season", "all_season.csv")
        form_files_created = manager.create_all_form_files(season_data_path)
        info(f"Utworzono pliki formy dla {form_files_created} rywali")
        
        info(f"Przetworzono {len(manager.rivals)} rywali")
        info(f"Utworzono {folders_created} katalogów, pliki H2H dla {files_created} rywali i pliki formy dla {form_files_created} rywali")
        
        if folders_created != len(manager.rivals) or files_created != folders_created or form_files_created != folders_created:
            warning("Uwaga: Nie wszystkie katalogi, pliki H2H lub pliki formy zostały utworzone")
            warning(f"Liczba rywali: {len(manager.rivals)}, utworzonych katalogów: {folders_created}, utworzonych plików H2H: {files_created}, utworzonych plików formy: {form_files_created}")
        
        info("=== ZAKOŃCZENIE TWORZENIA KATALOGÓW I PLIKÓW RYWALI ===")
    
    except Exception as e:
        critical(f"Nieoczekiwany błąd podczas wykonywania skryptu: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()