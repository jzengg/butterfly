from flask import Flask, jsonify, request
from models import Butterfly, Match
from elo import get_new_rating
from db import Session
from sqlalchemy.sql import func
from config import ADMIN_PASSWORD, API_KEY
from flask_cors import CORS
from functools import wraps
from flask import request, abort
from waitress import serve

INITIAL_RATING = 1600
DEFAULT_LEADERBOARD_LIMIT = 50
MATCHUP_THRESHOLD = 30

app = Flask(__name__)
CORS(app)

# The actual decorator function
def require_appkey(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        if request.args.get('apikey') and request.args.get('apikey') == API_KEY:
            return view_function(*args, **kwargs)
        else:
            abort(401)
    return decorated_function


@app.route("/")
@require_appkey
def hello_world():
    return "<p>Hello, World! allison is here</p>"


@app.route("/admin/reset_data", methods=["POST"])
@require_appkey
def reset_data():
    data = request.get_json()
    if data and data["admin_pw"] == ADMIN_PASSWORD:
        with Session() as session:
            matches = session.query(Match).delete()
            session.query(Butterfly).update({"rating": INITIAL_RATING})
            session.commit()
            return "reset data", 200
    else:
        return "auth failed", 400


@app.route("/leaderboard", methods=["GET"])
@require_appkey
def get_leaderboard():
    args = request.args
    count = args.get("count") or 50
    with Session() as session:
        butterflies = (
            session.query(Butterfly)
            .order_by(Butterfly.rating.desc())
            .limit(count)
            .all()
        )
    response = {
        "leaderboard": [serialize_butterfly(butterfly) for butterfly in butterflies]
    }
    return jsonify(response)


@app.route("/matches", methods=["GET"])
@require_appkey
def get_matches():
    args = request.args
    count = args.get("count") or 50
    with Session() as session:
        matches = (
            session.query(Match).order_by(Match.timestamp.desc()).limit(count).all()
        )
        butterflies = session.query(Butterfly).all()
        butterfly_id_to_data = {b.id: b for b in butterflies}
    response = {"matches": [serialize_match(m, butterfly_id_to_data) for m in matches]}
    return jsonify(response)


@app.route("/match", methods=["POST"])
@require_appkey
def create_match():
    with Session() as session:
        player = session.query(Butterfly).order_by(func.random()).first()
        opponent = (
            session.query(Butterfly)
            .filter(Butterfly.id != player.id)
            .filter(
                Butterfly.rating.between(
                    player.rating - MATCHUP_THRESHOLD, player.rating + MATCHUP_THRESHOLD
                )
            )
            .order_by(func.random())
            .first()
        )
        if not opponent:
            print("couldn't find opponent within 30 points, choosing random opponent")
            opponent = (
                session.query(Butterfly)
                .filter(Butterfly.id != player.id)
                .order_by(func.random())
                .first()
            )
    response = {
        "player": serialize_butterfly(player),
        "opponent": serialize_butterfly(opponent),
    }
    return jsonify(response)


@app.route("/match_result", methods=["POST"])
@require_appkey
def create_match_result():
    data = request.get_json()
    winner_id = data["winner_id"]
    loser_id = data["loser_id"]
    session_id = data["session_id"]
    with Session() as session, session.begin():
        winner = session.query(Butterfly).get(winner_id)
        loser = session.query(Butterfly).get(loser_id)
        old_winner_rating = winner.rating
        old_loser_rating = loser.rating
        new_winner_rating = get_new_rating(
            opponent_rating=old_loser_rating,
            player_rating=old_winner_rating,
            player_won=True,
        )
        new_loser_rating = get_new_rating(
            opponent_rating=old_winner_rating,
            player_rating=old_loser_rating,
            player_won=False,
        )
        match = Match(
            session_id=session_id,
            winner_id=winner.id,
            loser_id=loser.id,
            winner_initial_rating=old_winner_rating,
            winner_final_rating=new_winner_rating,
            loser_initial_rating=old_loser_rating,
            loser_final_rating=new_loser_rating,
        )
        session.add(match)
        winner.rating = new_winner_rating
        loser.rating = new_loser_rating
        response = {
            "winner": serialize_butterfly(winner),
            "loser": serialize_butterfly(loser),
            "rating_change": new_winner_rating - old_winner_rating,
        }
    return jsonify(response)


def serialize_butterfly(butterfly):
    props = {
        "name": butterfly.name,
        "id": butterfly.id,
        "image_url": butterfly.image_url,
        "rating": butterfly.rating,
    }
    return props


def serialize_match(match, butterfly_id_to_data):
    props = {
        "timestamp": match.timestamp,
        "session_id": match.session_id,
        "winner_id": match.winner_id,
        "winner": serialize_butterfly(butterfly_id_to_data.get(match.winner_id)),
        "loser_id": match.loser_id,
        "loser": serialize_butterfly(butterfly_id_to_data.get(match.loser_id)),
        "winner_initial_rating": match.winner_initial_rating,
        "winner_final_rating": match.winner_final_rating,
        "loser_initial_rating": match.loser_initial_rating,
        "loser_final_rating": match.loser_final_rating,
    }
    return props


if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
    # app.run(host="0.0.0.0", port=5000, debug=True)
