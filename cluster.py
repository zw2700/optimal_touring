import sys
import OptimalTouring as Game
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import linear_sum_assignment
import time

## input, calculate efficiency & sort

x = Game.OptimalTouring("sample.txt") # may need to adjust this

addresses = []
time_value = []
days = []

sites = x.getSites().copy()
efficiencies = []
for i in range(len(sites)):
    site = sites[i]
    addresses.append(site[:2])
    time_value.append(site[2:4])
    days.append(site[4])

    efficiency = site[3]/site[2]
    efficiencies.append(efficiency)

addresses = np.array(addresses)
time_value = np.array(time_value)
days = np.array(days)
efficiencies = np.array(efficiencies)

order = np.flip(np.argsort(efficiencies))

## Value-Balanced K-Means Clustering Weighted by Efficiency Initialized at Most Efficient Places

k = x.getDay()
value_per_cluster = np.sum(time_value[:,1])/k

# clustering w/ value balancing
centroids = addresses[order[:k]].astype(float)
assignments = np.zeros(len(addresses),dtype=int)-1
converged = False # check convergence
count = 1 # count iterations
while not converged:
    converged = True
    value_acc = np.zeros(len(centroids))
    available_centroids = np.arange(len(centroids),dtype=int)
    # assignments
    for i in order:
        distances = np.zeros(len(centroids))+np.inf
        for j in available_centroids:
            distances[j] = np.linalg.norm(addresses[i]-centroids[j],ord=1)
        if assignments[i] != np.argmin(distances):
            converged = False
            assignments[i] = np.argmin(distances)
        value_acc[assignments[i]] += time_value[i][1]
        if value_acc[assignments[i]] > value_per_cluster:
            available_centroids = np.delete(available_centroids,np.argwhere(available_centroids==assignments[i]))
        
    # centroids shifting
    for j in range(len(centroids)):
        centroids[j] = np.average(addresses[assignments==j],weights=efficiencies[assignments==j],axis=0)
    count += 1

## Cluster-Day Assignment

cluster_orders = []
for i in range(k):
    cluster_orders.append(np.flip(np.argsort(efficiencies[assignments==i])))

# method to measure value of a day-cluster pair
def day_cluster_value(day,cluster):
    open_hours = days[assignments==cluster][cluster_orders[cluster]][:,day,:]
    time_needed = time_value[assignments==cluster][cluster_orders[cluster]][:,0]
    schedule = np.zeros(24)-1
    value = 0
    # print(open_hours,time_needed)
    
    # allocate places in cluster by iteratively checking, prioritize by efficiency
    for i in range(len(open_hours)):
        begin,end,time = open_hours[i,0]//60,open_hours[i,1]//60,time_needed[i]
        if (end-begin)*60>=time:
            leave = np.ceil(time/60).astype(int)
            # slide window to find available time slot
            while begin+leave<=end:
                if np.all(schedule[begin:begin+leave]==-1):
                    # print(i,begin,end,time,leave)
                    schedule[begin:begin+leave] = cluster_orders[cluster][i]
                    value += time_value[assignments==cluster][cluster_orders[cluster][i],1]
                    break
                begin += 1
    # print(schedule)
    return value

day_cluster_values = np.zeros((k,k))
for i in range(k):
    for j in range(k):
        day_cluster_values[i,j] = day_cluster_value(i,j) # day i, cluster j

# Hungarian Algorithm for Linear Sum Assignment Problem
_, day_cluster_assignment = linear_sum_assignment(day_cluster_values, maximize = True)
selected_elements = day_cluster_values[np.arange(k), day_cluster_assignment]
print(day_cluster_assignment, selected_elements, np.sum(selected_elements))

def cluster_for_day(day):
    return np.argwhere(assignments == day_cluster_assignment[day]).flatten()