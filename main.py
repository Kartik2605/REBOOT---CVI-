"""Demo code showing how to estimate human head pose.

There are three major steps:
1. Detect human face in the video frame.
2. Run facial landmark detection on the face image.
3. Estimate the pose by solving a PnP problem.

To find more details, please refer to:
https://github.com/yinguobing/head-pose-estimation
"""
from argparse import ArgumentParser

import cv2
import os
import time
import handTrackingModule as htm

from mark_detector import MarkDetector
from pose_estimator import PoseEstimator

print(__doc__)
print("OpenCV version: {}".format(cv2.__version__))

# Parse arguments from user input.
parser = ArgumentParser()
parser.add_argument("--video", type=str, default=None,
                    help="Video file to be processed.")
parser.add_argument("--cam", type=int, default=None,
                    help="The webcam index.")
args = parser.parse_args()

def getNumber(ar):
    s=""
    for i in ar:
       s+=str(ar[i]);

    if(s=="00000"):
        return (0)
    elif(s=="01000"):
        return(1)
    elif(s=="01100"):
        return(2)
    elif(s=="01110"):
        return(3)
    elif(s=="01111"):
        return(4)
    elif(s=="11111"):
        return(5)
    elif(s=="01001"):
        return(6)
    elif(s=="01011"):
        return(7)


if __name__ == '__main__':
    # Before estimation started, there are some startup works to do.

    # 1. Setup the video source from webcam or video file.
    video_src = args.cam if args.cam is not None else args.video
    if video_src is None:
        print("Video source not assigned, default webcam will be used.")
        video_src = 0

    cap = cv2.VideoCapture(video_src)

    # Get the frame size. This will be used by the pose estimator.
    wcam,hcam=640,480
    cap.set(3,wcam)
    cap.set(4,hcam)

    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    pTime=0

    # 2. Introduce a pose estimator to solve pose.
    pose_estimator = PoseEstimator(img_size=(height, width))

    # 3. Introduce a mark detector to detect landmarks.
    mark_detector = MarkDetector()

    # 4. Measure the performance with a tick meter.
    tm = cv2.TickMeter()

    detector = htm.handDetector(detectionCon=0.75)
    # Now, let the frames flow.
    while True:

        # Read a frame.
        frame_got, frame = cap.read()
        if frame_got is False:
            break

        # If the frame comes from webcam, flip it so it looks like a mirror.
        if video_src == 0:
            frame = cv2.flip(frame, 2)

        # Step 1: Get a face from current frame.
        facebox = mark_detector.extract_cnn_facebox(frame)



        # Any face found?
        if facebox is not None:

            # Step 2: Detect landmarks. Crop and feed the face area into the
            # mark detector.
            x1, y1, x2, y2 = facebox
            face_img = frame[y1: y2, x1: x2]

            # Run the detection.
            tm.start()
            marks = mark_detector.detect_marks(face_img)
            tm.stop()

            # Convert the locations from local face area to the global image.
            marks *= (x2 - x1)
            marks[:, 0] += x1
            marks[:, 1] += y1

            # Try pose estimation with 68 points.
            pose = pose_estimator.solve_pose_by_68_points(marks)

            print("The pose track for frame is: \n")
            print(pose[1][0])
            print(pose[1][1])
            print(pose[1][2])
            # All done. The best way to show the result would be drawing the
            # pose on the frame in realtime.

            # Do you want to see the pose annotation?
            pose_estimator.draw_annotation_box(
                frame, pose[0], pose[1], color=(0, 255, 0))

            # Do you want to see the head axes?
            # pose_estimator.draw_axes(frame, pose[0], pose[1])

            # Do you want to see the marks?
            # mark_detector.draw_marks(frame, marks, color=(0, 255, 0))

            # Do you want to see the facebox?
            # mark_detector.draw_box(frame, [facebox])

        img = detector.findHands(frame, draw=True )
        lmList=detector.findPosition(img,draw=False)
        #print(lmList)
        tipId=[4,8,12,16,20]
        if(len(lmList)!=0):
            fingers=[]
            #thumb
            if(lmList[tipId[0]][1]>lmList[tipId[0]-1][1]):
                fingers.append(1)
            else :
                fingers.append(0)
            #4 fingers
            for id in range(1,len(tipId)):

                if(lmList[tipId[id]][2]<lmList[tipId[id]-2][2]):
                    fingers.append(1)

                else :
                    fingers.append(0)

            value = getNumber(fingers)
            print("\nThe value of the fingers is: \n")
            print(value)

            cv2.rectangle(img,(20,255),(170,425),(0,255,0),cv2.FILLED)
            cv2.putText(img,str(value),(45,375),cv2.FONT_HERSHEY_PLAIN,
                                             10,(255,0,0),20)

        # Show preview.
        cTime=time.time()
        fps=1/(cTime-pTime)
        pTime=cTime
        cv2.putText(img, f'FPS: {int(fps)}',(400,70),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,0),3)
        cv2.imshow("Preview", frame)
        if cv2.waitKey(1) == 27:
            break
