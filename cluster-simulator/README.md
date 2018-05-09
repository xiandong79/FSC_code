
# cluster simulator 


## Sec 1. Class and its attributes/functions



- class Machine:
	- self.id = id
	- def assign_task(self, task):
	- def check\_if_vacant(self):
	- def reset(self):
	

- class Job:

- class Task:
	- def handle\_task_submission

- class Event(object):
	- Type = enum('JobSubmit', 'JobComplete', 'StageSubmit', 'StageComplete', 'TaskSubmit', 'TaskComplete')
	
- class Cluster
	 -  def make_offers(self):
		- [return the available resources to the framework scheduler]
      	- return self.vacant\_machine_list [需要修改，不同类型的 机器有不同的‘vacant_machine_list’]
    - def calculate_targetAlloc(self): [需要大修]
    - def assign_task(self, machineId, task):
 	- def release_task(self, task):
 	
	
- class Scheduler:

    - def task\_buffer_insert(self, taskset):
    -  def task\_buffer_delete(self, task):
    -  def check_waiting(self):
    -  def do_allocate(self, time): [需要大修]
    -  def submit_job(self, job):  
    -  def submit_stage(self, stage, time): 
    -  def stage\_complete(self, stage):
    - def handle\_job_completion(self, job):
    
- class Simulator
	- self.job_list = list()  # list of lists. A job list for each user.
   - self.job_durations = {}
  	- self.stage_durations = {}
	- self.event_queue = Q.PriorityQueue()
	- def run [推动整个模拟进程]
	- def generate\_job_profile 
	
	 	
## Sec 2. 设计思想

### 0.

在 workloads 文件夹中，是cluster simulator 的输入数据。

### 1. 

在 FSC cluster simulator中，

1. 每个用户 有自己的 ownership ，运行时候按ownership内的数量（slot per type）为自己的所有 job 进行 FIFO (先进先出) policy 。
2. 用户有 preference value， 
3. task_buffer 应该是 为每一个用户 设置一个 isolated task buffer
4. task duration 对于不同的机器，task duration 不一样。 （用preference value 进行调整长度）


### 1.
Simulator submits jobs and stages to the scheduler
Scheduler submits tasks to the cluster

### 2. 
queue (priority queue in python3) — A synchronized queue class
The queue module implements multi-producer, multi-consumer queues. 

queue 中是一个一个的按时间顺序的 event。于是这个simulator 变成了 一个 event-driven 的模拟器。


## Sec 3. 不确定疑问

### 1. 是否保留？
        self.stageIdToUsedMachineId = dict()
        self.stageIdToAllowedMachineId = dict()
        
### 2. 陈的文件夹内 scheduler.py 有 wait-time。

也可以进一步利用， 如和delay scheduling 比较。
