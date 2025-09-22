
import pandas as pd
import numpy as np
import os
import sys

current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
from helpers.logger import info,warning,debug,error
from helpers.file_utils import FileUtils


data_25 = os.path.join(FileUtils.get_project_root(),"Data","Excele","oceny_pilkarzy_2025.xlsx")
data_20_24 = os.path.join(FileUtils.get_project_root(),"Data","Excele","real_players_match_19-24.xlsx")
avg_stats_20_24 = FileUtils.load_excel_safe(data_20_24,sheet_name="mecze20240911")
avg_stats_25 = FileUtils.load_excel_safe(data_25,sheet_name="mecze_20250319")

avg_stats_20_24.rename(columns={"data": "match_date",
                                "gospodarz":"home_team",
                                "gość":"away_team",
                                "bramki [gosp]":"home_goals",
                                "bramki [gość]":"away_goals",
                                "trener [red.]":"coach_editor_rating",
                                "trener [userzy]":"coach_users_rating",
                                "Real [red.]":"team_editor_rating",
                                "Real [userzy]":"team_users_rating",
                                "rywal [red.]":"rival_editor_rating",
                                "rywal [userzy]":"rival_users_rating"},inplace=True)

avg_stats_25.rename(columns={"name":"home_team",
                             "name.1":"away_team",
                             "editor_madrid_manager_rating":"coach_editor_rating",
                             "avg_madrid_manager_rating":"coach_users_rating",
                             "editor_madrid_team_rating":"team_editor_rating",
                             "avg_madrid_team_rating":"team_users_rating",
                             "editor_opposing_team_rating":"rival_editor_rating",
                             "avg_opposing_team_rating":"rival_users_rating"},inplace=True)
avg_stats_20_24.drop(labels=['sędzia [red.]', 
                            'sędzia [userzy]', 
                            'śr. piłkarzy [red.]',
                            'śr. piłkarzy [userzy]', 
                            'trener [opis]',
                            'sędzia [opis]'],axis=1,inplace=True)
avg_stats_25.drop(labels=['editor_referee_rating', 
                          'avg_referee_rating',
                          'editor_all_players_rating', 
                          'avg_all_players_rating',
                          'madrid_manager_description', 
                          'referee_description'], axis=1, inplace=True)
avg_stats_20_24["match_date"] = pd.to_datetime(avg_stats_20_24["match_date"])
avg_stats_25["match_date"] = pd.to_datetime(avg_stats_25["match_date"])

avg_stats_20_24  = avg_stats_20_24[avg_stats_20_24["match_date"] >= "2020-09-20"] 
avg_stats_all = pd.concat([avg_stats_20_24,avg_stats_25])
avg_stats_all.sort_values(by="match_date", inplace=True)
avg_stats_all.reset_index(drop=True, inplace=True)
RM_matches = FileUtils.load_csv_safe(os.path.join(FileUtils.get_project_root(),"Data","Real","RM_matches.csv"))

# Upewnij się, że daty są w tym samym formacie

RM_matches["match_date"] = pd.to_datetime(RM_matches["match_date"])

# Znajdź mecze w avg_stats_all, których daty występują w RM_matches
matching_stats = avg_stats_all[avg_stats_all["match_date"].isin(RM_matches["match_date"])]
matching_stats.reset_index(drop=True, inplace=True)
len(RM_matches["match_date"])
len(matching_stats["match_date"])
matching_stats[matching_stats["match_date"].duplicated(keep=False)]
