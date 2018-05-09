# Experiment for FSC

## Todo list
- ✅  generate input data
  - ✅ workload.csv from google trace 
  - ✅  sampled\_job_info.csv (input job) from  workload.csv 
  		- ✅  job id, job arrive time
  		- ✅  task numer , task durantion
  		- ✅  user id
  - ✅  preference_value.csv
  		- ✅ number of user
  		- ✅ number of machine
  - ✅  initial_ownership.csv
    	- ✅  number of user
  		- ✅  number of machine
  		- ✅  total number of machine
  		
- [ ] Multiple - TTC 
	- ✅ algorithm
  - ✅ subagent preference, subagnet ownership
  - [ ] Debug
  
- [ ] Large scale simulation (cluster-simulator file folder)
	- ✅ machine class
	- [ ] user class 
	- [ ] simulator class
	- [ ] compare with "DS"
	- [ ] compare with "Choosy"
	
- [ ] plugin on Spark (implemention)(micro-benchmark) 
	- [ ] which framework
	- [ ] which scripts


# Step-2: Multiple - TTC 

## Explination on algorithm 

Based on a exsiting python implementation for Top Trading Cycle algorithm which is used for matching in housing setting (download from Github). And traditional TTC  一个用户只能拥有一类机器且数量是一。我改进的地方是 ： 一个用户可以拥有多类机器，每类的数量是自然数。


During the FSC procedure, each agent is divided into several atomic subagents, each of which is assigned exactly one good from the original agents’ endowments. Then, the standard TTC procedure is applied to these atomic subagents.


standard TTC  （traditional TTC ） 的 算法是： Each person points to most preferred house and each house points to its owner. This creates a directed graph, with at least one cycle. Remove all cycles, assigning people to the house they are pointing at. Then, repeat using preference lists where the assigned houses have been deleted. 【traditional TTC.py 倒着看 还是比较明显的 如上面所说的 流程】

## trade example

```
def trade(transaction, cycle, G):

对于[Vertex(2), Vertex('e2'), Vertex(4), Vertex('a4')] 这个 graph G 中的 Cycle cycle ，我们已经确定 可以发生交易的数量是 transaction。

从cycle中，提取出参加交易的子用户 # ['e2', 'a4']
提取出参加交易的 house # [2, 4]

开始交易（修改边edge的数值）
    # (edge.source=2, edge.target=‘e2’, edge.capacity = edge.capacity - transaction)
    # (4, 'a4', capacity - transaction)
意思是：
 子用户 e2 的 house 2 所有权 减少了 transaction 的数量
子用户 a4 的 house 4 所有权 减少了 transaction 的数量


将上面的 子用户名字 修改   # ['e4’, 'a2’]
 将上面的 house 顺序 修改     # [4, 2]

    # 目的是：
    # ('e4', 4, capacity + transaction)
    # ('a2', 2, capacity + transaction)

需要这样修改的原因是 house 4 对于 e 用户，只能被 e4 子用户拥有，而不能被 作出贡献的 e2 拥有。
```

## ERRORs in code & Solution

### Error-1

```
File "/Users/dong/Dropbox/Soft-Constraints/Code_Experiment/multiple-TTC/Multiple-TTC.py", line 233, in topTradingCycles
    for source_target, capacity in G.edges.items():
RuntimeError: dictionary changed size during iteration
```

Solution:

1. https://stackoverflow.com/questions/11941817/how-to-avoid-runtimeerror-dictionary-changed-size-during-iteration-error
2. https://stackoverflow.com/questions/45830124/dictionary-changed-size-during-iteration-code-works-in-py2-not-in-py3

1. 使用 python2 就可以避免。

或者：

One resolution which will work on both python2.x and python3.x is to always create a snapshot using the list builtin:

```
for k, value in list(kwargs.items()):
    ...
Or, alternatively, create a snapshot by copying the dict:
for k, value in kwargs.copy().items():
    ...
```

### Error-2

```
  File "/Users/dong/Dropbox/Soft-Constraints/Code_Experiment/multiple-TTC/Multiple-TTC.py", line 240, in topTradingCycles
    if len(filter(lambda v: v in houses, G.vertices.keys())) == 0:
TypeError: object of type 'filter' has no len()
```

Solution:

https://stackoverflow.com/questions/19182188/how-to-find-the-length-of-a-filter-object-in-python

```
l = list(filter(lambda x: x > 3, n))

len(l)  # <--
```

Explination:

The docs for python 3 say it returns an iterator "Construct an iterator from those elements of iterable for which function returns true."
In python 2 it returned a list: see here. You will need to iterate the filter object to find its length.

Similar to `map`, `filter` function in Python3 returns a filter object or the `iterator` which gets **lazily evaluated**. Neither we can access the elements of the filter object with `index` nor we can use `len()` to find the length of the filter object.




