import cv2
import mediapipe as mp
import numpy as np
import math

class HandTracker:
    def __init__(self, mode=False, max_hands=2, detection_con=0.5, track_con=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(self.mode, self.max_hands, 1, self.detection_con, self.track_con)
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img

    def get_landmark_list(self, img):
        lm_list_all = []
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                hand_pos = []
                for id, lm in enumerate(hand_lms.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    hand_pos.append([id, cx, cy])
                lm_list_all.append(hand_pos)
        return lm_list_all

    def find_distance(self, p1_idx, p2_idx, lm_list):
        if len(lm_list) > max(p1_idx, p2_idx):
            x1, y1 = lm_list[p1_idx][1], lm_list[p1_idx][2]
            x2, y2 = lm_list[p2_idx][1], lm_list[p2_idx][2]
            length = math.hypot(x2 - x1, y2 - y1)
            return length, (x1, y1), (x2, y2)
        return None, None, None


def main():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker(max_hands=2)

    try:
        img = cv2.imread("images/test_image.jpg")
        if img is None:
            raise FileNotFoundError
    except FileNotFoundError:
        print("Error: Could not load image. Make sure 'test_image.jpg' is in the 'images' folder.")
        return

    h_img, w_img, _ = img.shape
    scale = 1.0
    center_x, center_y = w_img // 2, h_img // 2
    angle = 0
    
    pos_x, pos_y = center_x, center_y
    smooth_scale, smooth_angle = scale, angle
    smooth_x, smooth_y = pos_x, pos_y

    last_pan_pos = None
    last_zoom_dist = 0
    start_rot_angle = 0
    start_rot_vector = None

    while True:
        success, frame = cap.read()
        if not success:
            break
        
        frame = cv2.flip(frame, 1)
        frame = tracker.find_hands(frame)
        lm_list_all = tracker.get_landmark_list(frame)

        if len(lm_list_all) == 1:
            hand_landmarks = lm_list_all[0]
            
            dist, p1, p2 = tracker.find_distance(4, 8, hand_landmarks)
            
            if dist is not None:
                if dist < 50:
                    if last_zoom_dist == 0: last_zoom_dist = dist
                    scale += (dist - last_zoom_dist) * 0.05
                    last_zoom_dist = dist
                else:
                    last_zoom_dist = 0
                
                if dist > 80:
                    palm_center = hand_landmarks[0][1:]
                    if last_pan_pos is None: last_pan_pos = palm_center
                    dx = palm_center[0] - last_pan_pos[0]
                    dy = palm_center[1] - last_pan_pos[1]
                    pos_x -= dx
                    pos_y -= dy
                    last_pan_pos = palm_center
                else:
                    last_pan_pos = None

        elif len(lm_list_all) == 2:
            hand1_landmarks = lm_list_all[0]
            hand2_landmarks = lm_list_all[1]
            
            p1 = hand1_landmarks[0][1:]
            p2 = hand2_landmarks[0][1:]

            if start_rot_vector is None:
                start_rot_vector = (p2[0] - p1[0], p2[1] - p1[1])
                start_rot_angle = angle

            current_rot_vector = (p2[0] - p1[0], p2[1] - p1[1])
            
            angle1 = math.atan2(start_rot_vector[1], start_rot_vector[0])
            angle2 = math.atan2(current_rot_vector[1], current_rot_vector[0])
            
            angle_change = math.degrees(angle2 - angle1)
            angle = start_rot_angle + angle_change

        else:
            last_pan_pos = None
            last_zoom_dist = 0
            start_rot_vector = None

        scale = np.clip(scale, 0.2, 5.0)

        smoothing_factor = 0.2
        smooth_scale = (1 - smoothing_factor) * smooth_scale + smoothing_factor * scale
        smooth_angle = (1 - smoothing_factor) * smooth_angle + smoothing_factor * angle
        smooth_x = (1 - smoothing_factor) * smooth_x + smoothing_factor * pos_x
        smooth_y = (1 - smoothing_factor) * smooth_y + smoothing_factor * pos_y

        M = cv2.getRotationMatrix2D((w_img//2, h_img//2), smooth_angle, smooth_scale)
        M[0, 2] += (w_img/2) - smooth_x
        M[1, 2] += (h_img/2) - smooth_y
        
        output = cv2.warpAffine(img, M, (w_img, h_img))

        cv2.imshow("Gesture Controlled Viewer", output)
        cv2.imshow("Webcam Feed", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()