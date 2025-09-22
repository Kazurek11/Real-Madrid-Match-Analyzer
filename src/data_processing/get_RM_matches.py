"""
Moduł do wyodrębniania i analizy meczów Realu Madryt.

Ten moduł pozwala na wyodrębnienie meczów Realu Madryt z połączonych danych sezonowych,
dodanie specyficznych kolumn informacyjnych oraz analizę wyników drużyny.
"""

import pandas as pd
import numpy as np
import os
import sys

current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(current_dir)  
sys.path.append(project_root)

from helpers.logger import info, debug, warning, error
from helpers.file_utils import FileUtils
from data_processing.merge_all_season_data import DataMerger

class RealMadridMatches:
    """
    Klasa odpowiedzialna za wyodrębnianie i analizę meczów Realu Madryt.
    
    Notes:
    - Wczytanie połączonych danych sezonowych
    - Wyodrębnienie meczów Realu Madryt
    - Dodanie specyficznych kolumn dla meczów RM (is_home, real_result)
    - Zapis wyodrębnionych danych do pliku
    - Analizę podstawowych statystyk zespołu
    """
    
    def __init__(self, all_matches_df=None):
        """
        Inicjalizuje obiekt RealMadridMatches.
        
        Args:
            all_matches_df (pd.DataFrame, optional): DataFrame z danymi wszystkich meczów.
                Powinien zawierać kolumny: match_id, home_team, away_team, home_team_id, away_team_id.
        """
        self.file_utils = FileUtils()
        self.project_root = self.file_utils.get_project_root()
        self.data_dir = os.path.join(self.project_root, "Data", "Mecze", "all_season")
        self.all_matches = all_matches_df
        self.rm_matches = None
        
        self.output_folder = "rm_matches"
        self.output_file = "rm_matches.csv"
        self.output_path = os.path.join(self.data_dir, self.output_folder, self.output_file)
    
    def load_from_merged_file(self):
        """
        Wczytuje dane wszystkich meczów z pliku połączonych sezonów.
        
        Returns:
            bool: True jeśli operacja się powiodła, False w przypadku błędu
        """
        if self.all_matches is not None:
            info("Dane meczowe już wczytane.")
            return True
            
        try:
            merged_file = os.path.join(self.data_dir, "merged_matches", "all_matches.csv")
            if os.path.exists(merged_file):
                info(f"Wczytywanie danych z pliku: {merged_file}")
                self.all_matches = self.file_utils.load_csv_safe(merged_file, index_col="match_id")
                if self.all_matches is None:
                    error(f"Nie udało się wczytać pliku: {merged_file}")
                    return False
                    
                info(f"Pomyślnie wczytano dane {len(self.all_matches)} meczów.")
                return True
            else:
                error(f"Nie znaleziono pliku z połączonymi danymi: {merged_file}")
                return False
            
        except Exception as e:
            error(f"Błąd podczas wczytywania danych meczowych: {str(e)}")
            return False
    
    def extract_real_madrid_matches(self):
        """
        Wyodrębnia mecze Realu Madryt i dodaje dodatkowe kolumny.
        
        Returns:
            bool: True jeśli operacja się powiodła, False w przypadku błędu
        """
        if self.all_matches is None:
            if not self.load_from_merged_file():
                error("Nie można wyodrębnić meczów RM - brak danych.")
                return False
                
        try:
            real_madrid_id = 1
            real_madrid_name = "Real Madrid CF"
            
            real_madrid_filter = (
                (self.all_matches["home_team_id"] == real_madrid_id) | 
                (self.all_matches["away_team_id"] == real_madrid_id) |
                (self.all_matches["home_team"] == real_madrid_name) | 
                (self.all_matches["away_team"] == real_madrid_name)
            )
            
            rm_matches = self.all_matches[real_madrid_filter].copy()
            
            rm_matches["is_home"] = 0
            rm_matches.loc[rm_matches["home_team_id"] == real_madrid_id, "is_home"] = 1
            rm_matches.loc[rm_matches["home_team"] == real_madrid_name, "is_home"] = 1
            
            rm_matches["real_result"] = 0.0
            if "result" in rm_matches.columns:
                if rm_matches["result"].dtype == object:
                    rm_matches.loc[(rm_matches["is_home"] == 1) & (rm_matches["result"] == "H"), "real_result"] = 1.0
                    rm_matches.loc[(rm_matches["is_home"] == 0) & (rm_matches["result"] == "A"), "real_result"] = 1.0
                    rm_matches.loc[rm_matches["result"] == "D", "real_result"] = 0.5
                else:
                    rm_matches.loc[(rm_matches["is_home"] == 1) & (rm_matches["result"] == 1), "real_result"] = 1.0
                    rm_matches.loc[(rm_matches["is_home"] == 0) & (rm_matches["result"] == 2), "real_result"] = 1.0
                    rm_matches.loc[rm_matches["result"] == 0, "real_result"] = 0.5
            
            numeric_cols = rm_matches.select_dtypes(include=["float64"]).columns
            rm_matches[numeric_cols] = rm_matches[numeric_cols].round(2)
            
            self.rm_matches = rm_matches
            info(f"Wyodrębniono {len(rm_matches)} meczów Realu Madryt.")
            return True
            
        except Exception as e:
            error(f"Błąd podczas wyodrębniania meczów Realu: {str(e)}")
            return False
    
    def get_real_madrid_matches(self):
        """
        Zwraca DataFrame z przetworzonymi meczami Realu Madryt.
        
        Returns:
            pd.DataFrame: DataFrame z meczami Realu Madryt lub None w przypadku błędu
        """
        if self.rm_matches is not None:
            return self.rm_matches
            
        if not self.load_from_merged_file():
            return None
            
        if not self.extract_real_madrid_matches():
            return None
            
        return self.rm_matches
    
    def save_rm_matches(self, output_path=None):
        """
        Zapisuje wyodrębnione mecze Realu Madryt do pliku CSV.
        
        Args:
            output_path (str, optional): Ścieżka do pliku wynikowego.
                Jeśli None, używana jest domyślna ścieżka.
        
        Returns:
            bool: True jeśli operacja zapisu się powiodła, False w przeciwnym przypadku
        """
        if self.rm_matches is None:
            if self.get_real_madrid_matches() is None:
                error("Nie można zapisać danych - brak wyodrębnionych meczów Realu Madryt.")
                return False
        
        if output_path is None:
            output_path = self.output_path
            
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                info(f"Utworzono katalog: {output_dir}")
            except Exception as e:
                error(f"Nie udało się utworzyć katalogu {output_dir}: {str(e)}")
                return False
        
        try:
            df_to_save = self.rm_matches.copy()
            if "match_id" in df_to_save.columns:
                df_to_save = df_to_save.set_index("match_id")
                
            result = self.file_utils.save_csv_safe(df=df_to_save, file_path=output_path, index=True)
            
            if result:
                info(f"Zapisano {len(df_to_save)} meczów Realu Madryt do pliku: {output_path}")
            else:
                error(f"Nie udało się zapisać pliku: {output_path}")
                
            return result
            
        except Exception as e:
            error(f"Błąd podczas zapisywania meczów Realu Madryt: {str(e)}")
            return False
    
    def analyze_rm_stats(self):
        """
        Analizuje podstawowe statystyki Realu Madryt.
        
        Returns:
            dict: Słownik z obliczonymi statystykami
        """
        if self.rm_matches is None:
            if self.get_real_madrid_matches() is None:
                error("Nie można analizować statystyk - brak wyodrębnionych meczów Realu Madryt.")
                return {}
        
        try:
            stats = {}
            
            stats["total_matches"] = len(self.rm_matches)
            
            stats["wins"] = int((self.rm_matches["real_result"] == 1.0).sum())
            stats["draws"] = int((self.rm_matches["real_result"] == 0.5).sum())
            stats["losses"] = stats["total_matches"] - stats["wins"] - stats["draws"]
            
            stats["win_rate"] = round(stats["wins"] / stats["total_matches"] * 100, 2) if stats["total_matches"] > 0 else 0
            
            if "is_home" in self.rm_matches.columns and "home_goals" in self.rm_matches.columns and "away_goals" in self.rm_matches.columns:
                home_matches = self.rm_matches[self.rm_matches["is_home"] == 1]
                away_matches = self.rm_matches[self.rm_matches["is_home"] == 0]
                
                stats["avg_goals_scored"] = round((
                    home_matches["home_goals"].sum() + away_matches["away_goals"].sum()
                ) / stats["total_matches"], 2) if stats["total_matches"] > 0 else 0
                
                stats["avg_goals_conceded"] = round((
                    home_matches["away_goals"].sum() + away_matches["home_goals"].sum()
                ) / stats["total_matches"], 2) if stats["total_matches"] > 0 else 0
            
            info(f"Statystyki Realu Madryt dla {stats['total_matches']} meczów:")
            info(f"Zwycięstwa: {stats['wins']} ({stats['win_rate']}%)")
            info(f"Remisy: {stats['draws']}")
            info(f"Porażki: {stats['losses']}")
            if "avg_goals_scored" in stats:
                info(f"Średnio bramek zdobytych: {stats['avg_goals_scored']}")
                info(f"Średnio bramek straconych: {stats['avg_goals_conceded']}")
            
            return stats
            
        except Exception as e:
            error(f"Błąd podczas analizowania statystyk Realu Madryt: {str(e)}")
            return {}

def main():
    """
    Główna funkcja modułu, wykonuje wyodrębnienie i analizę meczów Realu Madryt.
    """
    info("Rozpoczęcie procesu wyodrębniania meczów Realu Madryt...")
    
    rm_extractor = RealMadridMatches()
    
    if not rm_extractor.load_from_merged_file():
        error("Nie udało się wczytać danych meczowych. Przerywanie.")
        return
    
    if not rm_extractor.extract_real_madrid_matches():
        error("Nie udało się wyodrębnić meczów Realu Madryt. Przerywanie.")
        return
    
    if not rm_extractor.save_rm_matches():
        warning("Nie udało się zapisać meczów Realu Madryt do pliku.")
    
    rm_extractor.analyze_rm_stats()
    
    info("Zakończenie procesu wyodrębniania meczów Realu Madryt.")

if __name__ == "__main__":
    main()