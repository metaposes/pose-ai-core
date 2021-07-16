from flask import *
import CalcRDC as CR
import MetaModule as mm
import correct as rb
import redis
import CorrectWord

model = mm.meta_model_calc()
Pool = redis.ConnectionPool(
    host='node1.host.smallsaas.cn', port=6379, max_connections=10, decode_responses=True, password='root')
app = Flask(__name__)
cw = CorrectWord.CorrectWord
# 用户动作进度数据
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
model_date_k_v_map = {
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


@app.route('/api/ai/correction', methods=['GET', 'POST'])
def Dispatch():
    if request.method == 'POST':
        user_pose_data = request.json
        posename = user_pose_data.get('posename')
        if posename == 'squat':
            return Squat(user_pose_data)
        else:
            return dict(success='no such pose')


# 用于从用户原始坐标数据生成对应的模型角度数据
def get_model_data_from_origin_joints(user_data_origin_joint):
    # 待返回的模型数据
    model_data = {}

    # 计算 各个 对应角度结果
    for key in main_angle_names:
        res = model.findAngle(
            user_data_origin_joint.get(
                model_date_k_v_map[key]['joint_keys'][0]),
            user_data_origin_joint.get(
                model_date_k_v_map[key]['joint_keys'][1]),
            user_data_origin_joint.get(
                model_date_k_v_map[key]['joint_keys'][2]))

        model_data[model_date_k_v_map[key]['angle_keys'][0]] = res[0]
        model_data[model_date_k_v_map[key]['angle_keys'][1]] = res[1]
        model_data[model_date_k_v_map[key]['angle_keys'][2]] = res[2]

    return model_data


# 将标准模型数据与用户模型数据根据阈值进行对比返回差异最大的角度
def get_max_diff_angle(standard_model_data, user_model_data, thresholds):
    max_diff_angle = 0.0
    model_name = None
    for key in main_angle_names:
        l = standard_model_data[key]
        r = user_model_data[key]
        diff = abs(l - r)
        threshold = thresholds.get(key) or 0
        print('获取到', key, '的标准角度值：', l)
        print('获取到', key, '的用户角度值：', r)
        print('角度相差值为；', diff)
        if diff >= threshold and diff > max_diff_angle:
            max_diff_angle = diff
            model_name = key

    return None if max_diff_angle == 0 else {'name': model_name, 'diff_angle': max_diff_angle}


def Squat(user_pose_data):
    # 用户ID
    user_id = user_pose_data.get('userid')
    # 姿势数据
    pose_data = user_pose_data.get('posedata')
    # 模型基础名称
    model_base_name = user_pose_data.get('posename')
    # 当前用户
    current_user = user_dict.get(user_id, None)

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
    if current_user is None:
        # 起始索引
        idx = 0
        # 用户记录
        user_record = CR.greed(idx)
        # 对应的动作数量
        keys_len = len(key_pose_standard_joints_keys)
    else:
        idx = current_user['current_idx']
        user_record = current_user['user_record']
        keys_len = current_user['count']

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
                key_pose_standard_joints_arr[idx][key] or 0)
        # 提取标准动作模型角度阈值
        for key in threshold_map_name_keys:
            key_pose_joints_threshold[key] = float(
                key_pose_joints_threshold_arr[idx][key] or 0)
        # 收集原始用户节点数据
        for key in pose_name_keys:
            user_data_origin_joint[key] = pose_data.get(key) or {
                'x': 0.0, 'y': 0.0}
    except():
        return dict(success=False)

    # 根据用户原始数据生成的模型数据
    model_data = get_model_data_from_origin_joints(user_data_origin_joint)

    # 差异最大角度 {'name': 'xxx', 'diff_angle': 78.281}
    max_diff_angle = get_max_diff_angle(key_pose_standard_joints, model_data,
                                        key_pose_joints_threshold)

    print(max_diff_angle)

    # 保存用户状态
    user_dict[user_id] = dict(
        current_idx=(idx + 1) % keys_len, count=keys_len, user_record=user_record)

    return dict(success=True)


if __name__ == '__main__':
    app.run(debug=True)