# Step-1: generate input data `file`

## Explination on workload.csv

Fisrt, we get `workload.csv` which includes 1000 jobs from google-trace-2011,

jobArriveTimes |  jobSizes  | taskDuration (average)
------|  -------- | --------
16222820763 | 1 | 1973279538
16227244582 | 1 | 36237132
16227251260 |  1 | 26119096
16227262245 | 1 | 24164135
16232522117 | 1 | 44339347 
16239317672 |  8 |  13827807
16242676198 |  1 | 24031124

Second, from `workload.csv` we randnly sample `2000` jobs to `sampled_job_info` file by script `get_sampled_job_info_from_google_trace.py`

## Explination on sampled\_job\_info.csv

job_id   | user_id |  submitTime.|  Task Number  | runtime每task |  总的task数
----- | ----- | ------ | ----| ------- | ----
0	| 15	| 0	  | 8000	| 72519	| 8000
1	 | 2	| 48 |	20 |	177593	 | 8020
2	| 9	| 48 | 	30 | 	203153	| 8050



Third, using the `sampled_job_info` we generate the detailed infomation of input-jobs by script `transfer_sampled_job_to_json.py`. The output files are `job_info.json`, 	`stage_profile.json`, `runtime.json`


## Explination on preference_value.csv

generated by script  `generate_preference_value.py`

  - 1. random preference value
  - 2. normalize the largest one of each user (each row) to "1"

`generated_preference_value(num_user=20, num_machine=20)`


Reuslts:

```
[[1.  0.2 0.8 0.8 0.8 0.4 0.8 0.6 1.  0.2 0.2 1.  0.6 0.4 0.2 0.4 0.4 0.2 0.4 1. ]
 [0.8 0.2 0.8 0.2 0.6 0.8 0.2 0.4 0.8 0.8 0.8 0.2 0.4 0.4 0.4 0.2 0.6 1. 0.8 0.8]
 [0.6 1.  0.6 0.2 0.2 1.  0.2 1.  0.4 1.  0.4 0.6 0.6 0.2 0.4 0.4 0.4 0.4  0.8 0.8]
 [0.6 0.8 0.2 0.8 1.  0.4 0.6 1.  0.8 1.  1.  1.  0.8 1.  1.  1.  0.2 1.  0.8 0.6]
 [0.2 0.4 0.4 0.8 0.2 0.2 0.4 0.6 1.  0.6 0.2 0.8 0.6 0.6 0.2 0.4 0.2 0.6 0.6 0.8]
 [0.6 0.8 0.6 0.4 0.6 0.8 0.8 0.8 0.6 0.8 1.  0.4 0.6 0.8 0.4 0.6 0.4 1. 0.6 0.8]
 [0.2 0.8 0.6 0.8 0.2 0.2 0.2 0.8 0.6 0.8 0.2 1.  0.2 0.2 0.6 0.8 0.6 0.8  0.2 0.2]
 [0.2 0.8 0.2 0.6 0.6 0.2 1.  0.8 1.  0.2 1.  0.8 0.8 1.  0.4 0.8 0.2 0.2 0.2 0.4]
 [0.2 1.  0.4 0.8 0.4 0.2 0.2 1.  0.8 0.8 0.4 0.2 0.2 0.4 0.6 0.2 0.8 0.4 0.4 1. ]
 [0.2 0.2 0.8 0.6 0.8 0.6 1.  0.8 0.8 0.2 0.8 0.2 1.  0.6 0.8 1.  0.2 0.6 0.8 0.8]
 [0.4 0.8 1.  0.8 0.8 0.4 0.4 0.4 0.8 0.6 0.6 1.  0.8 0.4 0.6 0.8 0.4 1. 0.6 0.6]
 [0.2 0.4 0.2 1.  0.2 0.8 0.6 0.2 0.2 0.4 0.4 0.2 0.8 0.2 0.8 0.2 1.  1.  0.2 0.4]
 [0.8 1.  0.8 0.6 0.4 0.4 0.6 0.4 1.  0.6 1.  1.  0.6 0.8 0.8 0.4 0.6 1. 0.8 0.8]
 [0.4 0.4 0.4 0.4 0.6 0.2 0.8 0.4 1.  0.8 0.4 0.4 0.6 0.2 0.2 0.6 1.  0.2 1.  0.8]
 [0.8 0.2 0.2 0.8 0.8 0.2 0.8 0.2 0.6 0.4 0.2 1.  0.2 0.8 1.  1.  0.4 0.2  0.6 1. ]
 [1.  0.6 1.  0.8 0.6 0.8 0.2 0.2 0.2 0.8 1.  1.  0.6 0.6 1.  0.4 0.8 0.8 0.8 0.4]
 [0.6 0.6 0.8 0.6 0.8 1.  1.  0.6 0.4 0.6 0.2 0.8 0.2 0.6 1.  0.8 0.6 0.4  0.6 0.4]
 [1.  0.4 0.2 0.2 0.2 0.2 0.2 0.4 0.2 0.8 0.4 1.  0.4 0.6 1.  0.2 0.2 0.6 0.2 1. ]
 [1.  1.  0.4 0.4 1.  0.4 0.4 0.8 0.4 0.8 0.8 0.4 0.4 0.4 0.2 0.8 0.2 1. 0.4 1. ]
 [0.2 0.8 0.6 0.4 1.  1.  1.  0.2 0.2 0.6 0.2 0.8 0.8 1.  0.4 1.  0.8 0.8 0.8 1. ]]

```


