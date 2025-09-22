"""
Funkcje narzędziowe do walidacji danych i sprawdzania typów.

Moduł zawiera funkcje pomocnicze do sprawdzania typów kolumn,
wykrywania wartości NaN, konwersji typów danych oraz dodawania
brakujących kolumn do DataFrame'ów używanych w analizie drużynowej.
"""

import pandas as pd
import numpy as np
from helpers.logger import info, error


def check_type_in_dataframe(df, column_name, expected_type):
    """
    Sprawdza typ kolumny w DataFrame i konwertuje jeśli potrzeba.
    
    Args:
        df (pd.DataFrame): DataFrame do sprawdzenia
        column_name (str): Nazwa kolumny do sprawdzenia
        expected_type (str): Oczekiwany typ danych (np. 'datetime64[ns]')
        
    Returns:
        bool: True jeśli typ jest poprawny lub udało się skonwertować, False w przeciwnym razie
        
    Notes:
        - Automatycznie próbuje konwertować datetime gdy expected_type='datetime64[ns]'
        - Modyfikuje DataFrame in-place przy konwersji datetime
        - Loguje informacje o typach i próbach konwersji
        - Zwraca False jeśli kolumna nie istnieje
    """
    if column_name in df.columns:
        actual_type = df[column_name].dtype
        if actual_type != expected_type:
            info(f"Typ kolumny {column_name} w DataFrame jest {actual_type}, próbuję konwertować na {expected_type}.")
            try:
                if expected_type == 'datetime64[ns]':
                    df[column_name] = pd.to_datetime(df[column_name], errors='coerce')
                    info(f"Pomyślnie przekonwertowano kolumnę {column_name} na typ {expected_type}.")
                    return True
            except Exception as e:
                error(f"Nie udało się przekonwertować kolumny {column_name}: {str(e)}")
                return False
            return False
        else:
            info(f"Typ kolumny {column_name} jest poprawny: {actual_type}.")
            return True
    else:
        error(f"Kolumna {column_name} nie istnieje w DataFrame.")
        return False


def check_NAN_in_dataframe(df, column_name):
    """
    Sprawdza obecność wartości NaN w określonej kolumnie DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame do sprawdzenia
        column_name (str): Nazwa kolumny do sprawdzenia
        
    Returns:
        bool: True jeśli kolumna zawiera NaN, False jeśli nie zawiera lub kolumna nie istnieje
        
    Notes:
        - Używa pandas.isnull() do wykrywania NaN
        - Loguje informacje o wynikach sprawdzenia
        - Zwraca False i loguje błąd jeśli kolumna nie istnieje
        - Nie modyfikuje danych, tylko sprawdza
    """
    if column_name in df.columns:
        if df[column_name].isnull().any():
            error(f"Kolumna {column_name} zawiera wartości NaN.")
            return True
        else:
            info(f"Kolumna {column_name} nie zawiera wartości NaN.")
            return False
    else:
        error(f"Kolumna {column_name} nie istnieje w DataFrame.")
        return False


def check_NaN_column_in_RM_matches(dataframe):
    """
    Sprawdza i uzupełnia wartości NaN w kluczowych kolumnach meczów RM.
    
    Args:
        dataframe (pd.DataFrame): DataFrame z danymi meczów Real Madryt
        
    Returns:
        bool: True jeśli nie znaleziono NaN, False jeśli znaleziono i uzupełniono
        
    Notes:
        - Sprawdza kluczowe kolumny: daty, drużyny, gole, punkty, oceny
        - Automatycznie uzupełnia NaN wartościami 0
        - Modyfikuje DataFrame in-place przy uzupełnianiu
        - Używa konfiguracji kolumn z config.py
        - Loguje informacje o znalezionych i uzupełnionych NaN
    """
    from .config import RM_COACH_RATING, RM_TEAM_RATING, OPP_RATING
    
    not_null_columns = [
        'match_date', 'home_team', 'away_team', 'home_goals', 
        'away_goals', 'home_points', 'away_points', 
        RM_COACH_RATING, RM_TEAM_RATING, OPP_RATING
    ]
    any_nan_found = False
    
    for column in not_null_columns:
        if column in dataframe.columns and dataframe[column].isnull().any():
            error(f"Kolumna {column} zawiera wartości NaN. Uzupełniam je zerami.")
            dataframe[column] = dataframe[column].fillna(0)
            any_nan_found = True
            
    return not any_nan_found


def add_missing_columns(df, columns_to_add):
    """
    Dodaje brakujące kolumny do DataFrame z wartościami NaN.
    
    Args:
        df (pd.DataFrame): DataFrame do rozszerzenia
        columns_to_add (list): Lista nazw kolumn do dodania
        
    Returns:
        pd.DataFrame: DataFrame z dodanymi kolumnami lub oryginalny jeśli brak nowych
        
    Notes:
        - Sprawdza które kolumny z listy nie istnieją w df
        - Inicjalizuje nowe kolumny z wartościami np.nan
        - Zachowuje indeks oryginalnego DataFrame
        - Używa pd.concat() do łączenia kolumn
        - Zwraca oryginalny DataFrame jeśli wszystkie kolumny już istnieją
        - Nowe kolumny są dodawane po prawej stronie
    """
    new_columns = {}
    for column in columns_to_add:
        if column not in df.columns:
            new_columns[column] = np.nan

    if new_columns:
        new_df = pd.DataFrame(new_columns, index=df.index)
        return pd.concat([df, new_df], axis=1)
    return df