import plotly.plotly as py
import plotly
import plotly.graph_objs as go
import cv2
import sys, time
from twilio.rest import Client
from copy import deepcopy
from ast import literal_eval as make_tuple
import numpy
import threading

def get_tracker(tracker_type):
    if tracker_type == 'BOOSTING':
        tracker = cv2.TrackerBoosting_create()
    if tracker_type == 'MIL':
        tracker = cv2.TrackerMIL_create()
    if tracker_type == 'KCF':
        tracker = cv2.TrackerKCF_create()
    if tracker_type == "CSRT":
        tracker = cv2.TrackerCSRT_create()
    if tracker_type == 'MEDIANFLOW':
        tracker = cv2.TrackerMedianFlow_create()
    return tracker

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

def update_box(frame,color,tracker_box):
    p1 = (int(tracker_box[0]), int(tracker_box[1]))
    p2 = (int(tracker_box[0] + tracker_box[2]), int(tracker_box[1] + tracker_box[3]))
    cv2.rectangle(frame, p1, p2, color, 2, 1)

def check_free_spot(frame,tracker_box,initial_box, bound):
    # print("X :" + str(abs(initial_box[0] - int(tracker_box[0]))) + " Y : " +  str(abs(initial_box[1] - int(tracker_box[1]))))
    if (abs(initial_box[0] - int(tracker_box[0])) >= bound and abs(initial_box[1] - int(tracker_box[1])) >= bound) or \
            (abs(initial_box[0] - int(tracker_box[0])) >= 120) or (abs(initial_box[1] - int(tracker_box[1])) >= 120):
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
    client.messages \
        .create(
        body= message,
        from_='+12063396544',
        to=to
    )

def log_bounding_box(start_x,start_y,tracker_box , video_source, video):
    width = video.get(3)
    print("X:" + str(abs(tracker_box[0] - start_x)))
    print("Y:" + str(abs(tracker_box[1] - start_y)))
    f = open("./stats/kcf_bound.txt","a")
    f.write("Video source :" +  video_source + "\n")
    f.write("X:" + str(start_x)  + " " + "Y:" + str(start_y) + "\n")
    f.write("X:" + str(abs(tracker_box[0] - start_x)) + "  "  + "Y:" + str(abs(tracker_box[1] - start_y)) + "\n")
    f.write("Video width :" + str(width) + "\n")
    f.write("\n")

