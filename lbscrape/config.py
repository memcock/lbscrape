import yaml
import sys
import logging
import os
from types import SimpleNamespace
import os.path
from collections import namedtuple

BUILT_IN_DEFAULTS = { # These can be overridden in the config file. They are just here so that you don't HAVE to define them and the module still works
			'meta':{
				"version": "dev_build",
				"app" : "unknown",
				},
			'logging': {
				"logfile" : None,
				"loglvl" : "debug",
				"log_rotation": False,
				"logfmt" : '%(asctime)s %(name)s %(levelname)s: %(message)s',
				"datefmt" : '%d-%m-%y %I:%M:%S %p',
				# "datefmt" : '%d-%m-%y %I:%M:%s %p',
				"debugging" : False,
				}
}

# Instert Default values for app config here instead of mixing them with BUILT_IN_DEFAULTS
# These can be use to override BUILT_IN_DEFAULTS as well
APP_DEFAULTS = {
			'meta': {
				"config_directory": './'
				}
}

BUILT_IN_DEFAULTS.update(APP_DEFAULTS)

def injectIntoModule(**kwargs):
	configModule = sys.modules[__name__]
	for key, value in kwargs.items():
		setattr(configModule, key, value)

class Whitelist(logging.Filter):
    def __init__(self, *whitelist):
        self.whitelist = [logging.Filter(name) for name in whitelist]

    def filter(self, record):
        return any(f.filter(record) for f in self.whitelist)

class Blacklist(Whitelist):
    def filter(self, record):
        return not Whitelist.filter(self, record)

def parseLogLevel(text, default = 30):
	text = text.lower()
	levelValues = {
            'critical' : 50,
            'error' : 40,
            'warning' : 30,
            'info' : 20,
            'debug' : 10
	}
	return levelValues.get(text, default)

def setupLogging():
	rootLogger = logging.getLogger()
	rootLogger.setLevel(config.logging.loglvl)

	formatter = logging.Formatter(fmt=config.logging.logfmt, datefmt=config.logging.datefmt)

	streamHandler = logging.StreamHandler()
	streamHandler.setFormatter(formatter)

	rootLogger.addHandler(streamHandler)

	if config.logging.logfile:
		if config.logging.log_rotation:
			handler = logging.handlers.RotatingFileHandler(
				config.logging.logfile, maxBytes=10*1024*1024, backupCount=2)
		else:
			handler = logging.FileHandler(config.logging.logfile)

		handler.setFormatter(formatter)
		rootLogger.addHandler(handler)

	# for handler in logging.root.handlers:
		# handler.addFilter(Blacklist(some, stuff, here))
	baseLogger = logging.getLogger(config.meta.app)
	baseLogger.info('Starting %s: version %s'%(config.meta.app, config.meta.version))
	injectIntoModule(BASE_LOGGER=baseLogger)

def getLogger(name):
	configModule = sys.modules[__name__]
	baselogger = getattr(configModule, 'BASE_LOGGER', None)
	if baselogger:
		return baselogger.getChild(name)
	else:
		return logging.getLogger(name)

def recursivelyUpdateDict(orig, new):
	updated = orig.copy()
	updateFrom = new.copy()
	for key, value in updated.items():
		if key in new:
			if not isinstance(value, dict):
				updated[key] = updateFrom.pop(key)
			else:
				updated[key] = recursivelyUpdateDict(value, updateFrom.pop(key))
	for key, value in updateFrom.items():
		updated[key] = value
	return updated

def createNamespace(mapping, name = 'config'):
	data = {}
	for key, value in mapping.items():
		if not isinstance(value, dict):
			data[key] = value
		else:
			data[key] = createNamespace(value, key)
	nt = namedtuple(name, list(data.keys()))
	return nt(**data)

def loadYAML(path):
	with open(path) as configFile:
            return yaml.load(configFile)

def loadImports(mapping, configDir = '.'):
	loaded = mapping.copy()
	parsed = {}
	for key, value in loaded.items():
		if isinstance(value, str):
			if os.path.exists(configDir + '/' + value) and value.split('.')[-1] == 'yaml':
				parsed[key] = loadImports(loadYAML(configDir + '/' + value),  configDir)
			else:
				parsed[key] = value
		elif isinstance(value, dict):
			parsed[key] = loadImports(value, configDir)
		else:
			parsed[key] = value
	return parsed

def loadConfig(path = 'main.yaml'):
	configDir = os.path.dirname(path)
	loadedConfig = loadYAML(path)
	loadedConfig = loadImports(loadedConfig, configDir = configDir)

	# config = {**BUILT_IN_DEFAULTS, **loadedConfig} # Merge loaded config with the defaults
	config = recursivelyUpdateDict(BUILT_IN_DEFAULTS, loadedConfig)
	config = loadFromEnv(config)

	config['logging']['loglvl'] = parseLogLevel(config['logging']['loglvl']) # Parse the loglvl
	if config['logging']['loglvl'] <= 10:
		config['logging']['debugging'] = True
	# configModule = sys.modules[__name__]	# This is pretty hacky but it works...
	#
	# # Set the config values to their respective keys
	# for key, value in config.items():
	# 	configModule.__dict__[key] = value	# Dirty Hacks
	injectIntoModule(configDict=config)
	return createNamespace(config) # Return the config for good measure

def loadFromEnv(config, namespace = []):
	newConfig = config.copy()
	for key, value in config.items():
		if not isinstance(value, dict):
			configVar = '_'.join(namespace + [key.upper()])
			print('checking %s'%configVar)
			env = os.getenv(configVar, None)
			if env:
				newConfig[key] = env
		else:
			newConfig[key] = loadFromEnv(value, namespace=namespace + [key.upper()])
	return newConfig

if os.path.exists('config_stub.yaml'):
	configPath = loadYAML('config_stub.yaml').get('config_directory', None)
	if not configPath:
		configPath = BUILT_IN_DEFAULTS['meta']['config_directory']
else:
	configPath = BUILT_IN_DEFAULTS['meta']['config_directory']

def getParentModule(name):
	return sys.modules.get(name, None)

def loadByName(name, root = None):
	if isinstance(root, str):
		root = getParentModule(root)

	if root:
		sub = name.split('.')
		if len(sub) > 1:
			return loadByName('.'.join(sub[1:]), root = getattr(root, sub[0], None))
		else:
			return getattr(root, name,  None)
	else:
		raise KeyError('%s not found in config!'%name)

# from lib.terrain import terrain_constructor
# yaml.add_constructor('!terrain', terrain_constructor)

injectIntoModule(config = loadConfig(configPath + 'config.yaml'))
# CONFIG = loadConfig(file='config.json')
setupLogging()
if config.logging.debugging:
	BASE_LOGGER.info("Debugging Enabled")
