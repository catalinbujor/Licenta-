import cv2
import sys

def get_tracker(tracker_type):
    if tracker_type == 'BOOSTING':
            tracker = cv2.TrackerBoosting_create()
    if tracker_type == 'MIL':
            tracker = cv2.TrackerMIL_create()
    if tracker_type == 'KCF':
            tracker = cv2.TrackerKCF_create()
    if tracker_type == 'TLD':
            tracker = cv2.TrackerTLD_create()
    if tracker_type == 'MEDIANFLOW':
            tracker = cv2.TrackerMedianFlow_create()
    if tracker_type == 'GOTURN':
            tracker = cv2.TrackerGOTURN_create()
    if tracker_type == "CSRT":
            tracker = cv2.TrackerCSRT_create()
    return tracker

if __name__ == '__main__':

    tracker_types = ['BOOSTING', 'MIL', 'KCF', 'CSRT']

    boosting_tracker = get_tracker('BOOSTING')
    kcf_tracker  = get_tracker('KCF')
    csrt_tracker = get_tracker('CSRT')
    mil_tracker = get_tracker('MIL')

    video = cv2.VideoCapture("./balls.mp4")

    if not video.isOpened():
        print ("Could not open video")
        sys.exit()

    read_first_frame, first_frame = video.read()
    if not read_first_frame:
        print ('Cannot read video file')
        sys.exit()

    csrt_box = cv2.selectROI(first_frame, False)
    boosting_box = cv2.selectROI(first_frame, False)
    kcf_box = cv2.selectROI(first_frame, False)
    mil_box = cv2.selectROI(first_frame, False)

    csrt_init = csrt_tracker.init(first_frame, csrt_box)
    boosting_init = boosting_tracker.init(first_frame, boosting_box)
    kfc_init = kcf_tracker.init(first_frame, kcf_box)
    mil_init = mil_tracker.init(first_frame, mil_box)

    while True:

        read_next_frame, frame = video.read()
        if not read_next_frame:
            break
        
        timer = cv2.getTickCount()

        csrt_succes, csrt_box = csrt_tracker.update(frame)
        boosting_succes , boosting_box = boosting_tracker.update(frame)
        kcf_succes , kcf_box = kcf_tracker.update(frame)
        mil_succes , mil_box = mil_tracker.update(frame)

        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);

        if csrt_succes:
            p1 = (int(csrt_box[0]), int(csrt_box[1]))
            p2 = (int(csrt_box[0] + csrt_box[2]), int(csrt_box[1] + csrt_box[3]))
            cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
        else :
            cv2.putText(frame, "Tracking on csrt failure detected", (0,100), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,255),2)

        if boosting_succes:
            p1 = (int(boosting_box[0]), int(boosting_box[1]))
            p2 = (int(boosting_box[0] + boosting_box[2]), int(boosting_box[1] + boosting_box[3]))
            cv2.rectangle(frame, p1, p2, (0, 0, 255), 2, 1)
        else:
            cv2.putText(frame, "Tracking on boosting failure detected", (0, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 2)

        if kcf_succes:
            p1 = (int(kcf_box[0]), int(kcf_box[1]))
            p2 = (int(kcf_box[0] + kcf_box[2]), int(kcf_box[1] + kcf_box[3]))
            cv2.rectangle(frame, p1, p2, (0, 255, 0), 2, 1)
        else:
            cv2.putText(frame, "Tracking on kcf failure detected", (0, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 2)

        if mil_succes:
            p1 = (int(mil_box[0]), int(mil_box[1]))
            p2 = (int(mil_box[0] + mil_box[2]), int(mil_box[1] + mil_box[3]))
            cv2.rectangle(frame, p1, p2, (255, 247, 22), 2, 1)
        else:
            cv2.putText(frame, "Tracking on mil failure detected", (0, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        cv2.putText(frame, "CSRT" + " Tracker", (0,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0),2);
        cv2.putText(frame, "Boosting" + " Tracker", (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2);
        cv2.putText(frame, "Kcf" + " Tracker", (0, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2);
        cv2.putText(frame, "Mil" + " Tracker", (0, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,247,22), 2);


        cv2.putText(frame, "FPS : " + str(int(fps)), (200,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50,170,50), 2);

        cv2.imshow("Licenta", frame)

        k = cv2.waitKey(1) & 0xff
        if k == 27 : break
