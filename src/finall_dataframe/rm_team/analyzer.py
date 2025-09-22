"""
Główny moduł analizy drużyny Real Madryt.

Ten moduł łączy analizę zawodników z analizą drużynową, obliczając statystyki
trenera, wydajność przeciwko różnym typom przeciwników oraz metryki sezonowe.
Generuje kompletny DataFrame z wszystkimi metrykami potrzebnymi do analizy.
"""

import pandas as pd
import os
import sys
import numpy as np
import traceback

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(os.path.dirname(current_dir))
project_root = os.path.dirname(src_dir)

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# from finall_dataframe.rm_players.analyzer import RealMadridPlayersAnalyzer
from finall_dataframe.rm_players.season_manager import SeasonManager
from helpers.file_utils import FileUtils
from helpers.logger import info, error, warning, critical, debug

from finall_dataframe.rm_team.config import COLUMNS_TO_ADD
from finall_dataframe.rm_team.utils import add_missing_columns
from finall_dataframe.rm_team.coach_manager import CoachManager
from finall_dataframe.rm_team.stats_calculator import StatsCalculator
from finall_dataframe.rm_team.season_calculator import SeasonCalculator


class RealMadridTeamAnalyzer:
    """
    Główna klasa analizy drużyny Real Madryt.
    
    Łączy dane zawodników z analizą drużynową, obliczając kompleksowe
    statystyki obejmujące trenera, wydajność sezonową i metryki przeciwko
    różnym typom przeciwników. Generuje gotowy DataFrame do machine learning.
    
    Attributes:
        team_id (int): ID drużyny (1 dla Real Madryt)
        base_df (pd.DataFrame): Podstawowy DataFrame z analizy zawodników
        df_prepared (pd.DataFrame): DataFrame rozszerzony o kolumny drużynowe
        coach_manager (CoachManager): Manager danych trenerów
        stats_calculator (StatsCalculator): Kalkulator statystyk meczowych
        season_calculator (SeasonCalculator): Kalkulator statystyk sezonowych
        df_first_date (datetime): Data pierwszego meczu w analizie
    """
    
    def __init__(self, team_id=1):
        """
        Inicjalizuje analizator drużyny.
        
        Args:
            team_id (int): ID drużyny (domyślnie 1 dla Real Madryt)
            
        Notes:
            - Automatycznie inicjalizuje źródła danych i managery
            - Ustawia podstawowe atrybuty dla analizy
            - base_df zostanie ustawiony przez set_base_dataframe()
        """
        self.team_id = team_id
        self.base_df = None
        self.df_prepared = None
        self.df_first_date = None
        self.setup_data_sources()
        self.setup_managers()
    
    def set_base_dataframe(self, df):
        """
        Ustawia bazowy DataFrame z analizy zawodników.
        
        Args:
            df (pd.DataFrame): DataFrame z analizy zawodników
            
        Notes:
            - Konwertuje kolumnę M_DATE do datetime jeśli potrzeba
            - Ustawia df_first_date jako punkt odniesienia czasowego
            - Przygotowuje DataFrame do dalszej analizy drużynowej
        """
        self.base_df = df.copy()
        
        if self.base_df["M_DATE"].dtype == 'object':
            self.base_df["M_DATE"] = pd.to_datetime(self.base_df["M_DATE"], format="%Y-%m-%d")
        
        self.df_first_date = self.base_df["M_DATE"].min()
        info(f"Ustawiono bazowy DataFrame: {len(self.base_df)} wierszy, data od: {self.df_first_date}")
    
    def setup_data_sources(self):
        """
        Inicjalizuje źródła danych dla analizy drużynowej.
        
        Raises:
            FileNotFoundError: Gdy brak wymaganych plików CSV
            
        Notes:
            - Wczytuje dane trenerów z RM_coach.csv
            - Wczytuje mecze RM z RM_all_matches_stats.csv
            - Wczytuje mecze przeciwników z all_matches.csv
            - Konwertuje daty do formatu datetime64[ns]
        """
        rm_path = os.path.join(FileUtils.get_project_root(), 'Data', 'Real')
        opp_path = os.path.join(FileUtils.get_project_root(), 'Data', 'Mecze', 'all_season', 'merged_matches')
        
        self.coach_data = FileUtils.load_csv_safe(os.path.join(rm_path, 'RM_coach.csv'))
        self.rm_matches = FileUtils.load_csv_safe(os.path.join(rm_path, 'RM_all_matches_stats.csv'))
        self.opp_matches = FileUtils.load_csv_safe(os.path.join(opp_path, 'all_matches.csv'))
        
        info("Źródła danych dla analizy drużynowej załadowane pomyślnie")
    
    def setup_managers(self):
        """
        Inicjalizuje klasy zarządzające różnymi aspektami analizy.
        
        Notes:
            - CoachManager: zarządzanie danymi trenerów (ID, okresy kadencji)
            - StatsCalculator: obliczenia statystyk ostatnich meczów i ocen trenerów
            - SeasonCalculator: metryki sezonowe i przeciwko poziomom drużyn (TOP/MID/LOW)
            - SeasonManager: zarządzanie datami sezonów La Liga
        """
        season_manager = SeasonManager()
        self.coach_manager = CoachManager(self.coach_data)
        self.stats_calculator = StatsCalculator(self.rm_matches, self.opp_matches, season_manager)
        self.season_calculator = SeasonCalculator(self.rm_matches, season_manager, team_id=self.team_id)
        
        info("Managery analizy drużynowej zainicjalizowane pomyślnie")
    
    def prepare_dataframe(self):
        """
        Przygotowuje DataFrame z dodatkowymi kolumnami drużynowymi.
        
        Returns:
            pd.DataFrame: DataFrame z dodanymi kolumnami zdefiniowanymi w COLUMNS_TO_ADD
            
        Raises:
            ValueError: Gdy base_df nie został ustawiony
            
        Notes:
            - Wymaga wcześniejszego wywołania set_base_dataframe()
            - Kopiuje bazowy DataFrame zawodników
            - Dodaje wszystkie kolumny wymagane dla analizy drużynowej
            - Inicjalizuje nowe kolumny z wartościami NaN
        """
        if self.base_df is None:
            raise ValueError("Bazowy DataFrame nie został ustawiony. Wywołaj set_base_dataframe() najpierw.")
        
        self.df_prepared = add_missing_columns(self.base_df.copy(), COLUMNS_TO_ADD)
        info(f"DataFrame przygotowany: dodano {len(COLUMNS_TO_ADD)} kolumn drużynowych")
        return self.df_prepared
    
    def calculate_match_statistics(self):
        """
        Oblicza statystyki dla wszystkich meczów Real Madryt.
        
        Returns:
            dict: Słownik {match_id: {kolumna: wartość}} ze statystykami
            
        Notes:
            - Przetwarza tylko mecze po dacie df_first_date
            - Dla każdego meczu oblicza:
              * ID trenera i jego oceny (ostatni sezon, ostatnie 5 meczów)
              * Statystyki ostatnich 5 meczów (gole, punkty, różnica bramek)
              * Średnie sezonowe punktów na mecz
              * Wydajność przeciwko drużynom TOP/MID/LOW
            - Obsługuje błędy z fallback do wartości NaN
            - Zaokrągla wszystkie wartości do 3 miejsc po przecinku
        """
        match_stats_dict = {}
        
        # Filtruj mecze i zlicz
        filtered_matches = self.rm_matches[
            pd.to_datetime(self.rm_matches['match_date']) >= pd.to_datetime(self.df_first_date)
        ].copy()
        
        total_matches = len(filtered_matches)
        processed_matches = 0
        successful_matches = 0
        failed_matches = 0
        
        info(f"=== ROZPOCZYNAM OBLICZANIE STATYSTYK DRUŻYNOWYCH ===")
        info(f"Liczba meczów do przetworzenia: {total_matches}")
        info(f"Okres analizy: od {self.df_first_date}")
        
        for _, match in filtered_matches.iterrows():
            match_id = match['match_id']
            match_date = match['match_date']
            processed_matches += 1
            
            # Log co 10 meczów
            if processed_matches % 10 == 0:
                progress = (processed_matches / total_matches) * 100
                info(f"Postęp meczów: {processed_matches}/{total_matches} ({progress:.1f}%) - Udane: {successful_matches}, Błędy: {failed_matches}")
            
            coach_id = self.coach_manager.get_coach_id_by_date(match_date)
            if coach_id is None:
                error(f"Nie znaleziono trenera dla meczu z datą {match_date}")
                failed_matches += 1
                continue
            
            if not self.coach_manager.validate_coach_exists(coach_id):
                failed_matches += 1
                continue
            
            try:
                debug(f"Obliczam statystyki dla meczu ID: {match_id}, data: {match_date}")
                
                last_5_stats = self.stats_calculator.calculate_last_5_stats(match_date, 1, 5)
                
                match_stats = {
                    'RM_C_ID': coach_id,
                    'RM_C_RT_PS': round(self.stats_calculator.calculate_coach_rating_last_season(coach_id, match_date), 3),
                    'RM_C_FORM5': round(self.stats_calculator.calculate_coach_rating_last_5(match_date), 3),
                    'RM_PPM_SEA': round(self.season_calculator.calculate_team_points_per_match_season(match_date), 3),
                    
                    'RM_GPM_VS_TOP': round(self.season_calculator.calculate_team_goals_against_top(match_date), 3),
                    'RM_PPM_VS_TOP': round(self.season_calculator.calculate_team_points_against_top(match_date), 3),
                    'RM_GPM_VS_MID': round(self.season_calculator.calculate_team_goals_against_mid(match_date), 3),
                    'RM_PPM_VS_MID': round(self.season_calculator.calculate_team_points_against_mid(match_date), 3),
                    'RM_GPM_VS_LOW': round(self.season_calculator.calculate_team_goals_against_low(match_date), 3),
                    'RM_PPM_VS_LOW': round(self.season_calculator.calculate_team_points_against_low(match_date), 3)
                }
                
                if last_5_stats:
                    for key, value in last_5_stats.items():
                        match_stats[key] = round(value, 3)
                else:
                    for key in ['RM_G_SCO_L5', 'RM_G_CON_L5', 'RM_GDIF_L5', 'RM_PPM_L5', 'RM_OPP_PPM_L5']:
                        match_stats[key] = np.nan
                
                successful_matches += 1
                debug(f"✓ Pomyślnie obliczono statystyki dla meczu ID: {match_id}")
                
            except Exception as e:
                failed_matches += 1
                error(f"✗ Błąd dla meczu (ID: {match_id}): {str(e)}")
                error(f"Stacktrace: {traceback.format_exc()}")
                
                match_stats = {col: np.nan for col in COLUMNS_TO_ADD}
                match_stats['RM_C_ID'] = coach_id
            
            match_stats_dict[match_id] = match_stats
        
        info(f"=== ZAKOŃCZONO OBLICZANIE STATYSTYK DRUŻYNOWYCH ===")
        info(f"Łącznie przetworzono: {processed_matches} meczów")
        info(f"Pomyślnie: {successful_matches} ({(successful_matches/processed_matches)*100:.1f}%)")
        info(f"Błędy: {failed_matches} ({(failed_matches/processed_matches)*100:.1f}%)")
        info(f"Utworzono statystyki dla {len(match_stats_dict)} meczów")
        
        return match_stats_dict
    
    def fill_dataframe_with_stats(self, match_stats_dict):
        """
        Wypełnia DataFrame obliczonymi statystykami drużynowymi.
        
        Args:
            match_stats_dict (dict): Słownik ze statystykami dla każdego meczu
            
        Returns:
            pd.DataFrame: DataFrame z wypełnionymi statystykami drużynowymi
            
        Notes:
            - Mapuje statystyki na podstawie MATCH_ID
            - Zachowuje wszystkie istniejące dane z analizy zawodników
            - Wypełnia tylko te wiersze, dla których istnieją statystyki
            - Pozostawia NaN dla meczów bez obliczonych statystyk
        """
        filled_count = 0
        total_rows = len(self.df_prepared)
        
        info(f"=== ROZPOCZYNAM WYPEŁNIANIE DATAFRAME ===")
        info(f"Liczba wierszy do wypełnienia: {total_rows}")
        info(f"Dostępne statystyki dla {len(match_stats_dict)} meczów")
        
        for idx, row in self.df_prepared.iterrows():
            match_id = row['MATCH_ID']
            
            if match_id in match_stats_dict:
                stats = match_stats_dict[match_id]
                
                for col_name, value in stats.items():
                    self.df_prepared.at[idx, col_name] = value
                
                filled_count += 1
                
                # Log co 20 wypełnień
                if filled_count % 20 == 0:
                    progress = (filled_count / len(match_stats_dict)) * 100
                    debug(f"Wypełniono: {filled_count}/{len(match_stats_dict)} ({progress:.1f}%)")
        
        success_rate = (filled_count / total_rows) * 100
        info(f"=== ZAKOŃCZONO WYPEŁNIANIE DATAFRAME ===")
        info(f"Wypełniono statystyki dla {filled_count}/{total_rows} wierszy ({success_rate:.1f}%)")
        
        if filled_count < total_rows:
            warning(f"{total_rows - filled_count} wierszy pozostało bez statystyk drużynowych")
        
        return self.df_prepared
    
    def analyze(self):
        """
        Główna metoda analizy drużyny Real Madryt.
        
        Returns:
            pd.DataFrame: Kompletny DataFrame z analizą zawodników i drużyny
            
        Raises:
            ValueError: Gdy base_df nie został ustawiony
            
        Notes:
            - Wykonuje pełny pipeline analizy:
              1. Przygotowanie DataFrame z dodatkowymi kolumnami
              2. Obliczenie statystyk dla wszystkich meczów
              3. Wypełnienie DataFrame obliczonymi wartościami
            - Wymaga wcześniejszego wywołania set_base_dataframe()
            - Łączy analizę zawodników z metrykami drużynowymi
            - Zwraca gotowy DataFrame do dalszego przetwarzania
        """
        if self.base_df is None:
            raise ValueError("Bazowy DataFrame nie został ustawiony. Wywołaj set_base_dataframe() najpierw.")
        
        info("Rozpoczynam analizę zespołu Real Madrid")
        
        self.prepare_dataframe()
        match_stats = self.calculate_match_statistics()
        result_df = self.fill_dataframe_with_stats(match_stats)
        
        info(f"Zakończono analizę zespołu Real Madrid: {len(result_df)} wierszy, {len(result_df.columns)} kolumn")
        return result_df