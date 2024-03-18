from flask import Flask, render_template, redirect, url_for, render_template_string, request, session, jsonify
import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
import spacy

from const import *
from rest import google_news_GET, chat_gpt_GET, team_id_GET, team_statistics_GET, team_recent_transfers_GET, team_recent_injuries_GET, team_lastest_score_GET, large_language_model_classifier

app = Flask(__name__)
app.secret_key = "hello"

# Load the English language model for spaCy
nlp = spacy.load("en_core_web_sm")

def extract_names(text):
    # Process the text with spaCy
    doc = nlp(text)
    
    # Initialize lists to store extracted names
    names = []
    football_entities = []

    # Extract names and potential football team/league names
    for ent in doc.ents:
        if ent.label_ == "PERSON":  # Extract person names
            names.append(ent.text)
        elif ent.label_ == "ORG":   # Extract organization names
            football_entities.append(ent.text)

    return names, football_entities

def extract_news(url):
    # Send a GET request to the URL
    response = requests.get(url)
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the title of the article
    title = soup.find('h1').text.strip()

    # Find the image associated with the article (if any)
    image = soup.find('img')['src'] if soup.find('img') else None

    # Find all paragraphs within the main article content
    paragraphs = []
    for paragraph in soup.find_all('p'):
        # Exclude paragraphs that contain links or advertisements
        if not paragraph.find('a') and not paragraph.find(class_='advertisement'):
            paragraphs.append(paragraph.text.strip())

    # Combine paragraphs into a single string
    article_content = '\n'.join(paragraphs)
    
    print(title)
    print(image)
    print(article_content)

    return title, image, article_content

def generate_queries(team_interests, content_interests):
    queries = []
    for team, team_interest in team_interests.items():
        for content, content_interest in content_interests.items():
            relevance_score = team_interest * content_interest
            if relevance_score > 0:
                queries.append((team, content, relevance_score))
    
    # Sort queries based on relevance score in descending order
    queries.sort(key=lambda x: x[2], reverse=True)
    
    return queries

def format_news_feed_post(query):
    item_name = query[0]
    news_type = query[1]

    if news_type == 'Team News Updates':
        #data = google_news_GET(item_name, news_type)
        data = {
            "title": str(item_name) + " " + str(news_type),
        }
    elif news_type == 'Injury News':
        #data = team_recent_transfers_GET(item_name)
        data = {
            "title": str(item_name) + " " + str(news_type),
        }
    elif news_type == 'Transfer News':
        #data = team_recent_transfers_GET(item_name)
        data = {
            "title": str(item_name) + " " + str(news_type),
        }
    elif news_type == 'Team Statistics':
        #data = team_statistics_GET(item_name)
        data = {
            "title": str(item_name) + " " + str(news_type),
        }
    elif news_type == 'Last Fixture':
        #data = team_lastest_score_GET(item_name)
        data = {
            "title": str(item_name) + " " + str(news_type),
        }
    else:
        # Handle unsupported news type
        print("error!!!")

    return {'item': item_name, 'news_type': news_type, 'data': data}

def generate_formatted_news_feed(queries, proportions, total_articles):
    formatted_news_feed = []
    for query, proportion in zip(queries, proportions):
        num_articles = int(total_articles * proportion)
        formatted_news_feed.extend([format_news_feed_post(query)] * num_articles)
    return formatted_news_feed

def calculate_proportions(queries):
    total_probability = sum(query[2] for query in queries)
    proportions = [query[2] / total_probability for query in queries]
    return proportions

@app.route('/')
def index():

    if 'user profile' not in session and 'interests profile' not in session and 'content style profile' not in session:
        return redirect(url_for('form'))

    # Generate queries
    queries = generate_queries(session['interests profile'], session['content style profile'])

    session['queries'] = queries

    # Display generated queries
    for query in queries:
        print(f"Query: {query[0]} {query[1]} (Relevance Score: {query[2]})")

    proportions = calculate_proportions(queries)
    print(proportions)

    total_articles = len(queries)

    formatted_news_feed = generate_formatted_news_feed(queries, proportions, total_articles)

    print("Formatted News Feed:", formatted_news_feed)

    print(session['interests profile'])
    print(session['content style profile'])
    # print(session['demographic profile'])

    return render_template("feed.html", news_feed=formatted_news_feed)

