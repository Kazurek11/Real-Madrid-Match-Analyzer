import pandas as pd
import numpy as np
from helpers.logger import info, warning

class DataFrameImputer:
    """
    Klasa odpowiedzialna za inteligentne uzupełnianie brakujących 
    wartości (NaN) w finalnym zbiorze danych.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        info("DataFrameImputer zainicjalizowany.")
        # KROK 0: Konwersja typów danych, aby uniknąć problemów z downcastingiem
        self._coerce_numeric_types()

    def _coerce_numeric_types(self):
        """
        Prywatna metoda do jawnej konwersji kolumn na typ numeryczny,
        gdzie to możliwe. Zapobiega ostrzeżeniom o downcastingu.
        """
        info("Konwersja typów danych w celu zapewnienia spójności...")
        for col in self.df.columns:
            # Nie ruszamy kolumn z pozycjami i datami
            if col.endswith('_POS') or col == 'M_DATE':
                continue
            
            # Próbujemy skonwertować kolumnę na numeryczną.
            # `errors='coerce'` zamieni wszystko, czego nie da się skonwertować, na NaT/NaN.
            original_type = self.df[col].dtype
            converted_series = pd.to_numeric(self.df[col], errors='coerce')
            
            # Jeśli konwersja nie spowodowała utraty wszystkich danych, zastosuj ją
            if converted_series.notna().sum() > 0:
                self.df[col] = converted_series
                if original_type != self.df[col].dtype:
                    info(f"  - Skonwertowano kolumnę '{col}' z {original_type} na {self.df[col].dtype}.")

    def impute_player_stats(self):
        # ... (bez zmian) ...
        info("Rozpoczynam imputację dla statystyk zawodników...")
        player_pos_cols = [col for col in self.df.columns if col.startswith('RM_PX_') and col.endswith('_POS')]
        player_num_cols = [col for col in self.df.columns if col.startswith('RM_PX_') and col not in player_pos_cols]
        
        player_pos_nan = self.df[player_pos_cols].columns[self.df[player_pos_cols].isna().any()].tolist()
        player_num_nan = self.df[player_num_cols].columns[self.df[player_num_cols].isna().any()].tolist()

        if player_pos_nan:
            self.df[player_pos_nan] = self.df[player_pos_nan].fillna('NoPos')
            info(f"  - Uzupełniono {len(player_pos_nan)} kolumn pozycji jako 'NoPos'.")
        if player_num_nan:
            self.df[player_num_nan] = self.df[player_num_nan].fillna(0)
            info(f"  - Uzupełniono {len(player_num_nan)} kolumn numerycznych zerami.")
            
        info("✅ Ukończono imputację danych zawodników.")
        return self

    def impute_h2h_stats(self):
        # ... (bez zmian) ...
        info("Rozpoczynam imputację dla statystyk H2H...")
        h2h_cols = [col for col in self.df.columns if col.startswith('H2H_') and col != 'H2H_EXISTS']
        if not h2h_cols:
            info("  - Brak kolumn H2H do imputacji.")
            return self
            
        missing_h2h_mask = (self.df['H2H_EXISTS'] == 0)
        for col in h2h_cols:
             self.df.loc[missing_h2h_mask, col] = self.df.loc[missing_h2h_mask, col].fillna(0)

        info(f"✅ Ukończono imputację danych H2H dla {missing_h2h_mask.sum()} meczów bez historii.")
        return self

    def impute_opponent_stats(self):
        # ... (bez zmian, teraz powinno działać bez ostrzeżeń) ...
        info("Rozpoczynam imputację dla statystyk przeciwników...")
        vs_cols_map = {
            'OP_GPM_VS_TOP': 'OP_G_SCO_ALL', 'OP_PPM_VS_TOP': 'OP_PPM_SEA',
            'OP_GPM_VS_MID': 'OP_G_SCO_ALL', 'OP_PPM_VS_MID': 'OP_PPM_SEA',
            'OP_GPM_VS_LOW': 'OP_G_SCO_ALL', 'OP_PPM_VS_LOW': 'OP_PPM_SEA'
        }
        for vs_col, sea_col in vs_cols_map.items():
            if vs_col in self.df.columns and self.df[vs_col].isnull().any():
                self.df[vs_col] = self.df[vs_col].fillna(self.df[sea_col])
                info(f"  - Uzupełniono braki w '{vs_col}' wartościami z '{sea_col}'.")
        
        l5_cols = [col for col in self.df.columns if col.startswith('OP_') and col.endswith('_L5')]
        mask_beniaminek_l5 = self.df['OP_PPM_L5'].isnull()
        if mask_beniaminek_l5.any():
            info(f"  - Znaleziono {mask_beniaminek_l5.sum()} wiersz(e) z brakiem danych _L5 (beniaminki).")
            low_teams_mask = self.df['OP_PPM_SEA'] < 1.2
            for col in l5_cols:
                if low_teams_mask.any():
                    median_for_low_teams = self.df.loc[low_teams_mask, col].median()
                else: 
                    median_for_low_teams = self.df[col].median()
                if pd.notna(median_for_low_teams):
                    self.df.loc[mask_beniaminek_l5, col] = median_for_low_teams
                    info(f"    - Uzupełniono '{col}' dla beniaminków wartością: {median_for_low_teams:.3f}")
                else:
                    global_median = self.df[col].median()
                    self.df.loc[mask_beniaminek_l5, col] = global_median
                    warning(f"    - Nie można było obliczyć mediany dla '{col}' dla drużyn LOW, użyto globalnej mediany: {global_median:.3f}")

        info("✅ Ukończono imputację danych przeciwników.")
        return self
        
    def impute_remaining(self):
        # ... (bez zmian, teraz powinno działać bez ostrzeżeń) ...
        remaining_nan_cols = self.df.columns[self.df.isnull().any()].tolist()
        if not remaining_nan_cols:
            info("✅ Brak pozostałych wartości NaN do uzupełnienia.")
            return self

        info(f"Rozpoczynam ostateczne czyszczenie {len(remaining_nan_cols)} pozostałych kolumn...")
        for col in remaining_nan_cols:
            if pd.api.types.is_numeric_dtype(self.df[col]):
                median_val = self.df[col].median()
                self.df[col] = self.df[col].fillna(median_val)
                info(f"  - Uzupełniono numeryczną kolumnę '{col}' medianą: {median_val:.3f}")
            else:
                mode_val = self.df[col].mode()[0]
                self.df[col] = self.df[col].fillna(mode_val)
                info(f"  - Uzupełniono kategoryczną kolumnę '{col}' dominantą: '{mode_val}'")
        return self

    def run(self):
        self.impute_player_stats()
        self.impute_h2h_stats()
        self.impute_opponent_stats()
        self.impute_remaining()
        
        final_nan_count = self.df.isnull().sum().sum()
        if final_nan_count == 0:
            info("✅✅✅ Imputacja zakończona sukcesem. Finalny DataFrame jest czysty.")
        else:
            warning(f"⚠️ Po imputacji wciąż pozostało {final_nan_count} wartości NaN.")
            
        return self.df