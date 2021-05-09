import meta_module as mm

model = mm.meta_model_calc()

class right_arm_body_correct():
    def __init__(self, arm_angle, body_angle, arm_body_angle, correct_arm_angle, correct_body_angle, correct_arm_body_angle, threshold):
        self.arm_angle = arm_angle
        self.body_angle = body_angle
        self.arm_body_angle = arm_body_angle
        self.correct_arm_angle = correct_arm_angle
        self.correct_body_angle = correct_body_angle
        self.correct_arm_body_angle = correct_arm_body_angle
        self.threshold = threshold

    def correct(self):
        self.angle_correct, self.position_correct = model.wrong_bond(self.arm_angle, self.body_angle, self.arm_body_angle,
                                                                     self.correct_arm_angle, self.correct_body_angle, self.correct_arm_body_angle,
                            self.threshold)
        if not self.angle_correct:
            print("you are correct, please do the next")
            return
        elif self.angle_correct > 0:
            if self.position_correct == 1:
                print("please lift right arm" + str(self.angle_correct))
                return
            elif self.position_correct == 2:
                print("body up" + str(self.angle_correct))
                return
        else:
            if self.position_correct == 1:
                print("please right arm down" + str(abs(self.angle_correct)))
                return
            elif self.position_correct == 2:
                print("body down" + str(abs(self.angle_correct)))
                return



