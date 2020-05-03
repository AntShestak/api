from app import api

from flask import jsonify, request, url_for
from app import db
from app.models import User, Item
from app.errors import bad_request, not_found, internal_error, forbidden

#registration route
@api.route('/registration', methods=['POST'])
def create_user():
	#extract request data or none
	data = request.get_json() or {}
	#check if required fields exist
	if 'login' not in data or 'password' not in data:
		return bad_request('login and password fields must be included')
	#check if entity with this login exists
	if User.query.filter_by(login=data['login']).first():
		return bad_request('please use a different login')
	#create user
	user = User(login=data['login'], password=data['password'])
	db.session.add(user)
	db.session.commit()
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
		response = jsonify(user.get_auth_token())
		response.status_code = 200
		return response
	else:
		#user doesn't exist
		return not_found('Wrong login or password.')
		
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
		forbidden('User not authorised.')
	
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
		return not_found('Wrong item id.')
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
		forbidden('User not authorised.')
	
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
		forbidden('User not authorised.')

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
	if not item:
		return not_found('Wrong item id.')
	#check if the recipient exists
	recipient = User.query.filter_by(login=data['login']).first()
	if not recipient:
		return not_found("Wrong recipient's login.")
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
		forbidden('User not authorised.')
	
	
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
		recipient = item.check_item_token(data['token'])
		if recipient:
			#get user from recipients login
			user = User.query.filter_by(login=recipient).first()
			if user:
				#change owner of the item
				item.owner = user
				db.session.commit()
				#create response
				response = jsonify("Object was succesfully transfered")
				response.status_code = 200
				return response
			else:
				not_found('User not found.')
		else:
			bad_request('Token not recognised')
	else:
		return not_found('Item not found.')
	
		
	