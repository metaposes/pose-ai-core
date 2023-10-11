import MetaModule as mm
import redis
import CorrectWord
import time
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

# 用于从用户原始坐标数据生成对应的模型角度数据
def get_model_data_from_origin_joints(user_data_origin_joint, camera):
    # 待返回的模型数据
    model_data = {}

    # 计算 各个 对应角度结果
    for key in main_angle_names:
        swap_key = model_data_k_v_map[key]['swap'] if camera == 1 else key
        res = model.findAngle(
            user_data_origin_joint.get(
                model_data_k_v_map[key]['joint_keys'][0]),
            user_data_origin_joint.get(
                model_data_k_v_map[key]['joint_keys'][1]),
            user_data_origin_joint.get(
                model_data_k_v_map[key]['joint_keys'][2]))
 

        model_data[model_data_k_v_map[swap_key]['angle_keys'][0]] = res[0]
        model_data[model_data_k_v_map[swap_key]['angle_keys'][1]] = res[1]
        model_data[model_data_k_v_map[swap_key]['angle_keys'][2]] = res[2]

    return model_data

# 将标准模型数据与用户模型数据根据阈值进行对比返回差异最大的角度
def get_max_diff_angle(user_data_origin_joint, standard_model_data, user_model_data, thresholds):
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
        threshold = thresholds.get(key) or 90

        print(model_data_k_v_map[key]['joint_keys'][0], ':', user_data_origin_joint[model_data_k_v_map[key]['joint_keys'][0]])
        print(model_data_k_v_map[key]['joint_keys'][1], ':', user_data_origin_joint[model_data_k_v_map[key]['joint_keys'][1]])
        print(model_data_k_v_map[key]['joint_keys'][2], ':', user_data_origin_joint[model_data_k_v_map[key]['joint_keys'][2]])
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
            
    return res if res['diff_angle'] != 0.0 else True

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


def get_max_diff_angle_info(user_pose_data):
    # 用户ID
    user_id = user_pose_data.get('userid')
    # 姿势数据
    pose_data = user_pose_data.get('posedata')
    # 模型基础名称
    model_base_name = user_pose_data.get('posename')
    camera = user_pose_data.get('camera', 1)

    # 当前用户
    user_info = user_dict.get(user_id, {})

    if pose_data is None:
        return False

    # Redis连接对象
    r = redis.Redis(connection_pool=Pool)
    # 动作模型标准数据
    key_pose_standard_joints = {}
    # 动作模型数据角度阈值
    key_pose_joints_threshold = {}
    # 用户数据原始坐标集合
    user_data_origin_joint = {}

    # 获取用户动作进度数据
    pose_idx = user_info.get('pose_idx', 0)
    pose_info_key = model_base_name + '_' + str(pose_idx)
    threshold_key = 'threshold_' + model_base_name + '_' + str(pose_idx)
    try:
        # 拼接标准动作模型数据
        for key,value in r.hgetall(pose_info_key).items():
            if key in all_model_data_keys:
                key_pose_standard_joints[key] = float(value)

        # 拼接阈值数据
        for key,value in r.hgetall(threshold_key).items():
            key_pose_joints_threshold[key] = float(value)

        # 收集原始用户节点数据
        for key in pose_name_keys:
            user_data_origin_joint[key] = pose_data.get(key) or {
                'x': 0.0, 'y': 0.0}
    except():
        return False

    # 根据用户原始数据生成的模型数据
    model_data = get_model_data_from_origin_joints(user_data_origin_joint, camera)

    # 差异最大角度 {'name': 'xxx', 'diff_angle': 78.281, 'correct_word': 'LEFT_ARM_POSI'}
    max_diff_angle_info = get_max_diff_angle(user_data_origin_joint, key_pose_standard_joints, model_data,
                                        key_pose_joints_threshold)

    return max_diff_angle_info

