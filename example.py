import OptimalTouring as Game
import numpy as np

x = Game.OptimalTouring("test.txt")

# read data
addresses = []
time_value = []
days = []

sites = x.getSites().copy()
for i in range(len(sites)):
    site = sites[i]
    addresses.append(site[:2])
    time_value.append(site[2:4])
    days.append(site[4])

addresses = np.array(addresses)
time_value = np.array(time_value)
days = np.array(days)

def convert_action(paths):
    for day in range(1,len(paths)):
        for i in range(len(paths[day])):
            # print(day,i)
            site = paths[day][i]

            x.sendMove(siteId=site)
            print(x.getLocation(), x.getTime())
            if i + 1 >= len(paths[day]):
                leave = day*1440
            else:
                leave = max(x.getTime(),(day-1)*1440+days[site-1][day-1][0]) + time_value[site-1][0]
            x.sendMove(visitTime=leave-x.getTime())
            print(x.getLocation(), x.getTime(),x.getRevenue())
    x.settlement()

paths_2 = [[], [12, 84, 170, 136, 79, 195], [128, 174, 109, 60, 61], [75, 23, 34, 178, 88, 154, 120], [141, 21, 49, 90, 118, 132, 138], [116, 93, 182, 15, 78], [59, 148, 140, 125, 191], [32, 146, 103, 46, 107, 113], [100, 143, 7, 172], [47, 192, 119, 27, 156, 155, 200], [13, 35, 43, 65]]
# paths = [[], [79, 84, 136, 170, 195], [109, 174, 151, 128, 61], [75, 178, 34, 65, 88], [21, 141, 49, 40, 90, 132], [116, 15, 182, 93], [59, 114, 148, 140], [146, 103, 76, 32, 113], [100, 143, 172], [119, 192, 47, 31, 27, 156], [78, 120, 154, 13, 35]]
convert_action(paths_2)

# i = 1
# while x.getTime() < x.getDay()*1440:
#     x.sendMove(siteId=i)
#     print(x.getLocation(), x.getTime())
#     x.sendMove(visitTime=1439)
#     print(x.getLocation(), x.getTime(),x.getRevenue())
#     i+=1
# x.settlement()
