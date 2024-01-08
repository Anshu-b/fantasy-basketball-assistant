# Fantasy Basketball Assistant 🏀
#### Video Demo: <https://youtu.be/aYPiZ3_h0ME>
#### Description: Hi! You are reading the README for Ansh Bhatnagar's CS50x final project: Fantasy Basketball Assistant 🏀.
Fantasy sports are a way for fanatics, such as myself, to get a glimpse of what it would be like to be a general manager for a sports franchise, dictating trades, drafting players, waiver wire signings, and experiencing the results of their work with weekly matchups.
There a number of different formats (category, head-to-head points, legacy, etc) and platforms (ESPN, Yahoo, Sleeper, etc) that support this game, and although this Flask application was made with head-to-head points ESPN leagues in mind, the information provided by this site is vital to all formats and platforms (just with slightly adjusted metrics).

As an avid NBA and NFL fan and fantasy league manager, I came up with this idea to help fantasy players of all experience levels elevate their game, from helping beginners sort by fantasy points per game to aid them with drafts, to providing scheduling breakdowns to help more advanced players later in the season with prioritizing playoff scheduling.

I am proud of my project, as I believe its practical applications are very helpful for fantasy users from various backgroundsa nd experience levels, and is very simple to use.

The languages used in this full-stack programming project are as follows:

1. Python [Flask] (back-end)
2. JavaScript, HTML [Jinja], CSS [Bootstrap] (front-end)

My code is broken up into multiple files:

1. helpers.py:
    - This file starts with importing the ESPN [API](https://github.com/cwendt94/espn-api) that I used along with other necessary imports such as json, datetime, and cs50's library.
    - From there, I set up my database and utilized the API's functions to gather a list of Player objects and insert their attributes in tables called players and player_stats.
    - Next I created a list of dictionaries of NBA teams and used 2 functions and numerous variables to get each team's game schedules
    - After completing the rest of my code, I added code to update the players and player_stats tables with up-to-date data.

2. project.db:
    - .schema of tables
   ```
   CREATE TABLE players(playerId INTEGER NOT NULL PRIMARY KEY, name TEXT NOT NULL, proTeam TEXT NOT NULL, position TEXT NOT NULL, projected_total_points INTEGER, projected_avg_points INTEGER, posRANK INTEGER, injured BOOLEAN, schedule TEXT);
   CREATE UNIQUE INDEX playerId ON players(playerId);
   CREATE TABLE games(team TEXT NOT NULL, DATE TEXT NOT NULL, opponent TEXT NOT NULL, week TEXT NOT NULL);
   CREATE TABLE player_stats (fantasy_points_per_game REAL, points REAL, blocks REAL, steals REAL, assists REAL, offensive_rebounds REAL, defensive_rebounds REAL, rebounds REAL, fouls REAL, turnovers REAL, made_field_goals REAL, attempted_field_goals REAL, made_free_throws REAL, attempted_free_throws REAL, made_threes REAL, attempted_threes REAL, field_goal_percentage REAL, free_throw_percentage REAL, three_point_percentage REAL, minutes REAL, games_played INTEGER, name TEXT NOT NULL,last_7_fantasy_points_per_game REAL, last_15_fantasy_points_per_game REAL, last_30_fantasy_points_per_game REAL);
   ```
3. app.py AND templates:
    - Starting off with standard imports and setting up the Flask application.
    - @app.route("/")
        - This flask route doesn't have any logic, it simply returns the index.html template (homepage)
    - @app.route("/schedule", methods=["GET", "POST"])
        - schedule.html
            - This template is rendered with a GET request, and gives the user an option to select whether they want to view schedule by team or by week. Using JavaScript, the user's response triggers another select question asking which team or week they'd like to see
        - schedule2.html
            - The Flask portion of the code handles requests to see the schedule by week, and prints 2 tables, one for the amount of games each team has that week, and the other with the list of matchups that week.
        - schedule3.html
            - This handles requests to see schedule by team, where the number of games per week for the entire season are printed for the requested team.
    - @app.route("/stats", methods=["GET", "POST"])
        - stats.html
            - This template is rendered with a GET request, and gives the user an option to select which statistic they wish to sort by. This is especially important for determining rising stars and for anything related to category leagues.
        - stats2.html
            - Internally, the server runs queries on the players and player_stats tables and displays a table based on the requested statistic.
    - @app.route("/trade", methods=["GET", "POST"])
        - trade.html
            - This template is rendered with a GET request, and gives the user an option to input the number of players they would like to trade and recieve, and using JavaScript the number of boxes requested are dynamically displayed. The user then enters all the players.
        - trade2.html
            - Using valuation logic that I've developed myself as a fantasy user for years, I created a key and queried values from the database, applied my "algorithms" to calculate the valuations, and displayed the key, statistics for both sides, and the calculated valuations for both sides along with a summarizing message.
    - @app.route("/research", methods=["GET", "POST"])
        - research.html
            - This template is rendered with a GET request, and gives the user an option to select which topic they want to research.
        - research2.html
            - This displays "Bust Watch," which highlights players underperfoming their preseason valuations by at least 4 fantasy points. Results are printed using Jinja logic, as with most of the other tables explained above.
        - research3.html
            - This displays "Breakout Watch," which highlights players overperfoming their preseason valuations by at least 4 fantasy points. Similar to Bust Watch.
        - research4.html
            - This feature extracts all the players who are currently injured in the database and lists potential replacements for them who may provide significant fantasy value if available in leagues. The suggested players are on the same team as the injured player and listed at the same position.

4. static (styles.css) & Bootstrap
    - Contains CSS classes to style the website, such as the headers, input forms, etc

Overall, I've gained a lot of experience with APIs and full-stack programming and have learned a lot through the process of creating my first fully-indepedent web application. I look forward to building more in the future and to come back to this project once I gain a further understanding of AI, to potentially use AI to reccomend trades and to track player trends even more accurately.

I'm Ansh Bhatnagar. Thanks for reading my README. This IS Fantasy Basketball Assistant. This WAS CS50.


