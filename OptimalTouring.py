import time
import matplotlib.pyplot as plt


class OptimalTouring:
    def __init__(self, _siteFile):
        self.startTime = time.time()
        self.visitedSites = []
        self.time = 0
        self.day = 0
        self.revenue = 0
        self.current_site = -1
        self.passNight = 1
        self.unfinished = [[0 for i in range(200)] for j in range(10)]
        self.sites = self.readSites(_siteFile)

    # input will be provided by professor
    def readSites(self, fileName):
        ret = []
        for i in range(200):
            ret.append([])

        with open(fileName, "r") as f:
            lines = f.readlines()
        state = 0
        for line in lines:
            line = line[:-1]
            if "beginhour" in line:
                state = 2
                continue
            elif "desiredtime" in line:
                state = 1
                continue

            line = line.split(" ")
            if len(line)<4 or len(line[0])==0:
                continue
            if state == 1:
                ret[int(line[0]) - 1] = [
                    int(line[1]),
                    int(line[2]),
                    float(line[3]),
                    float(line[4]),
                    [[0, 0] for i in range(10)],
                ] # [avenue, street, desiredTime, value, [beginTime, endTime]]]
            elif state == 2:
                if ret[int(line[0]) - 1] == []:
                    raise Exception("Site " + str(line[0]) + " not exist")
                ret[int(line[0]) - 1][4][int(line[1]) - 1] = [
                    int(line[2]) * 60,
                    (int(line[3]) + 1) * 60,
                ]
                self.day = max(self.day, int(line[1]))

        while ret[-1] == []:
            ret = ret[:-1]

        return ret

    # move and stay should be 2 seperate move
    # siteId have priority to be read
    # visitTime in minutes
    # the free move only avaliable at midnight
    def sendMove(self, siteId=-1, visitTime=-1):
        # move to a new site
        if int(self.time / 1440) >= self.day:
            return 0
        while self.passNight:
            self.passNight -= 1
            self.visitedSites.append([])
        if 200 >= siteId > 0:
            if self.sites[siteId - 1] == []:
                raise Exception("Site Not Exist")
            if self.getTime() % 1440 != 0:
                old_day = int(self.time / 1440)
                self.time += abs(
                    self.sites[self.current_site - 1][1] - self.sites[siteId - 1][1]
                ) + abs(
                    self.sites[self.current_site - 1][0] - self.sites[siteId - 1][0]
                )
                if int(self.time / 1440) > old_day:
                    self.passNight = int(self.time / 1440) - old_day
            self.visitedSites[-1].append(siteId)
            self.current_site = siteId

        elif visitTime > 0:
            if self.current_site <= 0:
                return 0
            old_day = int(self.time / 1440)
            # if it goes into next day, split it
            if 1440 - (self.time % 1440) < visitTime:
                x = 1440 - (self.time % 1440)
                self.sendMove(visitTime=x)
                self.sendMove(visitTime=visitTime - x)
                return
            site = self.sites[self.current_site - 1]
            # possible to finish visit
            if site[2] <= visitTime:
                # come at open hour
                if (
                    site[4][int(self.time / 1440)][0]
                    <= self.time % 1440
                    <= site[4][int(self.time / 1440)][1]
                ):
                    # finish visit
                    if (
                        self.unfinished[int(self.time / 1440)][self.current_site - 1]
                        + site[4][int(self.time / 1440)][1]
                        - self.time % 1440
                        >= site[2]
                    ):
                        self.revenue += site[3]
                        site[3] = 0
                # come early
                elif self.time % 1440 <= site[4][int(self.time / 1440)][0]:
                    # finish visit
                    if (
                        self.time % 1440 + visitTime - site[4][int(self.time / 1440)][0]
                        >= site[2]
                    ):
                        self.revenue += site[3]
                        site[3] = 0
                    else:
                        self.unfinished[int(self.time / 1440)][
                            self.current_site - 1
                        ] += max(
                            0,
                            self.time % 1440
                            + visitTime
                            - site[4][int(self.time / 1440)][0],
                        )
            else:
                if (
                    site[4][int(self.time / 1440)][0]
                    <= self.time % 1440
                    <= site[4][int(self.time / 1440)][1]
                ):
                    self.unfinished[int(self.time / 1440)][
                        self.current_site - 1
                    ] += min(
                        visitTime, site[4][int(self.time / 1440)][1] - self.time % 1440
                    )
                    if (
                        self.unfinished[int(self.time / 1440)][self.current_site - 1]
                        >= site[2]
                    ):
                        self.revenue += site[3]
                        site[3] = 0
                elif self.time % 1440 <= site[4][int(self.time / 1440)][0]:
                    self.unfinished[int(self.time / 1440)][
                        self.current_site - 1
                    ] += max(
                        0,
                        self.time % 1440
                        + visitTime
                        - site[4][int(self.time / 1440)][0],
                    )
            self.time += visitTime
            if int(self.time / 1440) > old_day:
                self.passNight = int(self.time / 1440) - old_day
        else:
            return 0
        return 1

    # end the game
    def settlement(self):
        print("It takes " + str(time.time() - self.startTime) + " seconds for running.")
        for i in range(len(self.visitedSites)):
            print("Day " + str(i) + ":", end="")
            today_trip = self.visitedSites[i]
            for j in range(len(today_trip)):
                if j == i == 0:
                    print(" " + str(today_trip[j]), end="")
                else:
                    print(" => " + str(today_trip[j]), end="")
            print()
        print("Total revenue is: " + str(int(self.revenue * 1000) / 1000))

    def getRevenue(self):
        return int(self.revenue * 1000) / 1000

    def getSites(self):
        return self.sites

    def getTime(self):
        return self.time

    def getLocation(self):
        return self.current_site

    def getMaxSitesNo(self):
        return len(self.sites)

    def vizLayout(self):
        # TODO: this will be done
        pass

    # max day
    def getDay(self):
        return self.day

    def getState(self):
        return self.getRevenue(), self.getDay(), self.getTime(), self.getSites()


