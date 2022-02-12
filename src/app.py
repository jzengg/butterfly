from flask import Flask, jsonify, request, send_file
from models import Butterfly, Match, SessionFraud
from elo import get_new_rating
from db import Session
from sqlalchemy.sql import func
from sqlalchemy import or_
from config import ADMIN_PASSWORD, API_KEY
from flask_cors import CORS
from functools import wraps
from flask import request, abort
import datetime
from waitress import serve
import csv
import io

INITIAL_RATING = 1600
DEFAULT_LEADERBOARD_LIMIT = 50
MATCHUP_THRESHOLD = 30
# how many matches to look back when checking for fraudulent voting
NUM_MATCH_LOOKBACK = 9
# min amount of time that should pass for the number of matches we're looking back
# to detect voting too frequently
MIN_MATCH_LOOKBACK_DURATION_SECONDS = 5

app = Flask(__name__)
CORS(app)

# The actual decorator function
def require_appkey(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        if request.args.get("apikey") and request.args.get("apikey") == API_KEY:
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
            session_frauds = session.query(SessionFraud).delete()
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
    response_format = args.get("format")
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
    if response_format == "csv":
        csv_contents = write_json_to_csv(response["leaderboard"])
        return csv_contents
    else:
        return jsonify(response)


@app.route("/matches", methods=["GET"])
@require_appkey
def get_matches():
    args = request.args
    count = args.get("count") or 50
    session_id = args.get("session_id")
    response_format = args.get("format")
    with Session() as session:
        query = (
            session.query(Match).order_by(Match.timestamp.desc())
        )
        if session_id is not None:
            query = query.filter(Match.session_id == session_id)
        matches = query.limit(count).all()
        butterflies = session.query(Butterfly).all()
        butterfly_id_to_data = {b.id: b for b in butterflies}
    response = {"matches": [serialize_match(m, butterfly_id_to_data) for m in matches]}
    if response_format == "csv":
        csv_contents = write_json_to_csv(response["matches"])
        return csv_contents
    else:
        return jsonify(response)


@app.route("/session_frauds", methods=["GET"])
@require_appkey
def get_session_frauds():
    args = request.args
    count = args.get("count") or 50
    only_show_workers = args.get("only_show_workers") == "true"
    with Session() as session:
        query = (
            session.query(SessionFraud)
            .filter(
                or_(
                    SessionFraud.same_side_voting_count > 0,
                    SessionFraud.frequent_voting_count > 0,
                )
            )
            .order_by(SessionFraud.id.desc())
        )
        if only_show_workers:
            query = query.filter(SessionFraud.worker_id != None)
        session_frauds = query.limit(count).all()
    response = {"session_frauds": [serialize_session_fraud(s) for s in session_frauds]}
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
            print("------------------------------")
            print("couldn't find opponent within 30 points, choosing random opponent")
            print("------------------------------")
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
    voter_ip = data["voter_ip"]
    country = data["country"]
    city = data["city"]
    region = data["region"]
    position = data["position"]
    with Session() as session, session.begin():
        winner = session.query(Butterfly).get(winner_id)
        loser = session.query(Butterfly).get(loser_id)
        old_winner_rating = winner.rating
        old_loser_rating = loser.rating
        comment = ""
        is_voting_too_frequently, too_frequent_comment = is_user_voting_too_frequently(
            session, session_id
        )
        (
            is_voting_in_same_position,
            same_position_comment,
        ) = is_user_voting_same_position(session, session_id, position)
        if is_voting_in_same_position or is_voting_too_frequently:
            comment += too_frequent_comment
            comment += same_position_comment
            new_winner_rating = old_winner_rating
            new_loser_rating = old_loser_rating
        else:
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
            voter_ip=voter_ip,
            position=position,
            comment=comment,
            country=country,
            region=region,
            city=city,
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
        }
    return jsonify(response)


@app.route("/worker", methods=["POST"])
@require_appkey
def create_session_worker():
    data = request.get_json()
    session_id = data["session_id"]
    worker_id = data["worker_id"]
    with Session() as session:
        session_fraud = find_or_create_session_fraud(session, session_id)
    response = {
        "session_fraud": serialize_session_fraud(session_fraud),
    }
    return jsonify(response)


