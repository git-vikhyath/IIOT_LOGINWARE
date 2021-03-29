#main.py FILE CONFIGURATION PART
DATABASENAME = "erp.db" #if db file is located somewhere please mention full path
LOCALSERVER_IPADDRESS = "127.0.0.1"
PORT = "5002"
HEADERS = {'Content-Type' : 'application/json'}
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + 'erp.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'
CORS_HEADERS = 'Content-Type'
SERVER_IP = '192.168.0.120'
SERVER_ENDPOINT_START = '/be/api/iiot'