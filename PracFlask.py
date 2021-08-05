from flask import *
import CalcRDC as CR
import MetaModule as mm
import correct as rb
import redis
import CorrectWord
import datetime
import random
import logging
from pathlib import Path

model = mm.meta_model_calc()
Pool = redis.ConnectionPool(
    host='node1.host.smallsaas.cn', port=6379, max_connections=10, decode_responses=True, password='root')
app = Flask(__name__)
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
        'joint_keys': ['right_shoulder_1_joint', 'right_forearm_joint', 'right_hand_joint'],
        'angle_keys': ['right_upper_arm', 'right_lower_arm', 'right_arm']
    },
    'left_arm': {
        'joint_keys': ['left_shoulder_1_joint', 'left_forearm_joint', 'left_hand_joint'],
        'angle_keys': ['left_upper_arm', 'left_lower_arm', 'left_arm']
    },
    'right_leg': {
        'joint_keys': ['right_upLeg_joint', 'right_leg_joint', 'right_foot_joint'],
        'angle_keys': ['right_upper_leg', 'right_lower_leg', 'right_leg']
    },
    'left_leg': {
        'joint_keys': ['left_upLeg_joint', 'left_leg_joint', 'left_foot_joint'],
        'angle_keys': ['left_upper_leg', 'left_lower_leg', 'left_leg']
    },
    'left_leg_body': {
        'joint_keys': ['left_shoulder_1_joint', 'left_upLeg_joint', 'left_foot_joint'],
        'angle_keys': ['left_body', 'left_upper_leg', 'left_leg_body']
    },
    'right_leg_body': {
        'joint_keys': ['right_shoulder_1_joint', 'right_upLeg_joint', 'right_foot_joint'],
        'angle_keys': ['right_body', 'right_upper_leg', 'right_leg_body']
    },
    'right_arm_body': {
        'joint_keys': ['right_forearm_joint', 'right_shoulder_1_joint', 'right_upLeg_joint'],
        'angle_keys': ['right_upper_arm', 'right_body', 'right_arm_body']
    },
    'left_arm_body': {
        'joint_keys': ['left_forearm_joint', 'left_shoulder_1_joint', 'left_upLeg_joint'],
        'angle_keys': ['left_upper_arm', 'left_body', 'left_arm_body']
    }
}
        
def init_logging_config():
    # 判断文件夹是否存在，不存在则创建
    Path('./logs').mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename='./logs/user_pose_data.log',
                        format='%(asctime)s - %(levelname)s -%(module)s:  %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S %p',
                        level=10)

# 用于从用户原始坐标数据生成对应的模型角度数据
def get_model_data_from_origin_joints(user_data_origin_joint):
    # 待返回的模型数据
    model_data = {}

    # 计算 各个 对应角度结果
    for key in main_angle_names:
        res = model.findAngle(
            user_data_origin_joint.get(
                model_data_k_v_map[key]['joint_keys'][0]),
            user_data_origin_joint.get(
                model_data_k_v_map[key]['joint_keys'][1]),
            user_data_origin_joint.get(
                model_data_k_v_map[key]['joint_keys'][2]))

        model_data[model_data_k_v_map[key]['angle_keys'][0]] = res[0]
        model_data[model_data_k_v_map[key]['angle_keys'][1]] = res[1]
        model_data[model_data_k_v_map[key]['angle_keys'][2]] = res[2]

    return model_data


# 将标准模型数据与用户模型数据根据阈值进行对比返回差异最大的角度
def get_max_diff_angle(standard_model_data, user_model_data, thresholds):
    res = {
        'name': '',
        # 角度差值 「用户角度值 - 标准角度值」
        'diff_angle': 0.0,
        # 角度最大差值「已取绝对值」
        'max_diff_angle': 0.0, 
        'horizontal_angle': 0.0, 
    }

    for key in main_angle_names:
        # 标准角度
        l = standard_model_data[key]
        # 用户角度
        r = user_model_data[key]
        diff_angle = r - l
        max_diff_angle = abs(diff_angle)
        # threshold = thresholds.get(key) or 0
        threshold = 10
        print('获取到', key, '的标准角度值：', l)
        print('获取到', key, '的用户角度值：', r)
        print('角度相差值为：', diff_angle)
        if max_diff_angle >= threshold and max_diff_angle > res['max_diff_angle']:
            # 生成水平夹角
            horizontal_angle_key = model_data_k_v_map[key]['angle_keys'][0]
            horizontal_angle = user_model_data[horizontal_angle_key] - \
                standard_model_data[horizontal_angle_key]
            # 刷新返回结果
            res = {
                'name': key,
                'diff_angle': diff_angle,
                'max_diff_angle': max_diff_angle, 
                'horizontal_angle': horizontal_angle, 
                'correct_word': get_correct_info(key, diff_angle),
                'user_angle': r,
                'standard_angle': l
            }
            
    return res