@app.route('/form/', methods=('GET', 'POST'))
def form():

    if 'user profile' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':

        Leagues = ['PremierLeague', 'LaLiga', 'Bundesliga', 'SerieA', 'Ligue1', 'MLS']
        type_of_content = ['Team Statistics', 'Transfer News', 'Injury News', 'Last Fixture', 'Team News Updates', 'Educational Content']

        name = request.form.get('name')
        birthday = request.form.get('birthday')

        leagues_of_interest = []

        for league in Leagues:
            if request.form.get(league) == "clicked":
                leagues_of_interest.append(league)

        premier_league_teams_x = request.form.getlist('PremierLeagueTeams')
        la_liga_league_teams_x = request.form.getlist('LaLigaTeams')
        bundesliga_league_teams_x = request.form.getlist('BundesligaTeams')
        seria_a_league_teams_x = request.form.getlist('SerieATeams')
        mls_league_teams_x = request.form.getlist('MLSTeams')

        country_x = request.form.get('country')

        content_of_interest_x = []

        for content in type_of_content:
            if request.form.get(content) == "clicked":
                content_of_interest_x.append(content)

        knowledge_x = request.form.get('knowledge')

        user = {'name': name, 'birthday': birthday,
                 'leagues' : leagues_of_interest,
                 'Premier League Teams' : premier_league_teams_x,
                 'La Liga League Teams' : la_liga_league_teams_x,
                 'Bundesliga League Teams' : bundesliga_league_teams_x,
                 'Seria A League Teams' : seria_a_league_teams_x,
                 'MLS League Teams' : mls_league_teams_x,
                 'country' : country_x,
                 'content' : content_of_interest_x,
                 'knowledge' : knowledge_x,}

        session['user profile'] = user

         # Combine all teams into one list
        all_teams = (leagues + premier_league_teams + la_liga_teams + bundesliga_teams +
                    serie_a_teams + ligue_1_teams + mls_teams)

        content = [
            "Team Statistics",
            "Transfer News",
            "Injury News",
            "Last Fixture",
            "Team News Updates",
            "Educational Content"
        ]

        print("Meep meep")
        # Create a hashmap with teams as keys and corresponding values initialized to 0
        team_scores = {team: 0 for team in all_teams} 
        content_scores = {c: 0 for c in content}

        for league in session['user profile']['leagues']:
            team_scores[league] += 0.5

        for team in session['user profile']['Premier League Teams']:
            team_scores[team] += 0.5
        
        for team in session['user profile']['La Liga League Teams']:
            team_scores[team] += 0.5

        for team in session['user profile']['Bundesliga League Teams']:
            team_scores[team] += 0.5

        for team in session['user profile']['Seria A League Teams']:
            team_scores[team] += 0.5

        for team in session['user profile']['MLS League Teams']:
            team_scores[team] += 0.5

        for content in session['user profile']['content']:
            content_scores[content] += 0.5

        demographic_info = {
            "Name" : session['user profile']['name'],
            "Age Range" : session['user profile']['birthday'],
            "Country" : session['user profile']['country'], 
            "Knowledge Level" : session['user profile']['knowledge']
        }

        print(team_scores)
        print("-----")
        print(content_scores)
        print("-----")
        print(demographic_info)
        print("-----")

        session['interests profile'] = team_scores
        session['content style profile'] = content_scores
        session['demographic profile'] = demographic_info

        return redirect(url_for('index'))
    return render_template("form.html")

@app.route('/clear')
def clear():
    session.pop("user profile", None)
    session.pop("interests profile", None)
    session.pop("content style profile", None)
    return redirect(url_for("index"))

# @app.route('/news')
# def news():
#     test = google_news_GET("VfL Wolfsburg", "Transfer News")
#     data  = json.dumps(test)
#     articles = json.loads(data)

    return render_template("news.html", articles=articles)

@app.route('/gpt/<word>', methods=['GET', 'POST'])
def gpt(word):
    return render_template("facts.html", word=word, info=chat_gpt_GET(word))

@app.route('/keywords/<word>', methods=['GET', 'POST'])
def keywords(word):
    return chat_gpt_GET()

@app.route('/id')
def id():
    test = team_id_GET("Liverpool")
    return "the id is : " + str(test) 

