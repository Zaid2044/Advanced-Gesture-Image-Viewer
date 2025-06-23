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
        self.tip_ids = [4, 8, 12, 16, 20]
        self.lm_list = []
        self.results = None

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img

    def find_position(self, img, hand_no=0):
        self.lm_list = []
        if self.results.multi_hand_landmarks:
            if hand_no < len(self.results.multi_hand_landmarks):
                my_hand = self.results.multi_hand_landmarks[hand_no]
                for id, lm in enumerate(my_hand.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    self.lm_list.append([id, cx, cy])
        return self.lm_list

    def find_distance(self, p1, p2, img=None):
        x1, y1 = self.lm_list[p1][1], self.lm_list[p1][2]
        x2, y2 = self.lm_list[p2][1], self.lm_list[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]

def main():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker(max_hands=2)

    img = cv2.imread("images/test_image.jpg")
    if img is None:
        print("Error: Could not load image. Make sure 'test_image.jpg' is in the 'images' folder.")
        return

    h, w, _ = img.shape
    scale = 1.0
    center_x, center_y = w // 2, h // 2
    angle = 0
    
    last_pan_pos = None
    last_zoom_dist = None
    last_rot_angle = None
    
    smoothing = 0.2

    while True:
        success, frame = cap.read()
        if not success:
            break
        
        frame = cv2.flip(frame, 1)
        frame = tracker.find_hands(frame)
        lm_list_all = []
        if tracker.results.multi_hand_landmarks:
            for hand_lms in tracker.results.multi_hand_landmarks:
                hand_pos = []
                for id, lm in enumerate(hand_lms.landmark):
                    h_cam, w_cam, c_cam = frame.shape
                    cx, cy = int(lm.x * w_cam), int(lm.y * h_cam)
                    hand_pos.append([id, cx, cy])
                lm_list_all.append(hand_pos)
        
        current_pan_pos = None
        current_zoom_dist = None
        current_rot_angle = None

        if len(lm_list_all) == 1:
            hand = lm_list_all[0]
            thumb_tip = hand[4]
            index_tip = hand[8]
            palm_center = hand[0]
            
            dist, _, _ = tracker.find_distance(4, 8, frame)
            
            if dist < 50: 
                if last_zoom_dist is None: last_zoom_dist = dist
                zoom_change = (dist - last_zoom_dist) * 0.01
                scale += zoom_change
                last_zoom_dist = dist
            else:
                last_zoom_dist = None

            if dist > 80:
                current_pan_pos = palm_center[1], palm_center[2]
                if last_pan_pos is None: last_pan_pos = current_pan_pos
                dx = current_pan_pos[0] - last_pan_pos[0]
                dy = current_pan_pos[1] - last_pan_pos[1]
                center_x -= dx
                center_y -= dy
                last_pan_pos = current_pan_pos
            else:
                last_pan_pos = None
        
        elif len(lm_list_all) == 2:
            hand1, hand2 = lm_list_all[0], lm_list_all[1]
            palm1_center = hand1[0]
            palm2_center = hand2[0]
            
            dx = palm2_center[1] - palm1_center[1]
            dy = palm2_center[2] - palm1_center[2]
            current_rot_angle = math.degrees(math.atan2(dy, dx))

            if last_rot_angle is None: last_rot_angle = current_rot_angle
            angle_change = current_rot_angle - last_rot_angle
            angle += angle_change
            last_rot_angle = current_rot_angle
        else:
            last_pan_pos = None
            last_zoom_dist = None
            last_rot_angle = None

        scale = np.clip(scale, 0.2, 5.0)

        M = cv2.getRotationMatrix2D((w//2, h//2), angle, scale)
        M[0, 2] += (w/2) - center_x
        M[1, 2] += (h/2) - center_y
        
        output = cv2.warpAffine(img, M, (w, h))

        cv2.imshow("Gesture Controlled Viewer", output)
        cv2.imshow("Webcam Feed", frame)

        if cv2.waitKey(1) & 0xFF in [ord('q'), 27]:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()