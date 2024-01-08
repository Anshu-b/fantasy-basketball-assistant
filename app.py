from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from collections import OrderedDict
from espn_api.basketball import League, Player
from datetime import datetime
from helpers import league, free_agent_players, rostered_players, players, nba_franchises, nba_rosters, team_agenda, db, get_week_range, week_range_list, week_ranges_list
import json

#Configure application
app = Flask(__name__)

#No logic required, just explain the website
@app.route("/")
def index():
    return render_template("index.html")

#allow user to select an NBA team/week and get the entire schedule (preferably on a weekly breakdown)
@app.route("/schedule", methods=["GET", "POST"])
def schedule():
    if request.method == "POST":
        schedule_format = request.form.get("schedule_format")
        if schedule_format == "weekly":
            week = request.form.get("week")
            games_that_week = db.execute("SELECT team, DATE, opponent FROM games WHERE week = ? ORDER BY DATE", week)
            num_games_that_week = {}
            for match in games_that_week:
                if match["team"] in num_games_that_week:
                    num_games_that_week[match["team"]] += 1
                else:
                    num_games_that_week[match["team"]] = 1
            return render_template("schedule2.html", games_that_week=games_that_week, num_games_that_week=num_games_that_week, nba_franchises=nba_franchises, week=week)
        else:
            team = request.form.get("team")
            week_data = db.execute("SELECT week FROM games WHERE team = ? ORDER BY DATE", team)
            week_count = {}
            for week in week_data:
                if week["week"] in week_count:
                    week_count[week["week"]] += 1
                else:
                    week_count[week["week"]] = 1
            return render_template("schedule3.html", week_count=week_count, team=team)
    else: #GET
        return render_template("schedule.html", week_range_list=week_range_list, week_ranges_list=week_ranges_list, nba_franchises=nba_franchises)

#query and sort based on the stat the user wants
@app.route("/stats", methods=["GET", "POST"])
def stats():
    bines = db.execute("SELECT * FROM player_stats WHERE name='Tyrese Haliburton'")
    stat_selection = list(bines[0].keys())
    if request.method == "POST":
        stat = request.form.get("stat")
        order = request.form.get("order")
        ordered_list = db.execute(f"SELECT DISTINCT(players.name), proTeam, position, posRANK, {stat} FROM player_stats JOIN players ON player_stats.name=players.name ORDER BY {stat} {order}")
        return render_template("stats2.html", ordered_list=ordered_list, stat=stat, order=order)
    else:
        return render_template("stats.html", stat_selection=stat_selection)

#trade analyzer
@app.route("/trade", methods=["GET", "POST"])
def trade():
    if request.method == "POST":
        trade_away = request.form.getlist("input1_values[]")
        trade_recieve = request.form.getlist("input2_values[]")
        names_dict = db.execute("SELECT name FROM players")
        names_list = []
        for dict in names_dict:
            names_list.append(dict["name"])
        give_list = []
        recieve_list = []
        for player in trade_away:
            if player not in names_list:
                return render_template("error.html")
            else:
                give_list.append(db.execute("SELECT players.name, proTeam, position, posRANK, injured, fantasy_points_per_game, points, blocks, steals, assists, rebounds, turnovers, minutes, games_played, last_7_fantasy_points_per_game, last_15_fantasy_points_per_game, last_30_fantasy_points_per_game FROM players JOIN player_stats ON players.name=player_stats.name WHERE players.name = ?", player)[0])
        for player in trade_recieve:
            if player not in names_list:
                return render_template("error.html")
            else:
                recieve_list.append(db.execute("SELECT players.name, proTeam, position, posRANK, injured, fantasy_points_per_game, points, blocks, steals, assists, rebounds, turnovers, minutes, games_played, last_7_fantasy_points_per_game, last_15_fantasy_points_per_game, last_30_fantasy_points_per_game FROM players JOIN player_stats ON players.name=player_stats.name WHERE players.name = ?", player)[0])
        giving_slots = len(give_list)
        recieving_slots = len(recieve_list)
        giving_valuation = 0 #evaluation of package provided by giving team
        recieving_valuation = 0 #evaluation of package provided by recieving team
        net_slots = giving_slots - recieving_slots #negative if recieving more players than sending
        if net_slots < 0:
            giving_valuation += 25*abs(net_slots)
        elif net_slots > 0:
            recieving_valuation += 25*abs(net_slots)
        for player in give_list:
            giving_valuation += player["fantasy_points_per_game"]
            print("GIVING: ", giving_valuation)
            if player["injured"] == 1:
                giving_valuation += (-3)
            elif player["last_30_fantasy_points_per_game"] > player["fantasy_points_per_game"] + 4:
                giving_valuation += 3
            elif player["last_30_fantasy_points_per_game"] < player["fantasy_points_per_game"] - 4:
                giving_valuation += (-3)
            print("GIVING: ", giving_valuation)
        for player in recieve_list:
            recieving_valuation += player["fantasy_points_per_game"]
            print("RECIEVING: ", recieving_valuation)
            if player["injured"] == 1:
                recieving_valuation += (-3)
            elif player["last_30_fantasy_points_per_game"] > player["fantasy_points_per_game"] + 4:
                recieving_valuation += 3
            elif player["last_30_fantasy_points_per_game"] < player["fantasy_points_per_game"] - 4:
                recieving_valuation += (-3)
            difference = giving_valuation - recieving_valuation
            print("RECIEVING: ", recieving_valuation)
            print(difference)
            if abs(difference) < 5:
                response = f"THIS IS A FAIR TRADE! \n The difference in valuations, { giving_valuation } (giving up), { recieving_valuation } (receiving) is within 5 fantasy points."
            elif difference > 5:
                response = f"YOU LOSE THIS TRADE! \n The difference in valuations, { giving_valuation } (giving up), { recieving_valuation } (receiving) is over 5 fantasy points!"
            elif difference < -5:
                response = f"YOU WIN THIS TRADE! \n You gain more than you lose; The difference in valuations, { giving_valuation } (giving up), { recieving_valuation } (receiving) is over 5 fantasy points!"
        return render_template("trade2.html", trade_away=trade_away, trade_recieve=trade_recieve, give_list=give_list, recieve_list=recieve_list, giving_slots=giving_slots, recieving_slots=recieving_slots, giving_valuation=giving_valuation, recieving_valuation=recieving_valuation, difference=difference, response=response)
    else:
        return render_template("trade.html")

