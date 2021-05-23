
import numpy as np
import time

class greed():
    def __init__(self, frame_number):
        self.dir = 0
        self.repeat_times = 0
        self.pTime = 0
        self.cTime = 0
        self.duration = 0
        self.frame_number = frame_number
        self.per = 0
        self.frame = 0

    def calcRdc(self, current_angle, start_angle, end_angle):
        if start_angle > end_angle:
            start_angle, end_angle = end_angle, start_angle
            self.per = np.interp(current_angle, (start_angle, end_angle), (100, 0))
        elif start_angle < end_angle:
            self.per = np.interp(current_angle, (start_angle, end_angle), (0, 100))

        if self.per <= 15:
            if self.dir == 0:
                self.pTime = time.time()
                self.dir = 1

        if self.per >= 85:
            if self.dir == 1:
                self.frame += 1
                self.cTime = time.time()
                self.duration = self.cTime - self.pTime
                self.pTime = self.cTime
                self.dir = 0


        if self.frame == self.frame_number:
            self.repeat_times += 1
            self.frame = 0