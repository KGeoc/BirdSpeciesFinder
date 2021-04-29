import json

credentials_json = json.load(open('credentials.json'))

username=credentials_json['username']
password=credentials_json['password']
client_id = credentials_json['client_id']
client_secret = credentials_json['client_secret']
user_agent = credentials_json['user_agent']

