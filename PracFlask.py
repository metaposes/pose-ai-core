from flask import *
import CalcRDC as CR
import MetaModule as mm
import correct as rb
import redis
import etcd
import socket
import CorrectWord

model = mm.meta_model_calc()
Pool = redis.ConnectionPool(host='redis', port=6379, max_connections=10, decode_responses=True, password='root')
app = Flask(__name__)
user_dict = {}
cw = CorrectWord.CorrectWord

def register_etcd(service_name, port):
    client = etcd.Client(host='127.0.0.1', port=2379)

    host_name = socket.gethostname()
    node_name = '/services/ai/%s' % (service_name)
    print(client.get('/services/ai').value)
    client.write(node_name, '%s:%s' % (host_name, port), ttl=30)
    client.refresh(node_name, '%s:%s' % (host_name, port), ttl=60)
    return node_name


@app.route('/api/ai/correction/Squat', methods=['GET', 'POST'])
def Squat():

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
        user_pose_data = request.json
        userId = user_pose_data.get('userid')
        pose_data = user_pose_data.get(userId)
        # pose_name = user_pose_data.get('posename')
        current_user = user_dict.get(userId, None)


        # standard pose data first frame 根据 posename 取出
        # query = "SELECT *FROM squat"
        # print(query)
        # connection = db.get_db()
        r = redis.Redis(connection_pool=Pool)
        squat = []
        threshold = []

        frame_name = r.keys('squat*')
        frame_name.sort()

        threshold_name = r.keys('thresholdsquat*')
        threshold_name.sort()
        frame_number = len(frame_name)

        # import data from database
        if current_user is None:
            frame = 0
            user_record = CR.greed(frame_number)
        else:
            frame = current_user['frame_id']
            user_record = current_user['user_record']
        try:
            for i in frame_name:
                squat.append(r.hgetall(i))
            for i in threshold_name:
                threshold.append(r.hgetall(i))
            correct_right_arm_angle = int(squat[(frame + 1) % frame_number]['rightarmangle'])
            correct_right_body_angle = int(squat[(frame + 1) % frame_number]['rightbodyangle'])
            correct_right_arm_body_angle = int(squat[(frame + 1) % frame_number]['rightarmbodyangle'])
            correct_left_arm_angle = int(squat[(frame + 1) % frame_number]['leftarmangle'])
            correct_left_body_angle = int(squat[(frame + 1) % frame_number]['leftbodyangle'])
            correct_left_arm_body_angle = int(squat[(frame + 1) % frame_number]['leftarmbodyangle'])
            correct_right_upLeg_angle = int(squat[(frame + 1) % frame_number]['rightupLegangle'])
            correct_right_upLeg_body_angle = int(squat[frame % frame_number]['rightupLegbodyangle'])

            #threshold
            right_arm_body_threshold = int(threshold[(frame+1) % frame_number]['rightarmbody'])
            left_arm_body_threshold = int(threshold[(frame+1) % frame_number]['leftarmbody'])
            right_leg_threshold = int(threshold[(frame+1) % frame_number]['rightupLegbody'])




            # standard pose data next frame 根据下一个poseframe取出
            next_right_upLeg_body_angle = int(squat[(frame + 1) % frame_number]['rightupLegbodyangle'])

        except():
            return dict(success=False)


        #user pose data
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




    #right arm and body up and down correct model
    right_arm_angle, right_body_angle, right_arm_body_angle = model.findAngle(right_forearm_joint, right_shoulder_1_joint, right_upLeg_joint)
    correct_pattern1, angle1 = rb.correctModel(right_arm_angle, right_body_angle, right_arm_body_angle,
                                                 correct_right_arm_angle, correct_right_body_angle, correct_right_arm_body_angle,
                                               right_arm_body_threshold).rightArmBodyUpAndDown()
    if correct_pattern1 == cw.BODY_UP:
        correct_pattern1 = cw.CORRECT
        angle1 = 0

    # left arm and body up and down correct model
    left_arm_angle, left_body_angle, left_arm_body_angle = model.findAngle(left_forearm_joint,
                                                                           left_shoulder_1_joint, left_upLeg_joint)
    correct_pattern2, angle2 = rb.correctModel(left_arm_angle, left_body_angle, left_arm_body_angle,
                                               correct_left_arm_angle, correct_left_body_angle,
                                               correct_left_arm_body_angle,
                                               left_arm_body_threshold).leftArmBodyUpAndDown()
    if correct_pattern2 == cw.BODY_UP:
        correct_pattern2 = cw.CORRECT
        angle2 = 0

    #right leg correct model
    right_body_angle, right_upLeg_angle, right_upLeg_body_angle = model.findAngle(right_shoulder_1_joint, right_upLeg_joint, right_leg_joint)
    correct_pattern3, angle3 = rb.correctModel(right_upLeg_angle, right_body_angle, right_upLeg_body_angle,
                                       correct_right_upLeg_angle, correct_right_body_angle, next_right_upLeg_body_angle,
                                               right_leg_threshold).rightLegbend()





    #根据右腿判断计算 repeat_times duration completion
    user_record.calcRdc(right_upLeg_body_angle, correct_right_upLeg_body_angle, next_right_upLeg_body_angle)
    repeat_times = user_record.repeat_times
    duration = user_record.duration
    frame_complete = user_record.frame_complete
    coach_complete = user_record.coach_complete
    frame_id = user_record.frame



    res_value = dict(pose_frame=dict(name = str(frame_id), repeat_times = repeat_times, duration = duration, frame_complete = frame_complete,
                                     coach_complete = coach_complete),
                    userid = userId,
                    correct = dict(
                    correct_pattern1 = dict(correct_word = correct_pattern1.value, angle = angle1),
                    correct_pattern2 = dict(correct_word = correct_pattern2.value, angle = angle2),
                    correct_pattern3 = dict(correct_word = correct_pattern3.value, angle = angle3)))

    #保存用户状态
    user_dict[userId] = dict(frame_id = frame_id, frame_number = frame_number, user_record=user_record)

    return res_value

#register_etcd('squat', 5000)

if __name__ == '__main__':
    app.run()