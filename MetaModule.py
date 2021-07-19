import math


class meta_model_calc():
    # def __init__(self,  first_direct_angle, second_direct_angle, indirect_angle,
    #                     correct_first_direct_angle, correct_second_direct_angle, correct_indirect_angle):
    #     self.first_direct_angle = first_direct_angle
    #     self.second_direct_angle = second_direct_angle
    #     self.indirect_angle = indirect_angle
    #     self.correct_first_direct_angle = correct_first_direct_angle
    #     self.correct_second_direct_angle = correct_second_direct_angle
    #     self.correct_indirect_angle = correct_indirect_angle

    def findAngle(self, firstPoint, secondPoint, thirdPoint):

        # Get the landmarks
        x1, y1 = firstPoint.get('x'), firstPoint.get('y')
        x2, y2 = secondPoint.get('x'), secondPoint.get('y')
        x3, y3 = thirdPoint.get('x'), thirdPoint.get('y')

        # Calculate the Angle
        first_angle = math.degrees(math.atan2(y1 - y2, x1 - x2))
        second_angle = math.degrees(math.atan2(y3 - y2, x3 - x2))
        angle = second_angle - first_angle
        if angle < 0:
            angle += 360
        if angle > 180:
            angle = 360 - angle
        # if first_angle < 0:
        #     first_angle += 180
        # if second_angle < 0:
        #     second_angle += 180
        return first_angle, second_angle, angle

    def wrong_bond(self,  first_direct_angle, second_direct_angle, indirect_angle,
                   correct_first_direct_angle, correct_second_direct_angle, correct_indirect_angle,
                   threshold):
        self.indirect_deviation = correct_indirect_angle - indirect_angle
        if abs(self.indirect_deviation) > threshold:
            self.first_bond_deviation = abs(
                first_direct_angle - correct_first_direct_angle)
            self.second_bond_deviation = abs(
                second_direct_angle - correct_second_direct_angle)
            if self.indirect_deviation > 0:
                if self.first_bond_deviation > self.second_bond_deviation:
                    return self.indirect_deviation, 1
                else:
                    return self.indirect_deviation, 2
            else:
                if self.first_bond_deviation > self.second_bond_deviation:
                    return self.indirect_deviation, 1
                else:
                    return self.indirect_deviation, 2

        else:
            return 0, None
