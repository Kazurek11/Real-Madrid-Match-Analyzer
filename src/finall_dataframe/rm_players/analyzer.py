"""
Główny moduł analizy zawodników Real Madryt.

Ten moduł przeprowadza kompleksową analizę danych zawodników Real Madryt,
obliczając statystyki indywidualne, formę, wydajność oraz metryki zespołowe.
Generuje podstawowy DataFrame używany przez inne moduły analizy.
"""

import pandas as pd
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.getcwd(), 'src')

sys.path.insert(0, src_dir)

from finall_dataframe.rm_players.data_loader import DataLoader
from finall_dataframe.rm_players.season_manager import SeasonManager
from finall_dataframe.rm_players.player_manager import PlayerManager
from finall_dataframe.rm_players.statistics_calculator import StatisticsCalculator
from finall_dataframe.rm_players.data_agregator import DataAggregator

sys.path.insert(0, os.path.join(src_dir, 'helpers'))
from helpers.logger import info, error, debug, warning
from helpers.file_utils import FileUtils


class RealMadridPlayersAnalyzer:
    """
    Główna klasa analizy zawodników Real Madryt.
    
    Przeprowadza kompleksową analizę danych zawodników, obliczając
    statystyki indywidualne, formę, wydajność oraz metryki zespołowe.
    Generuje podstawowy DataFrame używany przez inne moduły analizy.
    
    Attributes:
        data_loader (DataLoader): Loader danych zawodników i meczów
        season_manager (SeasonManager): Manager sezonów La Liga
        player_manager (PlayerManager): Manager danych zawodników
        statistics_calculator (StatisticsCalculator): Kalkulator statystyk
        data_aggregator (DataAggregator): Agregator finalnych danych
        base_path (str): Ścieżka bazowa do danych
    """
    
    def __init__(self, base_path=None):
        """
        Inicjalizuje analizator danych zawodników Real Madryt.
        
        Args:
            base_path (str, optional): Ścieżka bazowa do katalogów z danymi
            
        Notes:
            - Automatycznie inicjalizuje wszystkie wymagane komponenty
            - Wczytuje dane przy tworzeniu obiektu dla szybszego dostępu
            - Przygotowuje struktury do dalszego przetwarzania
        """
        self.base_path = base_path
        self.setup_components()
        self.load_data()
        
        info("RealMadridPlayersAnalyzer zainicjalizowany pomyślnie")
    
    def setup_components(self):
        """
        Inicjalizuje wszystkie komponenty analizy zawodników.
        
        Notes:
            - DataLoader: ładowanie danych zawodników i meczów
            - SeasonManager: zarządzanie datami sezonów
            - PlayerManager: zarządzanie danymi zawodników
            - StatisticsCalculator: obliczenia statystyk
            - DataAggregator: agregacja finalnych wyników
        """
        self.data_loader = DataLoader(self.base_path)
        self.season_manager = SeasonManager()
        
        info("Komponenty bazowe zainicjalizowane")
    
    def load_data(self):
        """
        Ładuje wszystkie wymagane dane i inicjalizuje pozostałe komponenty.
        
        Notes:
            - Ładuje dane zawodników, meczów i statystyk
            - Inicjalizuje PlayerManager z danymi zawodników
            - Konfiguruje StatisticsCalculator i DataAggregator
            - Przygotowuje system do analizy
        """
        self.data_loader.load_all_data()
        
        self.player_manager = PlayerManager(self.data_loader.players)
        self.statistics_calculator = StatisticsCalculator(
            self.data_loader, 
            self.season_manager,
            self.player_manager
        )
        self.data_aggregator = DataAggregator(
            self.data_loader,
            self.season_manager,
            self.player_manager,
            self.statistics_calculator
        )
        
        info("Wszystkie dane załadowane i komponenty skonfigurowane")
    
    def validate_data_completeness(self, result_df):
        """
        Waliduje kompletność wygenerowanego DataFrame.
        
        Args:
            result_df (pd.DataFrame): DataFrame do walidacji
            
        Returns:
            dict: Raport walidacji z metrykami jakości
            
        Notes:
            - Sprawdza liczbę wierszy i kolumn
            - Oblicza procent brakujących wartości
            - Analizuje pokrycie zawodników
            - Generuje raport jakości danych
        """
        validation_report = {
            'total_matches': len(result_df),
            'total_columns': len(result_df.columns),
            'missing_values_count': result_df.isnull().sum().sum(),
            'missing_percentage': (result_df.isnull().sum().sum() / (len(result_df) * len(result_df.columns))) * 100,
            'date_range': {
                'start': result_df['M_DATE'].min() if 'M_DATE' in result_df.columns else None,
                'end': result_df['M_DATE'].max() if 'M_DATE' in result_df.columns else None
            },
            'player_columns': len([col for col in result_df.columns if col.startswith(('P1_', 'P2_', 'P3_'))])
        }
        
        info(f"Walidacja danych zawodników:")
        info(f"  - Mecze: {validation_report['total_matches']}")
        info(f"  - Kolumny: {validation_report['total_columns']}")
        info(f"  - Kolumny zawodników: {validation_report['player_columns']}")
        info(f"  - Kompletność: {100 - validation_report['missing_percentage']:.1f}%")
        
        return validation_report
    
    def analyze(self, skip_first_matches=5):
        """
        Przeprowadza pełną analizę zawodników i zwraca przetworzoną ramkę danych.
        
        Args:
            skip_first_matches (int): Liczba pierwszych meczów do pominięcia
            
        Returns:
            pd.DataFrame: Kompletna ramka danych ze wszystkimi statystykami zawodników
            
        Notes:
            - Wykonuje pełną analizę danych zawodników Real Madryt
            - Oblicza statystyki indywidualne dla maksymalnie 16 zawodników na mecz
            - Generuje podstawowy DataFrame dla innych modułów
            - Zawiera dane meczowe, statystyki zawodników oraz metryki zespołowe
            - Waliduje kompletność wyników
        """
        info("Rozpoczynam analizę zawodników Real Madryt")
        
        try:
            result_df = self.data_aggregator.process_all_matches()
            
            validation_report = self.validate_data_completeness(result_df)
            
            info(f"Analiza zawodników zakończona pomyślnie:")
            info(f"  - Wygenerowano dane dla {len(result_df)} meczów")
            info(f"  - DataFrame zawiera {len(result_df.columns)} kolumn")
            info(f"  - Okres analizy: {validation_report['date_range']['start']} - {validation_report['date_range']['end']}")
            
            return result_df
            
        except Exception as e:
            error(f"Błąd podczas analizy zawodników: {str(e)}")
            raise
    
    def get_summary_statistics(self, result_df):
        """
        Generuje statystyki podsumowujące analizę zawodników.
        
        Args:
            result_df (pd.DataFrame): DataFrame z wynikami analizy
            
        Returns:
            dict: Słownik ze statystykami podsumowującymi
            
        Notes:
            - Oblicza średnie oceny zawodników
            - Analizuje najczęściej występujących zawodników
            - Generuje metryki pokrycia danych
            - Przydatne do raportowania i debugowania
        """
        summary = {
            'total_matches_analyzed': len(result_df),
            'date_range': {
                'start': result_df['M_DATE'].min(),
                'end': result_df['M_DATE'].max()
            },
            'columns_breakdown': {
                'total': len(result_df.columns),
                'player_columns': len([col for col in result_df.columns if col.startswith(('P1_', 'P2_', 'P3_'))]),
                'match_columns': len([col for col in result_df.columns if col.startswith('M_')]),
                'other_columns': len(result_df.columns) - len([col for col in result_df.columns if col.startswith(('P1_', 'P2_', 'P3_', 'M_'))])
            },
            'data_completeness': (1 - result_df.isnull().sum().sum() / (len(result_df) * len(result_df.columns))) * 100
        }
        
        return summary