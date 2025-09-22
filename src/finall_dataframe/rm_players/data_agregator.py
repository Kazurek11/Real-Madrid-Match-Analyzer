import pandas as pd
import numpy as np
import traceback
import sys
import os
from .data_loader import DataLoader
from .player_manager import PlayerManager
from .statistics_calculator import StatisticsCalculator

current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from helpers.logger import info, error, debug, warning
from data_processing.const_variable import SEASON_DATES as SEASON

class DataAggregator:
    """Klasa odpowiedzialna za agregację przetworzonych danych do finalnej ramki danych"""
    
    def __init__(self, data_loader, season_manager, player_manager, statistics_calculator):
        """
        Inicjalizuje agregator danych z komponentami systemu.
        
        Args:
            data_loader (DataLoader): Obiekt dostarczający dane źródłowe
            season_manager (SeasonManager): Obiekt zarządzający sezonami
            player_manager (PlayerManager): Obiekt zarządzający informacjami o zawodnikach
            statistics_calculator (StatisticsCalculator): Obiekt obliczający statystyki
            
        Notes:
            - Przechowuje referencje do ramek danych z meczami i statystykami
            - Automatycznie definiuje schemat kolumn wyjściowych
        """
        self.data_loader = data_loader
        self.season_manager = season_manager
        self.player_manager = player_manager
        self.statistics_calculator = statistics_calculator
        
        self.matches = data_loader.matches
        self.individual = data_loader.individual
        
        self.columns = self._get_output_columns()
        
    def _get_output_columns(self):
        """
        Definiuje schemat kolumn dla wynikowej ramki danych.
        
        Returns:
            list: Lista nazw kolumn dla finalnej ramki danych
            
        Notes:
            - Zawiera 5 kolumn informacji o meczu
            - 176 kolumn danych zawodników (16 zawodników × 11 statystyk)
            - 3 kolumny statystyk drużynowych
        """
        match_columns = [
            'MATCH_ID', 'M_DATE', 'SEASON', 'IS_HOME', 'OPP_ID']
        
        player_columns = []
        for i in range(1, 17):  # For up to 16 players
            prefix = f'{i}'
            player_columns.extend([
                f'RM_PX_{prefix}',
                f'RM_PX_{prefix}_FSQ',
                f'RM_PX_{prefix}_R',
                f'RM_PX_{prefix}_POS',
                f'RM_PX_{prefix}_RT_M', 
                f'RM_PX_{prefix}__RT_PS',
                f'RM_PX_{prefix}_FORM5',
                f'RM_PX_{prefix}_WINR',
                f'RM_PX_{prefix}_G90',
                f'RM_PX_{prefix}_A90',
                f'RM_PX_{prefix}_KP9'
            ])
        
        team_columns = [
            'team_avg_rating',
            'team_form_last_5',
            'team_win_ratio'
        ]
        
        all_columns = match_columns + player_columns +  team_columns
        
        return all_columns
    
    def _create_match_players_dict(self):
        """
        Tworzy słownik zawodników dla każdego meczu z obliczonymi statystykami.
        
        Returns:
            dict: Słownik gdzie klucz to match_id, wartość to lista słowników z danymi zawodników
            
        Notes:
            - Filtruje dane po drugim sezonie (SEASON[1][0])
            - Wszystkie statystyki zaokrąglane do 3 miejsc po przecinku
            - W przypadku błędów tworzy domyślne dane z None
            - Każdy zawodnik ma 11 obliczonych statystyk
        """
        match_players_dict = {}
        
        processing_individual = self.individual[
            self.individual['match_date'] > pd.to_datetime(SEASON[1][0])].copy()
        
        total_players = len(processing_individual)
        processed_players = 0
        successful_players = 0
        failed_players = 0
        
        info(f"=== ROZPOCZYNAM PRZETWARZANIE ZAWODNIKÓW ===")
        info(f"Liczba rekordów do przetworzenia: {total_players}")
        
        for _, row in processing_individual.iterrows():
            match_id = row['match_id']
            player_name = row['player_name']
            match_date = row['match_date']
            processed_players += 1
            
            # Log co 50 zawodników
            if processed_players % 50 == 0:
                progress = (processed_players / total_players) * 100
                info(f"Postęp przetwarzania: {processed_players}/{total_players} ({progress:.1f}%) - Udane: {successful_players}, Błędy: {failed_players}")
            
            player_id = self.player_manager.get_player_id(player_name)
            if player_id is None:
                error(f"Zawodnik bez ID: {player_name}")
                failed_players += 1
                continue
                
            try:
                debug(f"Przetwarzam zawodnika: {player_name} (ID: {player_id}) w meczu {match_id}")
                
                player_data = {
                    'player_id': player_id,
                    'is_first_squad': row.get('is_first_squad', 0),
                    'is_value': row.get('is_value', 0),
                    'player_min': int(row.get('player_min', 0)),
                    'player_position': self.player_manager.get_player_position(player_id),
                    'last_match_rating': round(self.statistics_calculator.get_player_rating(player_id, match_date, 1), 3),
                    'last_season_rating': round(self.statistics_calculator.get_last_season_rating(player_id, match_date), 3),
                    'last_5_ratings': round(self.statistics_calculator.get_player_rating(player_id, match_date, 5), 3),
                    'win_ratio': round(self.statistics_calculator.get_player_win_ratio(player_id, match_date), 3),
                    'goals_per_90': round(self.statistics_calculator.get_player_stat(player_id, match_date, "G90"), 3),
                    'assists_per_90': round(self.statistics_calculator.get_player_stat(player_id, match_date, "A90"), 3),
                    'key_passes_per_90': round(self.statistics_calculator.get_player_stat(player_id, match_date, "KP90"), 3)
                }
                
                successful_players += 1
                debug(f"✓ Pomyślnie przetworzono: {player_name} - Ocena: {player_data['last_match_rating']}, Forma: {player_data['last_5_ratings']}")
                
            except Exception as e:
                failed_players += 1
                error(f"✗ Błąd przetwarzania zawodnika {player_name} (ID: {player_id}): {str(e)}")
                error(f"Stacktrace: {traceback.format_exc()}")
                
                player_data = {
                    'player_id': player_id,
                    'is_first_squad': row.get('is_first_squad', None),
                    'is_value': row.get('is_value', None),
                    'player_min': int(row.get('player_min', None)),
                    'player_position': 'unknown',
                    'last_match_rating':None,
                    'last_season_rating':None,
                    'last_5_ratings':None,
                    'win_ratio':None,
                    'goals_per_90':None,
                    'assists_per_90':None,
                    'key_passes_per_90':None
                }
                
            if match_id not in match_players_dict:
                match_players_dict[match_id] = []
                
            match_players_dict[match_id].append(player_data)
        
        info(f"=== ZAKOŃCZONO PRZETWARZANIE ZAWODNIKÓW ===")
        info(f"Łącznie przetworzono: {processed_players} rekordów")
        info(f"✓ Pomyślnie: {successful_players} ({(successful_players/processed_players)*100:.1f}%)")
        info(f"✗ Błędy: {failed_players} ({(failed_players/processed_players)*100:.1f}%)")
        info(f"📊 Utworzono dane dla {len(match_players_dict)} meczów")
            
        return match_players_dict
    
    def process_all_matches(self):
        """
        Przetwarza wszystkie mecze i tworzy finalną ramkę danych.
        
        Returns:
            pd.DataFrame: Kompletna ramka danych z przetworzonymi informacjami o 184 kolumnach
            
        Notes:
            - Filtruje mecze po drugim sezonie
            - Sortuje zawodników według składu i minut
            - Ogranicza do maksymalnie 16 zawodników na mecz
            - Wypełnia brakujące kolumny wartościami None/0
            - Zachowuje zdefiniowaną kolejność kolumn
        """
        try:
            info("=== ROZPOCZYNAM AGREGACJĘ MECZÓW ===")
            
            match_players_dict = self._create_match_players_dict()
            
            all_matches_data = []
            
            processing_matches = self.matches[
                self.matches['match_date'] > pd.to_datetime(SEASON[1][0])].copy()
            
            total_matches = len(processing_matches)
            processed_matches = 0
            
            info(f"Liczba meczów do przetworzenia: {total_matches}")
                
            for _, match in processing_matches.iterrows():
                match_id = match['match_id']
                processed_matches += 1
                
                if processed_matches % 20 == 0:
                    progress = (processed_matches / total_matches) * 100
                    info(f"Postęp meczów: {processed_matches}/{total_matches} ({progress:.1f}%)")
                
                if match_id not in match_players_dict:
                    debug(f"Brak danych zawodników dla meczu ID: {match_id}")
                    continue
                
                players_data = match_players_dict[match_id]
                debug(f"Przetwarzam mecz {match_id} z {len(players_data)} zawodnikami")
                
                players_data = sorted(
                    players_data, 
                    key=lambda x: (x['is_first_squad'], x['player_min']), 
                    reverse=True
                )
                
                players_data = players_data[:16]
                
                match_data = {
                    'MATCH_ID': match_id,
                    'M_DATE': match['match_date'],
                    'SEASON': self.season_manager.get_season_for_date(match['match_date'])['name'],
                    'IS_HOME': 1 if match['home_team_id'] == 1 else 0,
                    'OPP_ID': match['away_team_id'] if match['home_team_id'] == 1 else match['home_team_id']
                }
                
                team_stats = self._calculate_team_stats(match['match_date'], players_data)
                match_data.update(team_stats)
                
                starters_count = len([p for p in players_data if p.get('is_first_squad', 0) == 1])
                debug(f"✓ Mecz {match_id}: {len(players_data)} zawodników, {starters_count} w pierwszym składzie")
                
                for i, player in enumerate(players_data, 1):
                    if i > 16:
                        break
                        
                    prefix = f'{i}'
                    match_data.update({
                        f'RM_PX_{prefix}': player['player_id'],
                        f'RM_PX_{prefix}_FSQ': player['is_first_squad'],
                        f'RM_PX_{prefix}_R': player['is_value'],
                        f'RM_PX_{prefix}_POS': player['player_position'],
                        f'RM_PX_{prefix}_RT_M': player['last_match_rating'],
                        f'RM_PX_{prefix}__RT_PS': player['last_season_rating'],
                        f'RM_PX_{prefix}_FORM5': player['last_5_ratings'],
                        f'RM_PX_{prefix}_WINR': player['win_ratio'],
                        f'RM_PX_{prefix}_G90': player['goals_per_90'],
                        f'RM_PX_{prefix}_A90': player['assists_per_90'],
                        f'RM_PX_{prefix}_KP9': player['key_passes_per_90']
                    })
                
                for i in range(len(players_data) + 1, 17):
                    prefix = f'{i}'
                    match_data.update({
                        f'RM_PX_{prefix}': None,
                        f'RM_PX_{prefix}_FSQ': None,
                        f'RM_PX_{prefix}_R': None,
                        f'RM_PX_{prefix}_POS': None,
                        f'RM_PX_{prefix}_RT_M': None,
                        f'RM_PX_{prefix}__RT_PS': None,
                        f'RM_PX_{prefix}_FORM5': None,
                        f'RM_PX_{prefix}_WINR': None,
                        f'RM_PX_{prefix}_G90': None,
                        f'RM_PX_{prefix}_A90': None,
                        f'RM_PX_{prefix}_KP9': None
                    })
                
                all_matches_data.append(match_data)
            
            info(f"=== ZAKOŃCZONO AGREGACJĘ MECZÓW ===")
            info(f"✓ Pomyślnie przetworzono {len(all_matches_data)} meczów")
            
            result_df = pd.DataFrame(all_matches_data)
            
            missing_columns = set(self.columns) - set(result_df.columns)
            if missing_columns:
                info(f"Dodaję {len(missing_columns)} brakujących kolumn")
                default_values = {col: 0 for col in missing_columns}
                missing_df = pd.DataFrame([default_values] * len(result_df))
                result_df = pd.concat([result_df, missing_df], axis=1)
            
            result_df = result_df[self.columns]
            
            info(f"Finalny DataFrame: {len(result_df)} wierszy, {len(result_df.columns)} kolumn")
            
            return result_df
            
        except Exception as e:
            error(f"Błąd podczas przetwarzania meczów: {str(e)}")
            error(traceback.format_exc())
            return pd.DataFrame(columns=self.columns)
    
    def _calculate_team_stats(self, match_date, players_data):
        """
        Oblicza statystyki drużynowe na podstawie zawodników pierwszego składu.
        
        Args:
            match_date: Data meczu
            players_data: Lista słowników z danymi zawodników
            
        Returns:
            dict: Słownik z 3 statystykami drużynowymi zaokrąglonymi do 3 miejsc
            
        Notes:
            - Uwzględnia tylko zawodników pierwszego składu (is_first_squad = 1)
            - Oblicza średnią ocenę, formę i win_ratio
            - W przypadku braku zawodników zwraca 0.000
        """
        try:
            starters = [p for p in players_data if p.get('is_first_squad', 0) == 1]
            
            debug(f"Obliczam statystyki drużyny z {len(starters)} zawodników pierwszego składu")
            
            if not starters:
                warning("Brak zawodników pierwszego składu - używam wartości domyślnych")
                return {
                    'team_avg_rating': 0.000,
                    'team_form_last_5': 0.000,
                    'team_win_ratio': 0.000
                }
            
            avg_rating = np.mean([p.get('last_match_rating', 0) for p in starters])
            avg_form = np.mean([p.get('last_5_ratings', 0) for p in starters])
            avg_win_ratio = np.mean([p.get('win_ratio', 0) for p in starters])
            
            team_stats = {
                'team_avg_rating': round(avg_rating, 3),
                'team_form_last_5': round(avg_form, 3),
                'team_win_ratio': round(avg_win_ratio, 3)
            }
            
            debug(f"✓ Statystyki drużyny: Ocena={team_stats['team_avg_rating']}, Forma={team_stats['team_form_last_5']}, WinRatio={team_stats['team_win_ratio']}")
            
            return team_stats
            
        except Exception as e:
            error(f"Błąd podczas obliczania statystyk drużyny: {str(e)}")
            return {
                'team_avg_rating': None,
                'team_form_last_5': None,
                'team_win_ratio': None
            }