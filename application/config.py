class Config(object):
	DEBUG = False
	TESTING = False
	CLOUDSTACK_URL = ""

class DevelopmentConfig(Config):
	DEBUG = True
	TESTING = True
	CLOUDSTACK_URL = "http://localhost:8080/cloudstack"

class ProductionConfig(Config):
	DEBUG = False
	TESTING = False