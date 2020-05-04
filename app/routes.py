from app import api

from flask import jsonify, request, url_for
from app import db
from app.models import User, Item
from app.errors import error_response, bad_request
from app.exceptions import DatabaseError
from sqlalchemy import exc

#registration route
@api.route('/registration', methods=['POST'])
def create_user():
	#extract request data or none
	data = request.get_json() or {}
	#check if required fields exist
	if 'login' not in data or 'password' not in data:
		return bad_request('Login and password fields must be included.')
	#check if entity with this login exists
	if User.query.filter_by(login=data['login']).first():
		return bad_request('please use a different login')
	#create user
	user = User(login=data['login'], password=data['password'])
	db.session.add(user)
	try:
		db.session.commit()
	except exc.SQLAlchemyError:
		raise DatabaseError('Database error')
	#create response
	response = jsonify(f"User {data['login']} created!")
	response.status_code = 201
	return response
	
	
#authorisation route
@api.route('/login', methods=['POST'])
def auth_user():
	#extract request data or none
	data = request.get_json() or {}
	#check if required fields exist
	if 'login' not in data or 'password' not in data:
		return bad_request('Login and password fields must be included')
	#check if entity with this login exists & check password
	user = User.query.filter_by(login=data['login']).first()
	if user and user.check_password(data['password']):
		#create authorisation token for user
		response = jsonify({'token':user.get_auth_token()})
		response.status_code = 200
		return response
	else:
		#user doesn't exist
		return error_response(404,'Wrong login or password.')
		
#object creation route
@api.route('/items/new', methods=['POST'])
def create_item():
	#extract request data or none
	data = request.get_json() or {}
	#check if required fields exist
	if 'token' not in data or 'item' not in data:
		return bad_request('Token and item fields must be included')
	#check token
	user = User.check_auth_token(data['token'])
	if user:
		#create item
		item = Item(name=data['item'], owner=user)
		db.session.add(item)
		db.session.commit()
		#create response
		response = jsonify({
		'message' : 'Item Created',
		'id' : item.id,
		'item' : item.name 
		})
		response.status_code = 201
		return response
	else:
		error_response(403,'Please log in.')
	
#object deletion route
@api.route('/items/<int:id>', methods=['DELETE'])
def delete_item(id):
	#extract request data or none
	data = request.get_json() or {}
	#check if required fields exist
	if 'token' not in data:
		return bad_request('Token field must be included')
	#get required item (id is passed in endpoint)
	item = Item.query.get(id)
	if not item:
		return error_response(404,'Wrong item id.')
	#get user from token
	user = User.check_auth_token(data['token'])
	#check if user was found and if he is owner of the item
	if user and user is item.owner:
		#delete item
		db.session.delete(item)
		db.session.commit()
		#create response
		response = jsonify("Item deleted.")
		response.status_code = 200
		return response
	else:
		error_response(403,'Please log in.')
	
#objects list route
@api.route('/items', methods=['GET'])
def get_objects():
	#extract request data or none
	data = request.get_json() or {}
	#check if required fields exist
	if 'token' not in data:
		return bad_request('Token field must be included')
	#get user from token
	user = User.check_auth_token(data['token'])
	if user:
		response = jsonify([item.to_dict() for item in user.items.all()])
		response.status_code = 200
		return response
	else:
		error_response(403,'Please log in.')

#ADDITIONAL --------------------
#send object route
@api.route('/send', methods=['POST'])
def send_object():
	#extract request data or none
	data = request.get_json() or {}
	#check if required fields exist
	if 'token' not in data or 'id' not in data or 'login' not in data:
		return bad_request('Token, id and login fields must be included')
	#get required item 
	item = Item.query.get(data['id'])
	#check if the recipient exists
	recipient = User.query.filter_by(login=data['login']).first()
	if not item or not recipient:
		return error_response(404,"Item or recipient doesn't exist.")
	#get user from token
	user = User.check_auth_token(data['token'])
	#check if user was found and if he is owner of the item
	if user and user is item.owner:
		response = jsonify({
		'token' : item.generate_item_token(recipient),
		})
		response.status_code = 200
		return response
	else:
		error_response(403,'Please log in.')
	
	
#receive object
@api.route('/get', methods=['GET'])
def receive_object():
	#extract request data or none
	data = request.get_json() or {}
	#check if required fields exist
	if 'token' not in data and 'id' not in data:
		return bad_request('Token and id fields must be included')
	#get required item 
	item = Item.query.get(data['id'])
	if item:
		if item.check_item_token(data['token']):
			#create response
			response = jsonify("Object was succesfully transfered")
			response.status_code = 200
			return response
		else:
			return error_response(404,'Token issue.')
		
	else:
		return error_response(404,'Item not found.')
		
#wrong endpoint
@api.errorhandler(404)
def page_not_found(e):
	return error_response(404,'The resource could not be found')
	
#internal server error
@api.errorhandler(500)
def server_error(e):
	return error_response(500,'Internal server error.')
	
#database error
@api.errorhandler(DatabaseError)
def database_error(e):
	return error_response(e.status_code,e.message)