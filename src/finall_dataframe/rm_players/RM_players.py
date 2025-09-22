# import pandas as pd
# import numpy as np
# import os
# import sys
# import traceback
# from datetime import datetime

# current_dir = os.getcwd()
# project_root = os.path.dirname(current_dir)
# sys.path.append(project_root)

# from RM.RM_players_analyzer import RealMadridPlayersAnalyzer
# from helpers.logger import info, error, debug, warning
# from helpers.file_utils import FileUtils
# from data_processing.merge_all_season_data import DataMerger
# from data_processing.data_processor import DataProcessor
# from data_processing.const_variable import SEASON_DATES
# columns = [
#     'MATCH_ID',         # Identyfikator meczu
#     'M_DATE',           # Data meczu
#     'SEASON',           # Sezon rozgrywkowy (np. 2023-24)
#     'IS_HOME',          # Czy Real Madryt grał u siebie (1=tak, 0=nie)
#     'OPP_ID',           # ID drużyny przeciwnej
    
#     # Zawodnik 1
#     'RM_PX_1',          # ID zawodnika Realu Madryt z pozycji X (1)
#     'RM_PX_1_FSQ',      # Czy zawodnik był w pierwszym składzie (1=tak, 0=nie)
#     'RM_PX_1_RT',       # Czy zawodnik otrzymał ocenę w meczu (1=tak, 0=nie)
#     'RM_PX_1_POS',      # Pozycja zawodnika na boisku (GK, ST itd.)
#     'RM_PX_1_RT_M',     # Ocena zawodnika w poprzednim meczu
#     'RM_PX_1_RT_PS',    # Średnia ocen zawodnika w poprzednim sezonie
#     'RM_PX_1_FORM5',    # Średnia ocen zawodnika z ostatnich 5 meczów
#     'RM_PX_1_WINR',     # Procent wygranych gdy zawodnik grał w pierwszym składzie
#     'RM_PX_1_G90',      # Gole na 90 minut zawodnika w sezonie
#     'RM_PX_1_A90',      # Asysty na 90 minut zawodnika w sezonie
#     'RM_PX_1_KP90',     # Kluczowe podania na 90 minut zawodnika w sezonie
    
#     # Zawodnik 2
#     'RM_PX_2',          # ID zawodnika Realu Madryt z pozycji X (2)
#     'RM_PX_2_FSQ',      # Czy zawodnik był w pierwszym składzie (1=tak, 0=nie)
#     'RM_PX_2_RT',       # Czy zawodnik otrzymał ocenę w meczu (1=tak, 0=nie)
#     'RM_PX_2_POS',      # Pozycja zawodnika na boisku (GK, ST itd.)
#     'RM_PX_2_RT_M',     # Ocena zawodnika w poprzednim meczu
#     'RM_PX_2_RT_PS',    # Średnia ocen zawodnika w poprzednim sezonie
#     'RM_PX_2_FORM5',    # Średnia ocen zawodnika z ostatnich 5 meczów
#     'RM_PX_2_WINR',     # Procent wygranych gdy zawodnik grał w pierwszym składzie
#     'RM_PX_2_G90',      # Gole na 90 minut zawodnika w sezonie
#     'RM_PX_2_A90',      # Asysty na 90 minut zawodnika w sezonie
#     'RM_PX_2_KP90',     # Kluczowe podania na 90 minut zawodnika w sezonie
    
#     # Zawodnik 3
#     'RM_PX_3',          # ID zawodnika Realu Madryt z pozycji X (3)
#     'RM_PX_3_FSQ',      # Czy zawodnik był w pierwszym składzie (1=tak, 0=nie)
#     'RM_PX_3_RT',       # Czy zawodnik otrzymał ocenę w meczu (1=tak, 0=nie)
#     'RM_PX_3_POS',      # Pozycja zawodnika na boisku (GK, ST itd.)
#     'RM_PX_3_RT_M',     # Ocena zawodnika w poprzednim meczu
#     'RM_PX_3_RT_PS',    # Średnia ocen zawodnika w poprzednim sezonie
#     'RM_PX_3_FORM5',    # Średnia ocen zawodnika z ostatnich 5 meczów
#     'RM_PX_3_WINR',     # Procent wygranych gdy zawodnik grał w pierwszym składzie
#     'RM_PX_3_G90',      # Gole na 90 minut zawodnika w sezonie
#     'RM_PX_3_A90',      # Asysty na 90 minut zawodnika w sezonie
#     'RM_PX_3_KP90',     # Kluczowe podania na 90 minut zawodnika w sezonie
    
#     # Zawodnik 4
#     'RM_PX_4',          # ID zawodnika Realu Madryt z pozycji X (4)
#     'RM_PX_4_FSQ',      # Czy zawodnik był w pierwszym składzie (1=tak, 0=nie)
#     'RM_PX_4_RT',       # Czy zawodnik otrzymał ocenę w meczu (1=tak, 0=nie)
#     'RM_PX_4_POS',      # Pozycja zawodnika na boisku (GK, ST itd.)
#     'RM_PX_4_RT_M',     # Ocena zawodnika w poprzednim meczu
#     'RM_PX_4_RT_PS',    # Średnia ocen zawodnika w poprzednim sezonie
#     'RM_PX_4_FORM5',    # Średnia ocen zawodnika z ostatnich 5 meczów
#     'RM_PX_4_WINR',     # Procent wygranych gdy zawodnik grał w pierwszym składzie
#     'RM_PX_4_G90',      # Gole na 90 minut zawodnika w sezonie
#     'RM_PX_4_A90',      # Asysty na 90 minut zawodnika w sezonie
#     'RM_PX_4_KP90',     # Kluczowe podania na 90 minut zawodnika w sezonie
    
#     # Zawodnik 5
#     'RM_PX_5',          # ID zawodnika Realu Madryt z pozycji X (5)
#     'RM_PX_5_FSQ',      # Czy zawodnik był w pierwszym składzie (1=tak, 0=nie)
#     'RM_PX_5_RT',       # Czy zawodnik otrzymał ocenę w meczu (1=tak, 0=nie)
#     'RM_PX_5_POS',      # Pozycja zawodnika na boisku (GK, ST itd.)
#     'RM_PX_5_RT_M',     # Ocena zawodnika w poprzednim meczu
#     'RM_PX_5_RT_PS',    # Średnia ocen zawodnika w poprzednim sezonie
#     'RM_PX_5_FORM5',    # Średnia ocen zawodnika z ostatnich 5 meczów
#     'RM_PX_5_WINR',     # Procent wygranych gdy zawodnik grał w pierwszym składzie
#     'RM_PX_5_G90',      # Gole na 90 minut zawodnika w sezonie
#     'RM_PX_5_A90',      # Asysty na 90 minut zawodnika w sezonie
#     'RM_PX_5_KP90',     # Kluczowe podania na 90 minut zawodnika w sezonie
    
