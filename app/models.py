from app import db, api
from app.exceptions import DatabaseError

from flask import jsonify

import base64
from datetime import datetime, timedelta
import os
import jwt


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	login = db.Column(db.String(64), index=True, unique=True)
	password = db.Column(db.String(64))
	items = db.relationship('Item', backref='owner', lazy='dynamic')
	token = db.Column(db.String(32),index=True, unique=True)
	token_expiration = db.Column(db.DateTime)
	
	
	def __repr__(self):
		return '<User {}>'.format(self.login)
		
	def check_password(self, password):
		"""
		Compares given password to class entity password
		"""
		return password == self.password
		
	def get_auth_token(self,expires_in=3600):
		now = datetime.utcnow()
		if self.token and self.token_expiration > now + timedelta(seconds=60):
			return self.token
		self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
		self.token_expiration = now + timedelta(seconds=expires_in)
		db.session.add(self)
		db.session.commit()
		return self.token
	
	@staticmethod
	def check_auth_token(token):
		user = User.query.filter_by(token=token).first()
		if user is None or user.token_expiration < datetime.utcnow():
			return None
		return user
		
	
	
		
		
class Item(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(256))
	#relation to user
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	token = db.Column(db.String(32),index=True, unique=True)
	
	def __repr__(self):
		return '<Item {}>'.format(self.name)
		
	def to_dict(self):
		return {
		'id' : self.id,
		'name' : self.name,
		}
		
	def generate_item_token(self,recipient, expires_in=3600):
		"""
		Creates token used to pass this item
		"""
		try:
			payload = {
				'iat' : datetime.utcnow(),
				'exp' : datetime.utcnow() + timedelta(seconds=expires_in),
				'recipient' : recipient, #recipient's login
				'item_id' : self.id,
			}
			#encode token
			self.token = jwt.encode(payload,api.config['SECRET_KEY'],algorithm='HS256')
			db.session.add(self)
			db.session.commit()
			return self.token
		except Exception as e:
			raise DatabaseError(e)
		

	@staticmethod
	def decode_item_token(token):
		"""
		Returns item that is being transfered by this token
		"""
		try:
			payload = jwt.decode(token,api.config['SECRET_KEY'],algorithms='HS256')
			recipient = User.query.filter_by(login=payload['recipient']).first()
			item = Item.query.get(payload['item_id'])
			return recipient, item
		except jwt.ExpiredSignatureError:
			return None, None
		except jwt.InvalidTokenError:
			return None, None
		except Exception as e:
			raise DatabaseError(e)
		
		
		