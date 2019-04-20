import cv2
import sys, time
from twilio.rest import Client
from copy import deepcopy
import threading


def get_tracker(tracker_type):
    if tracker_type == 'BOOSTING':
        tracker = cv2.TrackerBoosting_create()
    if tracker_type == 'MIL':
        tracker = cv2.TrackerMIL_create()
    if tracker_type == 'KCF':
        tracker = cv2.TrackerKCF_create()
    if tracker_type == 'TLD':
        tracker = cv2.TrackerTLD_create()
    if tracker_type == "CSRT":
        tracker = cv2.TrackerCSRT_create()
    if tracker_type == 'MEDIANFLOW':
        tracker = cv2.TrackerMedianFlow_create()
    return tracker

def show_results(start_x,start_y,tracker_box , video_source, video):
    width = video.get(3)
    print("X:" + str(abs(tracker_box[0] - start_x)))
    print("Y:" + str(abs(tracker_box[1] - start_y)))
    f = open("./stats/kcf_bound.txt","a")
    f.write("Video source :" +  video_source + "\n")
    f.write("X:" + str(start_x)  + " " + "Y:" + str(start_y) + "\n")
    f.write("X:" + str(abs(tracker_box[0] - start_x)) + "  "  + "Y:" + str(abs(tracker_box[1] - start_y)) + "\n")
    f.write("Video width :" + str(width) + "\n")
    f.write("\n")

def update_box(frame,color,tracker_box):
    p1 = (int(tracker_box[0]), int(tracker_box[1]))
    p2 = (int(tracker_box[0] + tracker_box[2]), int(tracker_box[1] + tracker_box[3]))
    cv2.rectangle(frame, p1, p2, color, 2, 1)

def check_free_spot(frame,tracker_box,initial_box, bound):
    print("X :" + str(abs(initial_box[0] - int(tracker_box[0]))) + " Y : " +  str(abs(initial_box[1] - int(tracker_box[1]))))
    if abs(initial_box[0] - int(tracker_box[0])) >= bound or abs(initial_box[1] - int(tracker_box[1])) >= bound:
        cv2.putText(frame, "New free spot !", (250, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        p1 = (int(initial_box[0]), int(initial_box[1]))
        p2 = (int(initial_box[0] + initial_box[2]), int(initial_box[1] + initial_box[3]))
        cv2.rectangle(frame, p1, p2, (0, 255, 0), 2, 1)
        return True

    return False

def send_SMS(message,to):
    account_sid = 'AC06d44c1010f0d101b561c0f833ec8888'
    auth_token = '5b054991766ca520b892b64745c2cb83'
    client = Client(account_sid, auth_token)
    print("Se trimite mesajul .. ")
    message = client.messages \
        .create(
        body= message,
        from_='+12063396544',
        to=to
    )

def get_video(using_camera,video_source):
    if using_camera:
        video = cv2.VideoCapture(0)
        time.sleep(1.0)
    else:
        video = cv2.VideoCapture(video_source)
        if not video.isOpened():
            print("Could not open video")
            sys.exit()
    return video

def find_parking_spot(using_camera, video_source):

    video = get_video(using_camera, video_source)
    video_width = video.get(3)

    kcf_tracker = get_tracker('KCF')

    first_frame = video.read()[1]
    if video_width < 1280:
        first_frame = cv2.resize(first_frame, (1280,720))


    kcf_box = cv2.selectROI(first_frame,False)
    initial_box = deepcopy(kcf_box)
    kcf_tracker.init(first_frame, kcf_box)

    not_send = False

    while True:

        frame = video.read()[1]

        if video_width < 1280:
            try :
              frame = cv2.resize(frame, (1280,720))
            except:
                break

        timer = cv2.getTickCount()
        kcf_succes , kcf_box = kcf_tracker.update(frame)

        if check_free_spot(frame, kcf_box,initial_box,70) and  not not_send:
            #t1 = threading.Thread(target=send_SMS, args=("New free spot!", '+40745273125'))
            #t1.start()
            not_send = True

        if kcf_succes :
            kcf_color = (0, 0, 255)
            update_box(frame, kcf_color, kcf_box)
        else:
            kcf_tracker.init(first_frame, initial_box)
            #cv2.putText(frame, "Tracking on kcf failure detected", (0, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 2)

        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
        cv2.putText(frame, "KCF" + " Tracker", (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, "FPS : " + str(int(fps)), (0,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50,170,50), 2)

        try:
            cv2.imshow("Frame", frame)
        except:
            break

        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break

    show_results(initial_box[0], initial_box[1], kcf_box, video_source, video)
    cv2.destroyAllWindows()

find_parking_spot(False,"./videos/car2.mp4")

