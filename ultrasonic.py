import libultrasonic as lu

class Sensor(object):
    def __init__(self):
        self.sensors = [[8, 10], [12, 16], [18, 22], [24, 26]]
        for sensor in self.sensors:
            lu.setup(sensor[0], sensor[1])

    def poll(self):
        result = []
        for sensor in self.sensors:
            dist = lu.measure_distance(sensor[0], sensor[1])
            dist = dist / 100.0
            if dist > 2.0:
                dist = 2.0
            result.append(dist)
        return result
