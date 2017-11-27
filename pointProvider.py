from os import path

class PointProvider:
    def __init__(self):
        # reads points from a file
        ownPath = path.dirname(__file__)
        inFileName = path.join(ownPath, "points.txt")
        self.points = []
        self.index = 0
        with open(inFileName, 'r') as f:
            for line in f:
                """Whitespace is stripped, if anything is left, this is mapped
                to float and appended to the list of points"""
                line = line.strip()
                if len(line):
                    coords = line.split()
                    try:
                        self.points.append(map(float, coords))
                    except ValueError:
                        print "Failed at parsing:", line, coords
                        raise
        self.__len__ = self.points.__len__
                    
                    
    def getPoint(self):
        toReturn = self.points[self.index % self.__len__()]
        self.index += 1
        return toReturn
        
if __name__ == "__main__":
    from os import getcwd
    print getcwd()
    pp = PointProvider()
    print 'n_points:', len(pp)
    for i in range(12):
        print pp.getPoint()