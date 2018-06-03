#!/usr/bin/env python
# a bar plot with errorbars
import numpy as np
import matplotlib.pyplot as plt

#------------------------------------------- Preparation Block -------------
N = 6
scale = 0.3
ind = np.arange(0, 1.1, 0.2)
fig, ax = plt.subplots()
fig.set_size_inches(6, 5)

#------------------------------------------- Data Block -------------
#KMeans
Initial_=[58,45,30,27,23,20]
Initial = [i/float(Initial_[-1]) for i in Initial_]
upper_error_=[3,3,2.500,5.500,3.500,1.300]  
upper_error0 = [i/float(Initial_[-1]) for i in upper_error_]
lower_error_=[1.7,3.600,2.000,5.000,3.000,1.500] 
lower_error0 = [i/float(Initial_[-1]) for i in lower_error_]

#SVM
Initial_=[88,51,47,43,32,21]
Initial = [i/float(Initial_[-1]) for i in Initial_]
upper_error_=[3,7,6,10,4,5]
upper_error0 = [i/float(Initial_[-1]) for i in upper_error_]
lower_error_=[3,4,4,5,7,1] 
lower_error0 = [i/float(Initial_[-1]) for i in lower_error_]


#PageRank
Initial_=[110,62,62,60,58,37];
Initial = [i/float(Initial_[-1]) for i in Initial_]
upper_error_=[1,1,8,2,5,1];   
upper_error0 = [i/float(Initial_[-1]) for i in upper_error_]
lower_error_=[1,1.3,2.7,1,4,1];  
lower_error0 = [i/float(Initial_[-1]) for i in lower_error_]

upper_error = [i for i in upper_error0]
lower_error = [i for i in lower_error0]
error=[lower_error, upper_error]
(rects,caps,_) = ax.errorbar(ind, Initial, yerr=error, color='0.1',linewidth=3, elinewidth=3, ecolor='b', capsize=5,label='PageRank')



#------------------------------------------- Draw Action Block -------------


for cap in caps:
	cap.set_markeredgewidth(3)
#------------------------------------------- Axis Data Block -------------

xlabels=np.arange(0,1.1,0.2)
xlabels_s = [str(i) for i in xlabels]
ylabels=np.arange(0.0,4.1,1.0)
ylabels_s = [str(i) for i in ylabels]

#------------------------------------------- Axis Setting Block -------------
font = {'family' : 'Times New Roman',
	'size': 24}
ticklabelfont = {'family' : 'Times New Roman',
	'size': 24}
labelfont = {'family' : 'Times New Roman',
	'size': 24}
font2 = {'family' : 'Times New Roman',
	'size': 26}
plt.rc('font', **font) 

ax.set_xlim(xlabels[0], xlabels[-1])
ax.set_xticks(xlabels)
ax.set_xticklabels(xlabels_s, **font)

ax.set_ylim([ylabels[0], ylabels[-1]])
ax.set_yticks(ylabels)
ax.set_yticklabels((ylabels_s), **ticklabelfont)

ax.set_xlabel(r'Service Isolation $P$', **labelfont)
ax.set_ylabel('Slowdown', **labelfont)

ax.grid()

ax.legend(prop={'family':'Times New Roman', 'size':24, 'weight':'normal'})
#ax.legend([rects], ('KMeans'), 'upper right', prop={'family':'Times New Roman', 'size':24, 'weight':'normal'})


def autolabel(rects):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
	print rect.get_x(), rect.get_width()
        ax.text(rect.get_x() + rect.get_width()/2.5, height*1.5,
                '%.1f' % float(height),
                ha='center', va='bottom', size=24)

#autolabel(rects1)
#autolabel(rects2)

plt.gcf().subplots_adjust(left=0.3)
plt.gcf().subplots_adjust(bottom=0.2)
#plt.show()
fig.savefig("foo.pdf")
