from flask import Flask
from sqlalchemy import create_engine, text
from config import get_engine_url

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World! allison is here</p>"

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)

engine = create_engine(get_engine_url(), echo=True, future=True)
with engine.connect() as conn:
  result = conn.execute(text("select 'hello world'"))
  print(result.all())