def get_correct_info(pose_name, diff_angle):
    # 如：用户水平角度为-30度，标准水平角度为0度，则水平差距为「用户水平角度 - 标准水平角度 = -30度」
    # 因此当水平差距角度 > 0 则为 True 表示需放下一些 而 < 0 则为False 表示需抬升
    direction = diff_angle > 0
    map = {
        # right_arm
        main_angle_names[0]: {
            True: 'RIGHT_ARM_NEGA',
            False: 'RIGHT_ARM_POSI'
        },
        # left_arm
        main_angle_names[1]: {
            True: 'LEFT_ARM_NEGA',
            False: 'RIGHT_ARM_POSI'
        },
        # right_leg
        main_angle_names[2]: {
            True: 'RIGHT_LEG_NEGA',
            False: 'RIGHT_LEG_POSI'
        },
        # left_leg
        main_angle_names[3]: {
            True: 'LEFT_LEG_NEGA',
            False: 'RIGHT_LEG_POSI'
        },
        # left_leg_body
        main_angle_names[4]: {
            True: 'LEFT_LEG_BODY_NEGA',
            False: 'LEFT_LEG_BODY_POSI'
        },
        # right_leg_body
        main_angle_names[5]: {
            True: 'RIGHT_LEG_BODY_NEGA',
            False: 'RIGHT_LEG_BODY_POSI'
        },
        # right_arm_body
        main_angle_names[6]: {
            True: 'RIGHT_ARM_BODY_NEGA',
            False: 'RIGHT_ARM_BODY_POSI'
        },
        # left_arm_body
        main_angle_names[7]: {
            True: 'LEFT_ARM_BODY_NEGA',
            False: 'LEFT_ARM_BODY_POSI'
        }
    }
    return map.get(pose_name, {True: None, False: None})[direction]


def Squat(user_pose_data):
    return None

def get_max_diff_angle_info(user_pose_data):
    # 用户ID
    user_id = user_pose_data.get('userid')
    # 姿势数据
    pose_data = user_pose_data.get('posedata')
    # 模型基础名称
    model_base_name = user_pose_data.get('posename')
    # 当前用户
    user_info = user_dict.get(user_id, {})

    if pose_data is None:
        return False

    # Redis连接对象
    r = redis.Redis(connection_pool=Pool)
    # 动作模型标准数据集合
    key_pose_standard_joints_arr = []
    # 动作模型数据角度阈值集合
    key_pose_joints_threshold_arr = []
    # 动作模型标准数据
    key_pose_standard_joints = {}
    # 动作模型数据角度阈值
    key_pose_joints_threshold = {}
    # 用户数据原始坐标集合
    user_data_origin_joint = {}

    # 模型基础名称对应缓存中的所有标准数据Key集合
    key_pose_standard_joints_keys = r.keys(model_base_name + '_*')
    key_pose_standard_joints_keys.sort()
    # 模型基础名称对应缓存中的所有角度阈值Key集合
    threshold_keys = r.keys('threshold_' + model_base_name + '_*')
    threshold_keys.sort()

    # 获取用户动作进度数据
    current_post_count = user_info.get('pose_idx', 0)

    try:
        # 拼接所有的标准动作模型数据
        for key in key_pose_standard_joints_keys:
            key_pose_standard_joints_arr.append(r.hgetall(key))
        # 拼接所有的阈值数据
        for key in threshold_keys:
            key_pose_joints_threshold_arr.append(r.hgetall(key))
        # 提取标准动作模型角度数据
        for key in all_model_data_keys:
            key_pose_standard_joints[key] = float(
                key_pose_standard_joints_arr[current_post_count][key] or 0)
        # 提取标准动作模型角度阈值
        # for key in threshold_map_name_keys:
        #     key_pose_joints_threshold[key] = float(
        #         key_pose_joints_threshold_arr[current_post_count][key] or 0)
        # 收集原始用户节点数据
        for key in pose_name_keys:
            user_data_origin_joint[key] = pose_data.get(key) or {
                'x': 0.0, 'y': 0.0}
    except():
        return False

    # 根据用户原始数据生成的模型数据
    model_data = get_model_data_from_origin_joints(user_data_origin_joint)

    # 差异最大角度 {'name': 'xxx', 'diff_angle': 78.281, 'correct_word': 'LEFT_ARM_POSI'}
    max_diff_angle_info = get_max_diff_angle(key_pose_standard_joints, model_data,
                                        key_pose_joints_threshold)

    return max_diff_angle_info

