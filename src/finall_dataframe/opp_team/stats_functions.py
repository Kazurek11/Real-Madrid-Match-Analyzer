"""Functions using existing modules for opponent statistics calculation."""

import numpy as np

def calculate_OP_G_SCO_L5(stats, match_date, team_id):
    """
    Oblicza średnią goli zdobytych przez przeciwnika w ostatnich 5 meczach.
    
    Args:
        stats (StatsCalculator): Obiekt kalkulatora statystyk
        match_date (str/datetime): Data meczu
        team_id (int): ID drużyny przeciwnika
        
    Returns:
        float: Średnia goli zdobytych lub np.nan
    """
    result = stats._calculate_opponent_last_5(match_date, team_id, 5)
    if result:
        return result['OP_G_SCO_L5']
    return np.nan

def calculate_OP_G_CON_L5(stats, match_date, team_id):
    """
    Oblicza średnią goli straconych przez przeciwnika w ostatnich 5 meczach.
    
    Args:
        stats (StatsCalculator): Obiekt kalkulatora statystyk
        match_date (str/datetime): Data meczu
        team_id (int): ID drużyny przeciwnika
        
    Returns:
        float: Średnia goli straconych lub np.nan
    """
    result = stats._calculate_opponent_last_5(match_date, team_id, 5)
    if result:
        return result['OP_G_CON_L5']
    return np.nan

def calculate_OP_GDIF_L5(stats, match_date, team_id):
    """
    Oblicza średnią różnicę bramek przeciwnika w ostatnich 5 meczach.
    
    Args:
        stats (StatsCalculator): Obiekt kalkulatora statystyk
        match_date (str/datetime): Data meczu
        team_id (int): ID drużyny przeciwnika
        
    Returns:
        float: Średnia różnica bramek lub np.nan
    """
    result = stats._calculate_opponent_last_5(match_date, team_id, 5)
    if result:
        return result['OP_GDIF_L5']
    return np.nan

def calculate_OP_OPP_POS_L5(stats, match_date, team_id):
    """
    Oblicza średnią pozycji rywali przeciwnika z ostatnich 5 meczów.
    
    Args:
        stats (StatsCalculator): Obiekt kalkulatora statystyk
        match_date (str/datetime): Data meczu
        team_id (int): ID drużyny przeciwnika
        
    Returns:
        float: Średnia pozycja rywali lub np.nan
    """
    result = stats._calculate_opponent_last_5(match_date, team_id, 5)
    if result:
        return result['OP_OPP_PPM_L5']
    return np.nan

def calculate_OP_PPM_L5(stats, match_date, team_id):
    """
    Oblicza średnią punktów na mecz przeciwnika z ostatnich 5 meczów.
    
    Args:
        stats (StatsCalculator): Obiekt kalkulatora statystyk
        match_date (str/datetime): Data meczu
        team_id (int): ID drużyny przeciwnika
        
    Returns:
        float: Średnie punkty na mecz lub np.nan
    """
    result = stats._calculate_opponent_last_5(match_date, team_id, 5)
    if result:
        return result['OP_PPM_L5']
    return np.nan

def calculate_OP_PPM_SEA(calc, match_date):
    """
    Oblicza średnią punktów na mecz przeciwnika w sezonie.
    
    Args:
        calc (SeasonCalculator): Obiekt kalkulatora sezonowego
        match_date (str/datetime): Data meczu
        
    Returns:
        float: Średnie punkty na mecz w sezonie lub np.nan
    """
    result = calc.calculate_team_points_per_match_season(match_date)
    return result if result is not None else np.nan

def calculate_OP_GPM_1_9_PPR(calc, match_date):
    """
    Oblicza średnią goli na mecz przeciwnika z drużynami >1.9 PPM.
    
    Args:
        calc (SeasonCalculator): Obiekt kalkulatora sezonowego
        match_date (str/datetime): Data meczu
        
    Returns:
        float: Średnia goli przeciwko top drużynom lub np.nan
    """
    result = calc.calculate_team_goals_against_top(match_date)
    return result if result is not False else np.nan

def calculate_OP_PPM_1_9_PPR(calc, match_date):
    """
    Oblicza średnią punktów na mecz przeciwnika z drużynami >1.9 PPM.
    
    Args:
        calc (SeasonCalculator): Obiekt kalkulatora sezonowego
        match_date (str/datetime): Data meczu
        
    Returns:
        float: Średnie punkty przeciwko top drużynom lub np.nan
    """
    result = calc.calculate_team_points_against_top(match_date)
    return result if result is not False else np.nan

def calculate_OP_GPM_1_2__1_9_PPM(calc, match_date):
    """
    Oblicza średnią goli na mecz przeciwnika z drużynami 1.2-1.9 PPM.
    
    Args:
        calc (SeasonCalculator): Obiekt kalkulatora sezonowego
        match_date (str/datetime): Data meczu
        
    Returns:
        float: Średnia goli przeciwko średnim drużynom lub np.nan
    """
    result = calc.calculate_team_goals_against_mid(match_date)
    return result if result is not False else np.nan

def calculate_OP_PPM_1_2__1_9_PPM(calc, match_date):
    """
    Oblicza średnią punktów na mecz przeciwnika z drużynami 1.2-1.9 PPM.
    
    Args:
        calc (SeasonCalculator): Obiekt kalkulatora sezonowego
        match_date (str/datetime): Data meczu
        
    Returns:
        float: Średnie punkty przeciwko średnim drużynom lub np.nan
    """
    result = calc.calculate_team_points_against_mid(match_date)
    return result if result is not False else np.nan

def calculate_OP_GPM_0_1_2_PPM(calc, match_date):
    """
    Oblicza średnią goli na mecz przeciwnika z drużynami <1.2 PPM.
    
    Args:
        calc (SeasonCalculator): Obiekt kalkulatora sezonowego
        match_date (str/datetime): Data meczu
        
    Returns:
        float: Średnia goli przeciwko słabym drużynom lub np.nan
    """
    result = calc.calculate_team_goals_against_low(match_date)
    return result if result is not False else np.nan

def calculate_OP_PPM_0_1_2_PPM(calc, match_date):
    """
    Oblicza średnią punktów na mecz przeciwnika z drużynami <1.2 PPM.
    
    Args:
        calc (SeasonCalculator): Obiekt kalkulatora sezonowego
        match_date (str/datetime): Data meczu
        
    Returns:
        float: Średnie punkty przeciwko słabym drużynom lub np.nan
    """
    result = calc.calculate_team_points_against_low(match_date)
    return result if result is not False else np.nan