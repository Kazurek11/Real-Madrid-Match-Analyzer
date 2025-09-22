import pandas as pd
import os
import sys

current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from helpers.logger import info, error, debug, warning

class PlayerManager:
    """Klasa zarządzająca informacjami o zawodnikach i wyszukiwaniem danych"""
    
    def __init__(self, players_df):
        """
        Inicjalizuje manager zawodników.
        
        Tworzy obiekt zarządzający informacjami o zawodnikach,
        umożliwiający wyszukiwanie i pobieranie danych na podstawie
        identyfikatorów lub nazwisk.
        
        Parameters:
            players_df (pd.DataFrame): Ramka danych z informacjami o zawodnikach
            
        Notes:
            - Ramka danych powinna zawierać co najmniej kolumny 'player_id', 
              'player_name' i 'player_position'
        """
        self.players_df = players_df
    
    def get_player_id(self, name):
        """
        Pobiera ID zawodnika na podstawie nazwiska.
        
        Metoda wyszukuje zawodnika po dokładnym dopasowaniu nazwiska,
        a w przypadku niepowodzenia próbuje znormalizowane wyszukiwanie.
        
        Parameters:
            name (str): Nazwisko zawodnika do wyszukania
            
        Returns:
            int/None: ID zawodnika lub None, jeśli zawodnik nie został znaleziony
            
        Notes:
            - Metoda próbuje najpierw dokładnego dopasowania
            - W przypadku niepowodzenia, próbuje dopasowania po normalizacji (małe litery, usunięcie spacji)
            - Błędy wyszukiwania są logowane jako ostrzeżenia
        """
        matching_players = self.players_df[self.players_df['player_name'] == name]
        if not matching_players.empty:
            return matching_players['player_id'].values[0]
        
        name_normalized = name.strip().lower()
        normalized_players = self.players_df['player_name'].str.strip().str.lower()
        matching_idx = normalized_players[normalized_players == name_normalized].index
        
        if not matching_idx.empty:
            player_id = self.players_df.loc[matching_idx[0], 'player_id']
            warning(f"Znaleziono zawodnika '{name}' po normalizacji jako '{self.players_df.loc[matching_idx[0], 'player_name']}'")
            return player_id
        
        warning(f"Nie znaleziono zawodnika: '{name}'")
        return None
    
    def get_player_name(self, player_id):
        """
        Pobiera nazwisko zawodnika na podstawie ID.
        
        Metoda wyszukuje zawodnika po identyfikatorze i zwraca jego nazwisko.
        
        Parameters:
            player_id (int): ID zawodnika do wyszukania
            
        Returns:
            str/None: Nazwisko zawodnika lub None, jeśli zawodnik o podanym ID nie istnieje
            
        Notes:
            - Brak dopasowania jest logowany jako ostrzeżenie
        """
        matching_players = self.players_df[self.players_df['player_id'] == player_id]
        if matching_players.empty:
            warning(f"Nie znaleziono zawodnika z ID {player_id}")
            return None
        return matching_players['player_name'].values[0]
    
    def get_player_position(self, identifier):
        """
        Pobiera pozycję zawodnika na podstawie nazwiska lub ID.
        
        Metoda automatycznie wykrywa typ identyfikatora (ID lub nazwisko)
        i zwraca główną pozycję zawodnika.
        
        Parameters:
            identifier (int/str): ID lub nazwisko zawodnika
            
        Returns:
            str: Główna pozycja zawodnika lub "unknown" w przypadku błędu
            
        Notes:
            - Metoda obsługuje różne formaty pozycji (lista, string)
            - W przypadku wielu pozycji, zwracana jest pierwsza z listy
            - Brak dopasowania jest logowany jako ostrzeżenie
        """
        if isinstance(identifier, int) or str(identifier).isdigit():
            player_data = self.players_df[self.players_df['player_id'] == int(identifier)]
            if player_data.empty:
                warning(f"Nie znaleziono zawodnika z ID {identifier}")
                return "unknown"
            player_name = player_data['player_name'].values[0]
        else:
            player_name = identifier
        
        player_data = self.players_df[self.players_df['player_name'] == player_name]
        if player_data.empty:
            warning(f"Nie znaleziono zawodnika o nazwisku {player_name}")
            return "unknown"
            
        player_position = player_data['player_position'].values[0]
        
        if isinstance(player_position, list) and len(player_position) > 0:
            return player_position[0]
        elif isinstance(player_position, str):
            if player_position.startswith('[') and player_position.endswith(']'):
                positions = player_position.strip('[]').replace("'", "").split(', ')
                return positions[0]
        return player_position
    
    def get_same_position_players(self, position, exclude_player=None):
        """
        Pobiera listę zawodników grających na tej samej pozycji.
        
        Metoda wyszukuje wszystkich zawodników grających na podanej pozycji,
        z możliwością wykluczenia jednego zawodnika z wyników.
        
        Parameters:
            position (str): Pozycja do wyszukania
            exclude_player (str, optional): Nazwisko zawodnika do wykluczenia z wyników
            
        Returns:
            list: Lista nazwisk zawodników grających na podanej pozycji
            
        Notes:
            - Metoda sprawdza dokładne dopasowanie pozycji
            - Zwracana lista może być pusta, jeśli nie znaleziono dopasowań
        """
        same_position_players = []
        
        for _, player in self.players_df.iterrows():
            if player['player_position'] == position and player['player_name'] != exclude_player:
                same_position_players.append(player['player_name'])
                
        return same_position_players