def test(user_pose_data):
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

    # 初始化日志基础配置
    init_logging_config()
    logging.info('当前用户:' + user_id + '， 计数为:' + str(count) +
                 '，起始时间为：' + user_dict[user_id]['start_time'])
    logging.info('获取到的用户数据为:' + str(user_pose_data))
    logging.info('返回数据为：' + str(res))
    return res

# 基础纠正方法
def correct(user_pose_data):
    global user_dict
    # 用户ID
    userid = user_pose_data.get("userid")
    # 动作基础名称
    posename = user_pose_data.get("posename")
    # 动作数量
    pose_nums = user_pose_data.get('keyposes', 0)
    # 阶段标志：START / END
    stage = user_pose_data.get('stage')
    # 用户初始信息
    init_user_info = {
            'pose_nums': pose_nums,
            'pose_idx': 0,
            'start_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'pose_base_name': posename
    }
    # 用户信息
    user_info = user_dict.get(userid, init_user_info)

    # 初始化用户信息
    if stage == 'START' or user_info is None:
        user_info = init_user_info

    logging.info('当前用户:' + userid + ', 起始时间为：' + user_info.get('start_time', None))
    logging.info('获取到的用户数据为:' + str(user_pose_data))

    # 获取当前动作计数
    pose_idx = user_info.get('pose_idx', 0)
    # 获取纠正角度信息
    correct_angle_info = get_max_diff_angle_info(user_pose_data)

    # 响应结果
    res = {
        "code": 200,
        "data": {
            "posename": posename,
            "userid": userid,
            "pose_frame": {
                # "pose_name": user_info.get('pose_base_name') + '_' + str(user_info.get('pose_idx')),
                "coach_complete": {
                    "total": user_info.get('pose_nums', 0),
                    "current": user_info.get('pose_idx', 0)
                }
            }
        }
    }

    # TODO data.pose_frame.duration -> 动作时间待处理
    # TODO data.correct -> 动作纠正
    # TODO data.pose_frame.video_playback -> 视频回放时间戳
    # TODO data.pose_frame.pose_name -> 模型名称

    if correct_angle_info != False:
        # 当前动作正确 保存用户状态
        if correct_angle_info is None:
            user_info['pose_idx'] = pose_idx + 1
            # 准备下一个动作
            res['correct'] = {
                'correct_pattern1': {
                    'correct_term': 'NEXT_POSE'
                }
            }
            # 最初动作 返回录制标志
            if pose_idx == 0:
                res['data']['indication'] = 'record'
        elif correct_angle_info.get('correct_word'):
            # 动作不匹配 生成纠正话术
            res['data']['correct'] = {
                'correct_pattern1': {
                    'correct_angle': correct_angle_info.get('standard_angle'),
                    'current_angle': correct_angle_info.get('user_angle'),
                    'correct_term': correct_angle_info.get('correct_word')
                }
            }

    # 最终动作 返回分数
    if stage == 'END' or user_info['pose_idx'] == user_info['pose_nums'] - 1:
        user_dict.pop(userid, None)
        total = user_info.get('pose_nums', 1)
        current = user_info.get('pose_idx', 0)
        # 根据进度生成分数
        score = int(current / total * 100 + random.randint(0, 9))
        res['data']['score'] = {
            'percentage': score
        }
    else:
        # 保存用户数据
        user_dict[userid] = user_info

    logging.info('返回数据为：' + str(res))

    return res

@app.route('/api/ai/correction', methods=['GET', 'POST'])
def Dispatch():
    # 初始化日志基础配置
    init_logging_config()
    if request.method == 'POST':
        user_pose_data = request.json
        print('获取到的用户数据为:' + str(user_pose_data))
        posename = user_pose_data.get('posename')
        if posename == 'test':
            return test(user_pose_data)
        else:
            return correct(user_pose_data)

if __name__ == '__main__':
    app.run(debug=True)