def is_user_voting_too_frequently(session, session_id):
    voter_matches = (
        session.query(Match)
        .filter(Match.session_id == session_id)
        .order_by(Match.timestamp.desc())
        .limit(NUM_MATCH_LOOKBACK)
    )
    if voter_matches.count() < NUM_MATCH_LOOKBACK:
        return (False, "not enough matches to check for frequency")
    now = datetime.datetime.now()
    total_elapsed_time = now - voter_matches[-1].timestamp
    elapsed_seconds = total_elapsed_time.total_seconds()
    if elapsed_seconds < MIN_MATCH_LOOKBACK_DURATION_SECONDS:
        session_fraud = find_or_create_session_fraud(session, session_id)
        session_fraud.frequent_voting_count += 1
        return (
            True,
            f"vote invalid due to voting too frequently. total elapsed seconds: {round(elapsed_seconds, 1)}",
        )
    return (False, "")


def is_user_voting_same_position(session, session_id, position):
    voter_matches = (
        session.query(Match)
        .filter(Match.session_id == session_id)
        .order_by(Match.timestamp.desc())
        .limit(NUM_MATCH_LOOKBACK)
    )
    if voter_matches.count() < NUM_MATCH_LOOKBACK:
        return (False, "not enough matches to check for repeated position")
    if (
        len(set(m.position for m in voter_matches)) <= 1
        and voter_matches[-1].position == position
    ):
        session_fraud = find_or_create_session_fraud(session, session_id)
        session_fraud.same_side_voting_count += 1
        return (
            True,
            f"vote invalid due to voting the same position repeatedly. position: {position}",
        )
    return (False, "")


def find_or_create_session_fraud(session, session_id):
    session_fraud = (
        session.query(SessionFraud)
        .filter(SessionFraud.session_id == session_id)
        .first()
    )
    if session_fraud is None:
        session_fraud = SessionFraud(
            session_id=session_id, same_side_voting_count=0, frequent_voting_count=0
        )
        session.add(session_fraud)
    return session_fraud


def serialize_session_fraud(session_fraud):
    props = {
        "session_id": session_fraud.session_id,
        "timestamp": session_fraud.timestamp,
        "worker_id": session_fraud.worker_id,
        "same_side_voting_count": session_fraud.same_side_voting_count,
        "frequent_voting_count": session_fraud.frequent_voting_count,
    }
    return props


def serialize_butterfly(butterfly):
    props = {
        "name": butterfly.name,
        "id": butterfly.id,
        "image_url": butterfly.image_url,
        "rating": butterfly.rating,
    }
    return props


def serialize_match(match, butterfly_id_to_data):
    winner = butterfly_id_to_data.get(match.winner_id)
    loser = butterfly_id_to_data.get(match.loser_id)
    props = {
        "timestamp": match.timestamp,
        "session_id": match.session_id,
        "voter_ip": match.voter_ip,
        "comment": match.comment,
        "position": match.position,
        "city": match.city,
        "country": match.country,
        "region": match.region,
        "winner_id": match.winner_id,
        "winner_name": winner.name,
        "loser_name": loser.name,
        "winner": serialize_butterfly(butterfly_id_to_data.get(match.winner_id)),
        "loser_id": match.loser_id,
        "loser": serialize_butterfly(butterfly_id_to_data.get(match.loser_id)),
        "winner_initial_rating": match.winner_initial_rating,
        "winner_final_rating": match.winner_final_rating,
        "loser_initial_rating": match.loser_initial_rating,
        "loser_final_rating": match.loser_final_rating,
    }
    return props


def write_json_to_csv(data):
    output = io.StringIO()
    writer = csv.writer(output)
    for index, row in enumerate(data):
        if index == 0:
            # Writing headers of CSV file
            header = row.keys()
            writer.writerow(header)
        # Writing data of CSV file
        writer.writerow(row.values())
    return output.getvalue()


if __name__ == "__main__":
    # serve(app, host='0.0.0.0', port=5000)
    app.run(host="0.0.0.0", port=5000, debug=True)
