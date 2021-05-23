import MetaModule as mm
import CorrectWord
model = mm.meta_model_calc()
cw = CorrectWord.CorrectWord

class correctModel():
    def __init__(self, first_angle, second_angle, indirect_angle, correct_first_angle, correct_second_angle, correct_indirect_angle, threshold):
        self.first_angle = first_angle
        self.second_angle = second_angle
        self.indirect_angle = indirect_angle
        self.correct_first_angle = correct_first_angle
        self.correct_second_angle = correct_second_angle
        self.correct_indirect_angle = correct_indirect_angle
        self.threshold = threshold
        self.correction, self.position_correct = model.wrong_bond(self.first_angle, self.second_angle,
                                                                  self.indirect_angle,
                                                                  self.correct_first_angle, self.correct_second_angle,
                                                                  self.correct_indirect_angle,
                                                                  self.threshold)
    def rightArmBodyUpAndDown(self):

        if not self.correction:
            return cw.CORRECT, 0
        elif self.correction > 0:
            if self.position_correct == 1:
                return cw.LIFT_RIGHT_ARM, self.correction
            elif self.position_correct == 2:
                return cw.BODY_UP, self.correction
        else:
            if self.position_correct == 1:
                return cw.DOWN_RIGHT_ARM, abs(self.correction)
            elif self.position_correct == 2:
                return cw.BODY_DOWN, abs(self.correction)

    def leftArmBodyUpAndDown(self):

        if not self.correction:
            return cw.CORRECT, 0
        elif self.correction > 0:
            if self.position_correct == 1:
                return cw.LIFT_LEFT_ARM, self.correction
            elif self.position_correct == 2:
                return cw.BODY_UP, self.correction
        else:
            if self.position_correct == 1:
                return cw.DOWN_LEFT_ARM, abs(self.correction)
            elif self.position_correct == 2:
                return cw.BODY_DOWN, abs(self.correction)


    def rightLegbend(self):
        if not self.correction:
            return cw.CORRECT, 0
        elif self.correction > 0:

            return cw.BODY_UP, self.correction

        else:

            return cw.BODY_DOWN, abs(self.correction)