@app.route('/statistics/<word>', methods=['GET', 'POST'])
def statistics(word):
    id = team_id_GET(word)
    league_name, league_position, total_points, goal_difference, total_matches_played, matches_won, matches_lost, matches_drawn = team_statistics_GET(id)

    return render_template("stats.html", league_name=league_name, league_position=league_position, 
                           total_points=total_points, goal_difference=goal_difference, total_matches_played=total_matches_played,
                           matches_won=matches_won, matches_lost=matches_lost, matches_drawn=matches_drawn, team_name=word) 

@app.route('/transfers/<word>', methods=['GET', 'POST'])
def transfers(word):
    id = team_id_GET(word)
    transfer_info = team_recent_transfers_GET(id)

    return render_template("transfers.html", transfer_info=transfer_info, team_name=word)

@app.route('/injuries/<word>', methods=['GET', 'POST'])
def injuries(word):
    id = team_id_GET(word)
    injured_players = team_recent_injuries_GET(id)

    return render_template("injuries.html", injured_players=injured_players, team_name=word)

@app.route('/latest/<word>', methods=['GET', 'POST'])
def latest(word):
    id = team_id_GET(word)
    home_team_name, away_team_name, score, home_goals, away_goals, home_red_cards, away_red_cards, home_yellow_cards, away_yellow_cards = team_lastest_score_GET(id)

    return render_template("latest.html",home_team_name=home_team_name, away_team_name=away_team_name, score=score, home_goals=home_goals, away_goals=away_goals, home_red_cards=home_red_cards, away_red_cards=away_red_cards, home_yellow_cards=home_yellow_cards, away_yellow_cards=away_yellow_cards, team_name=word) 

@app.route('/news', methods=['GET', 'POST'])
def news():
        link = "https://www.manchestereveningnews.co.uk/sport/football/football-news/pep-guardiola-makes-arsenal-point-28782278"
        title, image, article_content = extract_news(link)
        return render_template('news.html', title=title, image=image, article_content=article_content)

@app.route('/like', methods=['POST'])
def like():
    if request.method == 'POST':
        # Retrieve data from the form
        word1 = request.form['word1']
        word2 = request.form['word2']
        print(f'Word 1: {word1}, Word 2: {word2}')

        session['interests profile'][word2] += 0.1
        session['content style profile'][word1] += 0.1

        print(session['interests profile'])
        print(session['content style profile'])
        print("-----")
        test = generate_queries(session['interests profile'], session['content style profile'])
        # Display generated queries
        for query in test:
            print(f"Query: {query[0]} {query[1]} (Relevance Score: {query[2]})")

        session['interests profile'] = session['interests profile']
        session['content style profile'] = session['content style profile']

        return 'Received like action.'

@app.route('/dislike', methods=['POST'])
def dislike():
    if request.method == 'POST':
        # Retrieve data from the form
        word1 = request.form['word1']
        word2 = request.form['word2']
        print(f'Word 1: {word1}, Word 2: {word2}')

        t1 = session['interests profile']
        t2 = session['content style profile']

        t1[word2] -= 0.1
        t2[word1] -= 0.1

        print(t1)
        print(t2)

        print("-----")
        test = generate_queries(t1, t2)
        for query in test:
            print(f"Query: {query[0]} {query[1]} (Relevance Score: {query[2]})")

        session['interests profile'] = t1
        session['content style profile'] = t2

        return 'Received dislike action.'

@app.route('/usermodel')
def usermodel():
    queries = session['queries']
    return render_template('userModel.html', queries=queries)

text = "Pep Guardiola makes Arsenal point ahead of Liverpool FC vs Man City Article ImageManchester City manager Pep Guardiola spoke about Arsenal's recent form when asked to look beyond Jurgen Klopp's Liverpool Get the latest City team news, transfer stories, match updates and analysis delivered straight to your inbox - FREE We have more newsletters Get the latest City team news, transfer stories, match updates and analysis delivered straight to your inbox - FREE We have more newsletters City trail Liverpool by a point heading into the game but both could be below Arsenal in the table when they kick off as Mikel Arteta's side look to continue their recent form that included them routing Sheffield United on Monday night. Asked if like would be easier without Klopp's Liverpool next season, Guardiola still expects them to challenge but also spoke about how strong Arsenal have looked recently after pushing City all the way last season. 'I would like to know but I don't think so,' he said. 'Liverpool have always been Liverpool and the contenders are there. 'Arsenal is already there, last season they were our biggest rivals. Look how they play. Liverpool need more than 90 minutes to win the game, sometimes more; Arsenal sometimes need just 25 minutes to win the games. That's why they are there. 'I guess Tottenham will make a step forward and United and Newcastle will maybe be back having one game a week. It's next season and I don't have the ability to think about what is going to happen next.'"