#     # Zawodnik 6
#     'RM_PX_6',          # ID zawodnika Realu Madryt z pozycji X (6)
#     'RM_PX_6_FSQ',      # Czy zawodnik był w pierwszym składzie (1=tak, 0=nie)
#     'RM_PX_6_RT',       # Czy zawodnik otrzymał ocenę w meczu (1=tak, 0=nie)
#     'RM_PX_6_POS',      # Pozycja zawodnika na boisku (GK, ST itd.)
#     'RM_PX_6_RT_M',     # Ocena zawodnika w poprzednim meczu
#     'RM_PX_6_RT_PS',    # Średnia ocen zawodnika w poprzednim sezonie
#     'RM_PX_6_FORM5',    # Średnia ocen zawodnika z ostatnich 5 meczów
#     'RM_PX_6_WINR',     # Procent wygranych gdy zawodnik grał w pierwszym składzie
#     'RM_PX_6_G90',      # Gole na 90 minut zawodnika w sezonie
#     'RM_PX_6_A90',      # Asysty na 90 minut zawodnika w sezonie
#     'RM_PX_6_KP90',     # Kluczowe podania na 90 minut zawodnika w sezonie
    
#     # Zawodnik 7
#     'RM_PX_7',          # ID zawodnika Realu Madryt z pozycji X (7)
#     'RM_PX_7_FSQ',      # Czy zawodnik był w pierwszym składzie (1=tak, 0=nie)
#     'RM_PX_7_RT',       # Czy zawodnik otrzymał ocenę w meczu (1=tak, 0=nie)
#     'RM_PX_7_POS',      # Pozycja zawodnika na boisku (GK, ST itd.)
#     'RM_PX_7_RT_M',     # Ocena zawodnika w poprzednim meczu
#     'RM_PX_7_RT_PS',    # Średnia ocen zawodnika w poprzednim sezonie
#     'RM_PX_7_FORM5',    # Średnia ocen zawodnika z ostatnich 5 meczów
#     'RM_PX_7_WINR',     # Procent wygranych gdy zawodnik grał w pierwszym składzie
#     'RM_PX_7_G90',      # Gole na 90 minut zawodnika w sezonie
#     'RM_PX_7_A90',      # Asysty na 90 minut zawodnika w sezonie
#     'RM_PX_7_KP90',     # Kluczowe podania na 90 minut zawodnika w sezonie
    
#     # Zawodnik 8
#     'RM_PX_8',          # ID zawodnika Realu Madryt z pozycji X (8)
#     'RM_PX_8_FSQ',      # Czy zawodnik był w pierwszym składzie (1=tak, 0=nie)
#     'RM_PX_8_RT',       # Czy zawodnik otrzymał ocenę w meczu (1=tak, 0=nie)
#     'RM_PX_8_POS',      # Pozycja zawodnika na boisku (GK, ST itd.)
#     'RM_PX_8_RT_M',     # Ocena zawodnika w poprzednim meczu
#     'RM_PX_8_RT_PS',    # Średnia ocen zawodnika w poprzednim sezonie
#     'RM_PX_8_FORM5',    # Średnia ocen zawodnika z ostatnich 5 meczów
#     'RM_PX_8_WINR',     # Procent wygranych gdy zawodnik grał w pierwszym składzie
#     'RM_PX_8_G90',      # Gole na 90 minut zawodnika w sezonie
#     'RM_PX_8_A90',      # Asysty na 90 minut zawodnika w sezonie
#     'RM_PX_8_KP90',     # Kluczowe podania na 90 minut zawodnika w sezonie
    
#     # Zawodnik 9
#     'RM_PX_9',          # ID zawodnika Realu Madryt z pozycji X (9)
#     'RM_PX_9_FSQ',      # Czy zawodnik był w pierwszym składzie (1=tak, 0=nie)
#     'RM_PX_9_RT',       # Czy zawodnik otrzymał ocenę w meczu (1=tak, 0=nie)
#     'RM_PX_9_POS',      # Pozycja zawodnika na boisku (GK, ST itd.)
#     'RM_PX_9_RT_M',     # Ocena zawodnika w poprzednim meczu
#     'RM_PX_9_RT_PS',    # Średnia ocen zawodnika w poprzednim sezonie
#     'RM_PX_9_FORM5',    # Średnia ocen zawodnika z ostatnich 5 meczów
#     'RM_PX_9_WINR',     # Procent wygranych gdy zawodnik grał w pierwszym składzie
#     'RM_PX_9_G90',      # Gole na 90 minut zawodnika w sezonie
#     'RM_PX_9_A90',      # Asysty na 90 minut zawodnika w sezonie
#     'RM_PX_9_KP90',     # Kluczowe podania na 90 minut zawodnika w sezonie
    
#     # Zawodnik 10
#     'RM_PX_10',         # ID zawodnika Realu Madryt z pozycji X (10)
#     'RM_PX_10_FSQ',     # Czy zawodnik był w pierwszym składzie (1=tak, 0=nie)
#     'RM_PX_10_RT',      # Czy zawodnik otrzymał ocenę w meczu (1=tak, 0=nie)
#     'RM_PX_10_POS',     # Pozycja zawodnika na boisku (GK, ST itd.)
#     'RM_PX_10_RT_M',    # Ocena zawodnika w poprzednim meczu
#     'RM_PX_10_RT_PS',   # Średnia ocen zawodnika w poprzednim sezonie
#     'RM_PX_10_FORM5',   # Średnia ocen zawodnika z ostatnich 5 meczów
#     'RM_PX_10_WINR',    # Procent wygranych gdy zawodnik grał w pierwszym składzie
#     'RM_PX_10_G90',     # Gole na 90 minut zawodnika w sezonie
#     'RM_PX_10_A90',     # Asysty na 90 minut zawodnika w sezonie
#     'RM_PX_10_KP90',    # Kluczowe podania na 90 minut zawodnika w sezonie
    
#     # Zawodnik 11
#     'RM_PX_11',         # ID zawodnika Realu Madryt z pozycji X (11)
#     'RM_PX_11_FSQ',     # Czy zawodnik był w pierwszym składzie (1=tak, 0=nie)
#     'RM_PX_11_RT',      # Czy zawodnik otrzymał ocenę w meczu (1=tak, 0=nie)
#     'RM_PX_11_POS',     # Pozycja zawodnika na boisku (GK, ST itd.)
#     'RM_PX_11_RT_M',    # Ocena zawodnika w poprzednim meczu
#     'RM_PX_11_RT_PS',   # Średnia ocen zawodnika w poprzednim sezonie
#     'RM_PX_11_FORM5',   # Średnia ocen zawodnika z ostatnich 5 meczów
#     'RM_PX_11_WINR',    # Procent wygranych gdy zawodnik grał w pierwszym składzie
#     'RM_PX_11_G90',     # Gole na 90 minut zawodnika w sezonie
#     'RM_PX_11_A90',     # Asysty na 90 minut zawodnika w sezonie
#     'RM_PX_11_KP90',    # Kluczowe podania na 90 minut zawodnika w sezonie
    
