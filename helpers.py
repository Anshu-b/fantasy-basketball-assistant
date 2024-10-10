#imports
from cs50 import SQL
from espn_api.basketball import League
import json
from datetime import datetime, timedelta

#external API source
#https://github.com/cwendt94/espn-api

#Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

#Load in the example league using API functions
league = League(league_id=1193171671, year=2025, espn_s2="AECsoGyILCezMlwBxyf6b0JntNit1rLHsRL6SkBG1m406LNsC%2Fm%2FJ5HfdmG8AO0qFL6gfBuuyuJH66EFiZsrGmTiNfMfmeqKFHF%2BYQmaiHWPM9G59sP3aimL7mlZTLI53R8yDSCUxsIq%2FzL7Tew6CP2QcAXcGur%2FiJPS0TenItb9Sa0v61VoEm1Paf0wnJ7YTPzhMjAlSsdgUCwdJOre5pXlV14g48%2BtKe8kd2dGMH20zSvXY3Nd45nwteooY%2FUoqxlZZSDnCACjewMKFsIZchMFTkaR7WvyZ3w%2FZS5kcmm5eA%3D%3D")
league.fetch_league()

#using API function to gather free agent players
free_agent_players = league.free_agents(size=None)


#gathering all rostered players
rostered_players = []
for team in league.teams:
    for player in team.roster:
        rostered_players.append(player)

#combining lists to get all players
players = rostered_players + free_agent_players

#populating the players table with every NBA player => ONE TIME COMMAND
#Handling date conversion in JSON
def datetime_serializer(obj):
       if isinstance(obj, datetime):
           return obj.isoformat()
'''
for player in players:
   print(player.name, player.playerId)
   schedule_json = json.dumps(player.schedule, default=datetime_serializer)
   stats_json = json.dumps(player.stats["2024_total"])
   #print(db.execute("SELECT name FROM players"))
   db.execute("INSERT INTO players (name, proTeam, position, projected_total_points, projected_avg_points, posRank, injured, schedule) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", player.name, player.proTeam, player.position, player.projected_total_points, player.projected_avg_points, player.posRank, player.injured, schedule_json)
'''

#Updating the players table with current information (daily or even hourly command-preferably, currently done manually)
'''
for player in players:
   schedule_json = json.dumps(player.schedule, default=datetime_serializer)
   cleaned_name = player.name.replace("'", "")
   db.execute(f"UPDATE players SET playerId={player.playerId}, name='{cleaned_name}', proTeam='{player.proTeam}', position='{player.position}', projected_total_points={player.projected_total_points}, projected_avg_points={player.projected_avg_points}, posRank={player.posRank}, injured={player.injured}, schedule='{player.schedule}' WHERE name = '{cleaned_name}' ")
   print(player.name)
'''

#list of dictionaries of NBA teams
nba_franchises = db.execute("SELECT proTeam FROM players GROUP BY proTeam")
#dictionary of lists of dictionaries of NBA rosters
nba_rosters = {}
for team in nba_franchises:
    nba_rosters[team["proTeam"]] = db.execute("SELECT name FROM players WHERE proTeam = ?", team["proTeam"])

