# Job information and logistics are hold here.
# @TODO 
# - 


job_id_counter = 0
def next_jid_counter() -> int:
    # increment jid
    global job_id_counter
    
    current_id = job_id_counter
    
    job_id_counter += 1
    
    return current_id
class Job:
    
    def __init__(self, JobConfiguration) -> None:
        self.JobConfiguration = JobConfiguration
        self.job_id = job_id_counter
        
        self.status = "pending"

        job_id_counter += 1
        


class JobConfiguration:
    
    """
        Information about the job input needs and setup
    """

    
    def __init__(self, filename):
        self.file_name = filename
        self.mapper_func_path =""
        self.reducer_func_path = ""
        
        self.data_set_Ready = False
        self.mapper_func_Ready = False
        self.reducer_func_Ready = False
        
        

    def __repr__(self) -> str:
        return f"\nJob configuration\n\nfilename={self.file_name}\nmapper_func={self.mapper_func_path}\nreducer_func={self.reducer_func_path}\n"
            

    
    def ready(self):
        return self.data_set_Ready or self.mapper_func_Ready or self.reducer_func_Ready
        


    

t = JobConfiguration("word_count_data.txt")
print(t)

print(t.ready())