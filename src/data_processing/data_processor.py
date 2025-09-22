import os
import pandas as pd
import sys
import numpy as np
from data_processing.const_variable import TEAM_NAMES_MAPPING
current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from helpers.logger import info, error, warning, debug
from helpers.file_utils import FileUtils

class DataProcessor:
    """
    Klasa odpowiedzialna za przetwarzanie plików CSV z danymi meczowymi.
    
    Zapewnia funkcjonalności:
    - Standaryzację nazw drużyn według ustalonego słownika mapowań
    - Usuwanie marży bukmacherskiej z kursów poprzez obliczanie uczciwych kursów
    - Weryfikację zgodności identyfikatorów drużyn z ich nazwami
    - Dodawanie identyfikatorów drużyn do DataFrame na podstawie ich nazw
    - Zaokrąglanie kolumn numerycznych do określonej liczby miejsc po przecinku
    
    Klasa wykorzystuje słowniki mapowania nazw drużyn oraz ich identyfikatorów,
    co pozwala na spójną reprezentację danych we wszystkich plikach projektu.
    Logowanie operacji jest realizowane przy użyciu modułu logger.
    """
    
    def __init__(self, root_dir):
        """
        Inicjalizuje obiekt DataProcessor z konfiguracją ścieżek i mapowań.
        
        Args:
            root_dir (str): Ścieżka do głównego katalogu z danymi do przetwarzania.
                           Wszystkie podkatalogi będą rekurencyjnie przeszukiwane.
                           
        Attributes:
            root_dir (str): Główny katalog z danymi
            file_utils (FileUtils): Instancja klasy pomocniczej do operacji na plikach
            project_root (str): Ścieżka do głównego katalogu projektu
            team_names_variants (dict): Słownik mapowania standardowych nazw drużyn na ich warianty
            team_names_mapping (dict): Słownik jednoznacznych mapowań nazw drużyn na ich standardowe formy
            team_columns (list): Lista nazw kolumn, które potencjalnie zawierają nazwy drużyn
            odds_columns (list): Lista nazw kolumn z kursami bukmacherskimi
            id_to_name (dict): Słownik mapowania ID drużyn na nazwy
            name_to_id (dict): Słownik mapowania nazw drużyn na ich ID
            files_processed (int): Licznik przetworzonych plików
            files_with_errors (int): Licznik plików z wykrytymi błędami
            total_errors (int): Całkowita liczba znalezionych błędów
        """
        self.root_dir = root_dir
        self.file_utils = FileUtils()
        self.project_root = self.file_utils.get_project_root()
        
        self.team_names_variants = TEAM_NAMES_MAPPING
        #{
        #     'Real Madrid CF': ['Real Madrid', 'Real Madryt', 'Real Madrid CF', 'Madrid'],
        #     'FC Barcelona': ['Barcelona', 'FC Barcelona', 'Barca', 'Barça'],
        #     'Atletico Madrid': ["Atlético Madryt",'Atletico Madrid', 'Atlético Madrid', 'Atletico', 'Atlético','Atl. Madrid'],
        #     'Athletic Club': ['Athletic Bilbao', 'Athletic Club', 'Athletic','Ath Bilbao'],
        #     'Sevilla FC': ['Sevilla', 'Sevilla FC'],
        #     'Valencia CF': ['Valencia', 'Valencia CF'],
        #     'Villarreal CF': ['Villarreal', 'Villarreal CF'],
        #     'Real Sociedad': ['Real Sociedad', 'RSSS'],
        #     'Real Betis': ['Real Betis', 'Betis'],
        #     'RC Celta': ['Celta Vigo', 'RC Celta', 'Celta'],
        #     'CA Osasuna': ['Osasuna', 'CA Osasuna'],
        #     'RCD Mallorca': ['Mallorca', 'RCD Mallorca'],
        #     'RCD Espanyol': ['Espanyol', 'RCD Espanyol'],
        #     'Getafe CF': ['Getafe', 'Getafe CF'],
        #     'Elche CF': ['Elche', 'Elche CF'],
        #     'Granada CF': ['Granada', 'Granada CF'],
        #     'Rayo Vallecano': ['Rayo Vallecano', 'Rayo'],
        #     'Cádiz CF': ['Cadiz CF', 'Cádiz CF', 'Cadiz', 'Cádiz'],
        #     'Deportivo Alaves': ['Alaves', 'Deportivo Alavés', 'Alavés'],
        #     'Levante UD': ['Levante', 'Levante UD'],
        #     'UD Las Palmas': ['Las Palmas', 'UD Las Palmas'],
        #     'CD Leganes': ['Leganes', 'CD Leganes','Leganés','CD Leganés'],
        #     'SD Huesca': ['Huesca'],
        #     'SD Eibar':['Eibar'],
        #     'Girona FC':['Girona',"Girona FC","Girona CF"],
        #     'Real Valladolid': ['Valladolid', 'Real Valladolid'],
        #     'UD Almeria': ['UD Almería', 'Almeria','UD Almería']
        # }
        
        self.team_names_mapping = {}
        for standard_name, variants in self.team_names_variants.items():
            for variant in variants:
                self.team_names_mapping[variant] = standard_name
        
        self.team_columns = ["gospodarz","gosc",'home_team', 'away_team', 'team', 
                             'opponent_name', 'team_name','nazwa_rywala','rival','rivals']
        
        self.odds_columns = ["home_odds", "draw_odds", "away_odds"]
        
        self.id_to_name = {}
        self.name_to_id = {}
        
        self.files_processed = 0
        self.files_with_errors = 0
        self.total_errors = 0
    
    def standardize_team_names(self, data=None, file_path=None):
        """
        Standaryzuje nazwy drużyn w DataFrame lub pliku CSV.
        
        Metoda wyszukuje kolumny zawierające nazwy drużyn i zastępuje różne warianty nazw
        ich standardowymi odpowiednikami zgodnie ze słownikiem mapowań. Zapewnia to spójność
        nazewnictwa we wszystkich plikach projektu.
        
        Args:
            data (pd.DataFrame, optional): DataFrame z danymi do standaryzacji.
                Jeśli podany, zmiany są dokonywane na kopii, a oryginał pozostaje niezmieniony.
            file_path (str, optional): Ścieżka do pliku CSV, który ma zostać przetworzony.
                Jeśli podana, plik zostanie wczytany, przetworzony i nadpisany zmodyfikowaną zawartością.
                
        Returns:
            tuple: (updated, df) gdzie:
                - updated (bool): True jeśli nazwy drużyn zostały zmienione, False w przeciwnym przypadku
                - df (pd.DataFrame): Zaktualizowany DataFrame lub None w przypadku błędu
                
        Raises:
            Exception: W przypadku błędów podczas przetwarzania, szczegóły są zapisywane w logach.
            
        Notes:
            - Jeśli podano zarówno data jak i file_path, priorytet ma parametr data
            - Zmiany zostają zapisane do pliku tylko jeśli wykryto faktyczne różnice w nazwach
            - Operacja nie zmienia innych kolumn ani struktury danych
        """
        try:
            df = None
            
            if data is not None:
                df = data.copy()
                source = "przekazany DataFrame"
            elif file_path is not None:
                df = self.file_utils.load_csv_safe(file_path)
                source = f"plik {file_path}"
                
                if df is None:
                    error(f"Nie można wczytać pliku: {file_path}")
                    return False, None
            else:
                error("Nie podano ani DataFrame ani ścieżki do pliku")
                return False, None
                    
            original_df = df.copy()
            
            columns_to_update = [col for col in self.team_columns if col in df.columns]
            
            if columns_to_update:
                for col in columns_to_update:
                    df[col] = df[col].replace(self.team_names_mapping)
                    
                if not df.equals(original_df):
                    info(f"Zaktualizowano nazwy drużyn w {source}")
                    
                    if file_path is not None:
                        sort_by = columns_to_update[0] if columns_to_update else None
                        success = self.file_utils.save_csv_safe(
                            df=df, 
                            file_path=file_path, 
                            index=False,
                            sort_by=sort_by
                        )
                        if not success:
                            warning(f"Nie udało się zapisać zmian do pliku: {file_path}")
                            return False, df
                            
                    return True, df
                else:
                    info(f"Brak zmian w nazwach drużyn w {source}")
                    return False, df
            else:
                info(f"Brak kolumn z nazwami drużyn w {source}")
                return False, df
                
        except Exception as e:
            error(f"Błąd podczas standaryzacji nazw drużyn: {str(e)}")
            return False, None
    
    def remove_bookmaker_margin(self, file_path):
        """
        Usuwa marżę z kursów bukmacherskich w pliku CSV i dodaje nowe kolumny z "uczciwymi" kursami.
        
        Metoda oblicza tzw. "uczciwe kursy" (fair odds) poprzez usunięcie marży bukmacherskiej
        z oryginalnych kursów. Kursy bez marży są zaokrąglane do 2 miejsc po przecinku i zapisywane
        jako nowe kolumny z przyrostkiem "_fair".
        
        Args:
            file_path (str): Ścieżka do pliku CSV zawierającego kolumny z kursami bukmacherskimi
            
        Returns:
            bool: True jeśli plik został pomyślnie zmodyfikowany, False w przypadku błędu
                 lub gdy plik nie zawiera wymaganych kolumn kursów
        
        Notes:
            - Wymagane kolumny: "home_odds", "draw_odds", "away_odds"
            - Dodawane kolumny: "home_odds_fair", "draw_odds_fair", "away_odds_fair"
            - Algorytm usuwania marży zakłada, że marża jest równomiernie rozłożona na wszystkie kursy
            - Zmodyfikowany plik jest zapisywany pod tą samą ścieżką, nadpisując oryginalny plik
        """
        try:
            df = self.file_utils.load_csv_safe(file_path)
            if df is None:
                error(f"Nie można wczytać pliku: {file_path}")
                return False
            
            if not all(col in df.columns for col in self.odds_columns):
                info(f"Brak kolumn kursów: {self.odds_columns} w pliku: {file_path}")
                return False
                
            # Oblicz prawdopodobieństwa implikowane przez kursy
            data_odds = df[self.odds_columns]
            implied_probs = 1 / data_odds
            margin = implied_probs.sum(axis=1)
            fair_probs = implied_probs.div(margin, axis=0)
            fair_odds = 1 / fair_probs
            
            # Dodaj nowe kolumny do DataFrame z zaokrągleniem do 2 miejsc po przecinku
            df["home_odds_fair"] = fair_odds["home_odds"].round(2)
            df["draw_odds_fair"] = fair_odds["draw_odds"].round(2)
            df["away_odds_fair"] = fair_odds["away_odds"].round(2)
            
            # Zapisz plik z nowymi kolumnami
            success = self.file_utils.save_csv_safe(
                df=df, 
                file_path=file_path, 
                index=False, 
                sort_by=None
            )
            
            if success:
                info(f"Dodano kolumny z kursami bez marży do pliku: {file_path} (zaokrąglone do 2 miejsc po przecinku)")
                return True
            else:
                error(f"Nie udało się zapisać pliku po usunięciu marży: {file_path}")
                return False
            
        except Exception as e:
            error(f"Błąd podczas usuwania marży w pliku {file_path}: {str(e)}")
            return False
    
    def process_all_files(self):
        """
        Przetwarza wszystkie pliki CSV w katalogu głównym i jego podkatalogach.
        
        Metoda rekurencyjnie przeszukuje wszystkie katalogi w poszukiwaniu plików CSV
        i wykonuje dla każdego z nich operacje standaryzacji nazw drużyn oraz usuwania
        marży bukmacherskiej z kursów.
        
        Returns:
            tuple: (processed_files, names_updated, odds_updated)
                - processed_files (int): Liczba przetworzonych plików CSV
                - names_updated (int): Liczba plików, w których zaktualizowano nazwy drużyn
                - odds_updated (int): Liczba plików, w których dodano kursy bez marży
                
        Notes:
            - Operacje są wykonywane sekwencyjnie dla każdego pliku
            - Szczegółowe informacje o przetwarzaniu są zapisywane w logach
            - Metoda nie przerywa przetwarzania w przypadku błędów z pojedynczym plikiem
        """
        processed_files = 0
        names_updated = 0
        odds_updated = 0
        
        info(f"Rozpoczynam przetwarzanie plików CSV w katalogu: {self.root_dir}")
        
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.csv'):
                    file_path = os.path.join(root, file)
                    processed_files += 1
                    
                    info(f"Przetwarzam plik ({processed_files}): {file_path}")
                    updated, _ = self.standardize_team_names(file_path=file_path)
                    if updated:
                        names_updated += 1
                    
                    if self.remove_bookmaker_margin(file_path):
                        odds_updated += 1
        
        info(f"Zakończono przetwarzanie.")
        info(f"Przetworzono plików: {processed_files}")
        info(f"Zaktualizowano nazwy drużyn w {names_updated} plikach")
        info(f"Dodano kursy bez marży w {odds_updated} plikach")
        
        return processed_files, names_updated, odds_updated
    
    
    def load_team_id_template(self) -> bool:
        """
        Wczytuje mapowania identyfikatorów drużyn z pliku szablonowego.
        
        Metoda wczytuje plik 'rywale.csv' zawierający mapowania ID drużyn do ich nazw
        i przygotowuje dwukierunkowe słowniki mapowań, które będą używane do weryfikacji
        spójności identyfikatorów z nazwami w plikach danych.
        
        Returns:
            bool: True jeśli mapowania zostały pomyślnie wczytane, 
                  False w przypadku błędu lub braku wymaganych kolumn
        
        Notes:
            - Lokalizacja pliku szablonu: "[project_root]/Data/Mecze/id_nazwa/rywale.csv"
            - Wymagane kolumny: 'team_id' i 'team_name' (lub ich alternatywy)
            - W przypadku braku pliku lub problemów z wczytaniem, informacje są zapisywane w logach
            - Obsługiwane są alternatywne nazwy kolumn: 'id_rywala' zamiast 'team_id' 
              oraz 'nazwa_rywala' zamiast 'team_name'
        """
        try:
            template_path = os.path.join(self.project_root, "Data", "Mecze", "id_nazwa", "rywale.csv")
    
            debug(f"Próba wczytania szablonu z: {template_path}")
            template_df = self.file_utils.load_csv_safe(template_path)
            
            if template_df is None:
                error(f"Nie można wczytać pliku szablonu: {template_path}")
                return False
                
            if template_df.empty:
                error(f"Plik szablonu jest pusty: {template_path}")
                return False
                
            required_columns = ['team_id', 'team_name']
            
            column_alternatives = {
                'team_id': ['team_id', 'id_rywala'],
                'team_name': ['team_name', 'nazwa_rywala']
            }
            
            column_mapping = {}
            
            for req_col in required_columns:
                found = False
                for alt_col in column_alternatives[req_col]:
                    if alt_col in template_df.columns:
                        column_mapping[req_col] = alt_col
                        found = True
                        break
                
                if not found:
                    error(f"Brak wymaganej kolumny '{req_col}' w szablonie. Dostępne kolumny: {template_df.columns.tolist()}")
                    return False
            
            id_col = column_mapping['team_id']
            name_col = column_mapping['team_name']
            
            self.id_to_name = dict(zip(template_df[id_col], template_df[name_col]))
            self.name_to_id = dict(zip(template_df[name_col], template_df[id_col]))
            
            info(f"Wczytano szablon z {len(self.id_to_name)} powiązaniami ID-nazwa drużyny.")
            return True
            
        except FileNotFoundError:
            error(f"Nie znaleziono pliku szablonu")
            return False
        except Exception as e:
            error(f"Błąd podczas wczytywania szablonu: {str(e)}")
            return False
    
    def validate_team_ids_in_file(self, file_path: str) -> list:
        """
        Weryfikuje spójność identyfikatorów drużyn z ich nazwami w pliku CSV.
        
        Metoda sprawdza, czy identyfikatory drużyn gospodarzy i gości odpowiadają
        ich nazwom zgodnie z wczytanym szablonem mapowań. Wykrywa niezgodności
        takie jak nieprawidłowe ID dla danej nazwy lub nieprawidłowa nazwa dla danego ID.
        
        Args:
            file_path (str): Ścieżka do pliku CSV, który ma zostać zweryfikowany
            
        Returns:
            list: Lista wykrytych błędów w formacie [(wiersz, opis_błędu), ...], 
                  gdzie wiersz to indeks DataFrame (wiersz - 1 w pliku CSV).
                  Pusta lista oznacza brak błędów.
        
        Notes:
            - Metoda wymaga wcześniejszego wywołania load_team_id_template()
            - Weryfikowane są pary kolumn: home_team/home_team_id oraz away_team/away_team_id
            - Plik CSV musi zawierać co najmniej jedną z tych par kolumn
            - Wartości NaN są ignorowane podczas weryfikacji
        """
        errors = []
        
        try:
            df = self.file_utils.load_csv_safe(file_path)
            if df is None:
                error(f"Nie można wczytać pliku: {file_path}")
                errors.append((-1, f"Błąd wczytywania pliku: {file_path}"))
                return errors
            
            home_cols = {"home_team", "home_team_id"}.issubset(df.columns)
            away_cols = {"away_team", "away_team_id"}.issubset(df.columns)
            
            if not (home_cols or away_cols):
                debug(f"Plik {file_path} nie zawiera kolumn drużyn i ID do walidacji.")
                return errors
                
            for idx, row in df.iterrows():
                if home_cols:
                    self._check_team_id_consistency(row["home_team_id"], row["home_team"], "home", idx, errors)
                
                if away_cols:
                    self._check_team_id_consistency(row["away_team_id"], row["away_team"], "away", idx, errors)
                    
            return errors
            
        except Exception as e:
            error(f"Błąd podczas walidacji pliku {file_path}: {str(e)}")
            errors.append((-1, f"Błąd przetwarzania: {str(e)}"))
            return errors
    
    def _check_team_id_consistency(self, team_id, team_name, team_type: str, row_idx: int, errors: list) -> None:
        """
        Sprawdza spójność identyfikatora drużyny z jej nazwą.
        
        Metoda pomocnicza, która weryfikuje zgodność pary (ID, nazwa) drużyny z mapowaniami 
        z szablonu. Wykrywa niezgodności w obu kierunkach mapowania. Błędy są dodawane
        do przekazanej listy.
        
        Args:
            team_id: Identyfikator drużyny do weryfikacji
            team_name: Nazwa drużyny do weryfikacji
            team_type (str): Typ drużyny ("home" lub "away")
            row_idx (int): Indeks wiersza w DataFrame, w którym sprawdzana jest para
            errors (list): Lista, do której dodawane są wykryte błędy
            
        Returns:
            None: Metoda nie zwraca wartości, a jedynie modyfikuje przekazaną listę errors
            
        Notes:
            - Metoda ignoruje wartości NaN
            - Wykrywane są cztery rodzaje błędów:
                1. Nieprawidłowy typ danych ID lub nazwy
                2. Nieznane ID drużyny (nie istnieje w szablonie)
                3. Nieznana nazwa drużyny (nie istnieje w szablonie)
                4. Niezgodność między ID a nazwą (nie pasują do siebie)
            - Błędy są dodawane do listy w formacie (indeks_wiersza, opis_błędu)
        """
        try:
            if pd.isna(team_id) or pd.isna(team_name):
                return
                
            try:
                team_id = int(team_id)
                team_name = str(team_name).strip()
            except (ValueError, TypeError):
                errors.append((row_idx, f"Nieprawidłowy typ danych: {team_type}_team_id={team_id}, {team_type}_team='{team_name}'"))
                return
                
            if team_id in self.id_to_name:
                expected_name = self.id_to_name[team_id]
                if team_name != expected_name:
                    errors.append((row_idx, f"{team_type}_team_id={team_id} ma nazwę '{team_name}', powinno być '{expected_name}'"))
            else:
                errors.append((row_idx, f"Nieznane {team_type}_team_id={team_id}"))
                
            if team_name in self.name_to_id:
                expected_id = self.name_to_id[team_name]
                if team_id != expected_id:
                    errors.append((row_idx, f"{team_type}_team='{team_name}' ma ID {team_id}, powinno być {expected_id}"))
            else:
                errors.append((row_idx, f"Nieznana nazwa {team_type}_team='{team_name}'"))
                
        except Exception as e:
            errors.append((row_idx, f"Błąd podczas sprawdzania spójności: {str(e)}"))
    
    def validate_all_team_ids(self) -> bool:
        """
        Weryfikuje spójność identyfikatorów drużyn z ich nazwami we wszystkich plikach CSV.
        
        Metoda rekurencyjnie przeszukuje wszystkie katalogi w poszukiwaniu plików CSV
        i weryfikuje spójność identyfikatorów drużyn z ich nazwami. Gromadzi statystyki
        dotyczące liczby przetworzonych plików, plików z błędami i całkowitej liczby błędów.
        
        Returns:
            bool: True jeśli nie znaleziono błędów we wszystkich plikach,
                  False jeśli wykryto błędy lub wystąpił problem podczas weryfikacji
        
        Notes:
            - Metoda automatycznie wczytuje szablon mapowań ID <-> nazwa
            - Szczegółowe informacje o weryfikacji i wykrytych błędach są zapisywane w logach
            - Błędy są raportowane z numerem wiersza w pliku (numeracja od 1, z uwzględnieniem nagłówka)
            - Metoda aktualizuje atrybuty klasy: files_processed, files_with_errors i total_errors
        """
        if not self.load_team_id_template():
            error("Nie można przeprowadzić weryfikacji bez poprawnego szablonu ID drużyn.")
            return False
        
        all_ok = True
        self.files_processed = 0
        self.files_with_errors = 0
        self.total_errors = 0
        
        info(f"=== ROZPOCZĘCIE WERYFIKACJI SPÓJNOŚCI ID DRUŻYN ===")
        info(f"Rozpoczynam sprawdzanie powiązań ID drużyn w katalogu: {self.root_dir}")
        
        try:
            for root, _, files in os.walk(self.root_dir):
                for file_name in files:
                    if not file_name.lower().endswith('.csv'):
                        continue
                        
                    file_path = os.path.join(root, file_name)
                    self.files_processed += 1
                    info(f"Sprawdzanie pliku ({self.files_processed}): {file_path}")
                    
                    file_errors = self.validate_team_ids_in_file(file_path)
                    
                    if file_errors:
                        self.files_with_errors += 1
                        self.total_errors += len(file_errors)
                        all_ok = False
                        
                        error(f"Znaleziono {len(file_errors)} błędów w pliku: {file_path}")
                        for row_idx, err_msg in file_errors:
                            error(f"  - Wiersz {row_idx+2}: {err_msg}")  # +2 bo indeksujemy od 0, a wiersz 1 to nagłówki
                    else:
                        info(f"Plik poprawny: {file_path}")
            
            info("=== PODSUMOWANIE WERYFIKACJI ===")
            info(f"Przeszukano plików CSV: {self.files_processed}")
            
            if all_ok:
                info("Wszystkie pliki są poprawne. Nie znaleziono niezgodności.")
            else:
                warning(f"Znaleziono {self.total_errors} błędów w {self.files_with_errors} plikach.")
            
            info("=== ZAKOŃCZONO WERYFIKACJĘ SPÓJNOŚCI ID DRUŻYN ===")
            
            return all_ok
            
        except Exception as e:
            error(f"Błąd podczas weryfikacji katalogów: {str(e)}")
            return False
        
    def for_name_return_id(self, name_of_team):
        """
        Zwraca identyfikator drużyny na podstawie jej nazwy.
        
        Metoda wczytuje plik mapowania drużyn i wyszukuje identyfikator odpowiadający
        podanej nazwie drużyny. W przeciwieństwie do metody load_team_id_template(),
        ta metoda jest przeznaczona do jednorazowych odwołań do identyfikatorów drużyn.
        
        Args:
            name_of_team (str): Nazwa drużyny, dla której ma zostać odnaleziony identyfikator
                
        Returns:
            int lub None: Identyfikator drużyny (team_id) jeśli znaleziono w pliku mapowania,
                         None jeśli nie znaleziono dopasowania lub wystąpił błąd
        
        Notes:
            - Metoda wczytuje plik mapowania przy każdym wywołaniu, co może być nieefektywne
              przy wielokrotnych odwołaniach - w takim przypadku lepiej użyć load_team_id_template()
            - Lokalizacja pliku: "[project_root]/Data/Mecze/id_nazwa/rywale.csv"
        """
        data = self.file_utils.load_csv_safe(
            os.path.join(self.project_root, "Data", "Mecze", "id_nazwa", "rywale.csv")
        )
        
        if data is None:
            error(f"Nie można wczytać pliku mapowania drużyn")
            return None
        
        for _, row in data.iterrows():
            if row["team_name"] == name_of_team:
                return row["team_id"]
        
        return None

    def add_team_ids_to_dataframe(self, df):
        """
        Dodaje identyfikatory drużyn do DataFrame na podstawie ich nazw.
        
        Metoda analizuje DataFrame w poszukiwaniu kolumn z nazwami drużyn (home_team, away_team)
        i dodaje odpowiadające im identyfikatory (home_team_id, away_team_id) poprzez
        odwołanie do pliku mapowania drużyn.
        
        Args:
            df (pd.DataFrame): DataFrame zawierający co najmniej kolumny home_team i away_team
                              z nazwami drużyn
            
        Returns:
            pd.DataFrame: Zaktualizowany DataFrame z dodanymi lub uzupełnionymi kolumnami
                         home_team_id i away_team_id
                         
        Notes:
            - Jeśli kolumny ID już istnieją, są aktualizowane tylko brakujące wartości
            - Metoda nie modyfikuje wartości ID, które już istnieją w DataFrame
            - W przypadku braku dopasowania nazwy drużyny do ID, odpowiednie pole pozostaje NaN
            - Metoda nie modyfikuje oryginalnego DataFrame, zwraca jego zaktualizowaną kopię
            - Dla dużej liczby wierszy, metoda może być wolna ze względu na wczytywanie
              pliku mapowania przy każdym odwołaniu
        """
        try:
            if df is None or df.empty:
                error("Przekazany DataFrame jest pusty")
                return df
                
            if "home_team" not in df.columns or "away_team" not in df.columns:
                error("Brak wymaganych kolumn home_team i/lub away_team w DataFrame")
                return df
                
            # Kopia DataFrame, aby nie modyfikować oryginału
            result_df = df.copy()
            
            # Inicjalizuj kolumny ID drużyn, jeśli nie istnieją
            if "home_team_id" not in result_df.columns:
                result_df["home_team_id"] = pd.NA
                
            if "away_team_id" not in result_df.columns:
                result_df["away_team_id"] = pd.NA
                
            # Dla każdego wiersza znajdź ID na podstawie nazwy drużyny
            for index, row in result_df.iterrows():
                # Dodaj ID drużyny gospodarzy, jeśli brakuje
                if pd.isna(row["home_team_id"]):
                    home_id = self.for_name_return_id(row["home_team"])
                    if home_id is not None:
                        result_df.at[index, "home_team_id"] = home_id
                    
                # Dodaj ID drużyny gości, jeśli brakuje
                if pd.isna(row["away_team_id"]):
                    away_id = self.for_name_return_id(row["away_team"])
                    if away_id is not None:
                        result_df.at[index, "away_team_id"] = away_id
            
            return result_df
                
        except Exception as e:
            error(f"Błąd podczas dodawania ID drużyn do DataFrame: {str(e)}")
            return df
    
    def round_numeric_columns(self, df, decimals=3):
        """
        Zaokrągla wszystkie kolumny numeryczne w DataFrame do określonej liczby miejsc po przecinku.
        
        Metoda identyfikuje wszystkie kolumny numeryczne w DataFrame i zaokrągla ich wartości
        do żądanej precyzji. Jest przydatna do ujednolicenia prezentacji danych liczbowych
        oraz zmniejszenia rozmiaru plików.
        
        Args:
            df (pd.DataFrame): DataFrame zawierający dane do zaokrąglenia
            decimals (int, optional): Liczba miejsc po przecinku do zaokrąglenia (domyślnie: 3)
            
        Returns:
            pd.DataFrame: Nowy DataFrame z zaokrąglonymi wartościami w kolumnach numerycznych
                         lub oryginalny DataFrame, jeśli był pusty lub nie zawierał kolumn numerycznych
                         
        Notes:
            - Zaokrąglane są tylko kolumny typu float64 i int64
            - Metoda nie modyfikuje oryginalnego DataFrame, zwraca jego zaktualizowaną kopię
            - Dla kolumn typu int64, zaokrąglenie nie zmienia wartości, ale zapewnia spójność
              w przypadku konwersji typów danych
        """
        if df is None or df.empty:
            return df
        
        rounded_df = df.copy()
        numeric_columns = rounded_df.select_dtypes(include=['float64', 'int64']).columns
        
        for col in numeric_columns:
            rounded_df[col] = rounded_df[col].round(decimals)
        
        return rounded_df       