#     # Zawodnik 12
#     'RM_PX_12',         # ID zawodnika Realu Madryt z pozycji X (12)
#     'RM_PX_12_FSQ',     # Czy zawodnik był w pierwszym składzie (1=tak, 0=nie)
#     'RM_PX_12_RT',      # Czy zawodnik otrzymał ocenę w meczu (1=tak, 0=nie)
#     'RM_PX_12_POS',     # Pozycja zawodnika na boisku (GK, ST itd.)
#     'RM_PX_12_RT_M',    # Ocena zawodnika w poprzednim meczu
#     'RM_PX_12_RT_PS',   # Średnia ocen zawodnika w poprzednim sezonie
#     'RM_PX_12_FORM5',   # Średnia ocen zawodnika z ostatnich 5 meczów
#     'RM_PX_12_WINR',    # Procent wygranych gdy zawodnik grał w pierwszym składzie
#     'RM_PX_12_G90',     # Gole na 90 minut zawodnika w sezonie
#     'RM_PX_12_A90',     # Asysty na 90 minut zawodnika w sezonie
#     'RM_PX_12_KP90',    # Kluczowe podania na 90 minut zawodnika w sezonie
    
#     # Zawodnik 13
#     'RM_PX_13',         # ID zawodnika Realu Madryt z pozycji X (13)
#     'RM_PX_13_FSQ',     # Czy zawodnik był w pierwszym składzie (1=tak, 0=nie)
#     'RM_PX_13_RT',      # Czy zawodnik otrzymał ocenę w meczu (1=tak, 0=nie)
#     'RM_PX_13_POS',     # Pozycja zawodnika na boisku (GK, ST itd.)
#     'RM_PX_13_RT_M',    # Ocena zawodnika w poprzednim meczu
#     'RM_PX_13_RT_PS',   # Średnia ocen zawodnika w poprzednim sezonie
#     'RM_PX_13_FORM5',   # Średnia ocen zawodnika z ostatnich 5 meczów
#     'RM_PX_13_WINR',    # Procent wygranych gdy zawodnik grał w pierwszym składzie
#     'RM_PX_13_G90',     # Gole na 90 minut zawodnika w sezonie
#     'RM_PX_13_A90',     # Asysty na 90 minut zawodnika w sezonie
#     'RM_PX_13_KP90',    # Kluczowe podania na 90 minut zawodnika w sezonie
    
#     # Zawodnik 14
#     'RM_PX_14',         # ID zawodnika Realu Madryt z pozycji X (14)
#     'RM_PX_14_FSQ',     # Czy zawodnik był w pierwszym składzie (1=tak, 0=nie)
#     'RM_PX_14_RT',      # Czy zawodnik otrzymał ocenę w meczu (1=tak, 0=nie)
#     'RM_PX_14_POS',     # Pozycja zawodnika na boisku (GK, ST itd.)
#     'RM_PX_14_RT_M',    # Ocena zawodnika w poprzednim meczu
#     'RM_PX_14_RT_PS',   # Średnia ocen zawodnika w poprzednim sezonie
#     'RM_PX_14_FORM5',   # Średnia ocen zawodnika z ostatnich 5 meczów
#     'RM_PX_14_WINR',    # Procent wygranych gdy zawodnik grał w pierwszym składzie
#     'RM_PX_14_G90',     # Gole na 90 minut zawodnika w sezonie
#     'RM_PX_14_A90',     # Asysty na 90 minut zawodnika w sezonie
#     'RM_PX_14_KP90',    # Kluczowe podania na 90 minut zawodnika w sezonie
    
#     # Zawodnik 15
#     'RM_PX_15',         # ID zawodnika Realu Madryt z pozycji X (15)
#     'RM_PX_15_FSQ',     # Czy zawodnik był w pierwszym składzie (1=tak, 0=nie)
#     'RM_PX_15_RT',      # Czy zawodnik otrzymał ocenę w meczu (1=tak, 0=nie)
#     'RM_PX_15_POS',     # Pozycja zawodnika na boisku (GK, ST itd.)
#     'RM_PX_15_RT_M',    # Ocena zawodnika w poprzednim meczu
#     'RM_PX_15_RT_PS',   # Średnia ocen zawodnika w poprzednim sezonie
#     'RM_PX_15_FORM5',   # Średnia ocen zawodnika z ostatnich 5 meczów
#     'RM_PX_15_WINR',    # Procent wygranych gdy zawodnik grał w pierwszym składzie
#     'RM_PX_15_G90',     # Gole na 90 minut zawodnika w sezonie
#     'RM_PX_15_A90',     # Asysty na 90 minut zawodnika w sezonie
#     'RM_PX_15_KP90',    # Kluczowe podania na 90 minut zawodnika w sezonie
    
#     # Zawodnik 16
#     'RM_PX_16',         # ID zawodnika Realu Madryt z pozycji X (16)
#     'RM_PX_16_FSQ',     # Czy zawodnik był w pierwszym składzie (1=tak, 0=nie)
#     'RM_PX_16_RT',      # Czy zawodnik otrzymał ocenę w meczu (1=tak, 0=nie)
#     'RM_PX_16_POS',     # Pozycja zawodnika na boisku (GK, ST itd.)
#     'RM_PX_16_RT_M',    # Ocena zawodnika w poprzednim meczu
#     'RM_PX_16_RT_PS',   # Średnia ocen zawodnika w poprzednim sezonie
#     'RM_PX_16_FORM5',   # Średnia ocen zawodnika z ostatnich 5 meczów
#     'RM_PX_16_WINR',    # Procent wygranych gdy zawodnik grał w pierwszym składzie
#     'RM_PX_16_G90',     # Gole na 90 minut zawodnika w sezonie
#     'RM_PX_16_A90',     # Asysty na 90 minut zawodnika w sezonie
#     'RM_PX_16_KP90',    # Kluczowe podania na 90 minut zawodnika w sezonie
    
#     # Dane trenera i zespołu
#     'RM_C_ID',          # ID trenera Realu Madryt
#     'RM_C_RT_PS',       # Średnia ocen trenera w poprzednim sezonie
#     'RM_C_FORM5',       # Średnia ocen trenera z ostatnich 5 meczów
#     'RM_G_SCO_L5',      # Średnia goli zdobytych przez Real w ostatnich 5 meczach
#     'RM_G_CON_L5',      # Średnia goli straconych przez Real w ostatnich 5 meczach
#     'RM_GDIF_L5',       # Średnia różnica bramek Realu w ostatnich 5 meczach
#     'RM_OPP_POS_L5',    # Średnia pozycji rywali Realu z ostatnich 5 meczów
#     'RM_PPM_L5',        # Średnia punktów na mecz Realu z ostatnich 5 meczów
#     'RM_PPM_SEA',       # Średnia punktów na mecz Realu w sezonie
    
#     # Statystyki Realu przeciwko różnym typom drużyn
#     'RM_GPM_1_9_PPR',   # Średnia goli na mecz Realu z drużynami które zdobywają powyżej 1.9 punktów na mecz
#     'RM_PPM_1_9_PPR',   # Średnia punktów na mecz Realu z drużynami które zdobywają powyżej 1.9 punktów na mecz
#     'RM_GPM_1_2__1_9_PPM', # Średnia goli na mecz Realu z drużynami które zdobywają powyżej 1.2 ale poniżej 1.9 punktów na mecz
#     'RM_PPM_1_2__1_9_PPM', # Średnia punktów na mecz Realu z drużynami które zdobywają powyżej 1.2 ale poniżej 1.9 punktów na mecz
#     'RM_GPM_0_1_2_PPM', # Średnia goli na mecz Realu z drużynami które zdobywają poniżej 1.2 punktów na mecz
#     'RM_PPM_0_1_2_PPM', # Średnia punktów na mecz Realu z drużynami które zdobywają poniżej 1.2 punktów na mecz
    