## Explination on  initial_ownership.csv [可以改进]

generated by script  `generate_initial_ownership.py`

1. split total 1000 machines into 20 parts for 20 users
2. split the machines of each user into 20 parts for 20 types

`generate_initial_ownership(num_user=20, num_machine=20, total_machine=1000)`

Reuslts:

```
[[3. 1. 1. 2. 4. 1. 5. 1. 6. 2. 6. 3. 3. 0. 2. 1. 2. 2. 5. 3.]
 [3. 1. 4. 3. 2. 3. 1. 4. 6. 2. 4. 2. 5. 2. 2. 4. 1. 7. 7. 1.]
 [3. 2. 4. 6. 1. 3. 3. 3. 1. 6. 2. 4. 3. 1. 4. 2. 4. 2. 0. 3.]
 [3. 3. 2. 5. 3. 2. 2. 0. 2. 3. 1. 3. 2. 1. 2. 3. 3. 3. 3. 3.]
 [2. 2. 4. 1. 2. 4. 3. 2. 0. 4. 2. 6. 0. 2. 0. 1. 0. 3. 0. 2.]
 [2. 2. 0. 3. 2. 3. 4. 5. 3. 0. 1. 3. 1. 2. 0. 2. 0. 5. 5. 2.]
 [1. 4. 3. 0. 1. 3. 2. 1. 5. 2. 2. 2. 3. 1. 2. 1. 1. 5. 1. 3.]
 [2. 1. 1. 0. 2. 2. 3. 2. 1. 0. 1. 4. 3. 3. 5. 7. 1. 2. 3. 1.]
 [0. 4. 2. 2. 3. 4. 3. 4. 1. 3. 1. 5. 3. 1. 4. 2. 1. 1. 2. 2.]
 [0. 1. 2. 2. 2. 1. 3. 4. 1. 2. 1. 4. 2. 3. 1. 1. 3. 3. 2. 6.]
 [4. 4. 5. 1. 3. 3. 6. 2. 2. 1. 0. 6. 4. 4. 2. 3. 1. 4. 1. 7.]
 [5. 2. 6. 1. 5. 5. 3. 2. 4. 1. 3. 2. 0. 2. 1. 6. 1. 2. 1. 2.]
 [2. 1. 4. 1. 3. 1. 1. 5. 6. 5. 4. 3. 1. 0. 2. 1. 1. 1. 4. 6.]
 [0. 4. 1. 1. 1. 4. 2. 3. 3. 5. 4. 2. 1. 1. 3. 2. 4. 5. 3. 4.]
 [2. 2. 1. 4. 0. 4. 4. 4. 2. 2. 3. 2. 2. 1. 3. 1. 5. 1. 4. 5.]
 [1. 2. 5. 3. 0. 2. 2. 2. 3. 1. 1. 2. 5. 1. 4. 2. 2. 4. 2. 1.]
 [3. 2. 5. 3. 3. 2. 3. 3. 1. 1. 4. 5. 2. 2. 3. 2. 4. 1. 0. 2.]
 [4. 3. 0. 2. 1. 0. 2. 1. 4. 0. 5. 1. 1. 0. 1. 2. 5. 1. 1. 5.]
 [4. 2. 2. 1. 3. 0. 0. 2. 1. 2. 2. 2. 2. 0. 2. 6. 9. 7. 2. 1.]
 [1. 3. 3. 7. 0. 4. 2. 1. 3. 2. 3. 3. 2. 3. 2. 4. 2. 2. 2. 5.]]
```

 [可以改进]
 1. 图中 0 的数量的太少了。
 
## Others 

### design philosophy

1. each job only has one stage.

2. all task in each job have same task durantion.


3. In simulator, the above "task duration" is prepared for the best machine user each user. For cetain, if a machine has prederence value with 0.8, the task duration of this machine is ("task duration" / 0.8).



