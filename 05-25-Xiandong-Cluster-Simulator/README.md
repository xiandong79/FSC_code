

# cluster simulator 

## Sec 0. How to run this script

```
python2 main.py 2>&1 |tee /Users/dong/Desktop/05-24-Xiandong-Cluster-Simulator-test-allocation/log/log-test-allocation-1.txt
```


## Sec 1. 设计思想

### 0.

在 workloads 文件夹中，是cluster simulator 的输入数据。

### 1. 

在 FSC cluster simulator中，

1. 每个用户 有自己的 ownership ，运行时候按 ownership 内的数量（slot per type）为自己的所有 job 进行 FIFO (先进先出) policy 。如：用户  user_id = 0, {1: 10, 2: 0} 即 machine type = 1 的机器上有 10 个 slot 的ownership。 那么，在整个运行过程中，她的 jobs 所占用的 machine type = 1 的slot 的数量不能超过 10。 （future extension: she can get the idle slot if other user has no job currently）
2. 用户有 preference value. 代表了在不同  machine type 的速度快慢（task duration）.  我们默认 workloads folder 中 task-duration.json 里储存的都是 最短的 task duration 即 最喜爱的机器类型的 task duration。 
3. task_buffer 应该是 为每一个用户 设置一个 isolated task buffer
4. job_list (lists in list) 代表了 每个用户的 所有job ， i.e., [[jobs of user-1], [jobs of user-2], .....]


### 1.
Simulator submits jobs and stages to the scheduler
Scheduler submits tasks to the cluster

### 2. 
queue (priority queue in python3) — A synchronized queue class
The queue module implements multi-producer, multi-consumer queues. 

queue 中是一个一个的按时间顺序的 event。于是这个 simulator 变成了 一个 event-driven 的模拟器。

显而易见，event Type 包括 enum('JobSubmit', 'JobComplete', 'StageSubmit', 'StageComplete', 'TaskSubmit', 'TaskComplete')

### 3.
if isinstance(event, EventReAlloc):
- periodically trigger the allocation process every 1000 time units

### 4. 
scheduler.sort_tasks() # - this function is very important! It determines the scheduling algorithms!
task 的排名顺序决定了 空闲的 slot 给谁.
## Notes

### 1
 msg = self.scheduler.do_allocate(event.time)

 这个返回内容是什么?

 msg = [[event.task.stage.not_submitted_tasks[0],event.task.machine_id]]

### 4
我当前,总是没能充分利用 机器,应该查错这里

```python
    def do_allocate(self, time):
        self.sort_tasks() # - this function is very important! It determines the scheduling algorithms!
        msg=list() # - msg returns the allocation scheme
        if len(self.cluster.make_offers()) == 0 or len(self.task_buffer) == 0:
            # - if there is no idle slot or no pending tasks, skip allocation immediately
```

### 4
current_job_index = dict()  # map from user id to its current running job index
current_job_index[user_index] = 0
current_job_index[event.job.user_id] = event.job.index
我觉得这里不对,不应该是 替换关系.一个用户可以有多个 job 同时运行吧.

    def check_waiting(self) in scheduler.py 是不是可以用上.

### 4
  
```py  
  def do_allocate(self, time):
                # - allocate all the idle slots to pending tasks
```


### 问题0: （当前简单的把多个用户默认用相同的 job 相同的submission 简化，以后再修改）
对于 simulator.py  中读入数据
for user_index in range(0, user_number):
读入数据，只要一次。
（于是，现在 workload/job.json 里面的 User ID 是完全没有被利用（可以考虑日后删去））


### 问题1:（已尝试修改）
assign_task 应该是assign 到 core 

def assign_task(self, machineId, task, time):
看起来不对 ，因为 task 是应该 被assign 到 core 上。这里是不是因为 chen 默认了 每个 core per machine  = 1.
self.vacant_machine_list.remove(machineId)   （只是被占用一个 core 不应该被直接remove）
 如果machine 的所有 core 完全被占用，再从 vacant_machine_list中 remove 掉


### 问题2:

 task = Task(Job_id, Stage_id, Task_id, i, runtime, time_out, job_priority[job_id])
当前，runtime of each task 已经被确定。但是在 FSC 中，runtime 是和 用户preference value ，和 assign task 时候 machine-id 相关的。

对的，可以在 assign_task 之后， 用 task.runtime 进行修改？？


### job_execution_profile  当前只记录了 一个用户 的所有 job .需要修改为记录 所有用户的所有 job

 xiandong 修改为:  
首先声明。
 
```
self.profile = {}   # 第一句不再循环里.
self.profile[event.job.user_id] = {}
```
然后记录。
```py

self.profile[event.job.user_id][job_id] = {}
self.profile[event.job.user_id][job_id]["duration"] = event.job.duration
self.profile[event.job.user_id][job_id]["execution_time"] = event.job.execution_time
```