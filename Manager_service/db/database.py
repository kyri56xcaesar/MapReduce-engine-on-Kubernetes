import sqlite3
from datetime import datetime
from os import path
from flask import current_app,g

from Jobs import *

def init_app(app, db_path):
    app.teardown_appcontext(close_db)
    
    
    with app.app_context():
        if not path.exists(db_path):
            with open(db_path, 'w'):
                pass
        db = sqlite3.connect(
                current_app.config["DATABASE"],
                detect_types=sqlite3.PARSE_DECLTYPES,
            )
    
    
        with current_app.open_resource("db/jobs_init.sql") as f:
            db.executescript(f.read().decode("utf-8"))
        
    print("You successfully initialized the db!")
    
    
    
    
    

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        
    return g.db
        
    
def close_db(e=None):
    db = g.pop("db", None)
    
    if db is not None:
        db.close()
        
def check_db():
    try:
        db = get_db()
        db.execute('SELECT 1')
        r = db.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="jobs"')
        table_exists = r.fetchone() is not None
        if not table_exists:
            return False, "Table 'jobs' does not exist"
        return True, "Database is active and table 'jobs' exists"
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"  
        
def get_job_by_id(jid) -> Job:
    db = get_db()
    
    try:
        row = db.execute('SELECT * \
            FROM jobs \
                WHERE jid = ?', (jid)).fetchone()
    except sqlite3.Error as e:
        print(f'error occured: {e}')
        return None
    
    if row is None:
        return None
    
    job: Job = Job()
    str_dt = row['created'].strftime("%Y-%m-%d %H:%M:%S")
    job.init(str(row['jid']), row['file_name'], row['mapper_func'], row['reducer_func'], str_dt, row['j_status'])
        
    
    return job

def get_all_jids() -> list:
    db = get_db()
    
    try:
        rows = db.execute('SELECT jid\
            FROM jobs;').fetchall()
        
        return [dict(row) for row in rows]
    
    except sqlite3.Error as e:
        print(f'error occured: {e}')
        return None
    

def insert_job(jobconf: JobConfiguration) -> tuple[bool, int]:

    db = get_db()
    try:
        
        c_dt = datetime.now()
        
        row = db.execute(
            'INSERT INTO jobs (file_name, mapper_func, reducer_func, created, j_status)\
            VALUES (?, ?, ?, ?, ?)',
            (jobconf.file_name, jobconf.mapper_func, jobconf.reducer_func, c_dt, "pending")
            
        )

        id = row.lastrowid
        
        db.commit()
        
        return True, id
    except sqlite3.Error as e:
        print(f'error occured: {e}')
        return False, -1
    
def delete_job_by_jid(jid: str) -> bool:
    
    db = get_db()
    try:
        db.execute(
            'DELETE\
                FROM jobs\
                    WHERE jid = ?',
                    (jid,)
        )
        db.commit()
        return True
    except sqlite3.Error as e:
        print(f'error occured: {e}')
        return False
    
 
def update_job_by_jid(jid :str, filename: str, mapper_func: str, reducer_func: str, status: str):
    db = get_db()    
   
    try:
        row = db.execute(
            'UPDATE jobs\
            SET file_name=?, mapper_func=?, reducer_func=?, j_status=?\
            WHERE jid = ?',
            (filename, mapper_func, reducer_func, status, jid)
        )
        if row.rowcount == 0:
            return False
       
        db.commit()
       
        return True
    except sqlite3.Error as e:
        print(f'error updating job: {e}')
        return False   
    
def update_job_mapper_by_jid(jid :str, mapper_func: str):
    db = get_db()    
    
    try:
        row = db.execute(
            'UPDATE jobs\
            SET mapper_func=?\
            WHERE jid = ?',
            (mapper_func, jid)
        )
        
        if row.rowcount == 0:
            return False
        db.commit()
        

        
        return True
    except sqlite3.Error as e:
        print(f'error updating job: {e}')
        return False
        

def update_job_reducer_by_jid(jid :str, reducer_func: str):
    db = get_db()    
    
    try:
        row = db.execute(
            'UPDATE jobs SET reducer_func=? WHERE jid = ?',
            (reducer_func, jid)
        )
        
        if row.rowcount == 0:
            return False
        db.commit()
        

        
        return True
    except sqlite3.Error as e:
        print(f'error updating job: {e}')
        return False
        
                    
def update_job_filename_by_jid(jid :str, filename: str):
    db = get_db()    
    
    try:
        row = db.execute(
            'UPDATE jobs\
            SET file_name=?\
            WHERE jid = ?',
            (filename, jid)
        )
        if row.rowcount == 0:
            return False        
        db.commit()
        
        return True
    except sqlite3.Error as e:
        print(f'error updating job: {e}')
        return False
                    
def update_job_status_by_jid(jid :str, status: str):
    db = get_db()    
    
    try:
        row = db.execute(
            'UPDATE jobs\
            SET j_status=?\
            WHERE jid = ?',
            (status, jid)
        )
        if row.rowcount == 0:
            return False
        
        db.commit()
        
        return True
    except sqlite3.Error as e:
        print(f'error updating job: {e}')
        return False
