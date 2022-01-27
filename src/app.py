from flask import Flask, jsonify, request
from models import Butterfly, Match
from elo import get_new_rating
from db import Session
from sqlalchemy.sql import func
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World! allison is here</p>"

@app.route("/leaderboard", methods=["GET"])
def get_leaderboard():
  with Session() as session:
    butterflies = session.query(Butterfly).order_by(Butterfly.rating.desc()).limit(50).all()
  response = {'leaderboard': [serialize_butterfly(butterfly) for butterfly in butterflies]}
  return jsonify(response)

@app.route("/match", methods=["POST"])
def create_match():
  with Session() as session:
    player = session.query(Butterfly).order_by(func.random()).first()
    opponent = session.query(Butterfly).filter(Butterfly.id != player.id).filter(Butterfly.rating.between(player.rating - 30, player.rating + 30)).order_by(func.random()).first()
    if not opponent:
      print("couldn't find opponent within 30 points, choosing random opponent")
      opponent = session.query(Butterfly).filter(Butterfly.id != player.id).order_by(func.random()).first()
  response = {'player': serialize_butterfly(player), 'opponent': serialize_butterfly(opponent)}
  return jsonify(response)

@app.route("/match_result", methods=["POST"])
def create_match_result():
  data = request.get_json()
  winner_id = data['winner_id']
  loser_id = data['loser_id']
  voter_ip = data['voter_ip']
  with Session() as session, session.begin():
    winner = session.query(Butterfly).get(winner_id)
    loser = session.query(Butterfly).get(loser_id)
    old_winner_rating = winner.rating
    old_loser_rating = loser.rating
    new_winner_rating = get_new_rating(opponent_rating=old_loser_rating, player_rating=old_winner_rating, player_won=True)
    new_loser_rating = get_new_rating(opponent_rating=old_winner_rating, player_rating=old_loser_rating, player_won=False)
    match = Match(voter_ip=voter_ip,
      winner_id=winner.id, loser_id=loser.id,
      winner_initial_rating=old_winner_rating, winner_final_rating=new_winner_rating,
      loser_initial_rating=old_loser_rating,
      loser_final_rating=new_loser_rating)
    session.add(match)
    winner.rating = new_winner_rating
    loser.rating = new_loser_rating
    response = {'winner': serialize_butterfly(winner), 'loser': serialize_butterfly(loser),
    'rating_change': new_winner_rating - old_winner_rating}
  return jsonify(response)

def serialize_butterfly(butterfly):
  props = {'name': butterfly.name, 'id': butterfly.id, 'image_url': butterfly.image_url, 'rating': butterfly.rating}
  return props

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
