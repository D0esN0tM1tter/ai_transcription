from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from functools import partial
from pathlib import Path


json_storage = partial(JSONStorage , indent=4)

class BaseRepository :

    _db_instances = {} 

    def __init__(self ,
                 db_path : str , 
                 tablename : str):
        
        absolute_path = Path(db_path).resolve() 

        if absolute_path not in BaseRepository._db_instances : 
            BaseRepository._db_instances[absolute_path] = TinyDB(absolute_path , storage = json_storage) 
        

        self.db = BaseRepository._db_instances[absolute_path] 
        self.table = self.db.table(tablename) 
        self.query = Query()

    
    def insert( self , data : dict) : 
        self.table.insert(data) 

    def get(self , key : str , value) :
        return self.table.get(self.query[key] == value)
    
    def update(self , key : str , value , fields : dict) :
        self.table.update(fields , self.query[key] == value)
    
    def all(self) : 
        return self.table.all()
    
    def remove(self , key : str , value ) : 
        self.table.remove(self.query[key] == value)

