from flask import Flask, jsonify
from models import Butterfly
from db import Session
from sqlalchemy.sql import func

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World! allison is here</p>"

@app.route("/match", methods=["POST"])
def match():
  with Session() as session:
    # player = session.query(Butterfly).order_by(func.random()).first()
    player = session.query(Butterfly).filter(Butterfly.name == "test_jimmy").first()
    opponent = session.query(Butterfly).filter(Butterfly.id != player.id).filter(Butterfly.rating.between(player.rating - 30, player.rating + 30)).order_by(func.random()).first()
  # return jsonify(name=player.name, opponent=opponent.name)
  response = {'player': serialize_butterfly(player), 'opponent': serialize_butterfly(opponent)}
  return jsonify(response)

def serialize_butterfly(butterfly):
  props = {'name': butterfly.name, 'id': butterfly.id, 'image_url': butterfly.image_url}
  return props

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
