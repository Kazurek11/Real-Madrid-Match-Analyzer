REAL_MADRYT_PL_2025_EXCEL_FILE ={
                    'name': 'home_team',
                    'name.1': 'away_team',
                    'editor_madrid_manager_rating': 'RM_coach_rating_EDI',
                    'avg_madrid_manager_rating': 'RM_coach_rating_USR',
                    'editor_madrid_team_rating': 'RM_team_rating_EDI',
                    'avg_madrid_team_rating': 'RM_team_rating_USR',
                    'editor_opposing_team_rating': 'rival_rating_EDI',
                    'avg_opposing_team_rating': 'rival_rating_USR',
                    'editor_referee_rating': 'referee_rating_EDI',
                    'avg_referee_rating': 'referee_rating_USR'
                } #RM_data_integration_pipeline.py

REAL_MADRYT_PL_2019_2024_EXCEL_FILE = {
                    'data': 'match_date',
                    'gospodarz': 'home_team',
                    'gość': 'away_team',
                    'bramki [gosp]': 'home_goals',
                    'bramki [gość]': 'away_goals',
                    'trener [red.]': 'RM_coach_rating_EDI',
                    'trener [userzy]': 'RM_coach_rating_USR',
                    'Real [red.]': 'RM_team_rating_EDI',
                    'Real [userzy]': 'RM_team_rating_USR',
                    'rywal [red.]': 'rival_rating_EDI',
                    'rywal [userzy]': 'rival_rating_USR',
                    'sędzia [red.]': 'referee_rating_EDI',
                    'sędzia [userzy]': 'referee_rating_USR'
                } #RM_data_integration_pipeline.py

COLUMN_TO_DROP_IN_EXCEL_FILE = [
                'avg_all_players_rating', 'editor_all_players_rating', 'madrid_manager_description',
                'referee_description', 'śr. piłkarzy [red.]', 'śr. piłkarzy [userzy]',
                'trener [opis]', 'sędzia [opis]', 'referee_rating_USR', 'referee_rating_EDI'
            ] #RM_data_integration_pipeline.py


MATCH_COLUMN_IN_ALL_MATCHES_DATASET = [
            "match_id", "round", "match_date", "home_team_id", "away_team_id", 
            "home_team", "away_team", "score", "result", "home_goals", "away_goals", 
            "home_odds", "draw_odds", "away_odds", "home_position", "away_position", 
            "season", "is_home", "real_result", "home_odds_fair", "draw_odds_fair", 
            "away_odds_fair", "PPM_H", "PPM_A"
        ] #RM_data_integration_pipeline.py

COACH_COLUMN_IN_FROM_EXCEL_TO_OUR_DATASET = [
                "RM_coach_rating_EDI", "RM_coach_rating_USR", 
                "RM_team_rating_EDI", "RM_team_rating_USR", 
                "rival_rating_EDI", "rival_rating_USR"
            ] #RM_data_integration_pipeline.py

GOALKEEPERS = ["Courtois", "Kepa", "Yáñez", "Łunin"]
LEFT_BACK = ["Fran García", "Mendy", "Marcelo", "Miguel Gutiérrez", "Camavinga"]
RIGHT_BACK = ["Carvajal", "Odriozola", "Lucas Vázquez", "Marvin", "Sergio Santos", "Nacho"]
CENTER_BACK = ["Lorenzo","Jacobo Ramón","Chust","Asencio", "Nacho", "Gila", "Rüdiger", "Tchouaméni", "Alaba", "Vallejo", "Varane", "Ramos", "Militão"]
DEF_MIDFILDER = ["Chema","Tchouaméni", "Kroos", "Blanco", "Camavinga", "Valverde", "Casemiro"]
MIDFILDER = ["Arribas","Nico Paz","Mario Martín","Chema","Isco", "Tchouaméni", "Kroos", "Blanco", "Camavinga", "Valverde", "Casemiro", "Modrić", "Ceballos", "Bellingham", "Arda Güler"]
OFENSIVE_MIDFILDER = ["Arribas","Ødegaard","Isco", "Bellingham", "Arda Güler", "Modrić","Nico Paz"]
RIGHT_WINGER = ["Peter","Asensio", "Rodrygo", "Valverde", "Arda Güler", "Brahim", "Mbappé","Bale"]
LEFT_WINGER = ["Vinícius", "Mbappé", "Hazard", "Rodrygo"]
STRIKER = ["Álvaro","Mariano","Endrick", "Mbappé", "Borja Mayoral", "Vinícius", "Jović", "Benzema","Latasa","Gonzalo","Hugo Duro","Joselu"]