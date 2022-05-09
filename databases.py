from tinydb import TinyDB, Query
import settings

def init():
    global logDatabase
    logDatabase = TinyDB(settings.application_root_directory + 'log.json')