def find_parking_spot(using_camera, video_source,tracker_type,box):

    start = time.time()
    video = get_video(using_camera, video_source)
    video_width = video.get(3)

    kcf_tracker = get_tracker(tracker_type)

    first_frame = video.read()[1]
    if video_width < 1280:
        first_frame = cv2.resize(first_frame, (1280,720))


    kcf_box = box
    initial_box = deepcopy(kcf_box)
    kcf_tracker.init(first_frame, kcf_box)

    not_send = False
    frames = []
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
            stop = time.time()

            print("Result for : " + tracker_type + " " + str(stop-start))
            f = open("./stats/time","a")
            f.write(video_source + " " + str(box) + " " + tracker_type + " a detectat loc liber dupa : " + str(stop-start) + "s" + "\n")
            # sms_sender = threading.Thread(target=send_SMS, args=("New free spot!", '+40745273125'))
            #sms_sender .start()

            kcf_tracker.init(frame, initial_box)
            not_send = True

        if kcf_succes :
            kcf_color = (0, 0, 255)
            update_box(frame, kcf_color, kcf_box)
        else:
            f = open("./stats/errors", "a")
            f.write("Eroare : " + video_source + " " + str(box) + " " + tracker_type + "\n")
            kcf_tracker.init(frame, initial_box)
            cv2.putText(frame, "Tracking on kcf failure detected", (0, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 2)

        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
        frames.append(fps)
        cv2.putText(frame, tracker_type + " Tracker", (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, "FPS : " + str(int(fps)), (0,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50,170,50), 2)

        try:
            cv2.imshow("Frame", frame)
        except:
            break

        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break

    f = open("./stats/frames", "a")
    f.write(video_source + " " + str(box) + " " + tracker_type + " media fps : " + str(numpy.mean(frames))+"\n")
    log_bounding_box(initial_box[0], initial_box[1], kcf_box, video_source, video)
    cv2.destroyAllWindows()

def get_stats():
    trackers = ['KCF','CSRT','BOOSTING','MIL', 'MEDIANFLOW' , 'TLD']
    video_sources = []
    video_boxes = []
    with open("./stats/video_boxes.txt") as fp:
        line = fp.readline()
        while line:
            video_sources.append(line.split(' ',1)[0])
            video_boxes.append((line.split(' ',1)[1].rstrip()))
            line = fp.readline()

    parsed_video_boxes = [ ]
    for video_box in video_boxes:
        parsed_video_boxes.append(make_tuple(video_box))

    for tracker in trackers:
        for i in range(0,len(video_sources)):
            find_parking_spot(False,video_sources[i],tracker,parsed_video_boxes[i])

def generate_chart():
    kcf_errors = []
    mil_errors = []
    boosting_errors =[]
    csrt_errors = []
    median_errors =[]
    with open("./stats/errors") as fp:
        line = fp.readline()
        while line:
            if 'KCF' in line:
                kcf_errors.append(line.rstrip())
            if 'MIL' in line:
                mil_errors.append(line.rstrip())
            if 'BOOSTING' in line:
                boosting_errors.append(line.rstrip())
            if 'CSRT' in line:
                csrt_errors.append(line.rstrip())
            if 'MEDIANFLOW' in line:
                median_errors.append(line.rstrip())
            line = fp.readline()
    kcf_errors = set(kcf_errors)
    mil_errors = set(mil_errors)
    csrt_errors = set(csrt_errors)
    median_errors = set(median_errors)
    boosting_errors = set(boosting_errors)

    kcf_time = []
    mil_time = []
    boosting_time = []
    csrt_time = []
    median_time = []
    with open("./stats/time") as fp:
        line = fp.readline()
        while line:
            if 'KCF' in line:
                kcf_time.append(float(line.split(':')[1].rstrip().lstrip()[:-1]))
            if 'MIL' in line:
                mil_time.append(float(line.split(':')[1].rstrip().lstrip()[:-1]))
            if 'BOOSTING' in line:
                boosting_time.append(float(line.split(':')[1].rstrip().lstrip()[:-1]))
            if 'CSRT' in line:
                csrt_time.append(float(line.split(':')[1].rstrip().lstrip()[:-1]))
            if 'MEDIANFLOW' in line:
                median_time.append(float(line.split(':')[1].rstrip().lstrip()[:-1]))
            line = fp.readline()

    plotly.tools.set_credentials_file(username='cataploty', api_key='WhW3fYZJLVlnFF0syU0m')

    errors = go.Bar(
                x=['KCF', 'BOOSTING', 'MIL', 'MEDIAN', 'CSRT'],
                y=[len(kcf_errors)-3, len(boosting_errors), len(mil_errors), len(median_errors), len(csrt_errors)],
                name='Number of errors',
                marker=dict(
                    color='rgb(255, 0, 0)'
                )
            )

    time = go.Bar(
                x=['KCF', 'BOOSTING', 'MIL', 'MEDIAN', 'CSRT'],
                y=[numpy.mean(kcf_time), numpy.mean(boosting_time), numpy.mean(mil_time), numpy.mean(median_time), numpy.mean(csrt_time)],
                name='Time to first detection',
                marker=dict(
                    color='rgb(0, 255, 0)',
                )
            )

    data = [errors,time]
    layout = go.Layout(
                xaxis=dict(tickangle=-45),
                barmode='group',
            )
    fig = go.Figure(data=data, layout=layout)
    py.iplot(fig, filename='angled-text-bar')
    print("New chart generated at : " + "https://plot.ly/organize/home/")

#get_stats()
generate_chart()
