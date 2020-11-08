import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
def get_drinks():
    all_drinks = Drink.query.all()
    drinks = [drink.short() for drink in all_drinks]
    return jsonify({
        "success": True,
        "drinks": drinks,
        "status_code": 200
    }), 200


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    all_drinks = Drink.query.all()
    drinks = [drink.long() for drink in all_drinks]
    return jsonify({
        "success": True,
        "drinks": drinks,
        "status_code": 200
    }), 200


@app.route('/drinks', methods=["POST"])
@requires_auth('post:drinks')
def create_drink(jwt):
    try:
        req_title = request.get_json().get('title', None)
        req_recipe = request.get_json().get('recipe', None)
        if not req_title and not req_recipe:
            abort(422)
        drink = Drink()
        drink.title = req_title
        drink.recipe = json.dumps(req_recipe)
        drink.insert()
        return jsonify({"success": True, "drinks": [drink.long()]}), 200
    except Exception as err:
        print('err ', err)


@app.route('/drinks/<id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    drink = Drink.query.get(id)
    if not drink:
        abort(404)
    try:
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)
        if not title and not recipe:
            abort(422)
        if title:
            drink.title = title
        if recipe:
            drink.recipe = json.dumps(recipe)
        drink.update()
        return jsonify({"success": True, "drinks": [drink.long()]}), 200
    except Exception as err:
        print('PATCH err ', err)


@app.route('/drinks/<id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    drink = Drink.query.get(id)
    if not drink:
        abort(404)
    try:
        drink.delete()
        return jsonify({"success": True, "delete": drink.id}), 200
    except Exception as err:
        print("DELETE err ", err)

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found():
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(400)
def not_found():
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
