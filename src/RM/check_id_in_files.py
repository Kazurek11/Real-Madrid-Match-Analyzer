import numpy as np
import pandas as pd
import os
from pathlib import Path
from helpers.logger import error, info, warning

CURRENT_PATH = os.path.dirname(__file__)
PROJECT_PATH = os.path.dirname(CURRENT_PATH)
project_filepath = PROJECT_PATH


def check_match_id_consistency(project_filepath):
    """
    Sprawdza spójność wartości match_id w trzech plikach:
    - all_matches.csv
    - RM_matches.csv
    - filtered_real_madrid_data_20_25.csv
    
    Bierze pod uwagę, że filtered_real_madrid_data zawiera wiele wierszy na mecz
    (jeden dla każdego zawodnika).
    
    Args:
        project_filepath (str): Ścieżka do głównego katalogu projektu
    
    Returns:
        bool: True jeśli wszystkie ID są spójne, False w przeciwnym razie
    """
    info("Rozpoczynam sprawdzanie spójności identyfikatorów meczów między plikami...")
    
    # Definiowanie ścieżek do plików
    file_all_season = os.path.join(project_filepath, 'Data', "Mecze", 'all_season', "all_matches.csv")
    file_RM_matches = os.path.join(project_filepath, 'Data', "Real", 'RM_matches.csv')
    filtered_data_path = os.path.join(project_filepath, 'Data', 'Real', 'filtered_real_madrid_data_20_25.csv')
    
    info(f"Ścieżki do plików:")
    info(f"  - all_matches.csv: {file_all_season}")
    info(f"  - RM_matches.csv: {file_RM_matches}")
    info(f"  - filtered_real_madrid_data_20_25.csv: {filtered_data_path}")
    
    # Sprawdzenie czy wszystkie pliki istnieją
    missing_files = []
    for filepath in [file_all_season, file_RM_matches, filtered_data_path]:
        if not os.path.exists(filepath):
            missing_files.append(filepath)
    
    if missing_files:
        for filepath in missing_files:
            error(f"Nie znaleziono pliku: {filepath}")
        return False
    
    # Wczytywanie plików danych
    try:
        info("Wczytuję plik all_matches.csv...")
        all_season = pd.read_csv(file_all_season)
        info(f"Pomyślnie wczytano plik all_matches.csv - znaleziono {len(all_season)} wierszy")
        
        info("Wczytuję plik RM_matches.csv...")
        try:
            RM_matches = pd.read_csv(file_RM_matches, index_col='match_id')
            RM_matches = RM_matches.reset_index()
            info("Plik RM_matches.csv zawiera match_id jako indeks - zresetowano indeks do kolumny")
        except:
            RM_matches = pd.read_csv(file_RM_matches)
            info("Wczytano plik RM_matches.csv bez indeksu")
        info(f"Pomyślnie wczytano plik RM_matches.csv - znaleziono {len(RM_matches)} wierszy")
        
        info("Wczytuję plik filtered_real_madrid_data_20_25.csv...")
        filtered_data = pd.read_csv(filtered_data_path)
        info(f"Pomyślnie wczytano plik filtered_real_madrid_data_20_25.csv - znaleziono {len(filtered_data)} wierszy")
            
    except Exception as e:
        error(f"Błąd podczas wczytywania plików: {str(e)}")
        return False
    
    # Sprawdzenie czy kolumny match_id istnieją we wszystkich plikach
    for df_name, df in [("all_matches.csv", all_season), ("RM_matches.csv", RM_matches), ("filtered_real_madrid_data_20_25.csv", filtered_data)]:
        if 'match_id' not in df.columns:
            error(f"Kolumna match_id nie istnieje w pliku {df_name}")
            return False
    
    # Standaryzacja kolumn dat
    try:
        info("Konwertuję kolumny dat na format datetime...")
        
        all_season['date'] = pd.to_datetime(all_season['date'])
        info("Przekonwertowano kolumnę 'date' w pliku all_matches.csv")
        
        if 'date' in RM_matches.columns:
            RM_matches['date'] = pd.to_datetime(RM_matches['date'])
            info("Przekonwertowano kolumnę 'date' w pliku RM_matches.csv")
        elif 'match_date' in RM_matches.columns:
            RM_matches['date'] = pd.to_datetime(RM_matches['match_date'])
            info("Przekonwertowano kolumnę 'match_date' na 'date' w pliku RM_matches.csv")
        else:
            error("Nie znaleziono kolumny z datą w pliku RM_matches.csv")
            return False
            
        filtered_data['match_date'] = pd.to_datetime(filtered_data['match_date'])
        info("Przekonwertowano kolumnę 'match_date' w pliku filtered_real_madrid_data_20_25.csv")
        
    except Exception as e:
        error(f"Błąd podczas standaryzacji kolumn dat: {str(e)}")
        return False
    
    # Filtrowanie meczów Realu Madryt (team_id = 1)
    info("Filtruję mecze Realu Madryt...")
    real_madrid_filter = (all_season['home_team_id'] == 1) | (all_season['away_team_id'] == 1)
    all_season_real = all_season[real_madrid_filter].copy()
    info(f"Znaleziono {len(all_season_real)} meczów Realu Madryt w pliku all_matches.csv")
    
    # Pobieranie unikalnych meczów z filtered_data (które ma wiele wierszy na mecz, po jednym dla każdego zawodnika)
    info("Wyodrębniam unikalne mecze z pliku filtered_real_madrid_data_20_25.csv...")
    filtered_data_unique = filtered_data.drop_duplicates(subset=['match_id', 'match_date', 'home_team_id', 'away_team_id'])
    info(f"Po usunięciu duplikatów, znaleziono {len(filtered_data_unique)} unikalnych meczów w pliku filtered_real_madrid_data_20_25.csv")
    
    # Tworzenie sygnatur meczów, które jednoznacznie identyfikują mecz na podstawie daty i drużyn
    info("Tworzę sygnatury meczów na podstawie daty, drużyny gospodarzy i gości...")
    
    def create_signature(date, home_id, away_id):
        """
        Tworzy unikalną sygnaturę meczu na podstawie daty i identyfikatorów drużyn.
        Format: YYYY-MM-DD_home_id_away_id
        """
        try:
            if isinstance(date, str):
                date_str = date[:10]  # Wyciągnięcie części YYYY-MM-DD
            else:
                date_str = date.strftime('%Y-%m-%d')
            
            # Konwersja identyfikatorów drużyn na liczby całkowite, jeśli to możliwe
            try:
                home_id = int(float(home_id))
                away_id = int(float(away_id))
            except:
                pass
                
            return f"{date_str}_{home_id}_{away_id}"
        except Exception as e:
            warning(f"Błąd podczas tworzenia sygnatury meczu: {str(e)}")
            return None
    
    # Tworzenie sygnatur dla all_season
    info("Tworzę sygnatury dla meczów z pliku all_matches.csv...")
    all_season_signatures = {}
    for _, row in all_season_real.iterrows():
        sig = create_signature(row['date'], row['home_team_id'], row['away_team_id'])
        if sig:
            all_season_signatures[sig] = int(row['match_id'])
    
    # Tworzenie sygnatur dla RM_matches
    info("Tworzę sygnatury dla meczów z pliku RM_matches.csv...")
    rm_matches_signatures = {}
    for _, row in RM_matches.iterrows():
        date_col = 'date' if 'date' in row else 'match_date'
        sig = create_signature(row[date_col], row['home_team_id'], row['away_team_id'])
        if sig:
            rm_matches_signatures[sig] = int(row['match_id'])
    
    # Tworzenie sygnatur dla filtered_data_unique
    info("Tworzę sygnatury dla meczów z pliku filtered_real_madrid_data_20_25.csv...")
    filtered_data_signatures = {}
    for _, row in filtered_data_unique.iterrows():
        sig = create_signature(row['match_date'], row['home_team_id'], row['away_team_id'])
        if sig:
            filtered_data_signatures[sig] = int(row['match_id'])
    
    info(f"Znaleziono {len(all_season_signatures)} unikalnych meczów Realu Madryt w pliku all_matches.csv")
    info(f"Znaleziono {len(rm_matches_signatures)} unikalnych meczów w pliku RM_matches.csv")
    info(f"Znaleziono {len(filtered_data_signatures)} unikalnych meczów w pliku filtered_real_madrid_data_20_25.csv")
    
    # Sprawdzanie niespójności ID
    inconsistencies_found = False
    
    # Porównanie all_season z RM_matches
    info("Sprawdzam spójność między plikami all_matches.csv i RM_matches.csv...")
    common_signatures = set(all_season_signatures.keys()) & set(rm_matches_signatures.keys())
    info(f"Znaleziono {len(common_signatures)} wspólnych meczów w obu plikach")
    
    for sig in common_signatures:
        all_season_id = all_season_signatures[sig]
        rm_matches_id = rm_matches_signatures[sig]
        
        if all_season_id != rm_matches_id:
            inconsistencies_found = True
            date, home, away = sig.split('_')
            warning(f"Niezgodność ID: Mecz z dnia {date} (drużyny {home}-{away}), all_matches.csv match_id={all_season_id}, RM_matches.csv match_id={rm_matches_id}")
    
    # Porównanie all_season z filtered_data
    info("Sprawdzam spójność między plikami all_matches.csv i filtered_real_madrid_data_20_25.csv...")
    common_signatures = set(all_season_signatures.keys()) & set(filtered_data_signatures.keys())
    info(f"Znaleziono {len(common_signatures)} wspólnych meczów w obu plikach")
    
    for sig in common_signatures:
        all_season_id = all_season_signatures[sig]
        filtered_data_id = filtered_data_signatures[sig]
        
        if all_season_id != filtered_data_id:
            inconsistencies_found = True
            date, home, away = sig.split('_')
            warning(f"Niezgodność ID: Mecz z dnia {date} (drużyny {home}-{away}), all_matches.csv match_id={all_season_id}, filtered_real_madrid_data match_id={filtered_data_id}")
    
    # Porównanie RM_matches z filtered_data
    info("Sprawdzam spójność między plikami RM_matches.csv i filtered_real_madrid_data_20_25.csv...")
    common_signatures = set(rm_matches_signatures.keys()) & set(filtered_data_signatures.keys())
    info(f"Znaleziono {len(common_signatures)} wspólnych meczów w obu plikach")
    
    for sig in common_signatures:
        rm_matches_id = rm_matches_signatures[sig]
        filtered_data_id = filtered_data_signatures[sig]
        
        if rm_matches_id != filtered_data_id:
            inconsistencies_found = True
            date, home, away = sig.split('_')
            warning(f"Niezgodność ID: Mecz z dnia {date} (drużyny {home}-{away}), RM_matches.csv match_id={rm_matches_id}, filtered_real_madrid_data match_id={filtered_data_id}")
    
    # Sprawdzanie meczów brakujących w filtered_data
    only_in_all_season = set(all_season_signatures.keys()) - set(filtered_data_signatures.keys())
    if only_in_all_season:
        info(f"Znaleziono {len(only_in_all_season)} meczów w pliku all_matches.csv, których brakuje w filtered_real_madrid_data_20_25.csv")
        for sig in only_in_all_season:
            date, home, away = sig.split('_')
            info(f"Mecz z dnia {date} (drużyny {home}-{away}) z ID={all_season_signatures[sig]} istnieje w all_matches.csv, ale nie ma go w filtered_real_madrid_data_20_25.csv")
    else:
        info("Wszystkie mecze z pliku all_matches.csv są również obecne w pliku filtered_real_madrid_data_20_25.csv")
    
    # Sprawdzanie meczów brakujących w all_season
    only_in_filtered = set(filtered_data_signatures.keys()) - set(all_season_signatures.keys())
    if only_in_filtered:
        info(f"Znaleziono {len(only_in_filtered)} meczów w pliku filtered_real_madrid_data_20_25.csv, których brakuje w all_matches.csv")
        for sig in only_in_filtered:
            date, home, away = sig.split('_')
            info(f"Mecz z dnia {date} (drużyny {home}-{away}) z ID={filtered_data_signatures[sig]} istnieje w filtered_real_madrid_data_20_25.csv, ale nie ma go w all_matches.csv")
    else:
        info("Wszystkie mecze z pliku filtered_real_madrid_data_20_25.csv są również obecne w pliku all_matches.csv")
    
    # Sprawdzanie meczów brakujących między RM_matches i all_season
    only_in_rm = set(rm_matches_signatures.keys()) - set(all_season_signatures.keys())
    if only_in_rm:
        info(f"Znaleziono {len(only_in_rm)} meczów w pliku RM_matches.csv, których brakuje w all_matches.csv")
        for sig in only_in_rm:
            date, home, away = sig.split('_')
            info(f"Mecz z dnia {date} (drużyny {home}-{away}) z ID={rm_matches_signatures[sig]} istnieje w RM_matches.csv, ale nie ma go w all_matches.csv")
    else:
        info("Wszystkie mecze z pliku RM_matches.csv są również obecne w pliku all_matches.csv")
    
    # Podsumowanie
    if inconsistencies_found:
        warning("Sprawdzanie spójności ID zakończone: ZNALEZIONO NIEZGODNOŚCI")
        return False
    else:
        info("Sprawdzanie spójności ID zakończone: WSZYSTKIE ID SĄ SPÓJNE między wspólnymi meczami")
        return True

