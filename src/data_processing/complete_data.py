"""
Moduł do weryfikacji i uzupełniania danych w plikach sezonowych.

Ten skrypt weryfikuje kompletność danych w plikach sezonowych,
sprawdzając obecność wymaganych kolumn, ewentualnie je uzupełniając,
a następnie łącząc wszystkie pliki w jeden główny zbiór danych.
"""

import pandas as pd
import os
import sys
from typing import Dict, List, Tuple, Optional

current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from data_processing.const_variable import SEASON_FILES, COLUMN_MATCHES
from helpers.logger import info, debug, warning, error
from helpers.file_utils import FileUtils
from data_processing.data_processor import DataProcessor
from data_processing.merge_all_season_data import DataMerger
from data_processing.table_actuall_PPM import SeasonPPMCalculator

def verify_season_files_columns() -> Dict[str, Dict[str, bool]]:
    """
    Sprawdza czy wszystkie pliki sezonowe zawierają wymagane kolumny.
    
    Funkcja weryfikuje obecność podstawowych kolumn w każdym pliku sezonowym
    zdefiniowanym w SEASON_FILES.
    
    Returns:
        Dict[str, Dict[str, bool]]: Słownik wyników weryfikacji dla każdego pliku,
        zawierający informacje o obecności poszczególnych kolumn.
        
    Example:
        {
            'mecze_rywala_19_20.csv': {
                'match_date': True,
                'home_team': True,
                'away_team': True,
                'home_goals': False,
                ...
            },
            ...
        }
    """
    required_columns = [
        'match_date', 'home_team', 'away_team', 
        'home_goals', 'away_goals', 
        'home_odds', 'draw_odds', 'away_odds',
        'result', 'score',
        'home_team_id', 'away_team_id',
        'PPM_H', 'PPM_A',
        'home_odds_fair', 'draw_odds_fair', 'away_odds_fair'
    ]
    
    file_utils = FileUtils()
    project_root = file_utils.get_project_root()
    seasons_dir = os.path.join(project_root, "Data", "Mecze", "all_season")
    
    results = {}
    
    for file_name in SEASON_FILES:
        file_path = os.path.join(seasons_dir, file_name)
        results[file_name] = {}
        
        for col in required_columns:
            results[file_name][col] = False
            
        if not os.path.exists(file_path):
            warning(f"Plik {file_name} nie istnieje w katalogu {seasons_dir}")
            continue
            
        try:
            df = pd.read_csv(file_path)
            
            for col in required_columns:
                results[file_name][col] = col in df.columns
                
            missing_columns = [col for col in required_columns if not results[file_name][col]]
            if missing_columns:
                warning(f"W pliku {file_name} brakuje kolumn: {', '.join(missing_columns)}")
            else:
                info(f"Plik {file_name} zawiera wszystkie wymagane kolumny")
                
        except Exception as e:
            error(f"Błąd podczas przetwarzania pliku {file_name}: {str(e)}")
            
    return results

