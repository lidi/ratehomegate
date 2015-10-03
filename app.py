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

@app.route('/api/v1.0/ratings/rating/all/<int:guid>', methods=['GET'])
def get_all_ratings_for_listing(guid):
    ratings = query_db("SELECT guid, rating, message FROM rating where guid = ?", [guid])
    return jsonify({'rating': ratings})

@app.route('/api/v1.0/ratings/rating/avg/<int:guid>', methods=['GET'])
def get_average_rating(guid):
    ratings = query_db("SELECT avg(rating) FROM rating where guid = ?", [guid])
    return jsonify({'rating': ratings})

@app.route('/api/v1.0/ratings', methods=['POST'])
def create_rating():
    if not request.json or not 'guid' in request.json:
        abort(400)

    guid = request.json['guid']
    rating = request.json['rating']
    message = request.json['message']
    query_db("INSERT INTO rating (guid, rating, message) VALUES (?,?,?)", [guid, rating, message])
    g.db.commit()
    return jsonify({'result': "success"}), 201

# @app.route('/api/v1.0/ratings/<int:guid>', methods=['PUT'])
# def update_rating(guid):
#     if not request.json or not 'guid' in request.json:
#         abort(400)

#     guid = request.json['guid']
#     rating = request.json['rating']
#     message = request.json['message']
#     query_db("UPDATE rating SET rating = ?, message = ? WHERE guid = ?", [rating, message, guid])
#     g.db.commit()
#     return jsonify({'result': "success"}), 201

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
