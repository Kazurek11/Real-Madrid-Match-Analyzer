"""
Główny moduł analizy drużyn przeciwników Real Madryt.

Ten moduł analizuje statystyki przeciwników Real Madryt, obliczając
wydajność ostatnich meczów, formy sezonowe, statystyki przeciwko różnym
poziomom drużyn oraz kursy bukmacherskie. Generuje kompletne metryki
przeciwników dla każdego meczu Real Madryt.
"""

import numpy as np
import pandas as pd
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(os.path.dirname(current_dir))
project_root = os.path.dirname(src_dir)

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from finall_dataframe.rm_team.season_calculator import SeasonCalculator
from finall_dataframe.rm_team.stats_calculator import StatsCalculator
from finall_dataframe.rm_players.season_manager import SeasonManager
from helpers.logger import info, warning, error
from helpers.file_utils import FileUtils

from finall_dataframe.opp_team.data_loader import DataLoader
from finall_dataframe.opp_team.stats_functions import *
from finall_dataframe.opp_team.extended_stats import *


class OpponentTeamAnalyzer:
    """
    Analizator statystyk drużyn przeciwników Real Madryt.
    
    Analizuje wydajność przeciwników w każdym meczu Real Madryt, obliczając
    kompleksowe metryki formy, statystyki sezonowe, wydajność przeciwko różnym
    poziomom drużyn oraz kursy bukmacherskie dla kompletnej oceny siły przeciwnika.
    
    Attributes:
        base_df (pd.DataFrame): Podstawowy DataFrame z poprzednich analiz
        data_loader (DataLoader): Loader danych meczowych
        season_manager (SeasonManager): Manager sezonów La Liga
        rm_matches (pd.DataFrame): Dane meczów Real Madryt
        opp_matches (pd.DataFrame): Dane wszystkich meczów La Liga
        df_first_date (datetime): Data pierwszego meczu w analizie
        columns_to_add (list): Lista kolumn do dodania w analizie
    """
    
    def __init__(self):
        """
        Inicjalizuje analizator drużyn przeciwników.
        
        Automatycznie przygotowuje wszystkie komponenty wymagane do analizy
        statystyk przeciwników Real Madryt.
        """
        self.base_df = None
        self.df_first_date = None
        self.setup_data_sources()
        self.setup_components()
        self.define_analysis_columns()
        
        info("OpponentTeamAnalyzer zainicjalizowany pomyślnie")
    
    def set_base_dataframe(self, df):
        """
        Ustawia bazowy DataFrame z poprzednich etapów analizy.
        
        Args:
            df (pd.DataFrame): DataFrame z wynikami analiz zawodników i drużyny
            
        Notes:
            - Konwertuje kolumnę M_DATE do typu datetime jeśli potrzeba
            - Ustala punkt czasowy rozpoczęcia analizy (df_first_date)
            - Kopiuje DataFrame aby uniknąć modyfikacji oryginału
        """
        self.base_df = df.copy()
        
        if self.base_df["M_DATE"].dtype == 'object':
            self.base_df["M_DATE"] = pd.to_datetime(self.base_df["M_DATE"], format="%Y-%m-%d")
        
        self.df_first_date = self.base_df["M_DATE"].min()
        info(f"Ustawiono bazowy DataFrame: {len(self.base_df)} wierszy, data od: {self.df_first_date}")
    
    def setup_data_sources(self):
        """
        Inicjalizuje źródła danych dla analizy przeciwników.
        
        Notes:
            - Przygotowuje DataLoader do wczytywania danych meczowych
            - Konfiguruje dostęp do danych Real Madryt i wszystkich meczów La Liga
        """
        self.data_loader = DataLoader()
        info("Źródła danych dla analizy przeciwników załadowane")
    
    def setup_components(self):
        """
        Inicjalizuje komponenty analizy przeciwników.
        
        Notes:
            - SeasonManager: zarządzanie datami i okresami sezonów La Liga
            - Przygotowuje infrastrukturę kalkulacyjną
        """
        self.season_manager = SeasonManager()
        info("Komponenty analizy przeciwników zainicjalizowane")
    
    def define_analysis_columns(self):
        """
        Definiuje kolumny statystyk przeciwników do analizy.
        
        Notes:
            - 17 różnych metryk przeciwników obejmujących:
              * Statystyki ostatnich 5 meczów (OP_*_L5)
              * Średnie sezonowe (OP_PPM_SEA)
              * Wydajność przeciwko różnym poziomom drużyn
              * Kursy bukmacherskie (OP_ODD_W_L5, OP_ODD_L_L5)
              * Ogólne statystyki strzeleckie (OP_G_SCO_ALL, OP_G_CON_ALL)
        """
        self.columns_to_add = [
            'OP_G_SCO_L5', 'OP_G_CON_L5', 'OP_GDIF_L5', 'OP_OPP_POS_L5', 'OP_PPM_L5',
            'OP_PPM_SEA', 'OP_GPM_VS_TOP', 'OP_PPM_VS_TOP', 'OP_GPM_VS_MID',
            'OP_PPM_VS_MID', 'OP_GPM_VS_LOW', 'OP_PPM_VS_LOW',
            'OP_G_SCO_ALL', 'OP_G_CON_ALL', 'OP_G_SCO_G_CON_RAT', 'OP_ODD_W_L5', 'OP_ODD_L_L5'
        ]
        info(f"Zdefiniowano {len(self.columns_to_add)} kolumn analizy przeciwników")
    def prepare_dataframe(self):
        """
        Przygotowuje DataFrame z dodatkowymi kolumnami przeciwników.
        
        Returns:
            pd.DataFrame: DataFrame rozszerzony o kolumny przeciwników zainicjalizowane wartościami NaN
            
        Raises:
            ValueError: Gdy bazowy DataFrame nie został wcześniej ustawiony
            
        Notes:
            - Dodaje wszystkie kolumny zdefiniowane w columns_to_add
            - Inicjalizuje nowe kolumny wartościami NaN
            - Zachowuje wszystkie istniejące dane z poprzednich analiz
        """
        if self.base_df is None:
            raise ValueError("Bazowy DataFrame nie został ustawiony. Wywołaj set_base_dataframe() najpierw.")
        
        prepared_df = self.data_loader.prepare_columns(self.base_df.copy(), self.columns_to_add)
        info(f"DataFrame przygotowany: dodano {len(self.columns_to_add)} kolumn przeciwników")
        return prepared_df
    
    def calculate_opponent_statistics(self, prepared_df):
        """
        Oblicza statystyki przeciwników dla wszystkich meczów w okresie analizy.
        
        Args:
            prepared_df (pd.DataFrame): DataFrame przygotowany z kolumnami przeciwników
            
        Returns:
            dict: Słownik {match_id: statystyki_przeciwnika} dla wszystkich przetworzonych meczów
            
        Notes:
            - Przetwarza tylko mecze po dacie df_first_date
            - Identyfikuje przeciwnika na podstawie home_team_id/away_team_id
            - Oblicza 17 różnych statystyk przeciwnika dla każdego meczu
            - Obsługuje błędy z fallback do wartości NaN
            - Zaokrągla wartości liczbowe do 3 miejsc po przecinku
            - Loguje postęp co 10 przetworzonych meczów
        """
        rm_matches, opp_matches = self.data_loader.load_match_data()
        
        match_stats_dict = {}
        processed_matches = 0
        
        for _, match in rm_matches.iterrows():
            if pd.to_datetime(match['match_date']) < pd.to_datetime(self.df_first_date):
                continue
            
            match_id = match['match_id']
            match_date = match['match_date']
            opponent_id = match['home_team_id'] if match['home_team_id'] != 1 else match['away_team_id']
            
            try:
                calc = SeasonCalculator(rm_matches, self.season_manager, team_id=opponent_id)
                stats = StatsCalculator(rm_matches, opp_matches, self.season_manager)
                
                match_stats = {
                    'OP_G_SCO_L5': calculate_OP_G_SCO_L5(stats, match_date, opponent_id),
                    'OP_G_CON_L5': calculate_OP_G_CON_L5(stats, match_date, opponent_id),
                    'OP_GDIF_L5': calculate_OP_GDIF_L5(stats, match_date, opponent_id),
                    'OP_OPP_POS_L5': calculate_OP_OPP_POS_L5(stats, match_date, opponent_id),
                    'OP_PPM_L5': calculate_OP_PPM_L5(stats, match_date, opponent_id),
                    'OP_PPM_SEA': calculate_OP_PPM_SEA(calc, match_date),
                    'OP_GPM_VS_TOP': calculate_OP_GPM_1_9_PPR(calc, match_date),
                    'OP_PPM_VS_TOP': calculate_OP_PPM_1_9_PPR(calc, match_date),
                    'OP_GPM_VS_MID': calculate_OP_GPM_1_2__1_9_PPM(calc, match_date),
                    'OP_PPM_VS_MID': calculate_OP_PPM_1_2__1_9_PPM(calc, match_date),
                    'OP_GPM_VS_LOW': calculate_OP_GPM_0_1_2_PPM(calc, match_date),
                    'OP_PPM_VS_LOW': calculate_OP_PPM_0_1_2_PPM(calc, match_date),
                    'OP_G_SCO_ALL': calculate_OP_G_SCO_ALL(opponent_id, match_date, self.season_manager),
                    'OP_G_CON_ALL': calculate_OP_G_CON_ALL(opponent_id, match_date, self.season_manager),
                    'OP_G_SCO_G_CON_RAT': calculate_OP_G_SCO_G_CON_RAT(opponent_id, match_date, self.season_manager),
                    'OP_ODD_W_L5': calculate_OP_ODD_W_L5(opponent_id, match_date),
                    'OP_ODD_L_L5': calculate_OP_ODD_L_L5(opponent_id, match_date)
                }
                for key, value in match_stats.items():
                    if isinstance(value, (int, float)) and not np.isnan(value):
                        match_stats[key] = round(value, 3)
                
                match_stats_dict[match_id] = match_stats
                processed_matches += 1
                
                if processed_matches % 10 == 0:
                    info(f"Przetworzono {processed_matches} meczów przeciwników")
                
            except Exception as e:
                error(f"Błąd dla meczu przeciwnika (ID: {match_id}): {str(e)}")
                match_stats = {col: np.nan for col in self.columns_to_add}
                match_stats_dict[match_id] = match_stats
        
        info(f"Obliczono statystyki przeciwników dla {len(match_stats_dict)} meczów")
        return match_stats_dict
    
    def fill_dataframe_with_stats(self, prepared_df, match_stats_dict):
        """
        Wypełnia DataFrame obliczonymi statystykami przeciwników.
        
        Args:
            prepared_df (pd.DataFrame): DataFrame przygotowany z kolumnami przeciwników
            match_stats_dict (dict): Słownik ze statystykami dla każdego meczu
            
        Returns:
            pd.DataFrame: DataFrame z wypełnionymi wartościami przeciwników
            
        Notes:
            - Mapuje statystyki na podstawie MATCH_ID
            - Zachowuje wszystkie istniejące dane z poprzednich analiz
            - Wypełnia tylko te wiersze, dla których istnieją obliczone statystyki
            - Pozostawia NaN dla meczów bez danych przeciwników
        """
        filled_count = 0
        
        for idx, row in prepared_df.iterrows():
            match_id = row['MATCH_ID']
            
            if match_id in match_stats_dict:
                stats = match_stats_dict[match_id]
                
                for col_name, value in stats.items():
                    if col_name in prepared_df.columns:
                        prepared_df.at[idx, col_name] = value
                
                filled_count += 1
        
        info(f"Wypełniono statystyki przeciwników dla {filled_count} wierszy")
        return prepared_df
    
    def validate_opponent_analysis(self, result_df):
        """
        Waliduje wyniki analizy przeciwników pod kątem kompletności i jakości.
        
        Args:
            result_df (pd.DataFrame): DataFrame z wynikami analizy przeciwników
            
        Returns:
            dict: Raport walidacji z metrykami jakości analizy
            
        Notes:
            - Sprawdza liczbę dodanych kolumn przeciwników
            - Oblicza procent kompletności danych
            - Analizuje rozkład wartości w kluczowych kolumnach
            - Generuje szczegółowy raport jakości
        """
        opponent_columns = [col for col in result_df.columns if col.startswith('OP_')]
        
        validation_report = {
            'total_matches': len(result_df),
            'opponent_columns_added': len(opponent_columns),
            'opponent_missing_values': result_df[opponent_columns].isnull().sum().sum(),
            'opponent_completeness': (1 - result_df[opponent_columns].isnull().sum().sum() / 
                                    (len(result_df) * len(opponent_columns))) * 100,
            'columns_summary': {col: result_df[col].describe() for col in opponent_columns[:5]}
        }
        
        info(f"Walidacja analizy przeciwników:")
        info(f"  - Mecze: {validation_report['total_matches']}")
        info(f"  - Kolumny przeciwników: {validation_report['opponent_columns_added']}")
        info(f"  - Kompletność przeciwników: {validation_report['opponent_completeness']:.1f}%")
        
        return validation_report
    
    def analyze(self):
        """
        Główna metoda wykonująca kompletną analizę przeciwników Real Madryt.
        
        Returns:
            pd.DataFrame: Kompletny DataFrame z dodanymi statystykami przeciwników
            
        Raises:
            ValueError: Gdy bazowy DataFrame nie został wcześniej ustawiony
            
        Notes:
            Proces analizy obejmuje:
            1. Przygotowanie DataFrame z kolumnami przeciwników
            2. Obliczenie statystyk dla wszystkich przeciwników
            3. Wypełnienie DataFrame obliczonymi wartościami
            4. Walidację wyników i utworzenie raportu
            
            Wynikowy DataFrame zawiera wszystkie poprzednie analizy plus:
            - 17 kolumn statystyk przeciwników
            - Metryki formy i wydajności przeciwników
            - Statystyki przeciwko różnym poziomom drużyn
            - Kursy bukmacherskie na wygraną/przegranie przeciwnika
        """
        if self.base_df is None:
            raise ValueError("Bazowy DataFrame nie został ustawiony. Wywołaj set_base_dataframe() najpierw.")
        
        info("Rozpoczynam analizę przeciwników Real Madrid")
        
        prepared_df = self.prepare_dataframe()
        match_stats = self.calculate_opponent_statistics(prepared_df)
        result_df = self.fill_dataframe_with_stats(prepared_df, match_stats)
        validation_report = self.validate_opponent_analysis(result_df)
        
        info(f"Zakończono analizę przeciwników Real Madrid:")
        info(f"  - {len(result_df)} wierszy, {len(result_df.columns)} kolumn")
        info(f"  - Dodano {validation_report['opponent_columns_added']} kolumn przeciwników")
        
        return result_df