# api
 
Setting:
	
	Set FLASK_APP=app.py

Format:
	
	Request and response format is JSON object

Endpoint information:

	'/registration' 
	
	Registers new user.

	Parameters: 'login' , 'password'

	Response:
		{ 
			"User  <login> created!"
		}

	
	'/login' 

	Log in registered user.

	Parameters: 'login' , 'password'

	Response:
		{ 
			"token" 	:	 "jID7mbv+OZkCz2S+e9I5HK37ivU0oR6G"
		}

	
	'/items/new' 

	Creates a new item for user. Pass item's name as 'item'. Requires authorisation.

	Parameters: 'token' , 'item'

	Response:
		{ 
			"message" 	: 	"Item Created",
			"id"		:	"1",
			"item"		:	"sky"
		}

	
	
	'/delete/<int:id>' 

	Deletes an item. Pass item's id in request's body. Requires authorisation.

	Parameters: 'token' 

	Response:
		{ 
			"Item deleted."
		}



	'/Items 

	Returns list of items that are under user's ownership. Pass authorisation token as parameter. 	Requires authorisation.

	Parameters: 'token' 

	Response:
		[
			{
				"id" : "1",
				"name" : "Sky"
			},
			{
				"id" : "2",
				"name" : "Can"
			},
			{
				"id" : "5",
				"name" : "Note"
			}
		]



	'/send' 

	Send item to user. Pass recipient's login as 'login'. Pass item using 'id'. Requires 	authorisation.

	Parameters: 'token' , 'login', 'id'

	Response:
		{ 
			"token" 	:	 "Mt+iPtq58rrpz1/o7TmGwvRwZGvgFH9u'"
		}



	'/get 

	Confirm receiving the item sent by method '/send'. Requires item token received from '/send' 	method. Pass token as 'token' and item's id as 'id'. 
	
	Note: 'token' parameter is NOT an authorisation token.

	Parameters: 'token' , 'id'

	Response:
		{ 
			"Object was succesfully transfered"
		}




Error responses:
	Example error response e:

	e.text:
		{ 
			"error"		:	"Not Found",
			"message"	:"	The resource could not be found"
		}
	
	e.status_code = 404
