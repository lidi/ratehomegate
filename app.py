#!ENV/bin/python
from flask import Flask
import sqlite3
from flask import g
import os.path
from flask import jsonify
from flask import request

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = 'ratings.db'
db_path = os.path.join(BASE_DIR, DATABASE)

def connect_db():
    return sqlite3.connect(db_path)

@app.before_request
def before_request():
    g.db = connect_db()

@app.after_request
def after_request(response):
    g.db.close()
    return response

@app.route('/api/v1.0/ratings/rating/<int:guid>', methods=['GET'])
def get_all_ratings_for_listing(guid):
    ratings = query_db("SELECT guid, rating, message FROM rating where guid = ?", [guid])
    avg = get_average_rating(guid)

    avg_value = avg[0].get('avg')

    data = {
      'ratings': ratings,
       'avg' : avg_value
    }
    resp = jsonify(data)
    resp.status_code = 200
    return resp

def get_average_rating(guid):
    return query_db("SELECT avg(rating) as avg FROM rating where guid = ?", [guid])

@app.route('/api/v1.0/ratings/rating/<int:guid>', methods=['POST'])
def create_rating(guid):
    if not request.json:
        abort(400)

    rating = request.json['rating']
    message = request.json['message']
    query_db("INSERT INTO rating (guid, rating, message) VALUES (?,?,?)", [guid, rating, message])
    g.db.commit()
    return jsonify({'result': "success"}), 201

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
