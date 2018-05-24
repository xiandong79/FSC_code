

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