#     # Statystyki przeciwnika
#     'OP_G_SCO_L5',      # Średnia goli zdobytych przez przeciwnika w ostatnich 5 meczach
#     'OP_G_CON_L5',      # Średnia goli straconych przez przeciwnika w ostatnich 5 meczach
#     'OP_GDIF_L5',       # Średnia różnica bramek przeciwnika w ostatnich 5 meczach
#     'OP_OPP_POS_L5',    # Średnia pozycji rywali przeciwnika z ostatnich 5 meczów
#     'OP_PPM_L5',        # Średnia punktów na mecz przeciwnika z ostatnich 5 meczów
#     'OP_PPM_SEA',       # Średnia punktów na mecz przeciwnika w sezonie
#     'OP_GPM_1_9_PPR',   # Średnia goli na mecz przeciwnika z drużynami które zdobywają powyżej 1.9 punktów na mecz
#     'OP_PPM_1_9_PPR',   # Średnia punktów na mecz przeciwnika z drużynami które zdobywają powyżej 1.9 punktów na mecz
#     'OP_GPM_1_2__1_9_PPM', # Średnia goli na mecz przeciwnika z drużynami które zdobywają powyżej 1.2 ale poniżej 1.9 punktów na mecz
#     'OP_PPM_1_2__1_9_PPM', # Średnia punktów na mecz przeciwnika z drużynami które zdobywają powyżej 1.2 ale poniżej 1.9 punktów na mecz
#     'OP_GPM_0_1_2_PPM', # Średnia goli na mecz przeciwnika z drużynami które zdobywają poniżej 1.2 punktów na mecz
#     'OP_PPM_0_1_2_PPM', # Średnia punktów na mecz przeciwnika z drużynami które zdobywają poniżej 1.2 punktów na mecz
#     'OP_G_SCO_ALL',     # Gole strzelone przez rywala w sezonie
#     'OP_G_CON_ALL',     # Gole stracone przez rywala w sezonie
#     'OP_G_SCO_G_CON_RAT', # Bilans bramkowy rywala w sezonie (stosunek goli strzelonych do straconych)
#     'OP_ODD_W_L5',      # Średni kurs na wygraną przeciwnika z ostatnich 5 meczów
#     'OP_ODD_L_L5',      # Średni kurs na porażkę przeciwnika z ostatnich 5 meczów
    
#     # Statystyki bezpośrednich spotkań (head-to-head)
#     'H2H_RM_W_L5',      # Procent wygranych Realu w ostatnich 5 bezpośrednich meczach
#     'H2H_RM_GDIF_L5',   # Bilans bramek Realu w ostatnich 5 bezpośrednich meczach
#     'H2H_RM_HW_L3',     # Procent wygranych Realu u siebie w ostatnich 3 bezpośrednich meczach
    
#     # Zmienna celu
#     'RM_ODD_W'          # Kurs na zwycięstwo Realu Madryt w meczu (TARGET)
# ]

# # [markdown]
# # Pobranie wszystkich plikow csv.

# # Wczytanie danych
# Real_path = os.path.join(FileUtils.get_project_root(),"Data","Real")
# RM_matches = FileUtils.load_csv_safe(os.path.join(Real_path,"RM_all_matches_stats.csv")).copy()
# RM_individual = FileUtils.load_csv_safe(os.path.join(Real_path,"RM_individual_stats.csv")).copy()
# ALL_matches = FileUtils.load_csv_safe(os.path.join(FileUtils.get_project_root(),"Data","Mecze","all_season","merged_matches","all_matches.csv")).copy()
# RM_players = FileUtils.load_csv_safe(os.path.join(Real_path,"RM_players.csv")).copy()
# RM_players_stats = FileUtils.load_csv_safe(os.path.join(Real_path,"RM_players_stats.csv")).copy()
# RM_old_matches = FileUtils.load_csv_safe(os.path.join(Real_path,"Old","RM_old_editor_data.csv")).copy()


# RM_matches_to_ratio = RM_matches.copy()
# RM_individual_to_ratio = RM_individual.copy()

# # [markdown]
# # Usuniecie pierwszych 5 spotkań z bazy ze wzgledu na czerpanie z nich danych na temat spotkań.

# # Dodaj tę linię na początku skryptu, po wczytaniu danych:
# RM_individual['match_date'] = pd.to_datetime(RM_individual['match_date'])
# RM_matches['match_date'] = pd.to_datetime(RM_matches['match_date'])

# # Popraw również sprawdzenie w funkcji last_season_player_rating:
# if isinstance(RM_individual["match_date"].iloc[0], str):  # Sprawdź na pierwszym elemencie
#     RM_individual["match_date"] = pd.to_datetime(RM_individual["match_date"])

# RM_first_5_matches = RM_matches.head(5)
# RM_matches = RM_matches[5:].copy()

# DF = pd.DataFrame(columns=columns)
# DF['MATCH_ID'] = RM_matches['match_id']

# # [markdown]
# # Uzupełnianie danych:
# # ```
# #     'MATCH_ID',         # Identyfikator meczu
# #     'M_DATE',           # Data meczu
# #     'SEASON',           # Sezon rozgrywkowy (np. 2023-24)
# #     'IS_HOME',          # Czy Real Madryt grał u siebie (1=tak, 0=nie)
# #     'OPP_ID',           # ID drużyny przeciwnej
# # ```

# # Ustawienie podstawowych danych meczowych

# DF['M_DATE'] = RM_matches['match_date']
# DF['SEASON'] = RM_matches['season']
# DF['IS_HOME'] = RM_matches['is_home']

# # Filtracja meczów domowych i wyjazdowych
# RM_home_game = RM_matches[RM_matches['is_home'] == 1]
# RM_away_game = RM_matches[RM_matches['is_home'] == 0]

# # Ustawienie ID przeciwników dla meczów domowych (przeciwnik = drużyna wyjazdowa)
# for match_id, row in RM_home_game.iterrows():
#     DF.loc[DF['MATCH_ID'] == row["match_id"], 'OPP_ID'] = row['away_team_id']

# # Ustawienie ID przeciwników dla meczów wyjazdowych (przeciwnik = drużyna domowa)
# for match_id, row in RM_away_game.iterrows():
#     DF.loc[DF['MATCH_ID'] == row["match_id"], 'OPP_ID'] = row['home_team_id']

# # [markdown]
# # Funkcja *get_player_id* na podstawie nazwy piłkarza zwraca jego id **('RM_PX_X')**

# RM_players.columns

# def get_player_id(name_of_player):
#     # Najpierw próbujemy dokładne dopasowanie
#     matching_players = RM_players[RM_players['player_name'] == name_of_player]
    
#     if not matching_players.empty:
#         return matching_players['player_id'].values[0]
    
#     # Jeśli nie znaleźliśmy dokładnego dopasowania, spróbujmy znormalizować
#     name_normalized = name_of_player.strip().lower()
#     normalized_players = RM_players['player_name'].str.strip().str.lower()
#     matching_idx = normalized_players[normalized_players == name_normalized].index
    
