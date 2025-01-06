from pandas import DataFrame

class DataPoint():
    def __init__(self, *,
                 time: float,
                 l_mean_size: float,
                 r_mean_size: float,
                 l_mean_speed: float,
                 r_mean_speed: float):
        self.time = time
        self.l_mean_size = l_mean_size
        self.r_mean_size = r_mean_size
        self.l_mean_speed = l_mean_speed
        self.r_mean_speed = r_mean_speed


class SimStats():
    def __init__(self):
        self.means = DataFrame({
            'time': [],
            'l_mean_size': [],
            'r_mean_size': [],
            'l_mean_speed': [],
            'r_mean_speed': []
        })
        
    def add_data(self, data: DataPoint):
        self.means.loc[len(self.means)] = [data.time,
                                           data.l_mean_size,
                                           data.r_mean_size,
                                           data.l_mean_speed,
                                           data.r_mean_speed]
    def times(self) -> list[float]:
        return list(self.means['time'])
    