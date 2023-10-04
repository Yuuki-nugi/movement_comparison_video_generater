import cv2
import csv
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# 各身体ポイントの座標データを定義
points = {
    0: ("nose", "X", "Y", "Z"),
    1: ("left eye (inner)", "X", "Y", "Z"),
    2: ("left eye", "X", "Y", "Z"),
    3: ("left eye (outer)", "X", "Y", "Z"),
    4: ("right eye (inner)", "X", "Y", "Z"),
    5: ("right eye", "X", "Y", "Z"),
    6: ("right eye (outer)", "X", "Y", "Z"),
    7: ("left ear", "X", "Y", "Z"),
    8: ("right ear", "X", "Y", "Z"),
    9: ("mouth (left)", "X", "Y", "Z"),
    10: ("mouth (right)", "X", "Y", "Z"),
    11: ("left shoulder", "X", "Y", "Z"),
    12: ("right shoulder", "X", "Y", "Z"),
    13: ("left elbow", "X", "Y", "Z"),
    14: ("right elbow", "X", "Y", "Z"),
    15: ("left wrist", "X", "Y", "Z"),
    16: ("right wrist", "X", "Y", "Z"),
    17: ("left pinky", "X", "Y", "Z"),
    18: ("right pinky", "X", "Y", "Z"),
    19: ("left index", "X", "Y", "Z"),
    20: ("right index", "X", "Y", "Z"),
    21: ("left thumb", "X", "Y", "Z"),
    22: ("right thumb", "X", "Y", "Z"),
    23: ("left hip", "X", "Y", "Z"),
    24: ("right hip", "X", "Y", "Z"),
    25: ("left knee", "X", "Y", "Z"),
    26: ("right knee", "X", "Y", "Z"),
    27: ("left ankle", "X", "Y", "Z"),
    28: ("right ankle", "X", "Y", "Z"),
    29: ("left heel", "X", "Y", "Z"),
    30: ("right heel", "X", "Y", "Z"),
    31: ("left foot index", "X", "Y", "Z"),
    32: ("right foot index", "X", "Y", "Z"),
}

def pose_detection(video_path) -> str:
    filename = video_path.split("/")[-1].split('.')[0]
    output_csv_path = f"exported/{filename}.csv"
    
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return

    with mp_pose.Pose(static_image_mode=False, min_detection_confidence=0, min_tracking_confidence=0.4) as pose:
        frame_number = 0

        with open(output_csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            
            # 配列を生成
            body_points_array = []

            for i in range(33):
                name, x, y, z = points[i]
                body_points_array.extend([f"{name}{x}", f"{name}{y}", f"{name}{z}"])

            writer.writerow(body_points_array)

            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    # 姿勢推定処理
                    results = pose.process(
                        cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                    row_data = []
                    if results.pose_landmarks:
                        image_height, image_width, _ = frame.shape

                        for i, landmark in enumerate(results.pose_landmarks.landmark):
                            row_data.append(landmark.x * image_width)
                            row_data.append(landmark.y * image_height)
                            row_data.append(landmark.z)

                    else:
                        row_data = [0] * 99  # 33 landmarks * 2 (x, y)

                    writer.writerow(row_data)
                    frame_number += 1
                else:
                    break

    cap.release()
    return output_csv_path