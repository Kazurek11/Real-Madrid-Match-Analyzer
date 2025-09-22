"""
Główny orchestrator analizy Real Madryt.

Koordynuje wszystkie moduły analizy danych: zawodników, drużyny, 
przeciwników i statystyk head-to-head. Tworzy kompletny dataset
gotowy do machine learning.
"""

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
from helpers.logger import info, error, warning, critical
from helpers.file_utils import FileUtils

from finall_dataframe.rm_players.analyzer import RealMadridPlayersAnalyzer
from finall_dataframe.rm_team.analyzer import RealMadridTeamAnalyzer
from finall_dataframe.opp_team.analyzer import OpponentTeamAnalyzer
from finall_dataframe.rm_h2h.analyzer import HeadToHeadAnalyzer
from finall_dataframe.rm_team.data_imputer import DataFrameImputer

class RealMadridMasterAnalyzer:
    """
    Główny analizator łączący wszystkie moduły analizy Real Madryt.
    
    Orchestruje proces analizy od zawodników przez drużynę po przeciwników
    i statystyki head-to-head. Tworzy jeden kompletny dataset z wszystkimi
    metrykami potrzebnymi do modelowania predykcyjnego.
    
    Attributes:
        base_output_path (str): Ścieżka do katalogu wyników
        players_analyzer: Analizator danych zawodników
        team_analyzer: Analizator statystyk drużynowych
        opponent_analyzer: Analizator statystyk przeciwników
        h2h_analyzer: Analizator statystyk head-to-head
    """
    
    def __init__(self, output_dir=None):
        """
        Inicjalizuje główny analizator.
        
        Args:
            output_dir (str, optional): Katalog wyników. Domyślnie Data/
        """
        self.base_output_path = output_dir or os.path.join(FileUtils.get_project_root(), 'Data' , '')
        self.setup_analyzers()
    
    def setup_analyzers(self):
        """
        Inicjalizuje wszystkie moduły analizujące.
        """
        info("Inicjalizuję moduły analizy...")
        self.players_analyzer = RealMadridPlayersAnalyzer()
        self.team_analyzer = RealMadridTeamAnalyzer()
        self.opponent_analyzer = OpponentTeamAnalyzer()
        self.h2h_analyzer = HeadToHeadAnalyzer()
        info("Wszystkie moduły analizy zainicjalizowane pomyślnie")
    
    def analyze_players(self):
        """
        Wykonuje analizę zawodników Real Madryt.
        """
        info("=== ROZPOCZYNAM ANALIZĘ ZAWODNIKÓW ===")
        try:
            players_df = self.players_analyzer.analyze()
            info(f"Analiza zawodników zakończona: {len(players_df)} meczów, {len(players_df.columns)} kolumn")
            return players_df
        except Exception as e:
            critical(f"Błąd krytyczny w analizie zawodników: {str(e)}")
            raise
    
    def analyze_team(self, base_df):
        """
        Wykonuje analizę drużynową na podstawie danych zawodników.
        """
        info("=== ROZPOCZYNAM ANALIZĘ DRUŻYNOWĄ ===")
        try:
            self.team_analyzer.set_base_dataframe(base_df)
            team_df = self.team_analyzer.analyze()
            info(f"Analiza drużynowa zakończona: dodano {len(team_df.columns) - len(base_df.columns)} nowych kolumn")
            return team_df
        except Exception as e:
            critical(f"Błąd krytyczny w analizie drużynowej: {str(e)}")
            raise
    
    def analyze_opponents(self, base_df):
        """
        Wykonuje analizę przeciwników na podstawie danych meczowych.
        """
        info("=== ROZPOCZYNAM ANALIZĘ PRZECIWNIKÓW ===")
        try:
            self.opponent_analyzer.set_base_dataframe(base_df)
            opponents_df = self.opponent_analyzer.analyze()
            info(f"Analiza przeciwników zakończona: dodano statystyki przeciwników")
            return opponents_df
        except Exception as e:
            critical(f"Błąd krytyczny w analizie przeciwników: {str(e)}")
            raise
    
    def analyze_head_to_head(self, base_df):
        """
        Wykonuje analizę head-to-head i dodaje kursy bukmacherskie.
        """
        info("=== ROZPOCZYNAM ANALIZĘ HEAD-TO-HEAD ===")
        try:
            self.h2h_analyzer.set_base_dataframe(base_df)
            h2h_df = self.h2h_analyzer.analyze()
            info(f"Analiza H2H zakończona: dodano statystyki historycznych spotkań")
            return h2h_df
        except Exception as e:
            critical(f"Błąd krytyczny w analizie H2H: {str(e)}")
            raise

    def impute_missing_data(self, df):
        """
        Wykonuje inteligentną imputację brakujących danych na finalnym zbiorze.
        
        Args:
            df (pd.DataFrame): Surowy DataFrame po wszystkich analizach.
            
        Returns:
            pd.DataFrame: Czysty DataFrame bez wartości NaN.
        """
        info("=== ROZPOCZYNAM PROCES IMPUTACJI DANYCH ===")
        try:
            imputer = DataFrameImputer(df)
            clean_df = imputer.run()
            info("Proces imputacji zakończony pomyślnie.")
            return clean_df
        except Exception as e:
            critical(f"Błąd krytyczny podczas imputacji danych: {str(e)}")
            raise

    def validate_final_dataset(self, df):
        """
        Waliduje finalny dataset pod kątem kompletności i jakości.
        """
        info("=== WALIDACJA FINALNEGO DATASETU ===")
        validation_report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().sum(),
            'missing_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
            'date_range': {
                'start': pd.to_datetime(df['M_DATE']).min() if 'M_DATE' in df.columns else None,
                'end': pd.to_datetime(df['M_DATE']).max() if 'M_DATE' in df.columns else None
            },
            'columns_by_module': {
                'players': len([col for col in df.columns if col.startswith('RM_PX_')]),
                'team': len([col for col in df.columns if col.startswith('RM_') and not col.startswith('RM_PX_')]),
                'opponents': len([col for col in df.columns if col.startswith('OP_')]),
                'h2h': len([col for col in df.columns if col.startswith('H2H_')])
            }
        }
        info(f"Walidacja zakończona:")
        info(f"  - Wierszy: {validation_report['total_rows']}")
        info(f"  - Kolumn: {validation_report['total_columns']}")
        info(f"  - Brakujące wartości: {validation_report['missing_percentage']:.2f}%")
        info(f"  - Zakres dat: {validation_report['date_range']['start'].date()} - {validation_report['date_range']['end'].date()}")
        return validation_report
    
    def create_master_dataset(self):
        """
        Tworzy kompletny, czysty dataset, łącząc wszystkie moduły analizy i imputacji.
        """
        start_time = datetime.now()
        info("=== ROZPOCZYNAM TWORZENIE MASTER DATASETU ===")
        
        try:
            # Krok 1: Analizy generujące dane (z potencjalnymi NaN)
            base_df = self.analyze_players()
            team_df = self.analyze_team(base_df)
            opponents_df = self.analyze_opponents(team_df)
            raw_final_df = self.analyze_head_to_head(opponents_df)
            
            # Krok 2: Imputacja brakujących danych
            final_df = self.impute_missing_data(raw_final_df)
            
            # Krok 3: Walidacja czystego zbioru
            validation_report = self.validate_final_dataset(final_df)
            
            # Krok 4: Zapis do pliku
            final_path = os.path.join(self.base_output_path, 'DataSet', 'real_madrid_master_dataset.csv')
            FileUtils.save_csv_safe(final_df, final_path)
            
            execution_time = datetime.now() - start_time
            info(f"=== MASTER DATASET UTWORZONY POMYŚLNIE ===")
            info(f"Czas wykonania: {execution_time}")
            info(f"Zapisano do: {final_path}")
            
            return final_df, validation_report
            
        except Exception as e:
            critical(f"Błąd krytyczny w tworzeniu master datasetu: {str(e)}")
            raise