#     if not matching_idx.empty:
#         player_id = RM_players.loc[matching_idx[0], 'player_id']
#         warning(f"Znaleziono zawodnika '{name_of_player}' po normalizacji jako '{RM_players.loc[matching_idx[0], 'player_name']}'")
#         return player_id
    
#     # Nadal brak dopasowania
#     warning(f"Nie znaleziono zawodnika o nazwie '{name_of_player}' w RM_players")
#     return None

# def get_player_name(player_id):
#     return RM_players[RM_players['player_id'] == player_id]['player_name'].values[0]

# # ,         # ID zawodnika Realu Madryt z pozycji X (15)
# #     ,     # Czy zawodnik był w pierwszym składzie (1=tak, 0=nie)
# #     'RM_PX_15_RT',      # Czy zawodnik otrzymał ocenę w meczu (1=tak, 0=nie)
# #         'RM_PX_15_RT_PS',   # Średnia ocen zawodnika w poprzednim sezonie
# #     'RM_PX_15_WINR',    # Procent wygranych gdy zawodnik grał w pierwszym składzie
# #     'RM_PX_15_G90',     # Gole na 90 minut zawodnika w sezonie
# #     'RM_PX_15_A90',     # Asysty na 90 minut zawodnika w sezonie
# #     'RM_PX_15_KP90'

# # [markdown]
# # Funkcja *get_main_player_position* zwraca aktualna pozcyje piłkarza **('RM_PX_X_POS')**

# def get_main_player_position(identifier):
#     """Get player position from either name or ID"""
#     if isinstance(identifier, int) or str(identifier).isdigit():
#         # If identifier is player_id
#         player_data = RM_players[RM_players['player_id'] == int(identifier)]
#         if player_data.empty:
#             warning(f"Nie znaleziono zawodnika o ID {identifier}")
#             return "unknown"
#         player_name = player_data['player_name'].values[0]
#     else:
#         # If identifier is player_name
#         player_name = identifier
    
#     player_data = RM_players.loc[RM_players['player_name'] == player_name]
#     if player_data.empty:
#         warning(f"Nie znaleziono zawodnika o nazwie {player_name}")
#         return "unknown"
        
#     player_position = player_data['player_position'].values[0]
    
#     # Process position format
#     if isinstance(player_position, list) and len(player_position) > 0:
#         return player_position[0]
#     elif isinstance(player_position, str):
#         if player_position.startswith('[') and player_position.endswith(']'):
#             positions = player_position.strip('[]').replace("'", "").split(', ')
#             return positions[0]
#     return player_position

# # [markdown]
# # W *get_player_rating* aktualnie biore pod uwage ocene redakcji **('RM_PX_X_RT_M')** oraz **('RM_PX_15_FORM5')**

# def get_player_rating(player_id, actual_match_date, number_of_matches=1):
#     """
#     Get average rating from a player's last N matches before a specified date.
    
#     Parameters:
#     -----------
#     player_id : int
#         The ID of the player
#     actual_match_date : datetime
#         Reference date - only consider matches before this date
#     number_of_matches : int, default=1
#         Number of previous matches to consider for the rating
        
#     Returns:
#     --------
#     float
#         Average rating from the last N matches, or overall average if not available
#     """
#     # Get the player's name from the ID to filter the individual stats
#     player_name = RM_players[RM_players['player_id'] == player_id]['player_name'].values[0]
    
#     # Filter data for this specific player by name, not id
#     data = RM_individual[RM_individual['player_name'] == player_name]
    
#     if data.empty:
#         return 0  # No data for this player
    
#     # Find the last N matches played before the specified date
#     last_n_matches = data[data['match_date'] < actual_match_date].sort_values(by='match_date', ascending=False).head(number_of_matches)
    
#     if not last_n_matches.empty:
#         # Filter to only include matches with valid ratings
#         valid_matches = last_n_matches[last_n_matches['is_value'] > 0]
        
       
#         if not valid_matches.empty:
#             # Calculate average rating from valid matches
#             if 'rating' in valid_matches.columns: # moze dodam poźniej do bazy danych rating czyli (editor rating + user_rating)/2
#                 return valid_matches['rating'].mean()
#             elif 'editor_rating' in valid_matches.columns:
#                 return valid_matches['editor_rating'].mean()
    
#     # If we don't have valid recent matches, return overall average from all valid matches
#     valid_all_matches = data[data['is_value'] > 0]
#     if not valid_all_matches.empty:
#         if 'rating' in valid_all_matches.columns:
#             return valid_all_matches['rating'].mean()
#         elif 'editor_rating' in valid_all_matches.columns:
#             return valid_all_matches['editor_rating'].mean()
    
#     # If all else fails
#     return 0


# SEASONS_1920 = {"start_date": pd.to_datetime(SEASON_DATES[0][0]), "end_date": pd.to_datetime(SEASON_DATES[0][1])}
# SEASONS_2021 = {"start_date": pd.to_datetime(SEASON_DATES[1][0]), "end_date": pd.to_datetime(SEASON_DATES[1][1])}
# SEASONS_2122 = {"start_date": pd.to_datetime(SEASON_DATES[2][0]), "end_date": pd.to_datetime(SEASON_DATES[2][1])}
# SEASONS_2223 = {"start_date": pd.to_datetime(SEASON_DATES[3][0]), "end_date": pd.to_datetime(SEASON_DATES[3][1])}
# SEASONS_2324 = {"start_date": pd.to_datetime(SEASON_DATES[4][0]), "end_date": pd.to_datetime(SEASON_DATES[4][1])}
# SEASONS_2425 = {"start_date": pd.to_datetime(SEASON_DATES[5][0]), "end_date": pd.to_datetime(SEASON_DATES[5][1])}

# SEASONS = [SEASONS_1920, SEASONS_2021, SEASONS_2122, SEASONS_2223, SEASONS_2324, SEASONS_2425]


# def return_season(match_date):
#     match_date = pd.to_datetime(match_date)  
#     for i, season in enumerate(SEASONS):
#         start_date, end_date = season["start_date"], season["end_date"]
#         if start_date <= match_date <= end_date:
#             return SEASONS[i]
#     return False

# def return_season_before(match_date):
#     match_date = pd.to_datetime(match_date)  
#     for i, season in enumerate(SEASONS):
#         start_date, end_date = season["start_date"], season["end_date"]
#         if start_date <= match_date <= end_date:
#             if i == 0: return True
#             else: return SEASONS[i-1]
#     return False

# def is_player_season_before(player_id,match_date):
#     player_name = get_player_name(player_id)
#     if player_name is None:
#         warning(f"Nie można sprawdzić historii zawodnika o ID {player_id} - brak w bazie")
#         return False
    
#     dates_of_season_before = return_season_before(match_date)
    
