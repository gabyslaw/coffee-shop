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

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/', methods=['GET'])
@app.route('/drinks', methods=['GET'])
def get_drinks():
    all_drinks = Drink.query.all()

    if all_drinks is None:
        abort(400)

    drinks_result = [drink.short() for drink in all_drinks]
    
    return jsonify({
        'success':True,
        'drinks':drinks_result
        })



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(jwt):
    all_drinks = Drink.query.all()
    if all_drinks is None:
        abort(400)

    drinks_result = [drink.long() for drink in all_drinks]

    return jsonify({
            'success':True,
            'drinks':drinks_result
            })



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
def add_drinks(jwt):
    data = request.get_json()

    if data is None:
        abort(400)
    try:
        new_title = data.get('title')
        new_recipe = json.dumps(data.get('recipe'))

        drink = Drink(title=new_title,recipe=new_recipe)
        drink.insert()

        return jsonify({
            'success':True,
            'drinks':drink.long()
            })

    except Exception as e:
        print(e)
        abort(422)



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
@app.route('/drinks/<int:id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt,id):
    try:
        drink = Drink.query.filter(Drink.id==id).first()
        if drink is None:
            abort(404)

        data = request.get_json()
        for item in data.keys():
            if item == 'title':
                drink.title = data['title']
            elif item == 'recipe':
                drink.recipe = json.dumps(data['recipe'])

        drink.update()

        return jsonify({
            'success':True,
            'drinks':[drink.long()]
            })

    except Exception as e:
        print(e)
        abort(401)



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
def delete_drink(jwt,id):
    drink = Drink.query.filter(Drink.id==id).one_or_none()
    if drink is None:
        abort(400)

    drink.delete()

    return jsonify({
        'success':True,
        'delete':(id)
        })


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found_error(error):
    return jsonify({
        'success':False,
        'error':404,
        'message':"Resource Not Found"
        }), 404

@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({
        'success':False,
        'error':400,
        'message':"Bad Request"
        })

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code