def set_match_id(path_to_file, path_to_save, type=1):
    """
    Ustawia match_id dla pliku "path_to_file":
    - sprawdza czy taki plik istnieje w katalogu "Data"
    - sprawdza czy istnieje w pliku kolumna "match_id", jeżeli nie to ustawia domyślne wartości dla match_id
    - zapisuje plik w "path_to_save"
    
    Args:
        path_to_file (str): Ścieżka do pliku do przetworzenia
        path_to_save (str): Ścieżka do zapisu pliku
        type (int): 
            "1" - oznacza działanie funkcji w sposób grupowania po meczach Realu
            "2" - oznacza działanie funkcji w sposób ogólny (indeksuje wszystkie spotkania w bazie)
    
    Returns:
        bool: True jeśli wszystko przebiegło dobrze i plik został zapisany, False w przeciwnym razie
    """
    # Sprawdzenie czy plik istnieje przed wczytaniem danych
    if not Path(path_to_file).exists(): 
        info(f"Plik {path_to_file} nie istnieje.")
        return False
    
    # Bezpieczne wczytanie danych z obsługą wyjątków
    try:
        data = pd.read_csv(path_to_file)
        info(f"Pomyślnie wczytano plik {path_to_file} z {len(data)} wierszami")
    except Exception as e:
        error(f"Błąd podczas wczytywania pliku {path_to_file}: {str(e)}")
        return False
    
    # Sprawdzenie wymaganych kolumn
    if 'home_team' not in data.columns or 'away_team' not in data.columns:
        info("Brak kolumn 'home_team' lub 'away_team' w pliku.")
        info(f"Kolumny dostępne w pliku: {data.columns.tolist()}")
        return False
    
    # Sprawdzenie kolumny match_id i utworzenie jej jeśli nie istnieje
    if 'match_id' not in data.columns:
        info('"match_id" nie istnieje w pliku. Tworzę nową kolumnę match_id.')
        data['match_id'] = np.nan
    
    # Sprawdzenie kolumny daty
    if 'match_date' not in data.columns and 'date' not in data.columns:
        info('Brak kolumny "match_date" lub "date" w pliku. Ta kolumna jest wymagana.')
        return False
    
    # Ustalenie kolumny, po której będziemy sortować
    date_column = 'match_date' if 'match_date' in data.columns else 'date'
    
    # Filtrowanie danych w zależności od typu
    if type == 1:
        # Filtrowanie tylko meczów Realu Madryt (team_id = 1)
        info("Filtrowanie: tylko mecze Realu Madryt")
        data = data.loc[(data["home_team"] == 1) | (data["away_team"] == 1)]
    else:  # type == 2
        # Wszystkie mecze bez filtrowania
        info("Filtrowanie: wszystkie mecze")
    
    # Sortowanie po dacie i przypisanie kolejnych ID
    data = data.sort_values(by=date_column)
    data["match_id"] = range(0, len(data))
    info(f"Przypisano match_id (0-{len(data)-1}) dla {len(data)} meczów")
    
    # Zapisanie pliku wynikowego
    try:
        data.to_csv(path_to_save, index=False)
        info(f"Pomyślnie zapisano plik z ustawionymi match_id do {path_to_save}")
        return True
    except Exception as e:
        error(f"Błąd podczas zapisywania pliku {path_to_save}: {str(e)}")
        return False


