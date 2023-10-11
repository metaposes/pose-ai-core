import MetaModule as mm
import redis
import CorrectWord
import datetime
import random

model = mm.meta_model_calc()
# Pool = redis.ConnectionPool(host='node1.host.smallsaas.cn', port=6379, max_connections=10, decode_responses=True, password='root')
Pool = redis.ConnectionPool(host='sports-redis', port=6379, max_connections=10, decode_responses=True, password='root')
cw = CorrectWord.CorrectWord
# 用户动作进度数据
global user_dict
user_dict = {}
# Redis中所有模型名称集合
all_model_data_keys = ['left_arm', 'left_lower_arm', 'left_upper_arm',
                       'left_arm_body', 'left_body', 'left_leg', 'left_lower_leg', 'left_upper_leg', 'left_leg_body', 'right_arm', 'right_lower_arm', 'right_upper_arm', 'right_arm_body', 'right_body', 'right_leg', 'right_lower_leg', 'right_upper_leg', 'right_leg_body']
# 阈值名称集合
threshold_map_name_keys = ['left_arm', 'left_arm_body',
                           'left_leg', 'left_leg_body', 'right_arm',  'right_arm_body',  'right_leg', 'right_leg_body']
# 部位名称集合
pose_name_keys = ['right_upLeg_joint',
                  'right_forearm_joint', 'left_leg_joint', 'left_hand_joint', 'left_ear_joint', 'left_forearm_joint', 'right_leg_joint', 'right_foot_joint', 'right_shoulder_1_joint', 'neck_1_joint', 'left_upLeg_joint', 'left_foot_joint', 'right_hand_joint', 'left_eye_joint', 'head_joint', 'right_eye_joint', 'right_ear_joint', 'left_shoulder_1_joint']
# 主要角度名称集合「8个」
main_angle_names = ['right_arm', 'left_arm', 'right_leg', 'left_leg',
                    'left_leg_body', 'right_leg_body', 'right_arm_body', 'left_arm_body']
# 映射集合
model_data_k_v_map = {
    'right_arm': {
        'swap': 'left_arm',
        'joint_keys': ['right_shoulder_1_joint', 'right_forearm_joint', 'right_hand_joint'],
        'angle_keys': ['right_upper_arm', 'right_lower_arm', 'right_arm']
    },
    'left_arm': {
        'swap': 'right_arm',
        'joint_keys': ['left_shoulder_1_joint', 'left_forearm_joint', 'left_hand_joint'],
        'angle_keys': ['left_upper_arm', 'left_lower_arm', 'left_arm']
    },
    'right_leg': {
        'swap': 'left_leg',
        'joint_keys': ['right_upLeg_joint', 'right_leg_joint', 'right_foot_joint'],
        'angle_keys': ['right_upper_leg', 'right_lower_leg', 'right_leg']
    },
    'left_leg': {
        'swap': 'right_leg',
        'joint_keys': ['left_upLeg_joint', 'left_leg_joint', 'left_foot_joint'],
        'angle_keys': ['left_upper_leg', 'left_lower_leg', 'left_leg']
    },
    'left_leg_body': {
        'swap': 'right_leg_body',
        'joint_keys': ['left_shoulder_1_joint', 'left_upLeg_joint', 'left_foot_joint'],
        'angle_keys': ['left_body', 'left_upper_leg', 'left_leg_body']
    },
    'right_leg_body': {
        'swap': 'left_leg_body',
        'joint_keys': ['right_shoulder_1_joint', 'right_upLeg_joint', 'right_foot_joint'],
        'angle_keys': ['right_body', 'right_upper_leg', 'right_leg_body']
    },
    'right_arm_body': {
        'swap': 'left_arm_body',
        'joint_keys': ['right_forearm_joint', 'right_shoulder_1_joint', 'right_upLeg_joint'],
        'angle_keys': ['right_upper_arm', 'right_body', 'right_arm_body']
    },
    'left_arm_body': {
        'swap': 'right_arm_body',
        'joint_keys': ['left_forearm_joint', 'left_shoulder_1_joint', 'left_upLeg_joint'],
        'angle_keys': ['left_upper_arm', 'left_body', 'left_arm_body']
    }
}

def test(user_pose_data, logging):
    global user_dict
    # 用户ID
    user_id = user_pose_data.get('userid')
    # 用户信息
    user_info = user_dict.get(user_id, {'count': 0})
    # stage
    stage = user_pose_data.get('stage')
    # 初始化标志
    init_flag = stage == 'START'
    # 计数器
    count = 0 if init_flag else user_info.get('count')

    print('接收到用户{', user_id, '}的请求，用户进度信息：', user_info)

    # 1请准备就绪 -> 2准备 -> 3伸展右手 -> 4下一个动作 -> 5垂放右手 -> 6完成 -> 7得分
    correct_word_map = {
        1: 'LET_POSE_READY',
        500: 'ACTION_PREPARE',
        1500: 'LIFT_RIGHT_ARM',
        2000: 'NEXT_POSE',
        2500: 'DOWN_RIGHT_ARM',
        3000: 'COMPLETE'
    }

    count += 1

    res = {
        'code': 200,
        'data': {
            'posename': 'test',
            'userid': user_id,
            'pose_frame': {
                'coach_complete': {
                    'total': 33,
                    'current': int(count / 100)
                },
                'frame_complete': random.uniform(0, 100),
                'repeat_times': {
                    'total': 3300,
                    'count': count
                }
            }
        }
    }

    if count == 400:
        res['data']['indication'] = 'record'

    if count == 100:
        res['data']['pose_frame']['video_playback'] = {
            'start_time': float(str(random.randint(0, 4)) + '.' + str(random.randint(0, 99))),
            'end_time': float(str(random.randint(5, 9)) + '.' + str(random.randint(0, 99)))
        }

    if correct_word_map.get(count):
        res['data']['correct'] = {
            'correct_pattern1': {
                'correct_term': correct_word_map[count],
                'current_angle': random.uniform(0, 180),
                'correct_angle': random.uniform(0, 180)
            }
        }
    elif count == 3300 or stage == 'END':
        res['data']['score'] = {
            'percentage': random.randint(80, 99)
        }
        res['start_time'] = user_info.get('start_time')
        res['end_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        count = 0

    # 初始化处理
    if user_dict.get(user_id) is None or init_flag:
        start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_dict[user_id] = {
            'start_time': start_time,
        }
        res['start_time'] = start_time

    # 储存用户进度信息
    user_dict[user_id]['count'] = count

    logging.info('当前用户:' + user_id + '， 计数为:' + str(count) +
                 '，起始时间为：' + user_dict[user_id]['start_time'])
    logging.info('获取到的用户数据为:' + str(user_pose_data))
    logging.info('返回数据为：' + str(res))
    return res