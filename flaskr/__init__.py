import os

from flask import *
import numpy as np
import time
import MetaModule as mm
import correct as rb
import json
from . import db

model = mm.meta_model_calc()

def query_db(query, args=(), one=False):
    cur = db.get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    db.init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/Squat', methods=['GET', 'POST'])
    def Squat():

        dir = 0
        repeat_times = 0
        pTime = time.time()
        cTime = 0
        duration = 0

        # if request.method == 'GET':
        #     arm_angle = int(request.args.get('arm_angle', ''))
        #     body_angle = int(request.args.get('body_angle', ''))
        #     arm_body_angle = int(request.args.get('arm_body_angle', ''))
        #     threshold = int(request.args.get('threshold', ''))
        #     angle_correct, position_correct = model.wrong_bond(arm_angle, body_angle, arm_body_angle,
        #                                                        correct_arm_angle, correct_body_angle,
        #                                                        correct_arm_body_angle,
        #                                                        threshold)

        if request.method == 'POST':
            user_pose_data = json.loads(request.json)
            userId = user_pose_data.get('userid')
            pose_data = user_pose_data.get(userId)
            pose_name = user_pose_data.get('posename')
            threshold = user_pose_data.get('threshold')

            # user pose data
            right_upLeg_joint = pose_data[0].get('location')
            right_forearm_joint = pose_data[1].get('location')
            left_leg_joint = pose_data[2].get('location')
            left_hand_joint = pose_data[3].get('location')
            left_ear_joint = pose_data[4].get('location')
            left_forearm_joint = pose_data[5].get('location')
            right_leg_joint = pose_data[6].get('location')
            right_foot_joint = pose_data[7].get('location')
            right_shoulder_1_joint = pose_data[8].get('location')
            neck_1_joint = pose_data[9].get('location')
            left_upLeg_joint = pose_data[10].get('location')
            left_foot_joint = pose_data[11].get('location')
            right_hand_joint = pose_data[12].get('location')
            left_eye_joint = pose_data[13].get('location')
            head_joint = pose_data[14].get('location')
            right_eye_joint = pose_data[15].get('location')
            right_ear_joint = pose_data[16].get('location')
            left_shoulder_1_joint = pose_data[17].get('location')


        else:
            return 'Error'

        # standard pose data present frame     import from database
        correct_right_arm_angle = 0
        correct_right_body_angle = 0
        correct_right_arm_body_angle = 0
        correct_right_upLeg_angle = 0
        correct_right_upLeg_body_angle = 0

        # standard pose data next frame
        next_right_upLeg_body_angle = 0

        # right arm and body up and down correct model
        right_arm_angle, right_body_angle, right_arm_body_angle = model.findAngle(right_forearm_joint,
                                                                                  right_shoulder_1_joint,
                                                                                  right_upLeg_joint)
        correct_pattern1 = rb.correctModel(right_arm_angle, right_body_angle, right_arm_body_angle,
                                           correct_right_arm_angle, correct_right_body_angle,
                                           correct_right_arm_body_angle,
                                           threshold).rightArmBodyUpAndDown()

        # right leg correct model
        right_upLeg_angle, right_body_angle, right_upLeg_body_angle = model.findAngle(right_shoulder_1_joint,
                                                                                      right_upLeg_joint,
                                                                                      right_leg_joint)
        correct_pattern2 = rb.correctModel(right_upLeg_angle, right_body_angle, right_upLeg_body_angle,
                                           correct_right_upLeg_angle, correct_right_body_angle,
                                           correct_right_upLeg_body_angle,
                                           threshold).rightLegbend()

        name = 0
        pass

        # 根据右腿判断计算 repeat_times duration completion
        right_leg_per = np.interp(right_upLeg_body_angle, (correct_right_upLeg_body_angle, next_right_upLeg_body_angle),
                                  (0, 100))
        if right_leg_per == 100:
            if dir == 0:
                repeat_times += 0.5
                dir = 1

                cTime = time.time()
                duration = cTime - pTime
                pTime = cTime

        if right_leg_per == 0:
            if dir == 1:
                repeat_times += 0.5
                dir = 0

                cTime = time.time()
                duration = cTime - pTime
                pTime = cTime

        completion = right_leg_per

        res_value = dict(
            pose_frame=dict(name=str(name), repeat_times=repeat_times, duration=duration, completion=completion),
            userid=userId,
            correct_pattern1=correct_pattern1,
            correct_pattern2=correct_pattern2)
        return res_value

        # if not angle_correct:
        #     return "you are correct, please do the next"
        # else:
        #     if position_correct == 1:
        #         return dict(wrong_part = 'right arm', deviation = str(angle_correct))
        #     elif position_correct == 2:
        #         return dict(wrong_part = 'body', deviation = str(angle_correct))
        # else:
        #     if position_correct == 1:
        #         return "please down right arm " + str(abs(angle_correct))
        #     elif position_correct == 2:
        #         return "body down " + str(abs(angle_correct))

    @app.route('/name', methods=['GET', 'POST'])
    def get_name():
        if request.method == 'POST':
            return 'zzc from POST'
        else:
            return 'zzc from GET'

    @app.route('/userProfile', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def get_profile():
        if request.method == 'GET':
            name = request.args.get('name', '')
            uid = request.args.get('uid', 7)
            fans = request.args.get('fans', '')
            print(name)
            print(fans)
            query = "SELECT *FROM userProfile"
            print(query)
            # 1. 获取数据库连接
            connection = db.get_db()
            cursor = connection.execute(query)
            result = cursor.fetchall()
            print(len(result))
            if result is None:
                return dict(message="not found")
            else:
                id = result[1]['id']
                username = result[1]['username']
                fans = result[1]['fans']
                return dict(id = id, fans = fans, username = username)
                cursor.close()
            # 2. 获取一个数据库的游标 cursor
            # 3. 写sql
            # 4. 执行sql
            # 5. 处理从数据库里读取的数据
            # 6. 将数据返回给调用者


            # if (name == 'zzc'):
            #     return dict(name='zzc', fans=1000)
            # else:
            #     return dict(name='bu shi zzc', fans=1000)
        elif request.method == 'POST':
            print(request.form)
            print(request.form.get('name'))
            print(request.form.get('fans'))
            print(request.data)
            print(request.json)
            # print(user['username']+1)
            return '1'

    return app