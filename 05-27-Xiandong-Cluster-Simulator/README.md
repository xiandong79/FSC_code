

# cluster simulator 

## Sec 0. How to run this script

```
python2 main.py 2>&1 |tee /Users/dong/Desktop/05-24-Xiandong-Cluster-Simulator-test-allocation/log/log-test-allocation-1.txt
```


## Sec 1. 设计思想

#### 0.

在 workloads 文件夹中，是cluster simulator 的输入数据。

#### 1. 

在 FSC cluster simulator中，

1. 每个用户 有自己的 ownership ，运行时候按 ownership 内的数量（slot per type）为自己的所有 job 进行 FIFO (先进先出) policy 。如：用户  user_id = 0, {1: 10, 2: 0} 即 machine type = 1 的机器上有 10 个 slot 的ownership。 那么，在整个运行过程中，她的 jobs 所占用的 machine type = 1 的slot 的数量不能超过 10。 （future extension: she can get the idle slot if other user has no job currently）
2. 用户有 preference value. 代表了在不同  machine type 的速度快慢（task duration）.  我们默认 workloads folder 中 task-duration.json 里储存的都是 最短的 task duration 即 最喜爱的机器类型的 task duration。 
3. task_buffer 应该是 为每一个用户 设置一个 isolated task buffer
4. job_list (lists in list) 代表了 每个用户的 所有job ， i.e., [[jobs of user-1], [jobs of user-2], .....]


#### 3.
Simulator submits jobs and stages to the scheduler
Scheduler submits tasks to the cluster

#### 4. 
queue (priority queue in python3) — A synchronized queue class
The queue module implements multi-producer, multi-consumer queues. 

queue 中是一个一个的按时间顺序的 event。于是这个 simulator 变成了 一个 event-driven 的模拟器。

显而易见，event Type 包括 enum('JobSubmit', 'JobComplete', 'StageSubmit', 'StageComplete', 'TaskSubmit', 'TaskComplete')


#### 5
`msg = self.scheduler.do_allocate(event.time)`

 这个返回内容是
`msg = [[event.task.stage.not_submitted_tasks[0],event.task.machine_id]]`





#### 问题0: （当前简单的把多个用户默认用相同的 job 相同的submission 简化，以后再修改）

对于 simulator.py  中读入数据
`for user_index in range(0, user_number):`
读入数据，只要一次。（于是，现在 workload/job.json 里面的 User ID 是完全没有被利用（可以考虑日后删去））


#### 05-24日志assign_task 应该是assign 到 core 


`def assign_task(self, machineId, task, time):`
看起来不对 ，因为 task 是应该 被assign 到 core 上。这里是不是因为 chen 默认了 每个 `core per machine  = 1`.
`self.vacant_machine_list.remove(machineId)`  （只是被占用一个 core 不应该被直接remove）
 如果machine 的所有 core 完全被占用，再从 `vacant_machine_list` 中 **remove** 掉



### 05-25日志 job_execution_profile 的修改

 当前只记录了 一个用户 的所有 job .需要修改为记录 所有用户的所有 job

 xiandong 在simulator.py中 修改:  
首先为每一个用户声明 self.profile：
 
```py
self.profile = {}   # 第一句不再循环里.
self.profile[event.job.user_id] = {}
```
然后在循环过程中记录信息：

```py
self.profile[event.job.user_id][job_id] = {}
self.profile[event.job.user_id][job_id]["duration"] = event.job.duration
self.profile[event.job.user_id][job_id]["execution_time"] = event.job.execution_time
```
### 05-26日志 xiandong尝试修改 task runtime 

因为 task runtime 随 machine_id 不同而改变。修改的幅度是 user preference[user_id][machine_id]

在simulator.py中，修改每一个item[0].runtime （item[0] is a ‘task’ object）（EventTaskComplete总计出现3次)

```py
new_events.append(EventTaskComplete(event.time + item[0].runtime, item[0], item[1]))

item[0].runtime = item[0].runtime / self.cluster.users.preference_value[event.task.stage.job.user_id][event.task.machine_id]
```

可是， `self.cluster.users/  self.cluster.machines` is a ‘list’ object, I can not use its original ‘preference_value
’ attributes.

于是，我直接传入 `preference_value` in simulator.py （也有其他方案）

```py
item[0].runtime = item[0].runtime / self.preference_value[event.task.stage.job.user_id][event.task.machine_id]
```

测试一： 传入成功。
`print("------:", self.preference_value)`

测试二：(正确性未知)

可是在 `isinstance(event, EventStageSubmit):`
虽然出现了 EventTaskComplete 但是 'EventStageSubmit' object has no attribute 'task' . Xiandong 也就无从修改她的 item[0].runtime/task.runtime.
 
在 `isinstance(event, EventReAlloc):`中， EventTaskComplete出现但从未被调用.

测试发现，其调用只存在于`elif isinstance(event, EventTaskComplete):`

### 05-27 工作日志： 限制每个用户的不同机器的使用量


#### 步骤一：看能不能找到 用户（all jobs）总使用量

in cluster.py 尝试增加

```py
    def assign_task(self, machineId, task, time):
        self.users[task.stage.job.user_id].alloc += 1
        # add by xiandong

   def release_task(self, task):
        self.users[task.stage.job.user_id].alloc -= 1
        # add by xiandong
```

#### 步骤二： 用户（all jobs）对于不同类型的机器的使用量 （重点修改了 user.py）

```
        # self.alloc = 0.0  # current allocation
        self.alloc = defaultdict(int)
        self.ownership = ownership  
        self.total_ownership = 
```

于是, in cluster.py 继续修改为：

```py
    def assign_task(self, machineId, task, time):
        self.users[task.stage.job.user_id].alloc[machineId] += 1
        # add by xiandong

   def release_task(self, task):
        self.users[task.stage.job.user_id].alloc[running_machine_id
] -= 1
        # add by xiandong
```


#### 步骤三：限制 每个用户的不同机器的使用量

在 scheduler.py 

```py
def sort_tasks(self):
 x.job.alloc / x.job.targetAlloc
# 修改为
 self.task_buffer.sort(key=lambda x: sum( [v] for _, v in self.cluster.users[x.job.user_id].alloc.iteritems())
 / self.cluster.users[x.job.user_id].total_ownership) 



def do_allocate(self, time):
# 增加了一行
 if self.cluster.users[x.job.user_id].alloc[machineId] < self.cluster.users[x.job.user_id].ownership[machineId]:
# revised by xiandong
# 以判断，用户在此一类机器的上使用量 是否已经。超过用户的ownership。
```



### 遗留问题：

#### 4

```
current_job_index = dict()  # map from user id to its current running job index
current_job_index[user_index] = 0
current_job_index[event.job.user_id] = event.job.index
```
我觉得这里不对,不应该是 替换关系.一个用户可以有多个 job 同时运行吧.

`def check_waiting(self)` in scheduler.py 是不是可以用上.
 
#### 其他疑惑的地方

发现每次 提交job 都会 calculate_targetAlloc

```py
    def submit_job(self, job):
        self.cluster.running_jobs.append(job)
        self.cluster.calculate_targetAlloc()

    def calculate_targetAlloc(self):
```

这次 需要修改吗？