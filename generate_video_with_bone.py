import cv2
import csv
import copy
import os
import datetime
import pytz
import math

colors = {
    "red": (0, 0, 255),
    "blue": (255, 0, 0),
    "green": (0, 255, 0),
    "yellow": (0, 255, 255),
    "white": (255, 255, 255),
    "black": (0, 0, 0)
}

body_parts_mapping = {
    "waistCenter": (23, 24),  # 特別なケース
    "nose": 0,
    "leftEyeInner": 1,
    "leftEye": 2,
    "leftEyeOuter": 3,
    "rightEyeInner": 4,
    "rightEye": 5,
    "rightEyeOuter": 6,
    "leftEar": 7,
    "rightEar": 8,
    "leftMouth": 9,
    "rightMouth": 10,
    "leftShoulder": 11,
    "rightShoulder": 12,
    "leftElbow": 13,
    "rightElbow": 14,
    "leftWrist": 15,
    "rightWrist": 16,
    "leftPinky": 17,
    "rightPinky": 18,
    "leftIndex": 19,
    "rightIndex": 20,
    "leftThumb": 21,
    "rightThumb": 22,
    "leftHip": 25,
    "rightHip": 26,
    "leftKnee": 27,
    "rightKnee": 28,
    "leftAnkle": 29,
    "rightAnkle": 30,
    "leftHeel": 31,
    "rightHeel": 32,
    "leftFootIndex": 33,
    "rightFootIndex": 34
}

