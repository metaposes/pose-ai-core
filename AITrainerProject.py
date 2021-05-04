import cv2
import numpy as np;
import time
import PoseModule as pm

cap = cv2.VideoCapture('./data/test2.mp4')
detector = pm.poseDetector()
count = 0
dir = 0
pTime = 0

while True:
    success, img = cap.read()
    img = cv2.resize(img, (1280, 720))
    # img = cv2.imread('./data/test1.jpg')
    img = detector.findPose(img, False)
    lmList = detector.findPosition(img, False)
    # print(lmList)
    if len(lmList) != 0:
        # Right Arm
        right_arm_angle = detector.findAngle(img, 12, 14, 16)
        right_arm_per = np.interp(right_arm_angle, (50, 170), (100, 0))
        right_arm_bar = np.interp(right_arm_angle, (50, 170), (100, 250))
        # # Left Arm
        lift_arm_angle = detector.findAngle(img, 11, 13, 15)
        lift_arm_per = np.interp(lift_arm_angle, (30, 160), (100, 0))
        lift_arm_bar = np.interp(lift_arm_angle, (30, 160), (350, 500))

        # print(angle, per)

        right_leg_angle = detector.findAngle(img, 23, 25, 27)
        left_leg_angle = detector.findAngle(img, 24, 26, 28)
        detector.findAngle(img, 24, 12, 14)
        detector.findAngle(img, 23, 11, 13)
        detector.findAngle(img, 12, 24, 26)
        detector.findAngle(img, 11, 23, 25)

        # Check for the dumbbell curls
        color = (255, 0, 255)
        if right_arm_per == 100 and lift_arm_per == 100:
            color = (0, 255, 0)
            if dir == 0:
                count += 0.5
                dir = 1
        if right_arm_per == 0 and lift_arm_per == 0:
            color = (0, 255, 0)
            if dir == 1:
                count += 0.5
                dir = 0
        print(count)

        # Draw Bar
        cv2.rectangle(img, (1100, 100), (1175, 250), color, 3)
        cv2.rectangle(img, (1100, int(right_arm_bar)), (1175, 250), color, cv2.FILLED)
        cv2.putText(img, f'{int(right_arm_per)} %', (1100, 75), cv2.FONT_HERSHEY_PLAIN, 4,
                    color, 4)

        cv2.rectangle(img, (1100, 350), (1175, 500), color, 3)
        cv2.rectangle(img, (1100, int(lift_arm_bar)), (1175, 500), color, cv2.FILLED)
        cv2.putText(img, f'{int(lift_arm_per)} %', (1100, 325), cv2.FONT_HERSHEY_PLAIN, 4,
                    color, 4)

        # Draw Curl Count
        cv2.rectangle(img, (0, 620), (100, 720), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(int(count)), (25, 690), cv2.FONT_HERSHEY_PLAIN, 4,
                    (255, 0, 0), 4)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (50, 100), cv2.FONT_HERSHEY_PLAIN, 5,
                (255, 0, 0), 5)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
cap.release()
cv2.destroyAllWindows()