#     if dates_of_season_before == False or dates_of_season_before == True:
#         info("Data jest niepoprawna albo piłkarz grał w pierszym sezonie z naszej bazy danych")
#         return False
#     else:
#         RM_individual_season_before = RM_individual[RM_individual['match_date'].between(dates_of_season_before["start_date"], dates_of_season_before["end_date"])] 
#         RM_individual_season_before = RM_individual_season_before[RM_individual_season_before['player_name'] == player_name]  
#         if RM_individual_season_before["player_min"].sum() >= 200: # Uznaje ze rozegranie 200 minut w sezonie to minimum aby uznać że zawodnik grał w tym sezonie
#             info(f"Zawodnik grał w poprzednim sezonie {dates_of_season_before['start_date']} do {dates_of_season_before['end_date']}")
#             return True
#         else:
#             info(f"Zawodnik nie grał od {dates_of_season_before['start_date']} do {dates_of_season_before['end_date']}")
#             return False

# def load_old_data(player_id):
#     count_matches = 0
#     sum_rating = 0
#     player_name = get_player_name(player_id)
#     RM_old_matches = RM_old_matches[RM_old_matches['match_date'] < pd.to_datetime(SEASON_DATES[1][0])]
#     for index, row in RM_old_matches.iterrows():
#         if row['player_name'] == player_name and row['is_value'] > 0:
#             sum_rating += row['editor_rating']
#             count_matches += 1
#     if count_matches > 0:
#         info(f"Zawodnik {player_name} ma {count_matches} meczów w bazie danych")
#         # Poprawione zaokrąglanie - w Pythonie round() to funkcja, nie metoda
#         return round(sum_rating / count_matches, 3)
#     warning(f"Zawodnik {player_name} nie ma meczów w bazie danych")
#     return 0

# def get_avg_player_rating_for_season(season):
#     start_date = season["start_date"]
#     end_date = season["end_date"]
#     season_matches = RM_matches[(RM_matches['match_date'] >= start_date) & (RM_matches['match_date'] <= end_date)]
#     if season_matches.empty:
#         return 0 
#     return season_matches['editor_rating'].mean()

# def last_season_player_rating(player_id, match_date):
#     match_date = pd.to_datetime(match_date)
#     season_variable = return_season_before(match_date=match_date)
#     if season_variable == True: # True wtedy kiedy mamy do czynienia z sezonem 2020/2021
#         info("Zawodnik grał w pierwszym sezonie w bazie. Korzystamy z danych z bazy RM_old_editor_data.csv " )
#         return load_old_data(player_id)
#     elif season_variable == False: # False wtedy kiedy nie ma sezonu dla daty meczu
#         warning("Nie można znaleźć sezonu dla daty meczu. Prawdopodobnie data meczu jest błedna.")
#         return False
#     else:
#         if is_player_season_before(player_id, match_date): # jeżeli zawodnik grał w sezonie przed aktualnym
#             info("Zawodnik grał w sezonach poprzednich względem: 2021/2022 lub 2022/2023 lub 2023/2024 lub  2024/2025. Obliczamy średnia ocene z sezonu wczesniejszego niż aktualny (oceniamy to na podstawie daty meczu)")
#             # Poprawiona linia sprawdzająca typ danych
#             if not isinstance(RM_individual["match_date"].iloc[0], pd.Timestamp):
#                 RM_individual["match_date"] = pd.to_datetime(RM_individual["match_date"])
#             player_name = RM_players[RM_players['player_id'] == player_id]['player_name'].values[0]    
#             return RM_individual[(RM_individual["match_date"] >= season_variable["start_date"]) &
#                         (RM_individual["match_date"] <= season_variable["end_date"]) &
#                         (RM_individual["player_name"] == player_name) & (RM_individual["is_value"] == 1)]["editor_rating"].mean()
#         else:
#             info(f"Mecz w terminie {match_date} nie jest w sezonie 2020/2021. Także mamy pewność że zawodnik nie grał w sezonie od czasu: {season_variable['start_date']} - {season_variable['end_date']}. Używamy średniej oceny wszystkich piłkarzy z sezonu dla tego zawodnika")
#             return get_avg_player_rating_for_season(season_variable)

# # [markdown]
# # W funkcji *player_ratio* oceniam dotychczasowy % wygranych jak zawodnik wychodził na mecz w pierwszej 11. 
# # 1-oznacza 100% 
# # 0.5-oznacza 50%
# # 0-oznacza 0%

# def check_if_dates_in_individual():
#     # Upewnij się, że wszystkie kolumny dat mają ten sam typ
#     if not isinstance(RM_old_matches['match_date'].iloc[0], pd.Timestamp):
#         RM_old_matches['match_date'] = pd.to_datetime(RM_old_matches['match_date'])
    
#     if not isinstance(RM_individual_to_ratio['match_date'].iloc[0], pd.Timestamp):
#         RM_individual_to_ratio['match_date'] = pd.to_datetime(RM_individual_to_ratio['match_date'])
        
#     # Bardziej efektywne porównanie za pomocą zbiorów
#     old_dates_set = set(RM_old_matches['match_date'])
#     individual_dates_set = set(RM_individual_to_ratio['match_date'])
    
#     # Sprawdź przecięcie zbiorów
#     individual_intersection = old_dates_set.intersection(individual_dates_set)
    
#     if individual_intersection:
#         warning(f"Znaleziono {len(individual_intersection)} dat z RM_old_matches w RM_individual")
#         return False
#     return True

# def add_old_data_to_individual():
#     # Upewnij się, że kolumna 'match_date' w RM_old_matches jest w formacie datetime
#     if not isinstance(RM_old_matches['match_date'].iloc[0], pd.Timestamp):
#         RM_old_matches['match_date'] = pd.to_datetime(RM_old_matches['match_date'])
    
#     # Upewnij się, że kolumna 'match_date' w RM_individual jest w formacie datetime
#     if not isinstance(RM_individual_to_ratio['match_date'].iloc[0], pd.Timestamp):
#         RM_individual_to_ratio['match_date'] = pd.to_datetime(RM_individual_to_ratio['match_date'])
    
#     # Dodaj dane z RM_old_matches do RM_individual_to_ratio
#     RM_old_and_now_data = pd.concat([RM_individual_to_ratio, RM_old_matches], ignore_index=True)
    
#     if check_if_dates_in_individual():
#         info("Nie znaleziono dat z RM_old_matches w RM_individual")
#         # Poprawiono usunięcie kolumn z wartościami NaN
#         RM_old_and_now_data = RM_old_and_now_data.dropna(axis=1, how='any')
#         return RM_old_and_now_data
    
#     error("Znaleziono daty z RM_old_matches w RM_individual. Nie można dodać danych ponieważ sie dublują.")
#     return False

# def get_player_ratio(player_id, match_date):
#     player_name = get_player_name(player_id)  
    
#     data = add_old_data_to_individual()
    
#     # Sprawdź czy funkcja add_old_data_to_individual() zwróciła prawidłowe dane
#     if data is False:
#         error(f"Nie można obliczyć współczynnika wygranych dla {player_name} - problem z danymi")
#         return 0
    
#     # Filtrowanie danych dla konkretnego zawodnika przed określoną datą
#     data = data[(data['player_name'] == player_name) &
#                 (data['match_date'] < pd.to_datetime(match_date)) &
#                 (data["is_first_squad"] == 1)]
    
#     # Sprawdź czy dataframe nie jest pusty po filtrowaniu
#     if data.empty:
#         info(f"Brak danych dla zawodnika {player_name} przed datą {match_date}")
#         return 0
    
