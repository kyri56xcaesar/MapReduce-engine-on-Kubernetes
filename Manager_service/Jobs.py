import json
# Job information and logistics are hold here.
# @TODO 
# - should use a database


class Job:
    
    
    def __init__(self):
        self.JobConfiguration = JobConfiguration()
        self.jid = ""
        
        self.j_status = "pending"
        self.created = ""
        

        
    def __repr__(self) -> str:
        return f'jid: {self.jid}\n {self.JobConfiguration}'
    
    def to_json(self) -> str:
        return json.dumps({
            "jid": self.jid,
            "j_status": self.j_status,
            "created": self.created,
            "JobConfiguration": {
                "file_name": self.JobConfiguration.file_name,
                "mapper_func": self.JobConfiguration.mapper_func,
                "reducer_func": self.JobConfiguration.reducer_func,
                "file_name_Ready": self.JobConfiguration.file_name_Ready,
                "mapper_func_Ready": self.JobConfiguration.mapper_func_Ready,
                "reducer_func_Ready": self.JobConfiguration.reducer_func_Ready
            }
        })
    def init(self, jid, filename, mapper, reducer, created, status):
        self.jid = jid
        self.created = created
        self.status = status
        
        self.setup_conf(mapper, reducer, filename)
        
    def setup_conf(self, mapper, reducer, filename):
        if mapper != "" and reducer != "" and filename != "":
        
            self.JobConfiguration.file_name = filename
            self.JobConfiguration.mapper_func = mapper
            self.JobConfiguration.reducer_func = reducer

            self.JobConfiguration.file_name_Ready = True
            self.JobConfiguration.mapper_func_Ready = True
            self.JobConfiguration.reducer_func_Ready = True

    def set_mapper_func(self, mapper):
        self.JobConfiguration.mapper_func = mapper
        self.JobConfiguration.mapper_func_Ready = True

    def set_reducer_func(self, reducer):
        self.JobConfiguration.reducer_func = reducer
        self.JobConfiguration.reducer_func_Ready = True

    def set_filename(self, filename):
        self.JobConfiguration.file_name = filename
        self.JobConfiguration.file_name_Ready = True


class JobConfiguration:
    
    """
        Information about the job input needs and setup
    """
    def __init__(self):
        self.file_name = ""
        self.mapper_func =""
        self.reducer_func = ""
        
        self.file_name_Ready = False
        self.mapper_func_Ready = False
        self.reducer_func_Ready = False
        

        

    def __repr__(self) -> str:
        return f''
            

    
    def ready(self) -> bool:
        return self.file_name_Ready or self.mapper_func_Ready or self.reducer_func_Ready
        


    