#Function to get the week ranges between 2 dates
def week_ranges(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    current_date = start_date - timedelta(days=start_date.weekday())
    result = []
    while current_date < end_date:
        monday = current_date + timedelta(days=(1 - current_date.weekday()))
        sunday = monday + timedelta(days=6)
        result.append((monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")))
        current_date += timedelta(weeks=1)
    return result

#function that returns the value of the above function
def get_week_range(date):
    start_datetime = datetime.strptime(date, "%Y-%m-%d")
    days_to_monday = (start_datetime.weekday() - 0) % 7
    start_of_week = start_datetime - timedelta(days=days_to_monday)
    end_of_week = start_of_week + timedelta(days=6)
    start_of_week_str = start_of_week.strftime("%Y-%m-%d")
    end_of_week_str = end_of_week.strftime("%Y-%m-%d")
    return week_ranges(start_of_week_str, end_of_week_str)

#Dictionary of each team's schedule
team_schedules = {}
for team in nba_franchises:
    temp = team["proTeam"]
    team_schedules[temp] = db.execute("SELECT schedule FROM players WHERE proTeam = ? AND schedule LIKE '%date%' LIMIT 1", temp)
game = []
#dictionary where each key is a team containing a list of games, where each list is a list with the opponent, date, week range
team_agenda = {}
for team in team_schedules:
    team_games = []
    for item in team_schedules[team]:
        schedule_dict = json.loads(item['schedule'])
        for game_id, game_info in schedule_dict.items():
            opponent = game_info['team']
            date_time = game_info['date']
            year, month, day = map(int, date_time.split('T')[0].split('-'))
            date = f"{year}-{month:02d}-{day:02d}"
            game = [opponent, date, get_week_range(date)] #a single game
            team_games.append(game)
    team_agenda[team] = team_games
    team_agenda[team] = sorted(team_agenda[team], key=lambda x: (x[1])) #sorting by date

#getting all week ranges for NBA season
week_ranges_list = week_ranges("2023-10-23", "2024-04-14")
week_range_list = []
for list in week_ranges_list:
    start_date = list[0]
    end_date = list[-1]
    week_range_list.append(start_date + "-" + end_date)


#loading NBA games into games database => ONE TIME COMMAND
'''
for team in nba_franchises:
    for game in team_agenda[team['proTeam']]:
        temp1 = game[2][0][0] #startdate
        temp2 = game[2][0][-1]#enddate
        span = temp1 + "-" + temp2
        opp = game[0]
        day = game[1]
        db.execute("INSERT INTO games(team, DATE, opponent, week) VALUES(?, ?, ?, ?)", team['proTeam'], day, opp, span)
'''

#loading player stats into database => ONE TIME COMMAND
'''
for player in players:
    if "2024_total" in player.stats:
        if "avg" in player.stats["2024_total"]:
            if "2024_last_7" in player.stats:
                if "2024_last_15" in player.stats:
                    if "2024_last_30" in player.stats:
                        print(player.name)
                        db.execute("""INSERT INTO player_stats(fantasy_points_per_game, points, blocks, steals, assists, offensive_rebounds,
                                        defensive_rebounds, rebounds, fouls, turnovers, made_field_goals, attempted_field_goals, made_free_throws,
                                        attempted_free_throws, made_threes, attempted_threes, field_goal_percentage, free_throw_percentage,
                                        three_point_percentage, minutes, games_played, name, last_7_fantasy_points_per_game, last_15_fantasy_points_per_game, last_30_fantasy_points_per_game)
                                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", player.stats["2024_total"]["applied_avg"], player.stats["2024_total"]["avg"]["PTS"], player.stats["2024_total"]["avg"]["BLK"], player.stats["2024_total"]["avg"]["STL"], player.stats["2024_total"]["avg"]["AST"], player.stats["2024_total"]["avg"]["OREB"], player.stats["2024_total"]["avg"]["DREB"], player.stats["2024_total"]["avg"]["REB"], player.stats["2024_total"]["avg"]["PF"], player.stats["2024_total"]["avg"]["TO"], player.stats["2024_total"]["avg"]["FGM"], player.stats["2024_total"]["avg"]["FGA"], player.stats["2024_total"]["avg"]["FTM"], player.stats["2024_total"]["avg"]["FTA"], player.stats["2024_total"]["avg"]["3PTM"], player.stats["2024_total"]["avg"]["3PTA"], player.stats["2024_total"]["avg"]["FG%"], player.stats["2024_total"]["avg"]["FT%"], player.stats["2024_total"]["avg"]["3PT%"], player.stats["2024_total"]["avg"]["MPG"], player.stats["2024_total"]["avg"]["GP"], player.name, player.stats["2024_last_7"]["applied_avg"], player.stats["2024_last_15"]["applied_avg"], player.stats["2024_last_30"]["applied_avg"])
'''

#updating player stats into games database (ideally done automatically at a set interval)
'''
for player in players:
    if "2024_total" in player.stats:
        if "avg" in player.stats["2024_total"]:
            if "2024_last_7" in player.stats:
                if "2024_last_15" in player.stats:
                    if "2024_last_30" in player.stats:
                        print(player.name)
                        cleaned_name = player.name.replace("'", "")
                        db.execute(f"""UPDATE player_stats SET fantasy_points_per_game={player.stats["2024_total"]["applied_avg"]}, points={player.stats["2024_total"]["avg"]["PTS"]}, blocks={player.stats["2024_total"]["avg"]["BLK"]}, steals={player.stats["2024_total"]["avg"]["STL"]}, assists={player.stats["2024_total"]["avg"]["AST"]}, offensive_rebounds={player.stats["2024_total"]["avg"]["OREB"]},
                                        defensive_rebounds={player.stats["2024_total"]["avg"]["DREB"]}, rebounds={player.stats["2024_total"]["avg"]["REB"]}, fouls={player.stats["2024_total"]["avg"]["PF"]}, turnovers={player.stats["2024_total"]["avg"]["TO"]}, made_field_goals={player.stats["2024_total"]["avg"]["FGM"]}, attempted_field_goals={player.stats["2024_total"]["avg"]["FGA"]}, made_free_throws={player.stats["2024_total"]["avg"]["FTM"]},
                                        attempted_free_throws={player.stats["2024_total"]["avg"]["FTA"]}, made_threes={player.stats["2024_total"]["avg"]["3PTM"]}, attempted_threes={player.stats["2024_total"]["avg"]["3PTA"]}, field_goal_percentage={player.stats["2024_total"]["avg"]["FG%"]}, free_throw_percentage={player.stats["2024_total"]["avg"]["FT%"]},
                                        three_point_percentage={player.stats["2024_total"]["avg"]["3PT%"]}, minutes={player.stats["2024_total"]["avg"]["MPG"]}, games_played={player.stats["2024_total"]["avg"]["GP"]}, name='{cleaned_name}', last_7_fantasy_points_per_game={player.stats["2024_last_7"]["applied_avg"]}, last_15_fantasy_points_per_game={player.stats["2024_last_15"]["applied_avg"]}, last_30_fantasy_points_per_game={player.stats["2024_last_30"]["applied_avg"]} WHERE name='{cleaned_name}' """)
'''

