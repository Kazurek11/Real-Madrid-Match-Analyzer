"""
Główny analizator Head-to-Head dla meczów Real Madryt.

Ten moduł oblicza statystyki historycznych starć między Real Madryt
a przeciwnikami, obejmujące wyniki ostatnich 5 spotkań, średnie punkty
na mecz w całej historii oraz kursy bukmacherskie na zwycięstwo RM.
"""

import numpy as np
import pandas as pd
from helpers.logger import info, error
from .config import H2H_COLUMNS
from .data_loader import H2HDataLoader
from .h2h_calculator import calculate_h2h_stats, calculate_h2h_overall_ppm
from .odds_calculator import get_rm_odds
from .validators import validate_h2h_analysis_results

class HeadToHeadAnalyzer:
    """
    Analizator statystyk Head-to-Head między Real Madryt a przeciwnikami.
    
    Oblicza kompleksowe statystyki historycznych starć obejmujące:
    - Procent wygranych w ostatnich 5 meczach
    - Różnicę bramkową w ostatnich 5 spotkaniach  
    - Średnie punkty na mecz w ostatnich 5 i ogólnie
    - Kursy bukmacherskie na zwycięstwo Real Madryt
    
    Attributes:
        base_df (pd.DataFrame): Bazowy DataFrame z poprzednich analiz
        df_first_date (pd.Timestamp): Data pierwszego meczu w analizie
        data_loader (H2HDataLoader): Ładowarka danych meczowych
        rm_matches (pd.DataFrame): Mecze Real Madryt z pełnymi statystykami
        opp_matches (pd.DataFrame): Mecze przeciwników z Liga
    """
    
    def __init__(self):
        """
        Inicjalizuje analizator Head-to-Head.
        
        Automatycznie ładuje dane meczowe Real Madryt i przeciwników
        oraz przygotowuje środowisko do obliczeń statystyk H2H.
        """
        self.base_df = None
        self.df_first_date = None
        self.data_loader = H2HDataLoader()
        self.rm_matches, self.opp_matches = self.data_loader.load_data()
        info("HeadToHeadAnalyzer zainicjalizowany pomyślnie")
    
    def set_base_dataframe(self, df):
        """
        Ustawia bazowy DataFrame z poprzednich etapów analizy.
        
        Args:
            df (pd.DataFrame): DataFrame z wynikami analiz zawodników, drużyny i przeciwników
            
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
    
    def prepare_dataframe(self):
        """
        Przygotowuje DataFrame z dodatkowymi kolumnami Head-to-Head.
        
        Returns:
            pd.DataFrame: DataFrame rozszerzony o kolumny H2H zainicjalizowane wartościami NaN
            
        Raises:
            ValueError: Gdy bazowy DataFrame nie został wcześniej ustawiony
            
        Notes:
            - Dodaje 5 kolumn H2H zdefiniowanych w H2H_COLUMNS
            - Inicjalizuje wszystkie nowe kolumny wartościami NaN
            - Zachowuje wszystkie istniejące dane z poprzednich analiz
        """
        if self.base_df is None:
            raise ValueError("Bazowy DataFrame nie został ustawiony. Wywołaj set_base_dataframe() najpierw.")
        
        prepared_df = self.base_df.copy()
        
        for col in H2H_COLUMNS:
            prepared_df[col] = np.nan
        
        info(f"DataFrame przygotowany: dodano {len(H2H_COLUMNS)} kolumn H2H")
        return prepared_df
    
    def calculate_match_h2h_stats(self, match_id, match_date, opponent_id):
        """
        Oblicza wszystkie statystyki Head-to-Head dla pojedynczego meczu.
        
        Args:
            match_id (int): Unikalny identyfikator meczu
            match_date (str/datetime): Data meczu
            opponent_id (int): ID drużyny przeciwnika
            
        Returns:
            dict: Słownik ze statystykami H2H:
                - H2H_RM_W_L5: Procent wygranych w ostatnich 5 meczach
                - H2H_RM_GDIF_L5: Średnia różnica bramkowa w ostatnich 5 meczach
                - H2H_PPM_L5: Średnie punkty na mecz w ostatnich 5 spotkaniach
                - H2H_PPM: Średnie punkty na mecz w całej historii starć
                - H2H_EXISTS: Czy istnieją wcześniejsze mecze H2H (0/1)
                - RM_ODD_W: Kurs bukmacherski na zwycięstwo Real Madryt
        """
        from .h2h_calculator import is_playing_before
        
        last_5_stats = calculate_h2h_stats(self.rm_matches, opponent_id, match_date, 5)
        overall_ppm = calculate_h2h_overall_ppm(self.rm_matches, opponent_id, match_date)
        rm_odds = get_rm_odds(self.rm_matches, match_id, opponent_id, match_date)
        h2h_exists = is_playing_before(self.rm_matches, match_date, opponent_id)
        
        h2h_stats = {
            'H2H_RM_W_L5': last_5_stats['win_ratio'] if last_5_stats else np.nan,
            'H2H_RM_GDIF_L5': last_5_stats['goals_balance'] if last_5_stats else np.nan,
            'H2H_PPM_L5': last_5_stats['points_per_match'] if last_5_stats else np.nan,
            'H2H_PPM': overall_ppm if overall_ppm is not None else np.nan,
            'H2H_EXISTS': 1 if h2h_exists else 0,  # Zawsze zwraca 0 lub 1
            'RM_ODD_W': rm_odds if rm_odds is not None else np.nan
        }
        
        # Zaokrąglij wartości numeryczne (oprócz H2H_EXISTS)
        for key, value in h2h_stats.items():
            if key != 'H2H_EXISTS' and isinstance(value, (int, float)) and not np.isnan(value):
                h2h_stats[key] = round(value, 3)
        
        return h2h_stats
    
    def calculate_h2h_statistics(self, prepared_df):
        """
        Oblicza statystyki Head-to-Head dla wszystkich meczów w okresie analizy.
        
        Args:
            prepared_df (pd.DataFrame): DataFrame przygotowany z kolumnami H2H
            
        Returns:
            dict: Słownik {match_id: statystyki_h2h} dla wszystkich przetworzonych meczów
            
        Notes:
            - Przetwarza tylko mecze po dacie df_first_date
            - Loguje postęp co 10 przetworzonych meczów
            - W przypadku błędów dla konkretnego meczu wypełnia kolumny wartościami NaN
            - Identyfikuje przeciwnika na podstawie home_team_id/away_team_id
        """
        h2h_stats_dict = {}
        processed_matches = 0
        
        for _, match in self.rm_matches.iterrows():
            if pd.to_datetime(match['match_date']) < pd.to_datetime(self.df_first_date):
                continue
            
            match_id = match['match_id']
            match_date = match['match_date']
            opponent_id = match['home_team_id'] if match['home_team_id'] != 1 else match['away_team_id']
            
            try:
                match_stats = self.calculate_match_h2h_stats(match_id, match_date, opponent_id)
                h2h_stats_dict[match_id] = match_stats
                processed_matches += 1
                
                if processed_matches % 10 == 0:
                    info(f"Przetworzono {processed_matches} meczów H2H")
                
            except Exception as e:
                error(f"Błąd przy obliczaniu statystyk H2H dla meczu {match_id}: {str(e)}")
                h2h_stats_dict[match_id] = {col: np.nan for col in H2H_COLUMNS}
        
        info(f"Obliczono statystyki H2H dla {len(h2h_stats_dict)} meczów")
        return h2h_stats_dict
    
    def fill_dataframe_with_stats(self, prepared_df, h2h_stats_dict):
        """
        Wypełnia DataFrame obliczonymi statystykami Head-to-Head.
        
        Args:
            prepared_df (pd.DataFrame): DataFrame przygotowany z kolumnami H2H
            h2h_stats_dict (dict): Słownik ze statystykami dla każdego meczu
            
        Returns:
            pd.DataFrame: DataFrame z wypełnionymi wartościami H2H
            
        Notes:
            - Mapuje statystyki na podstawie MATCH_ID
            - Wypełnia tylko te wiersze, dla których istnieją obliczone statystyki
            - Pozostawia NaN dla meczów bez danych H2H
            - Loguje liczbę pomyślnie wypełnionych wierszy
        """
        filled_count = 0
        
        for idx, row in prepared_df.iterrows():
            match_id = row.get('MATCH_ID')
            
            if match_id in h2h_stats_dict:
                stats = h2h_stats_dict[match_id]
                
                for col_name, value in stats.items():
                    if col_name in prepared_df.columns:
                        prepared_df.at[idx, col_name] = value
                
                filled_count += 1
        
        info(f"Wypełniono statystyki H2H dla {filled_count} wierszy")
        return prepared_df
    
    def analyze(self):
        """
        Główna metoda wykonująca kompletną analizę Head-to-Head.
        
        Returns:
            pd.DataFrame: Kompletny DataFrame z dodanymi statystykami H2H
            
        Raises:
            ValueError: Gdy bazowy DataFrame nie został wcześniej ustawiony
            
        Notes:
            Proces analizy obejmuje:
            1. Przygotowanie DataFrame z kolumnami H2H
            2. Obliczenie statystyk dla wszystkich meczów
            3. Wypełnienie DataFrame obliczonymi wartościami
            4. Walidację wyników i utworzenie raportu
            
            Wynikowy DataFrame zawiera wszystkie poprzednie analizy plus:
            - 5 kolumn statystyk Head-to-Head
            - Kursy bukmacherskie na zwycięstwo RM
            - Historyczne wyniki przeciwko każdemu przeciwnikowi
        """
        if self.base_df is None:
            raise ValueError("Bazowy DataFrame nie został ustawiony. Wywołaj set_base_dataframe() najpierw.")
        
        info("Rozpoczynam analizę Head-to-Head Real Madrid")
        
        prepared_df = self.prepare_dataframe()
        h2h_stats = self.calculate_h2h_statistics(prepared_df)
        result_df = self.fill_dataframe_with_stats(prepared_df, h2h_stats)
        validation_report = validate_h2h_analysis_results(result_df)
        
        info(f"Zakończono analizę H2H Real Madrid:")
        info(f"  - {len(result_df)} wierszy, {len(result_df.columns)} kolumn")
        info(f"  - Dodano {validation_report['h2h_columns_added']} kolumn H2H")
        
        return result_df