if __name__ == "__main__":
    # example usage
    x = OptimalTouring("sites.txt")
    print(x.getMaxSitesNo())
    # x = OptimalTouring("small_map_sites.txt", "example_strategy.txt")
    print("Welcome to the Optimal Touring Game.")
    print("You can:")
    print("1. getState")
    print("2. move [[siteId]]")
    print("3. stay [[time_in_minutes]]")
    print("4. print this again")
    print("5. end the game")
    while 1:
        y = input("what you want to do now:")
        y = y.replace("\n", "")
        if "getState" in y:
            t = x.getTime()
            print("Current site: ", x.current_site)
            print(
                "Time: "
                + "Day"
                + str(int(t / 1440))
                + " "
                + str(int((t % 1440) / 60))
                + ":"
                + str(t % 60)
            )
            print("Max day: " + str(x.getDay()))
            print("Current Revenue: " + str(x.getRevenue()))
            print("Sites:")
            sites = x.getSites()
            for i in range(len(sites)):
                if sites[i] == []:
                    continue
                print(str(i) + ":" + str(sites[i]))
        elif "move" in y:
            z = x.sendMove(siteId=int(y.split(" ")[1]))
            if z:
                print("go to " + str(x.current_site))
            else:
                print("Invalid Action")
                print(z)
        elif "stay" in y:
            if x.sendMove(visitTime=int(y.split(" ")[1])):
                print("stay for " + y.split(" ")[1] + " minutes")
            elif int(y.split(" ")[1]) > 1440:
                print("exceed one day. But still stayed")
            else:
                print("Invalid Action")
        elif "again" in y:
            print("Welcome to the Optimal Touring Game.")
            print("You can:")
            print("1. getState")
            print("2. move siteId")
            print("3. stay time_in_minutes")
            print("4. print this again")
            print("5. show the map")
            print("6. end the game")
        elif "end" in y:
            x.settlement()
            exit(0)
        else:
            print("invalid order")