def generate_download_video(video_path, csv_path, target_csv_path, target_fps, overlap_frame_base, overlap_frame_target, overlap_body_part_base, overlap_body_part_target, base_color, target_color, output_video_file_name) -> str:

    # dt_now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    # formatted_dt = dt_now.strftime('%Y-%m-%d-%H-%M-%S')
    
    if output_video_file_name == "":
        if target_csv_path == "":
            output_video_file_name = f"exported/{video_path.split('/')[-1].split('.')[0]}_output.mp4"
        else:
            output_video_file_name = f"exported/{video_path.split('/')[-1].split('.')[0]}_with_{target_csv_path.split('/')[-1].split('.')[0]}_output.mp4"
    else:
        output_video_file_name = f"exported/{output_video_file_name}.mp4"
            
    
    with open(csv_path, encoding='utf8', newline='') as f:
        csv_reader_base = list(csv.reader(f, delimiter=' ', quotechar='|'))
    if target_csv_path != "":
        with open(target_csv_path, encoding='utf8', newline='') as f:
            csv_reader_target = list(csv.reader(
                f, delimiter=' ', quotechar='|'))

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    out = cv2.VideoWriter(
        output_video_file_name, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

    index = 0

    target_index_value = (overlap_frame_target *
                            (fps / target_fps) - overlap_frame_base) * (target_fps / fps)

    while True:
        ret, frame = cap.read()
        if ret:
            image = copy.deepcopy(frame)
            csv_row = csv_reader_base[index+1][0].split(',')

            keypoints = []

            for points in range(0, len(csv_row), 3):

                keypoints.append(
                    (round(float(csv_row[points])), round(float(csv_row[points+1]))))

            drawed_image = draw_human_pose(
                image, keypoints, colors[base_color])

            if target_csv_path != "":
                # 列名分で+1
                target_index = math.floor(target_index_value)+1
                if 1 <= target_index and len(csv_reader_target) > target_index:
                    csv_row = csv_reader_target[target_index][0].split(',')

                    compare_keypoints = []

                    for points in range(0, len(csv_row), 3):

                        compare_keypoints.append(
                            (round(float(csv_row[points])), round(float(csv_row[points+1]))))

                    base_height = get_height(keypoints)
                    compare_height = get_height(compare_keypoints)

                    converted_compare_keypoints = []

                    ratio = 1

                    if compare_height != 0:
                        ratio = base_height / compare_height

                    for compare_keypoint in compare_keypoints:
                        adjusted_keypoint = get_adjusted_for_base_point(
                            get_body_part_points(keypoints, overlap_body_part_base), get_body_part_points(compare_keypoints, overlap_body_part_target), compare_keypoint, ratio)
                        converted_compare_keypoints.append(
                            adjusted_keypoint)
                        
                    drawed_image = draw_human_pose(
                        drawed_image, converted_compare_keypoints,  colors[target_color])

            out.write(cv2.resize(drawed_image,   # 画像データを指定
                                    (w, h)   # リサイズ後のサイズを指定
                                    ))
            index += 1
            target_index_value += target_fps / fps
        else:
            break

    cap.release()
    out.release()
    
    return output_video_file_name

def get_body_part_points(keypoints, body_part) -> tuple:
    index = body_parts_mapping.get(body_part)
    if index is not None:
        if body_part == "waistCenter":
            # 特別なケース: waistCenterの座標を計算
            x = (keypoints[23][0] + keypoints[24][0]) // 2
            y = (keypoints[23][1] + keypoints[24][1]) // 2
            body_part_position = (x, y)
            return body_part_position
        else:
            # 通常の場合: インデックスを使用して座標を取得
            x, y = keypoints[index]
            body_part_position = (x, y)
            return body_part_position
    else:
        return (0, 0)


def draw_human_pose(
    image,
    keypoints,
    color
):
    debug_image = copy.deepcopy(image)

    def draw_circle(keypoint):
        cv2.circle(debug_image, keypoint, 8, color, -1)

    def draw_line(start_keypoint, end_keypoint):
        cv2.line(debug_image, start_keypoint,
                 end_keypoint, color, 4)

    draw_circle(keypoints[11])  # Left shoulder
    draw_circle(keypoints[12])  # Right shoulder

    ear_center = (
        (keypoints[7][0] + keypoints[8][0])//2, (keypoints[7][1] + keypoints[8][1])//2)
    shoulder_center = (
        (keypoints[11][0] + keypoints[12][0])//2, (keypoints[11][1] + keypoints[12][1])//2)
    hip_center = ((keypoints[23][0] + keypoints[24][0])//2,
                  (keypoints[23][1] + keypoints[24][1])//2)

    draw_circle(ear_center)  # Ear center
    draw_circle(shoulder_center)  # Shoulder center
    draw_circle(hip_center)  # Hip center
    draw_line(ear_center, shoulder_center)
    draw_line(shoulder_center, hip_center)

    draw_line(keypoints[11], keypoints[12])  # Left shoulder to right shoulder
    draw_line(keypoints[23], keypoints[24])  # Left hip to right hip

    draw_circle(keypoints[13])  # Left elbow
    draw_circle(keypoints[14])  # Right elbow
    draw_circle(keypoints[15])  # Left wrist
    draw_circle(keypoints[16])  # Right wrist
    draw_circle(keypoints[19])  # Left index
    draw_circle(keypoints[20])  # Right index

    draw_line(keypoints[11], keypoints[13])  # Left shoulder to left elbow
    draw_line(keypoints[13], keypoints[15])  # Left elbow to left wrist
    draw_line(keypoints[15], keypoints[19])  # Left wrist to left index

    draw_line(keypoints[12], keypoints[14])  # Right shoulder to right elbow
    draw_line(keypoints[14], keypoints[16])  # Right elbow to right wrist
    draw_line(keypoints[16], keypoints[20])  # Right wrist to right index

    draw_circle(keypoints[25])  # Left knee
    draw_circle(keypoints[26])  # Right knee
    draw_circle(keypoints[27])  # Left ankle
    draw_circle(keypoints[28])  # Right ankle
    draw_circle(keypoints[29])  # Left heel
    draw_circle(keypoints[30])  # Right heel
    draw_circle(keypoints[31])  # Left foot index
    draw_circle(keypoints[32])  # Right foot index

    draw_line(keypoints[23], keypoints[25])  # Left hip to left knee
    draw_line(keypoints[25], keypoints[27])  # Left knee to left ankle
    draw_line(keypoints[27], keypoints[29])  # Left ankle to left heel
    draw_line(keypoints[29], keypoints[31])  # Left heel to left foot index

    draw_line(keypoints[24], keypoints[26])  # Right hip to right knee
    draw_line(keypoints[26], keypoints[28])  # Right knee to right ankle
    draw_line(keypoints[28], keypoints[30])  # Right ankle to right heel
    draw_line(keypoints[30], keypoints[32])  # Right hee

    return debug_image


def get_height(keypoints):
    def calculate_distance(point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance
        
    left_ear = (keypoints[7][0], keypoints[7][1])
    left_shoulder = (keypoints[11][0], keypoints[11][1])
    left_hip = (keypoints[23][0], keypoints[23][1])
    left_knee = (keypoints[25][0], keypoints[25][1])
    left_heel = (keypoints[29][0], keypoints[29][1])
    
    left_height = calculate_distance(left_ear, left_shoulder) + calculate_distance(left_shoulder, left_hip) + \
        calculate_distance(left_hip, left_knee) + \
        calculate_distance(left_knee, left_heel)
        
    right_ear = (keypoints[8][0], keypoints[8][1])
    right_shoulder = (keypoints[12][0], keypoints[12][1])
    right_hip = (keypoints[24][0], keypoints[24][1])
    right_knee = (keypoints[26][0], keypoints[26][1])
    right_heel = (keypoints[30][0], keypoints[30][1])
    
    right_height = calculate_distance(right_ear, right_shoulder) + calculate_distance(right_shoulder, right_hip) + \
        calculate_distance(right_hip, right_knee) + \
        calculate_distance(right_knee, right_heel)

    return (left_height + right_height)/2


def get_adjusted_for_base_point(base_overlap_point, target_overlap_point, target_point, ratio):
    if (base_overlap_point[0] == 0 and base_overlap_point[1] == 0) or (target_overlap_point[0] == 0 and target_overlap_point[1] == 0):
        return (0, 0)

    start = base_overlap_point
    end = (target_point[0] + base_overlap_point[0] - target_overlap_point[0],
           target_point[1] + base_overlap_point[1] - target_overlap_point[1])

    abX = end[0] - start[0]
    abY = end[1] - start[1]

    ab_length = math.sqrt(abX * abX + abY * abY)

    if ab_length == 0:
        return (0, 0)

    distance_to_c = ab_length * ratio

    ab_unitX = abX / ab_length
    ab_unitY = abY / ab_length

    return (round(start[0] + ab_unitX * distance_to_c), round(start[1] + ab_unitY * distance_to_c))