def complete_missing_columns(file_path: str) -> bool:
    """
    Uzupełnia brakujące kolumny w pliku CSV wykorzystując istniejące metody z innych modułów.
    
    Funkcja dodaje brakujące kolumny do pliku CSV przy użyciu metod z następujących modułów:
    - DataProcessor: do standardizacji nazw drużyn i dodania ID drużyn
    - DataMerger: do dodania kolumn score i result
    - DataProcessor: do usunięcia marży bukmacherskiej i dodania uczciwych kursów
    - SeasonPPMCalculator: do obliczenia PPM_H i PPM_A
    
    Args:
        file_path (str): Ścieżka do pliku CSV, który ma zostać uzupełniony
        
    Returns:
        bool: True jeśli operacja się powiodła, False w przypadku błędu
    """
    file_utils = FileUtils()
    data_dir = os.path.dirname(os.path.dirname(file_path))
    
    try:
        df = file_utils.load_csv_safe(file_path)
        if df is None:
            error(f"Nie można wczytać pliku: {file_path}")
            return False
            
        data_processor = DataProcessor(data_dir)
        
        updated, df = data_processor.standardize_team_names(data=df)
        if df is None:
            error(f"Błąd podczas standaryzacji nazw drużyn w pliku: {file_path}")
            return False
            
        if 'home_team_id' not in df.columns or 'away_team_id' not in df.columns:
            df = data_processor.add_team_ids_to_dataframe(df)
            if df is None:
                error(f"Błąd podczas dodawania ID drużyn do pliku: {file_path}")
                return False
                
        data_merger = DataMerger()
        
        if 'score' not in df.columns and 'home_goals' in df.columns and 'away_goals' in df.columns:
            df = data_merger.add_score_column(df)
            
        if 'result' not in df.columns and 'home_goals' in df.columns and 'away_goals' in df.columns:
            df = data_merger.add_result_column(df)
            
        odds_columns = ['home_odds_fair', 'draw_odds_fair', 'away_odds_fair']
        odds_exist = all(col in df.columns for col in odds_columns)
        
        if not odds_exist and all(col in df.columns for col in ['home_odds', 'draw_odds', 'away_odds']):
            temp_success = file_utils.save_csv_safe(df=df, file_path=file_path, index=False)
            if not temp_success:
                warning(f"Nie udało się zapisać tymczasowych zmian do pliku: {file_path}")
            
            odds_updated = data_processor.remove_bookmaker_margin(file_path)
            if odds_updated:
                df = file_utils.load_csv_safe(file_path)
                
        ppm_columns = ['PPM_H', 'PPM_A']
        ppm_exist = all(col in df.columns for col in ppm_columns)
        
        if not ppm_exist:
            temp_success = file_utils.save_csv_safe(df=df, file_path=file_path, index=False)
            if not temp_success:
                warning(f"Nie udało się zapisać tymczasowych zmian do pliku: {file_path}")
                
            ppm_calculator = SeasonPPMCalculator(file_path)
            if ppm_calculator.load_data():
                ppm_calculator.calculate_ppm()
                ppm_success = ppm_calculator.save()
                if ppm_success:
                    df = file_utils.load_csv_safe(file_path)
                else:
                    warning(f"Nie udało się zapisać PPM do pliku: {file_path}")
        
        if df is not None:
            success = file_utils.save_csv_safe(df=df, file_path=file_path, index=False)
            if success:
                info(f"Pomyślnie uzupełniono wszystkie brakujące kolumny w pliku: {file_path}")
            else:
                error(f"Nie udało się zapisać uzupełnionego pliku: {file_path}")
                return False
                
        return True
        
    except Exception as e:
        error(f"Błąd podczas uzupełniania kolumn w pliku {file_path}: {str(e)}")
        return False

def complete_all_season_files() -> Dict[str, bool]:
    """
    Uzupełnia brakujące kolumny we wszystkich plikach sezonowych.
    
    Returns:
        Dict[str, bool]: Słownik statusów operacji dla każdego pliku
    """
    file_utils = FileUtils()
    project_root = file_utils.get_project_root()
    seasons_dir = os.path.join(project_root, "Data", "Mecze", "all_season")
    
    results = {}
    
    info("Rozpoczynam uzupełnianie brakujących kolumn we wszystkich plikach sezonowych...")
    
    for file_name in SEASON_FILES:
        file_path = os.path.join(seasons_dir, file_name)
        
        if not os.path.exists(file_path):
            warning(f"Plik {file_name} nie istnieje w katalogu {seasons_dir}")
            results[file_name] = False
            continue
            
        info(f"Uzupełnianie brakujących kolumn w pliku: {file_name}")
        success = complete_missing_columns(file_path)
        results[file_name] = success
        
        if success:
            info(f"Pomyślnie zakończono uzupełnianie kolumn w pliku: {file_name}")
        else:
            warning(f"Wystąpiły problemy podczas uzupełniania kolumn w pliku: {file_name}")
            
    return results

def reorder_and_save_files() -> Dict[str, bool]:
    """
    Porządkuje kolumny we wszystkich plikach według wzoru COLUMN_MATCHES i zapisuje pliki.
    
    Funkcja:
    1. Ustawia kolumny w kolejności zgodnej z COLUMN_MATCHES
    2. Sprawdza czy nie ma wartości NaN w danych
    3. Zapisuje zaktualizowane pliki
    
    Returns:
        Dict[str, bool]: Słownik statusów operacji dla każdego pliku
    """
    file_utils = FileUtils()
    project_root = file_utils.get_project_root()
    seasons_dir = os.path.join(project_root, "Data", "Mecze", "all_season")
    data_merger = DataMerger()
    
    results = {}
    
    info("Rozpoczynam porządkowanie kolumn we wszystkich plikach sezonowych...")
    
    for file_name in SEASON_FILES:
        file_path = os.path.join(seasons_dir, file_name)
        
        if not os.path.exists(file_path):
            warning(f"Plik {file_name} nie istnieje w katalogu {seasons_dir}")
            results[file_name] = False
            continue
            
        try:
            info(f"Porządkowanie kolumn w pliku: {file_name}")
            
            df = file_utils.load_csv_safe(file_path)
            if df is None:
                error(f"Nie można wczytać pliku: {file_path}")
                results[file_name] = False
                continue
                
            data_merger.check_nan_value(df)
            
            available_columns = [col for col in COLUMN_MATCHES if col in df.columns]
            other_columns = [col for col in df.columns if col not in COLUMN_MATCHES]
            
            ordered_df = df[available_columns + other_columns]
            
            success = file_utils.save_csv_safe(df=ordered_df, file_path=file_path, index=False)
            results[file_name] = success
            
            if success:
                info(f"Pomyślnie uporządkowano kolumny w pliku: {file_name}")
            else:
                error(f"Nie udało się zapisać uporządkowanego pliku: {file_name}")
                
        except Exception as e:
            error(f"Błąd podczas porządkowania kolumn w pliku {file_name}: {str(e)}")
            results[file_name] = False
            
    return results

