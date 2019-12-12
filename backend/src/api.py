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

STATUS_CODE_SUCCESS = 200
STATUS_NOT_FOUND = 404
STATUS_UNPROCESSABLE = 422

def get_request_data(request):
    return json.loads(request.data.decode('utf-8'))

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = list(map(Drink.short, Drink.query.all()))
    result = {
        "success": True,
        "drinks": drinks
    }
    return jsonify(result)
'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = list(map(Drink.long, Drink.query.all()))
    result = {
        "success": True,
        "drinks": drinks
    }
    return jsonify(result)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks():
    if request.data:
        request_data = get_request_data(request)
        new_drink = Drink(title=request_data['title'], recipe=json.dumps(request_data['recipe']))
        Drink.insert(new_drink)
        drinks = list(map(Drink.long, [new_drink]))
        result = {
            "success": True,
            "drinks": drinks
        }
        return jsonify(result)
    else:
        abort(STATUS_UNPROCESSABLE)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(id):
    if request.data and id:
        request_data = get_request_data(request)
        drink = Drink.query.get(id)
        if 'title' in request_data:
            drink.title = request_data['title']
        if 'recipe' in request_data:
            drink.recipe = json.dumps(request_data['recipe'])
        Drink.update(drink)
        drinks = list(map(Drink.long, [drink]))
        result = {
            "success": True,
            "drinks": drinks
        }
        return jsonify(result)  
    else:
        abort(STATUS_NOT_FOUND)   
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(id):
    if id:
        drink = Drink.query.get(id)
        Drink.delete(drink)
        drinks = list(map(Drink.long, [drink]))
        result = {
            "success": True,
            "drinks": drinks
        }
        return jsonify(result)
    else:
        abort(STATUS_NOT_FOUND)

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(STATUS_UNPROCESSABLE)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": STATUS_UNPROCESSABLE,
                    "message": "unprocessable"
                    }), STATUS_UNPROCESSABLE

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(STATUS_NOT_FOUND)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": STATUS_NOT_FOUND,
                    "message": "resource not found"
                    }), STATUS_NOT_FOUND
'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify(e.error), e.status_code