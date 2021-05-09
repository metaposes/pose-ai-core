

class meta_model_calc():
    # def __init__(self,  first_direct_angle, second_direct_angle, indirect_angle,
    #                     correct_first_direct_angle, correct_second_direct_angle, correct_indirect_angle):
    #     self.first_direct_angle = first_direct_angle
    #     self.second_direct_angle = second_direct_angle
    #     self.indirect_angle = indirect_angle
    #     self.correct_first_direct_angle = correct_first_direct_angle
    #     self.correct_second_direct_angle = correct_second_direct_angle
    #     self.correct_indirect_angle = correct_indirect_angle

    def wrong_bond(self,  first_direct_angle, second_direct_angle, indirect_angle,
                         correct_first_direct_angle, correct_second_direct_angle, correct_indirect_angle,
                            threshold):
        self.indirect_deviation = correct_indirect_angle - indirect_angle
        if abs(self.indirect_deviation) > threshold:
            self.first_bond_deviation = abs(first_direct_angle - correct_first_direct_angle)
            self.second_bond_deviation = abs(second_direct_angle - correct_second_direct_angle)
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