def merge_all_files_into_one() -> Optional[pd.DataFrame]:
    """
    Łączy wszystkie pliki sezonowe w jeden główny zbiór danych.
    
    Returns:
        Optional[pd.DataFrame]: DataFrame ze wszystkimi połączonymi danymi lub None w przypadku błędu
    """
    info("Rozpoczynam łączenie wszystkich plików sezonowych w jeden zbiór danych...")
    
    try:
        data_merger = DataMerger()
        
        columns_ok = data_merger.check_all_column()
        if not columns_ok:
            warning("Kolumny w plikach sezonowych nie są zgodne. Próba naprawy...")
            
            fixed = True
            for file_path in data_merger.get_season_files():
                if not data_merger.check_and_fix_columns(file_path):
                    fixed = False
                    error(f"Nie udało się naprawić kolumn w pliku: {file_path}")
            
            if not fixed:
                error("Nie wszystkie pliki zostały naprawione")
                return None
        
        success, all_matches_df = data_merger.process_and_save_data()
        
        if success and all_matches_df is not None:
            info(f"Pomyślnie połączono wszystkie pliki sezonowe. Otrzymano {len(all_matches_df)} wierszy danych.")
            return all_matches_df
        else:
            error("Nie udało się połączyć plików sezonowych.")
            return None
            
    except Exception as e:
        error(f"Błąd podczas łączenia plików sezonowych: {str(e)}")
        return None

def main():
    """
    Funkcja główna uruchamiająca weryfikację, uzupełnianie kolumn i łączenie plików sezonowych.
    """
    info("Rozpoczynanie weryfikacji plików sezonowych...")
    results = verify_season_files_columns()
    
    info("\n=== PODSUMOWANIE WERYFIKACJI PLIKÓW SEZONOWYCH ===")
    files_with_missing_columns = []
    
    for file_name, columns in results.items():
        missing = [col for col, present in columns.items() if not present]
        if missing:
            warning(f"{file_name}: Brakujące kolumny: {', '.join(missing)}")
            files_with_missing_columns.append(file_name)
        else:
            info(f"{file_name}: Wszystkie kolumny obecne")
    
    if files_with_missing_columns:
        info("\n=== UZUPEŁNIANIE BRAKUJĄCYCH KOLUMN ===")
        completion_results = complete_all_season_files()
        
        info("\n=== PODSUMOWANIE UZUPEŁNIANIA KOLUMN ===")
        for file_name, success in completion_results.items():
            if success:
                info(f"{file_name}: Pomyślnie uzupełniono kolumny")
            else:
                warning(f"{file_name}: Nie udało się uzupełnić wszystkich kolumn")
    else:
        info("\nWszystkie pliki mają kompletne kolumny. Nie wymaga uzupełnienia.")
    
    info("\n=== PORZĄDKOWANIE KOLUMN W PLIKACH ===")
    reorder_results = reorder_and_save_files()
    
    info("\n=== PODSUMOWANIE PORZĄDKOWANIA KOLUMN ===")
    for file_name, success in reorder_results.items():
        if success:
            info(f"{file_name}: Pomyślnie uporządkowano kolumny")
        else:
            warning(f"{file_name}: Nie udało się uporządkować kolumn")
    
    info("\n=== ŁĄCZENIE WSZYSTKICH PLIKÓW SEZONOWYCH ===")
    all_matches_df = merge_all_files_into_one()
    
    if all_matches_df is not None:
        info(f"Utworzono główny zbiór danych zawierający {len(all_matches_df)} wierszy.")
    else:
        warning("Nie udało się utworzyć głównego zbioru danych.")
    
    info("=== KONIEC PRZETWARZANIA DANYCH ===\n")
    return all_matches_df

if __name__ == "__main__":
    main()