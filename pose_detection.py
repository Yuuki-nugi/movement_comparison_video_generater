import cv2
import csv
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def pose_detection(video_path) -> str:
    filename = video_path.split("/")[-1]
    output_csv_path = f"exported/{filename}.csv"
    
    cap = cv2.VideoCapture(video_path)
    frame_rate = cap.get(cv2.CAP_PROP_FPS)

    if not cap.isOpened():
        return

    with mp_pose.Pose(static_image_mode=False, min_detection_confidence=0, min_tracking_confidence=0.4) as pose:
        frame_number = 0

        with open(output_csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)

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