#research busts, breakthroughs, and injury replacements
@app.route("/research", methods=["GET", "POST"])
def research():
    if request.method == "POST":
        choice = request.form.get("choice")
        if choice == "bust":
            bust_list = db.execute("SELECT players.name, players.position, players.posRANK, players.proTeam, fantasy_points_per_game, projected_avg_points, players.injured FROM players JOIN player_stats ON player_stats.name=players.name WHERE projected_avg_points-4>fantasy_points_per_game ORDER BY projected_avg_points DESC")
            for player in bust_list:
                player["differential"] = player["fantasy_points_per_game"] - player["projected_avg_points"]
            sorted_bust_list = sorted(bust_list, key=lambda x: x['differential'])
            return render_template("research2.html", sorted_bust_list=sorted_bust_list)
        elif choice == "breakout":
            breakout_list = db.execute("SELECT players.name, players.position, players.posRANK, players.proTeam, fantasy_points_per_game, projected_avg_points, players.injured FROM players JOIN player_stats ON player_stats.name=players.name WHERE projected_avg_points+4<fantasy_points_per_game ORDER BY projected_avg_points DESC")
            for player in breakout_list:
                player["differential"] = player["fantasy_points_per_game"] - player["projected_avg_points"]
            nonstart_zero = []
            start_zero = []
            for dict in breakout_list:
                if dict["projected_avg_points"] != 0:
                    nonstart_zero.append(dict)
                else:
                    start_zero.append(dict)
            sorted_nonstart_zero = sorted(nonstart_zero, key=lambda x: x['differential'], reverse=True)
            sorted_start_zero = sorted(start_zero, key=lambda x: x['differential'], reverse=True)
            return render_template("research3.html", sorted_start_zero=sorted_start_zero, sorted_nonstart_zero=sorted_nonstart_zero)
        else:
            injured_list = []
            injured_player_list = []
            injury_replacements = []
            for franchise in nba_franchises:
                injured_list.append(db.execute(f"SELECT players.name, position, posRANK, proTeam, fantasy_points_per_game, injured FROM players JOIN player_stats ON players.name=player_stats.name WHERE proTeam = '{franchise['proTeam']}' AND fantasy_points_per_game > 0 AND injured = 1"))
            for list in injured_list:
                for player in list:
                    injured_player_list.append(player)
                    injury_replacements.append(db.execute(f"SELECT players.name, position, posRANK, proTeam, fantasy_points_per_game, injured FROM players JOIN player_stats ON players.name=player_stats.name WHERE proTeam = '{player['proTeam']}' AND position = '{player['position']}' AND fantasy_points_per_game > 0 AND injured = 0 ORDER BY posRANK ASC"))
            return render_template("research4.html", injured_player_list=injured_player_list, injury_replacements=injury_replacements)
    else:
        return render_template("research.html")
        
if __name__ == '__main__':
    app.run()