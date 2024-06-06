# Job information and logistics are hold here.
# @TODO 
# - 


job_id_counter = 0

class Job:
    
    def __init__(self, JobConfiguration) -> None:
        self.JobConfiguration = JobConfiguration
        self.job_id = str(job_id_counter)
        
        self.status = "pending"

        job_id_counter += 1
        
    def __init__(self) -> None:
        self.JobConfiguration = JobConfiguration()
        self.job_id = str(job_id_counter)
        
        self.status = "pending"
        
        job_id_counter += 1
        
    def __repr__(self) -> str:
        return
        
    def setup_conf(self, mapper, reducer, filename):
        if mapper != "" and reducer != "" and filename != "":
        
            self.JobConfiguration.file_name = filename
            self.JobConfiguration.mapper_func = mapper
            self.JobConfiguration.reducer_func = reducer

            self.JobConfiguration.file_name_Ready = True
            self.JobConfiguration.mapper_func_Ready = True
            self.JobConfiguration.reducer_func_Ready = True




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
        
    
    def __init__(self, filename):
        self.file_name = filename
        self.mapper_func = ""
        self.reducer_func = ""
        
        self.file_name_Ready = False
        self.mapper_func_Ready = False
        self.reducer_func_Ready = False
        
        

    def __repr__(self) -> str:
        return f''
            

    
    def ready(self):
        return self.file_name_Ready or self.mapper_func_Ready or self.reducer_func_Ready
        


    