def main():
    """
    Główna funkcja uruchamiająca cały proces analizy.
    """
    try:
        os.makedirs(os.path.join(FileUtils.get_project_root(), 'Data', 'DataSet'), exist_ok=True)
        
        master_analyzer = RealMadridMasterAnalyzer()
        final_dataset, validation_report = master_analyzer.create_master_dataset()
        
        info("\n" + "="*60)
        info("           REAL MADRID MASTER DATASET")
        info("="*60)
        info(f"✓ Wierszy danych: {len(final_dataset):,}")
        info(f"✓ Kolumn danych: {len(final_dataset.columns):,}")
        info(f"✓ Kompletność: {100 - validation_report['missing_percentage']:.1f}%")
        info(f"✓ Okres analizy: {validation_report['date_range']['start'].date()} - {validation_report['date_range']['end'].date()}")
        info("\nStatystyki kolumn:")
        info(f"  - Zawodnicy: {validation_report['columns_by_module']['players']} kolumn")
        info(f"  - Drużyna RM: {validation_report['columns_by_module']['team']} kolumn") 
        info(f"  - Przeciwnicy: {validation_report['columns_by_module']['opponents']} kolumn")
        info(f"  - Head-to-Head: {validation_report['columns_by_module']['h2h']} kolumn")
        info("="*60)
        info("Dataset gotowy do machine learning!")
        
    except Exception as e:
        critical(f"Krytyczny błąd w main(): {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)