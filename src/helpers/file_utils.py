import os
import pandas as pd
from typing import Optional, List, Dict, Union, Tuple
# pamietaj zeby moduły importować lokalnie
class FileUtils:
    """
    Klasa zawierająca narzędzia do zarządzania plikami i operacji na plikach CSV.
    """
    
    @staticmethod
    def get_project_root():
        """Zwraca ścieżkę do głównego katalogu projektu."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Jeśli jesteśmy w src/help_script, musimy iść o poziom wyżej
        parent_dir = os.path.dirname(current_dir)
        # Jeśli jesteśmy w src, musimy iść o poziom wyżej
        project_root = os.path.dirname(parent_dir)
        return project_root

    @staticmethod
    def load_csv_safe(file_path: str, index_col: Optional[Union[str, int]] = None, 
                     sort_by: Optional[Union[str, List[str]]] = None, 
                     ascending: bool = True) -> Optional[pd.DataFrame]:
        """
        Bezpieczne wczytanie pliku CSV z obsługą błędów.
        
        Args:
            file_path (str): Ścieżka do pliku CSV
            index_col (str lub int, optional): Nazwa kolumny lub indeks do ustawienia jako indeks
            sort_by (str lub lista[str], optional): Kolumna(y) do sortowania danych
            ascending (bool, optional): Kierunek sortowania, True=rosnąco, False=malejąco
            
        Returns:
            Optional[pd.DataFrame]: DataFrame z wczytanymi danymi lub None w przypadku błędu
        """
        try:
            if not os.path.exists(file_path):
                from helpers.logger import error  
                error(f"Plik nie istnieje: {file_path}")
                return None
                
            df = pd.read_csv(file_path, index_col=index_col)
            
            # Sortowanie danych, jeśli podano kolumnę
            if sort_by is not None:
                df = df.sort_values(by=sort_by, ascending=ascending)
                
            return df
        except Exception as e:
            from helpers.logger import error  
            error(f"Błąd podczas wczytywania pliku {file_path}: {str(e)}")
            return None

    @staticmethod
    def save_csv_safe(df: pd.DataFrame, file_path: str, index: bool = False, 
                     index_label: Optional[str] = None, sort_by: Optional[Union[str, List[str]]] = None, 
                     ascending: bool = True) -> bool:
        """
        Bezpieczny zapis DataFrame do pliku CSV z możliwością sortowania i ustawienia indeksu.
        
        Args:
            df (pd.DataFrame): DataFrame do zapisania
            file_path (str): Ścieżka docelowa pliku CSV
            index (bool, optional): Czy zapisać indeks jako kolumnę
            index_label (str, optional): Etykieta dla kolumny indeksu
            sort_by (str lub lista[str], optional): Kolumna(y) do sortowania danych przed zapisem
            ascending (bool, optional): Kierunek sortowania, True=rosnąco, False=malejąco
            
        Returns:
            bool: True jeśli zapis się powiódł, False w przeciwnym razie
        """
        try:        
            # Upewnij się, że katalog istnieje
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Sortowanie danych, jeśli podano kolumnę
            df_to_save = df.copy()
            if sort_by is not None:
                df_to_save = df_to_save.sort_values(by=sort_by, ascending=ascending)
            
            # Zapis pliku
            df_to_save.to_csv(file_path, index=index, index_label=index_label)
            from helpers.logger import debug  
            debug(f"Zapisano plik {file_path} pomyślnie. Wierszy: {len(df_to_save)}")
            return True
        except Exception as e:
            from helpers.logger import debug  
            debug(f"Błąd podczas zapisywania pliku {file_path}: {str(e)}")
            return False

    def ensure_directory_exists(self, directory_path):
        """
        Tworzy katalog jeśli nie istnieje.
        
        Args:
            directory_path (str): Ścieżka do katalogu
            
        Returns:
            bool: True jeśli katalog istnieje lub został utworzony, False w przeciwnym razie
        """
        try:
            os.makedirs(directory_path, exist_ok=True)
            from helpers.logger import info 
            info(f"Katalog {directory_path} jest dostępny")
            return True
        except Exception as e:
            from helpers.logger import error  
            error(f"Nie można utworzyć katalogu {directory_path}: {str(e)}")
            return False
    
    def get_results_directory(self, base_path=None, name_of_directory = "result"):
        """
        Zwraca standardowy katalog dla wyników, tworząc go jeśli nie istnieje.
        
        Args:
            base_path (str, optional): Ścieżka bazowa. Jeśli None, używa katalogu projektu.
            name_of_directory (str, optional): Nazwa tworzonego folderu wynikowego.
        Returns:
            str: Ścieżka do katalogu wyników
        """
        if base_path is None:
            base_path = self.get_project_root()
        
        results_dir = os.path.join(base_path, name_of_directory)
        self.ensure_directory_exists(results_dir)
        return results_dir
        
    def check_file_exists(self, file_path):
        """Sprawdza czy plik istnieje pod podaną ścieżką."""
        return os.path.exists(file_path) and os.path.isfile(file_path)
    
    def get_all_files_from_directory(self, directory_path):
        try:
            if not os.path.exists(directory_path):
                from helpers.logger import error  
                error(f"Katalog {directory_path} nie istnieje")
                return []
                
            if not os.path.isdir(directory_path):
                from helpers.logger import error  
                error(f"{directory_path} nie jest katalogiem")
                return []
                
            files = [
                os.path.join(directory_path, f)
                for f in os.listdir(directory_path)
                if os.path.isfile(os.path.join(directory_path, f))
            ]
            from helpers.logger import info 
            info(f"Znaleziono {len(files)} plików w katalogu {directory_path}")
            return files
            
        except Exception as e:
            from helpers.logger import error  
            error(f"Błąd podczas pobierania plików z katalogu {directory_path}: {str(e)}")
            return []
    @staticmethod
    def load_excel_safe(file_path: str, sheet_name=0) -> Optional[pd.DataFrame]:
        """
        Bezpieczne wczytanie pliku Excel z obsługą błędów.
        
        Args:
            file_path (str): Ścieżka do pliku Excel
            sheet_name (str lub int, optional): Nazwa lub indeks arkusza do wczytania. Domyślnie 0 (pierwszy arkusz).
                
        Returns:
            Optional[pd.DataFrame]: DataFrame z danymi z arkusza lub None w przypadku błędu
        """
        try:
            if not os.path.exists(file_path):
                from helpers.logger import error  
                error(f"Plik nie istnieje: {file_path}")
                return None
            return pd.read_excel(file_path, sheet_name=sheet_name)
        except Exception as e:
            from helpers.logger import error  
            error(f"Błąd podczas wczytywania pliku Excel {file_path} (arkusz: {sheet_name}): {str(e)}")
            return None

    @staticmethod
    def save_excel_safe(df: pd.DataFrame, file_path: str, sheet_name: str = 'Sheet1', 
                       index: bool = False, index_label: Optional[str] = None,
                       sort_by: Optional[Union[str, List[str]]] = None, 
                       ascending: bool = True) -> bool:
        """
        Bezpieczny zapis DataFrame do pliku Excel z możliwością sortowania.
        
        Args:
            df (pd.DataFrame): DataFrame do zapisania
            file_path (str): Ścieżka docelowa pliku Excel
            sheet_name (str): Nazwa arkusza
            index (bool): Czy zapisać indeks jako kolumnę
            index_label (str, optional): Etykieta dla kolumny indeksu
            sort_by (str lub lista[str], optional): Kolumna(y) do sortowania danych przed zapisem
            ascending (bool, optional): Kierunek sortowania, True=rosnąco, False=malejąco
        
        Returns:
            bool: True jeśli zapis się powiódł, False w przeciwnym razie
        """
        try:
            # Upewnij się, że katalog istnieje
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Sortowanie danych, jeśli podano kolumnę
            df_to_save = df.copy()
            if sort_by is not None:
                df_to_save = df_to_save.sort_values(by=sort_by, ascending=ascending)
            
            # Zapis pliku Excel
            df_to_save.to_excel(file_path, sheet_name=sheet_name, 
                              index=index, index_label=index_label)
            from helpers.logger import error  
            error(f"Zapisano plik Excel {file_path} pomyślnie.")
            return True
        except Exception as e:
            from helpers.logger import error  
            error(f"Błąd podczas zapisywania pliku Excel {file_path}: {str(e)}")
            return False

    def merge_csv_files(self, file_paths: List[str], output_path: str, 
                       index_col: Optional[str] = None, sort_by: Optional[str] = None, 
                       ascending: bool = True) -> bool:
        """
        Łączy wiele plików CSV w jeden plik.
        
        Args:
            file_paths (List[str]): Lista ścieżek do plików CSV
            output_path (str): Ścieżka docelowa dla połączonego pliku
            index_col (str, optional): Nazwa kolumny do ustawienia jako indeks
            sort_by (str, optional): Kolumna do sortowania danych po połączeniu
            ascending (bool, optional): Kierunek sortowania, True=rosnąco, False=malejąco
            
        Returns:
            bool: True jeśli operacja się powiodła, False w przeciwnym razie
        """
        try:
            dataframes = []
            for file_path in file_paths:
                df = self.load_csv_safe(file_path)
                if df is not None:
                    dataframes.append(df)
                    from helpers.logger import error  
                    error(f"Wczytano plik {file_path} ({len(df)} wierszy)")
                else:
                    from helpers.logger import error  
                    error(f"Nie udało się wczytać pliku {file_path}")
            
            if not dataframes:
                from helpers.logger import error  
                error("Nie udało się wczytać żadnego pliku CSV")
                return False
                
            # Łączenie wszystkich dataframes
            merged_df = pd.concat(dataframes, ignore_index=True)
            from helpers.logger import error  
            error(f"Połączono {len(dataframes)} plików, łącznie {len(merged_df)} wierszy")
            
            # Ustawienie indeksu, jeśli podany
            if index_col is not None and index_col in merged_df.columns:
                merged_df.set_index(index_col, inplace=True)
            
            # Sortowanie, jeśli podane
            if sort_by is not None:
                merged_df = merged_df.sort_values(by=sort_by, ascending=ascending)
            
            # Zapis połączonego pliku
            return self.save_csv_safe(
                df=merged_df, 
                file_path=output_path, 
                index=(index_col is not None)
            )
        except Exception as e:
            from helpers.logger import error  
            error(f"Błąd podczas łączenia plików CSV: {str(e)}")
            return False

    def filter_and_save(self, file_path: str, output_path: str, 
                       filter_condition: callable, 
                       sort_by: Optional[str] = None, 
                       ascending: bool = True) -> bool:
        """
        Wczytuje plik CSV, stosuje warunek filtrowania i zapisuje wynik.
        
        Args:
            file_path (str): Ścieżka do pliku wejściowego
            output_path (str): Ścieżka do pliku wynikowego
            filter_condition (callable): Funkcja filtrująca przyjmująca DataFrame i zwracająca DataFrame
            sort_by (str, optional): Kolumna do sortowania
            ascending (bool, optional): Kierunek sortowania
        
        Returns:
            bool: True jeśli operacja się powiodła, False w przeciwnym razie
        """
        try:
            # Wczytaj dane
            df = self.load_csv_safe(file_path)
            if df is None:
                return False
                
            # Zastosuj filtr
            filtered_df = filter_condition(df)
            
            # Sortuj i zapisz
            if sort_by is not None:
                filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
                
            return self.save_csv_safe(filtered_df, output_path)
        except Exception as e:
            from helpers.logger import error  
            error(f"Błąd podczas filtrowania i zapisywania danych: {str(e)}")
            return False
    
    def convert_excel_to_csv(self, excel_path: str, csv_path: str, 
                           sheet_name=0, index: bool = False,
                           sort_by: Optional[str] = None, 
                           ascending: bool = True) -> bool:
        """
        Konwertuje plik Excel do formatu CSV.
        
        Args:
            excel_path (str): Ścieżka do pliku Excel
            csv_path (str): Ścieżka docelowa pliku CSV
            sheet_name (str lub int): Nazwa lub indeks arkusza do konwersji
            index (bool): Czy zachować indeks w pliku CSV
            sort_by (str, optional): Kolumna do sortowania przed zapisem
            ascending (bool): Kierunek sortowania
            
        Returns:
            bool: True jeśli konwersja się powiodła, False w przeciwnym razie
        """
        try:
            # Wczytaj plik Excel
            df = self.load_excel_safe(excel_path, sheet_name)
            if df is None:
                return False
                
            # Sortuj i zapisz jako CSV
            return self.save_csv_safe(
                df=df, 
                file_path=csv_path, 
                index=index,
                sort_by=sort_by,
                ascending=ascending
            )
        except Exception as e:
            from helpers.logger import error  
            error(f"Błąd podczas konwersji pliku Excel do CSV: {str(e)}")
            return False