def ensure_required_parameter(user_pose_data):
    res = {
        'status': True
    }
    if user_pose_data is None:
        res['correct_term'] = 'MISSING_MAIN_BODY'
    elif user_pose_data.get('userid') is None:
        res['correct_term'] = 'MISSING_USER_ID'
    elif user_pose_data.get('posename') is None:
        res['correct_term'] = 'MISSING_POSE_NAME'

    if user_pose_data is not None and res.get('correct_term') is None:
        stage = user_pose_data.get('stage')
        if stage == 'START':
            if user_pose_data.get('keyposes') is None:
                res['correct_term'] = 'MISSING_KEY_POSE_NUM'
        elif stage != 'END':
            if user_pose_data.get('event') is None and user_pose_data.get('posedata') is None:
                res['correct_term'] = 'MISSING_POSEDATA'

    if res.get('correct_term'):
        res['status'] = False
    return res

def ensure_can_continue_correct(user_info):
    current_time = int(time.time())
    last_match_time = user_info.get('last_match_time', 0)
    duration = user_info.get('duration', 0)
    if user_info.get('event_flag', True) is False:
        event_flag_time = user_info.get('event_flag_time', 0)
        if current_time - event_flag_time > 6:
            user_info['event_flag'] = True
            user_info.pop('event_flag_time', None)
        else:  
            user_info['last_match_time'] = current_time
            return duration
    if duration != 0:
        diff = int(current_time - last_match_time)
        if diff < duration:
            return duration - diff
    return True

def init_user_info(pose_nums, pose_base_name):
    return {
        'pose_nums': pose_nums,
        'pose_idx': 0,
        'correct_count': 0,
        'start_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'start_timestamp': int(time.time()),
        'pose_base_name': pose_base_name,
        'joint_all_in': False
    }

def get_joint_count_from_user_pose_data(user_pose_data):
    pose_data = user_pose_data.get('posedata', {})
    count = 0
    # 收集原始用户节点数据
    for key in pose_name_keys:
        o = pose_data.get(key)
        if o and o.get('x', 0) != 0 and o.get('y', 0) != 0:
            count += 1
    return count

