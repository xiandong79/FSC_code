# Experiment for  Multiple - TTC 

## Todo list

- ✅  Multiple - TTC 
	- ✅ subagent preference, subagnet ownership
	- ✅ algorithm 
   - ✅ Debug
  
- [ ] Large scale simulation (cluster-simulator file folder)
	- ✅ rewrite classes
	- [ ] algorithm 
	- [ ]  Debug
	- [ ] compare with "DS"
	- [ ] compare with "Choosy"
	
- [ ] plugin on Spark (implemention)(micro-benchmark) 
	- [ ] which framework ??
	- [ ] which scripts ??


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