#     # Sprawdzanie duplikatów dat
#     if data.duplicated(subset=['match_date']).any():
#         warning(f"Znaleziono duplikaty dat w danych dla zawodnika {player_name}")
    
#     # Sprawdzanie obecności wymaganych kolumn
#     if "home_team_id" not in data.columns:
#         error("Nie znaleziono kolumny 'home_team_id' w danych RM_individual + RM_old_matches")
#         return 0
#     if "away_team_id" not in data.columns:
#         error("Nie znaleziono kolumny 'away_team_id' w danych RM_individual + RM_old_matches")
#         return 0
    
#     # Obliczanie wygranych meczów (Real Madrid ma ID=1)
#     win_matches = data[((data["home_team_id"] == 1) & (data["home_goals"] > data["away_goals"])) |
#                        ((data["away_team_id"] == 1) & (data["away_goals"] > data["home_goals"]))]
    
#     if win_matches.empty:
#         info(f"Zawodnik {player_name} nie wygrał żadnego meczu przed datą {match_date}")
#         return 0
    
#     # Procent wygranych meczów
#     return round(len(win_matches) / len(data) * 100, 2)

# def get_avg_stats_for_player(season, player_id):
#     # Funkcja do obliczania średnich statystyk zawodnika w danym sezonie jeżeli sezon jest w bazie danych
#     start_date = season["start_date"]
#     end_date = season["end_date"]
#     player_name = RM_players[RM_players['player_id'] == player_id]['player_name'].values[0]
    
#     # Filtracja danych dla danego zawodnika w danym sezonie
#     player_data = RM_individual[(RM_individual['player_name'] == player_name) & 
#                                  (RM_individual['match_date'] >= start_date) & 
#                                  (RM_individual['match_date'] <= end_date)]
    
#     if player_data.empty:
#         return 0 
    
#     if 'goals' not in player_data.columns:
#         warning(f"Brak kolumny 'goals' w danych zawodnika {player_name}")
#         return 0
    
#     if 'assists' not in player_data.columns:
#         warning(f"Brak kolumny 'assists' w danych zawodnika {player_name}")
#         return 0
    
#     if'key_passes' not in player_data.columns:
#         warning(f"Brak kolumny 'key_passes' w danych zawodnika {player_name}")
#         return 0
    
#     if 'player_min' not in player_data.columns:
#         warning(f"Brak kolumny 'player_min' w danych zawodnika {player_name}")
#         return 0
    
#     player_min = player_data['player_min'].sum()
    
#     if player_min == 0:
#         warning(f"Zawodnik {player_name} nie rozegrał żadnej minuty w sezonie {season['start_date']} do {season['end_date']}")
#         return {
#         'RM_PX_G90':0,
#         'RM_PX_A90': 0,
#         'RM_PX_KP90': 0
#     }
    
#     # 'RM_PX_16_G90',     
#     # 'RM_PX_16_A90',
#     # 'RM_PX_16_KP90'
#     goals = player_data['goals'].sum()
#     assists = player_data['assists'].sum()
#     key_passes = player_data['key_passes'].sum()
#     return {
#         'RM_PX_G90': round((goals / player_min),3),
#         'RM_PX_A90': round((assists / player_min),3),
#         'RM_PX_KP90': round((key_passes / player_min),3)
#     }

# def get_stats_from_dataset(dataset):
#     if dataset.empty:
#         return False 
    
#     required_columns = ['goals', 'assists', 'key_passes', 'player_min']
#     for col in required_columns:
#         if col not in dataset.columns:
#             warning(f"Brak kolumny '{col}' w datasetcie.")
#             return False
    
#     player_min = dataset['player_min'].sum()
    
#     if player_min == 0:
#         warning("Liczba rozegranych minut wynosi 0.")
#         return {
#             'RM_PX_G90': 0,
#             'RM_PX_A90': 0,
#             'RM_PX_KP90': 0
#         }
    
#     goals = dataset['goals'].sum()
#     assists = dataset['assists'].sum()
#     key_passes = dataset['key_passes'].sum()
    
#     return {
#         'RM_PX_G90': round((goals * 90) / player_min, 3),
#         'RM_PX_A90': round((assists * 90) / player_min, 3),
#         'RM_PX_KP90': round((key_passes * 90) / player_min, 3)
#     }

# def last_season_player_stats(player_id, match_date):
#     match_date = pd.to_datetime(match_date)
#     season_variable = return_season_before(match_date=match_date)
    
#     # Set default return value for error cases
#     default_stats = {
#         'RM_PX_G90': 0,
#         'RM_PX_A90': 0,
#         'RM_PX_KP90': 0
#     }
    
#     if season_variable == True:  # Sezon 2019/2020
#         info("Zawodnik grał w sezonie pierwszym sezonie. Korzystamy z danych z bazy RM_old_editor_data.csv") 
#         player_name = get_player_name(player_id)
#         player_matches = RM_old_matches[RM_old_matches['player_name'] == player_name]
        
#         if player_matches.empty:
#             info(f"Zawodnik {player_name} nie ma meczów w sezonie 2020/2021 oraz nie ma meczów w bazie RM_old_editor_data.csv") # RM_old_editor_data.csv to mecze z sezonu 2019/2020
            
#             # Get position and similar players
#             try:
#                 player_position = get_main_player_position(player_id)
#                 same_position_players = []
                
#                 # Properly iterate through DataFrame
#                 for _, player_row in RM_players.iterrows():
#                     if player_row['player_position'] == player_position and player_row['player_name'] != player_name:
#                         same_position_players.append(player_row['player_name'])
                
#                 # Get matches for similar position players
#                 RM_old_matches_same_position_DF = RM_old_matches[RM_old_matches['player_name'].isin(same_position_players)]
                
#                 if RM_old_matches_same_position_DF.empty:
#                     info(f"Nie znaleziono meczów dla zawodników na pozycji {player_position}")
#                     return default_stats
                    
#                 return get_stats_from_dataset(RM_old_matches_same_position_DF)
                
#             except Exception as e:
#                 error(f"Błąd podczas przetwarzania danych pozycji: {e}")
#                 return default_stats
                
#         # Don't forget the return keyword here!
#         return get_stats_from_dataset(player_matches)
        
#     elif season_variable == False:
#         warning("Nie można znaleźć sezonu dla daty meczu")
#         return default_stats
        
#     else:  # Other seasons
#         if is_player_season_before(player_id, match_date):
#             info("Zawodnik grał w sezonie poprzednim. Obliczamy średnią ocenę z tego sezonu")
            
#             if not isinstance(RM_individual["match_date"].iloc[0], pd.Timestamp):
#                 RM_individual["match_date"] = pd.to_datetime(RM_individual["match_date"])
                
#             player_name = get_player_name(player_id)
            
#             # Get complete player data, not just editor_rating
#             player_data = RM_individual[(RM_individual["match_date"] >= season_variable["start_date"]) &
#                                        (RM_individual["match_date"] <= season_variable["end_date"]) &
#                                        (RM_individual["player_name"] == player_name)]
            
#             if player_data.empty:
#                 error(f"Zawodnik {player_name} nie ma meczów w danym sezonie")
#                 return default_stats
                
#             return get_stats_from_dataset(player_data)
            