def set_team_id(path_to_file, path_to_save):
    """
    Ustawia home_team_id oraz away_team_id dla pliku "path_to_file":
    - sprawdza czy taki plik istnieje w katalogu "Data"
    - sprawdza czy istnieje w pliku kolumna "home_team" oraz "away_team" jeżeli nie to funkcja się kończy
    - pobiera dane o rywalach z pliku "Data/id_nazwa/rywale.csv" 
    - na podstawie tych danych ustawia home_team_id oraz away_team_id 
    - zapisuje plik w "path_to_save" 
    
    Args:
        path_to_file (str): Ścieżka do pliku do przetworzenia
        path_to_save (str): Ścieżka do zapisu pliku
    
    Returns:
        bool: True jeśli wszystko przebiegło dobrze i plik został zapisany, False w przeciwnym razie
    """
    # Sprawdzenie czy plik istnieje przed wczytaniem danych
    if not Path(path_to_file).exists(): 
        info(f"Plik {path_to_file} nie istnieje.")
        return False
    
    # Bezpieczne wczytanie danych z obsługą wyjątków
    try:
        data = pd.read_csv(path_to_file)
        info(f"Pomyślnie wczytano plik {path_to_file} z {len(data)} wierszami")
    except Exception as e:
        error(f"Błąd podczas wczytywania pliku {path_to_file}: {str(e)}")
        return False
    
    # Sprawdzenie wymaganych kolumn
    if 'home_team' not in data.columns or 'away_team' not in data.columns:
        info("Brak kolumn 'home_team' lub 'away_team' w pliku.")
        info(f"Kolumny dostępne w pliku: {data.columns.tolist()}")
        return False
    
    # Ścieżka do pliku z danymi rywali
    path_data = os.path.join(os.path.dirname(CURRENT_PATH), "Data","Mecze", "id_nazwa", "rywale.csv")
    
    # Sprawdzenie czy plik rywali istnieje
    if not Path(path_data).exists():
        info(f"Plik rywali {path_data} nie istnieje.")
        return False
    
    # Wczytanie danych rywali
    try:
        rivals_data = pd.read_csv(os.path.join(project_filepath,"Data","Mecze","id_nazwa","rywale.csv"))
        info(f"Pomyślnie wczytano plik rywali z {len(rivals_data)} drużynami")
        
        # Sprawdzenie wymaganych kolumn w pliku rywali
        if 'team_name' not in rivals_data.columns or 'team_id' not in rivals_data.columns:
            info("Brak kolumn 'team_name' lub 'team_id' w pliku rywali.")
            info(f"Kolumny dostępne w pliku rywali: {rivals_data.columns.tolist()}")
            return False
        
        # Tworzenie słownika mapującego nazwy drużyn na ich ID
        rivals_dict = dict(zip(rivals_data['team_name'], rivals_data['team_id']))
        
        # Mapowanie ID drużyn dla gospodarzy i gości
        data['home_team_id'] = data['home_team'].map(rivals_dict)
        data['away_team_id'] = data['away_team'].map(rivals_dict)
        
        # Sprawdzenie czy wszystkie drużyny zostały poprawnie zmapowane
        missing_home = data[data['home_team_id'].isna()]['home_team'].unique()
        missing_away = data[data['away_team_id'].isna()]['away_team'].unique()
        
        if len(missing_home) > 0 or len(missing_away) > 0:
            warning("Nie wszystkie drużyny zostały zmapowane:")
            if len(missing_home) > 0:
                warning(f"Brakujące drużyny gospodarzy: {missing_home.tolist()}")
            if len(missing_away) > 0:
                warning(f"Brakujące drużyny gości: {missing_away.tolist()}")
        # Usuniecie wartosci NaN z 'home_team_id', 'away_team_id'. 
            data = data.dropna(subset=['home_team_id', 'away_team_id'])
            info("Usuwam wiersze gdzie istnieją wartości Nan w kolumnach 'home_team_id', 'away_team_id'")
        # Zapisanie pliku wynikowego
        data.to_csv(path_to_save, index=False)
        info(f"Pomyślnie zapisano plik z ustawionymi team_id do {path_to_save}")
        return True
        
    except Exception as e:
        error(f"Błąd podczas przetwarzania: {str(e)}")
        return False

if __name__ == "__main__":

    info(f"Ścieżka bieżąca: {CURRENT_PATH}")
    info(f"Ścieżka projektu: {project_filepath}")
    RM_team_stats_path = os.path.join(project_filepath, "Data", "Real", "RM_team_stats.csv")
    RM_team_stats_path_new = os.path.join(project_filepath, "Data", "Real", "RM_team_stats2.csv")
    info(f"Ścieżka do pliku RM_team_stats: {RM_team_stats_path}")
    set_team_id(RM_team_stats_path, RM_team_stats_path_new)
    # check_match_id_consistency(project_filepath)