if __name__ == "__main__":
    file_utils = FileUtils()
    project_root = file_utils.get_project_root()
    data_dir = os.path.join(project_root, "Data")
    processor = DataProcessor(data_dir)
    
    print("\n=== PRZETWARZANIE DANYCH CSV ===")
    print(f"Katalog źródłowy: {data_dir}")
    print("\nWybierz operację do wykonania:")
    print("1. Standaryzuj nazwy drużyn")
    print("2. Usuń marżę z kursów bukmacherskich")
    print("3. Wykonaj obie operacje (1 + 2)")
    print("4. Weryfikuj spójność ID drużyn")
    print("5. Wykonaj wszystkie operacje (1 + 2 + 4)")
    print("0. Wyjdź bez zmian")
    
    try:
        choice = int(input("\nTwój wybór (0-5): "))
        
        if choice == 1:
            processed_files = 0
            names_updated = 0
            
            info("Rozpoczynam standaryzację nazw drużyn...")
            for root, _, files in os.walk(data_dir):
                for file in files:
                    if file.endswith('.csv'):
                        if file == "rywale_polskie_nazwy.csv":
                            info(f"Pomijam standaryzację pliku: {file} (zachowuję oryginalne nazwy polskie)")
                            continue
                        file_path = os.path.join(root, file)
                        processed_files += 1
                        info(f"Przetwarzam plik ({processed_files}): {file_path}")
                        if processor.standardize_team_names(file_path=file_path):
                            names_updated += 1
            
            info(f"Zakończono standaryzację nazw drużyn.")
            info(f"Przetworzono plików: {processed_files}")
            info(f"Zaktualizowano nazwy w {names_updated} plikach")
        
        elif choice == 2:
            processed_files = 0
            odds_updated = 0
            
            info("Rozpoczynam usuwanie marży z kursów...")
            for root, _, files in os.walk(data_dir):
                for file in files:
                    if file.endswith('.csv'):
                        file_path = os.path.join(root, file)
                        processed_files += 1
                        info(f"Przetwarzam plik ({processed_files}): {file_path}")
                        if processor.remove_bookmaker_margin(file_path):
                            odds_updated += 1
            
            info(f"Zakończono usuwanie marży z kursów.")
            info(f"Przetworzono plików: {processed_files}")
            info(f"Zmodyfikowano kursy w {odds_updated} plikach")
        
        elif choice == 3:
            processor.process_all_files()
        
        elif choice == 4:
            processor.validate_all_team_ids()
            
        elif choice == 5:
            info("Wykonywanie wszystkich operacji na plikach...")
            processor.process_all_files()
            processor.validate_all_team_ids()
        
        elif choice == 0:
            info("Wyjście bez zmian.")
        
        else:
            error("Nieprawidłowy wybór. Dozwolone opcje: 0-5.")
    
    except ValueError:
        error("Nieprawidłowy format wyboru. Wprowadź liczbę od 0 do 5.")
    except Exception as e:
        error(f"Wystąpił nieoczekiwany błąd: {str(e)}")