#         else:
#             info(f"Zawodnik nie grał w poprzednim sezonie")
#             player_name = get_player_name(player_id)
            
#             # First try with RM_old_matches
#             player_matches = RM_old_matches[RM_old_matches['player_name'] == player_name]
            
#             if not player_matches.empty:
#                 return get_stats_from_dataset(player_matches)
            
#             # Try with similar position players
#             try:
#                 player_position = get_main_player_position(player_id)
#                 same_position_players = []
                
#                 for _, player_row in RM_players.iterrows():
#                     if player_row['player_position'] == player_position and player_row['player_name'] != player_name:
#                         same_position_players.append(player_row['player_name'])
                
#                 # Create new DataFrame rather than referencing undefined one
#                 RM_same_position_DF = RM_individual.copy()
#                 RM_same_position_DF = RM_same_position_DF[RM_same_position_DF['player_name'].isin(same_position_players)]
#                 # Fixed date filtering condition
#                 RM_same_position_DF = RM_same_position_DF[
#                     (RM_same_position_DF['match_date'] >= season_variable["start_date"]) & 
#                     (RM_same_position_DF['match_date'] <= season_variable["end_date"])
#                 ]
                
#                 if RM_same_position_DF.empty:
#                     return default_stats
                    
#                 return get_stats_from_dataset(RM_same_position_DF)
                
#             except Exception as e:
#                 error(f"Błąd podczas przetwarzania: {e}")
#                 return default_stats

# def get_statistics_one_by_one(player_id, match_date, type_of_stats):
#     stats = last_season_player_stats(player_id, match_date) 
    
#     # Always return a number, not False
#     if stats == False or not isinstance(stats, dict):
#         return 0
        
#     if type_of_stats == "G90" and "RM_PX_G90" in stats:
#         return stats['RM_PX_G90']
#     elif type_of_stats == "A90" and "RM_PX_A90" in stats:
#         return stats['RM_PX_A90']
#     elif type_of_stats == "KP90" and "RM_PX_KP90" in stats:
#         return stats['RM_PX_KP90']
    
#     # Default to 0 if stat not found
#     return 0

# # Słownik do przechowywania danych piłkarzy dla każdego meczu
# match_players_dict = {}

# # Grupowanie piłkarzy według ID meczu wraz z dodatkowymi danymi
# for _, player_row in RM_individual.iterrows():
#     match_id = player_row['match_id']
#     player_name = player_row['player_name']
#     match_date = player_row['match_date']
#     # Tworzenie słownika z wszystkimi istotnymi danymi piłkarza z tego meczu
#     player_id = get_player_id(player_name)
    
#     if player_id is None:
#         error(f"Zawodnik bez ID: {player_name}")
#         continue
    
#     # Sprawdzamy czy ten zawodnik faktycznie istnieje w RM_players
#     check = RM_players[RM_players['player_id'] == player_id]
#     if check.empty:
#         error(f"UWAGA: Zawodnik {player_name} ma ID {player_id}, które nie istnieje w RM_players!")
#         continue
    
#     try:
#         # Kod wywołujący funkcje, które mogą powodować błąd
#         player_data = {
#             'player_id': player_id,
#             'is_first_squad': player_row.get('is_first_squad', 0),
#             'is_value': player_row.get('is_value', 0),
#             'player_min': int(player_row.get('player_min', 0)),
#             'player_position': get_main_player_position(player_name),
#             'last_match_rating': get_player_rating(player_id, match_date, number_of_matches=1),
#             'last_season_rating': last_season_player_rating(player_id, match_date),
#             'last_5_ratings': get_player_rating(player_id, match_date, number_of_matches=5), # korzystam z funkcji *avg_last_match_rating* 
#             'win_ratio': get_player_ratio(player_id, match_date),
#             # Dodajemy trzy nowe statystyki
#             'goals_per_90': get_statistics_one_by_one(player_id, match_date, "G90"),
#             'assists_per_90': get_statistics_one_by_one(player_id, match_date, "A90"),
#             'key_passes_per_90': get_statistics_one_by_one(player_id, match_date, "KP90")
#         }
#     except Exception as e:
#         error(f"Błąd dla zawodnika {player_name} (ID: {player_id}): {str(e)}")
#         error(f"Stacktrace: {traceback.format_exc()}")
#         # Tworzymy uproszczone dane dla tego zawodnika
#         player_data = {
#             'player_id': player_id,
#             'is_first_squad': player_row.get('is_first_squad', 0),
#             'is_value': player_row.get('is_value', 0),
#             'player_min': int(player_row.get('player_min', 0)),
#             'player_position': 'unknown',
#             'last_match_rating': 0,
#             'last_season_rating': 0,
#             'last_5_ratings': 0,
#             'win_ratio': 0,
#             'goals_per_90': 0,
#             'assists_per_90': 0,
#             'key_passes_per_90': 0
#         }
    
#     # Dodajemy piłkarza do słownika dla danego meczu
#     if match_id not in match_players_dict:
#         match_players_dict[match_id] = []
    
#     match_players_dict[match_id].append(player_data)

# # Wypełnianie DataFrame DF - podstawowe dane
# for idx, row in DF.iterrows():
#     match_id = row['MATCH_ID']
#     match_date = row['M_DATE']
    
#     if match_id in match_players_dict:
#         players = match_players_dict[match_id]
        
#         # Sortuj piłkarzy - najpierw pierwszy skład, potem według minut gry
#         players.sort(key=lambda x: (-x['is_first_squad'], -x['player_min']))
        
#         # Ograniczamy do 16 piłkarzy lub dostępnej liczby
#         for i, player_data in enumerate(players[:16], start=1):
#             # Podstawowe dane
#             DF.at[idx, f'RM_PX_{i}'] = player_data['player_id']
#             DF.at[idx, f'RM_PX_{i}_FSQ'] = player_data['is_first_squad']
#             DF.at[idx, f'RM_PX_{i}_RT'] = int(player_data['is_value'])
#             DF.at[idx, f'RM_PX_{i}_POS'] = player_data['player_position'] 
#             DF.at[idx, f'RM_PX_{i}_RT_M'] = player_data['last_match_rating']
#             DF.at[idx, f'RM_PX_{i}_RT_PS'] = player_data['last_season_rating']
#             DF.at[idx, f'RM_PX_{i}_FORM5'] = player_data['last_5_ratings']
#             DF.at[idx, f'RM_PX_{i}_WINR'] = player_data['win_ratio']
#             # Dodajemy trzy nowe statystyki do DataFrame
#             DF.at[idx, f'RM_PX_{i}_G90'] = player_data['goals_per_90']
#             DF.at[idx, f'RM_PX_{i}_A90'] = player_data['assists_per_90']
#             DF.at[idx, f'RM_PX_{i}_KP90'] = player_data['key_passes_per_90']

# columns_to_display = [
#     'MATCH_ID',
#     'RM_PX_1','RM_PX_1_WINR',
#     'RM_PX_2','RM_PX_2_WINR',
#     'RM_PX_3','RM_PX_3_WINR',
#     'RM_PX_4','RM_PX_4_WINR',
#     'RM_PX_13','RM_PX_13_WINR'
# ]

# DF[columns_to_display].head(30)


