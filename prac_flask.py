from flask import *
import meta_module as mm
import requests

model = mm.meta_model_calc()
app = Flask(__name__)

@app.route('/rightarmbody', methods=['GET', 'POST'])
def correct():
    correct_arm_angle = 0
    correct_body_angle = 0
    correct_arm_body_angle = 0
    if request.method == 'GET':
        arm_angle = request.args.get('arm_angle', '')
        body_angle = request.args.get('body_angle', '')
        arm_body_angle = request.args.get('arm_body_angle', '')
        threshold = request.args.get('threshold', '')
        angle_correct, position_correct = model.wrong_bond(arm_angle, body_angle, arm_body_angle,
                                                           correct_arm_angle, correct_body_angle,
                                                           correct_arm_body_angle,
                                                           threshold)
    elif request.method == 'POST':
        user_pose_data = request.json
        angle_correct, position_correct = model.wrong_bond(user_pose_data['arm_angle'], user_pose_data['body_angle'], user_pose_data['arm_body_angle'],
                                                                 correct_arm_angle, correct_body_angle,
                                                                 correct_arm_body_angle,
                                                           user_pose_data['threshold'])
    else:
        return 'error'


    if not angle_correct:
        return "you are correct, please do the next"
    else:
        if position_correct == 1:
            return dict(wrong_part = 'right arm', deviation = str(angle_correct))
        elif position_correct == 2:
            return dict(wrong_part = 'body', deviation = str(angle_correct))
    # else:
    #     if position_correct == 1:
    #         return "please down right arm " + str(abs(angle_correct))
    #     elif position_correct == 2:
    #         return "body down " + str(abs(angle_correct))

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
        fans = request.args.get('fans', '')
        print(name)
        print(fans)
        if(name == 'zzc'):
            return dict(name = 'zzc', fans = 1000)
        else:
            return dict(name = 'bu shi zzc', fans = 1000)
    elif request.method == 'POST':
        print(request.form)
        print(request.data)
        user = request.json
        print(user['username']+1)
        return '1'

# with app.test_request_context():
    # print(url_for('index'))
    # print(url_for('login'))
    # print(url_for('login', next='/'))
    # print(url_for('profile', username='zhang san'))

if __name__ == '__main__':

    app.run()