# 基础纠正方法
def correct(user_pose_data, logging):
    global user_dict

    # 确保关键参数存在
    verify_info = ensure_required_parameter(user_pose_data)

    if verify_info.get('status', False) is not True:
        return {'code': 200, 'data': {
            'correct': {
                'correct_pattern2': {
                    'correct_term': verify_info.get('correct_term')
                }
            }
        }}

    # 用户ID
    userid = user_pose_data.get("userid")
    # 动作基础名称
    pose_base_name = user_pose_data.get("posename")
    # 动作数量
    pose_nums = user_pose_data.get('keyposes', 0)
    # 阶段标志：START / END
    stage = user_pose_data.get('stage')
    # 事件
    event = user_pose_data.get('event')
    # 用户信息
    user_info = user_dict.get(userid, init_user_info(pose_nums, pose_base_name))

    # 初始化用户信息
    if stage == 'START' or user_info is None:
        user_info = init_user_info(pose_nums, pose_base_name)

    logging.info('当前用户:' + userid + ', 起始时间为：' + user_info.get('start_time', None))
    logging.info('获取到的用户数据为:' + str(user_pose_data))

    # 获取当前动作计数
    pose_idx = user_info.get('pose_idx', 0)
    # 正确动作数量
    correct_count = user_info.get('correct_count', 0)
    # Redis连接对象
    r = redis.Redis(connection_pool=Pool)
    # 动作信息
    pose_info = r.hgetall(pose_base_name + '_' + str(pose_idx))
    # 上一个动作信息
    last_pose_info = r.hgetall(pose_base_name + '_' + str(pose_idx - 1)) if pose_idx - 1 >= 0 else {'start_time': 0}
    # 动作描述
    action = pose_info.get('action', '').replace("\"", "")
    # 持续时间
    duration = int(pose_info.get('duration', 0))
    # 重复次数
    repeat_times = pose_info.get('repeat_times')
    # 开始时间
    video_start_time = float(last_pose_info.get('start_time', 0))
    # 结束时间
    video_end_time = float(pose_info.get('start_time', 0))

    video_start_time = video_end_time - 5 if (video_end_time - video_start_time) > 5 else video_start_time

    if event is not None:
        user_info['event_flag'] = True



    # 响应结果
    res = {
        "code": 200,
        "data": {
            "posename": pose_base_name,
            "userid": userid,
            "pose_frame": {
                "pose_name": action,
                "coach_complete": {
                    "total": user_info.get('pose_nums', 0),
                    "current": user_info.get('pose_idx', 0)
                }
            }
        }
    }


    verify_info = ensure_can_continue_correct(user_info)

    if user_info['joint_all_in'] is False:
        now_time = int(time.time())
        if now_time - user_info['start_timestamp'] > 5 or get_joint_count_from_user_pose_data(user_pose_data) == 18:
            user_info['joint_all_in'] = True
            user_info['duration'] = 5
            user_info['last_match_time'] = int(time.time())
            res['data']['correct'] = {
                'correct_pattern3': {
                    'correct_term': 'PREPARE_THREE_SECONDS'
                }
            }
        verify_info = False

    correct_angle_info = False
    if verify_info is True and correct_count != pose_nums:
        # 获取纠正角度信息
        correct_angle_info = get_max_diff_angle_info(user_pose_data)



    # TODO data.correct -> 动作纠正

    if correct_angle_info != False:
        # 当前动作正确 保存用户状态
        if correct_angle_info is True:
            user_info['pose_idx'] = pose_idx + 1
            user_info['correct_count'] = user_info.get('correct_count', 0) + 1
            user_info['duration'] = duration
            user_info['last_match_time'] = int(time.time())
            user_info['event_flag'] = False
            user_info['event_flag_time'] = int(time.time())
            verify_info = duration
            # 准备下一个动作
            res['data']['correct'] = {
                'correct_pattern3': {
                    'correct_term': 'NEXT_POSE' if duration <= 1 else 'WAIT_NEXT_POSE',
                    'param1': str(duration),
                    'param2': str(duration)
                }
            }
            res['data']['pose_frame']['coach_complete']['current'] = user_info['pose_idx']
            res['data']['pose_frame']['video_playback'] = {
                'start_time': video_start_time,
                'end_time': video_end_time
            }
            res['data']['pose_frame']['duration'] = {
                "total": duration
            }
            # 最初动作 返回录制标志
            if user_info['pose_idx'] == 1:
                res['data']['indication'] = 'record'
            # 最后动作 返回结束话术
            if user_info['correct_count'] == pose_nums and duration != 0:
                res['data']['correct']['correct_pattern3']['correct_term'] = 'WAITING_FOR_SCORE'
        elif correct_angle_info.get('user_angle', 0) != 0:
            # 动作不匹配 生成纠正话术
            res['data']['correct'] = {
                'correct_pattern1': {
                    'correct_angle': correct_angle_info.get('standard_angle'),
                    'current_angle': correct_angle_info.get('user_angle'),
                    'correct_term': correct_angle_info.get('correct_word')
                }
            }

    # 初始化
    if stage == 'START':
        res['data']['stage'] = 'STARTED'
    # 最终动作 返回分数
    elif verify_info is True and (stage == 'END' or user_info['correct_count'] == user_info['pose_nums']):
        total = user_info.get('pose_nums', 1)
        current = user_info.get('correct_count', 0)
        mins_time_consuming = (user_info.get('start_timestamp', int(time.time())) - int(time.time())) / 60
        mins_time_consuming = 1 if mins_time_consuming <= 0 else mins_time_consuming
        kcol = 7.8 * 50 / 60 * mins_time_consuming
        # 根据进度生成分数
        score = int(current / total * 100)
        score = score - 20 if score == 100 else score
        score = score + random.randint(0, 19)
        # 清空话术
        res['data'].pop('correct', None)
        # 清空视频时间戳
        res['data'].pop('video_playback', None)
        # 刷新最终进度
        res['data']['pose_frame']['coach_complete']['current'] = current
        # 返回分数信息
        res['data']['score'] = {
            'percentage': score,
            'kcol': kcol
        }

    # 保存用户数据
    user_dict[userid] = user_info

    logging.info('返回数据为：' + str(res))

    return res