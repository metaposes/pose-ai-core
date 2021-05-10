from flask import *
import meta_module as mm
import requests

model = mm.meta_model_calc()
app = Flask(__name__)

@app.route('/rightarmbody/<int:arm_angle>/<int:body_angle>/<int:arm_body_angle>/<int:correct_arm_angle>/<int:correct_body_angle>/<int:correct_arm_body_angle>/<int:threshold>')
def correct(arm_angle, body_angle, arm_body_angle,
            correct_arm_angle, correct_body_angle, correct_arm_body_angle,
            threshold):
    angle_correct, position_correct = model.wrong_bond(arm_angle, body_angle, arm_body_angle,
                                                                 correct_arm_angle, correct_body_angle,
                                                                 correct_arm_body_angle,
                                                                 threshold)
    if not angle_correct:
        return "you are correct, please do the next"
    elif angle_correct > 0:
        if position_correct == 1:
            return "please lift right arm " + str(angle_correct)
        elif position_correct == 2:
            return "body up" + str(angle_correct)
    else:
        if position_correct == 1:
            return "please down right arm " + str(abs(angle_correct))
        elif position_correct == 2:
            return "body down " + str(abs(angle_correct))

@app.route('/name',methods=['GET', 'POST'])
def get_name():
    if request.method == 'POST':
        return 'zzc from POST'
    else:
        return 'zzc from GET'

@app.route('/userProfile', methods=['GET', 'POST'])
def get_profile():
    if request.method == 'GET':
        name = request.args.get('name', '')
        print(name)
        if(name == 'zzc'):
            return dict(name = 'zzc', fans = 1000)
        else:
            return dict(name = 'bu shi zzc', fans = 1000)
    elif request.method == 'POST':
        print(request.form)
        print(request.data)
        print(request.json)
        return '1'

# with app.test_request_context():
    # print(url_for('index'))
    # print(url_for('login'))
    # print(url_for('login', next='/'))
    # print(url_for('profile', username='zhang san'))

if __name__ == '__main__':

    app.run()