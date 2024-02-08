from PyIAC import PyIAC
from PyIAC.tags import CVTEngine

dbfile = "app.db"
app = PyIAC()
app.set_mode('Development')
app.drop_db(dbfile=dbfile)
app.set_db(dbfile=dbfile)
db_worker = app.init_db()
tag_engine = CVTEngine()