# Extract names and potential football team/league names
names, football_entities = extract_names(text)

# Print the results
print("Names:", names)
print("Potential Football Teams/Leagues:", football_entities)

def process_categories(categories, opinion):
    category_list = categories.split(',')
    
    print("Category List: ")
    print(category_list)

    print("content: ")
    print(content)

    for category in category_list:
        if category.strip() in content:
            t = session['content style profile']
            if opinion == "like":
                if t[category.strip()] == 0:
                    t[category.strip()] += 0.5
                else:
                    t[category.strip()] += 0.1
            else:
                t[category.strip()] -= 0.1            
            session['content style profile'] = t

        else:
            t = session['interests profile']
            if opinion == "like":
                if t[category.strip()] == 0:
                    t[category.strip()] += 0.5
                else:
                    t[category.strip()] += 0.1
            else:
                t[category.strip()] -= 0.1          
            session['interests profile'] = t

@app.route('/classifierLike', methods=['POST'])
def classifierLike():

    if request.method == 'POST':

        article_title = request.form['word1']
        article_content = request.form['word2']

        # article = """
        #                 Pep Guardiola makes Arsenal point ahead of Liverpool FC vs Man City
        #                 Manchester City manager Pep Guardiola spoke about Arsenal's recent form when asked to look beyond Jurgen Klopp's Liverpool Get the latest City team news, transfer stories, match updates and analysis delivered straight to your inbox - FREE We have more newsletters Get the latest City team news, transfer stories, match updates and analysis delivered straight to your inbox - FREE We have more newsletters City trail Liverpool by a point heading into the game but both could be below Arsenal in the table when they kick off as Mikel Arteta's side look to continue their recent form that included them routing Sheffield United on Monday night. Asked if like would be easier without Klopp's Liverpool next season, Guardiola still expects them to challenge but also spoke about how strong Arsenal have looked recently after pushing City all the way last season. "I would like to know but I don't think so," he said. "Liverpool have always been Liverpool and the contenders are there. "Arsenal is already there, last season they were our biggest rivals. Look how they play. Liverpool need more than 90 minutes to win the game, sometimes more; Arsenal sometimes need just 25 minutes to win the games. That's why they are there. "I guess Tottenham will make a step forward and United and Newcastle will maybe be back having one game a week. It's next season and I don't have the ability to think about what is going to happen next."
        #                 """

        article = "Disliked Article: Title - {}, Content - {}".format(article_title, article_content)

        result = large_language_model_classifier(article)

        process_categories(result, "like")

        return result

@app.route('/classifierDislike', methods=['POST'])
def classifierDislike():

    if request.method == 'POST':

        article_title = request.form['word1']
        article_content = request.form['word2']

        # article = """
        #                 Pep Guardiola makes Arsenal point ahead of Liverpool FC vs Man City
        #                 Manchester City manager Pep Guardiola spoke about Arsenal's recent form when asked to look beyond Jurgen Klopp's Liverpool Get the latest City team news, transfer stories, match updates and analysis delivered straight to your inbox - FREE We have more newsletters Get the latest City team news, transfer stories, match updates and analysis delivered straight to your inbox - FREE We have more newsletters City trail Liverpool by a point heading into the game but both could be below Arsenal in the table when they kick off as Mikel Arteta's side look to continue their recent form that included them routing Sheffield United on Monday night. Asked if like would be easier without Klopp's Liverpool next season, Guardiola still expects them to challenge but also spoke about how strong Arsenal have looked recently after pushing City all the way last season. "I would like to know but I don't think so," he said. "Liverpool have always been Liverpool and the contenders are there. "Arsenal is already there, last season they were our biggest rivals. Look how they play. Liverpool need more than 90 minutes to win the game, sometimes more; Arsenal sometimes need just 25 minutes to win the games. That's why they are there. "I guess Tottenham will make a step forward and United and Newcastle will maybe be back having one game a week. It's next season and I don't have the ability to think about what is going to happen next."
        #                 """

        article = "Liked Article: Title - {}, Content - {}".format(article_title, article_content)

        result = large_language_model_classifier(article)
        process_categories(result, "dislike")

        return result
