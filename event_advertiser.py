import cv2
import sys, time
from copy import deepcopy
import numpy
import threading
from sms_sender import SmsSender


class EventAdvertiser:
    def __init__(self, video_source, use_camera,bounding_box,backup_tracker):
        self.video_source = video_source
        self.use_camera = use_camera
        self.bounding_box = bounding_box
        self.backup_tracker = backup_tracker

    def update_box(self, frame, color, tracker_box):
        p1 = (int(tracker_box[0]), int(tracker_box[1]))
        p2 = (int(tracker_box[0] + tracker_box[2]), int(tracker_box[1] + tracker_box[3]))
        cv2.rectangle(frame, p1, p2, color, 2, 1)

    def log_bounding_box(self, start_x, start_y, tracker_box, video_source, video):
        width = video.get(3)
        # print("X:" + str(abs(tracker_box[0] - start_x)))
        # print("Y:" + str(abs(tracker_box[1] - start_y)))
        f = open("./../stats/kcf_bound.txt", "a")
        f.write("Video source :" + video_source + "\n")
        f.write("X:" + str(start_x) + " " + "Y:" + str(start_y) + "\n")
        f.write("X:" + str(abs(tracker_box[0] - start_x)) + "  " + "Y:" + str(abs(tracker_box[1] - start_y)) + "\n")
        f.write("Video width :" + str(width) + "\n")
        f.write("\n")

    def log_message(self,filename,message):
        f = open(filename,"a")
        f.write(message)

    def get_tracker(self, tracker_type):
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

    def get_video(self, using_camera, video_source):
        if using_camera:
            video = cv2.VideoCapture(0)
            time.sleep(1.0)
        else:
            video = cv2.VideoCapture(video_source)
            if not video.isOpened():
                print("Could not open video")
                sys.exit()
        return video

    def check_free_spot(self, frame, tracker_box, initial_box, bound):
        if abs(initial_box[0] - int(tracker_box[0])) >= bound or abs(initial_box[1] - int(tracker_box[1])) >= bound:
            cv2.putText(frame, "New free spot !", (250, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            p1 = (int(initial_box[0]), int(initial_box[1]))
            p2 = (int(initial_box[0] + initial_box[2]), int(initial_box[1] + initial_box[3]))
            cv2.rectangle(frame, p1, p2, (0, 255, 0), 2, 1)
            return True

        return False

    def find_parking_spot(self):
        video = self.get_video(self.use_camera, self.video_source)
        video_width = video.get(3)

        kcf_tracker = self.get_tracker('KCF')
        backup_tracker = self.get_tracker(self.backup_tracker)

        first_frame = video.read()[1]
        if video_width < 1280:
            first_frame = cv2.resize(first_frame, (1280, 720))

        if self.bounding_box is None:
            kcf_box = cv2.selectROI(first_frame, False)
        else:
            kcf_box = self.bounding_box

        initial_box = deepcopy(kcf_box)

        kcf_tracker.init(first_frame, kcf_box)

        not_send = False
        use_backup = False
        backup_succes = False
        start = time.time()

        while True:

            frame = video.read()[1]

            timer = cv2.getTickCount()

            if video_width < 1280:
                try:
                    frame = cv2.resize(frame, (1280, 720))
                except:
                    break
            save = deepcopy(kcf_box)

            kcf_succes, kcf_box = kcf_tracker.update(frame)

            if use_backup:
                backup_succes, backup_box = backup_tracker.update(frame)

            if self.check_free_spot(frame, kcf_box, initial_box, 70) and not not_send:
                stop = time.time()
                self.log_message("./../stats/time", self.video_source + " " + str(initial_box) + " " + "KCF+" + self.backup_tracker + " a detectat loc liber dupa :" + str(stop - start) + "s" + "\n")
                # sender = SmsSender("New free spot!", '+40745273125')
                # t1 = threading.Thread(target=sender.send_SMS, args=(sender.message, sender.to))
                # t1.start()

                not_send = True

            if kcf_succes:
                use_backup = False
                kcf_color = (0, 0, 255)
                self.update_box(frame, kcf_color, kcf_box)
                cv2.putText(frame, "KCF" + " Tracker", (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            else:
                if not use_backup:
                    cv2.putText(frame, "Tracking on KCF failure detected", (0, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 0, 255), 2)
                    backup_box = deepcopy(save)
                    backup_tracker.init(frame, backup_box)
                    use_backup = True

            if backup_succes:
                kcf_color = (0, 0, 255)
                self.update_box(frame, kcf_color, backup_box)
                cv2.putText(frame, self.backup_tracker + " Tracker", (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            elif not backup_succes and use_backup:
                self.log_message("./../stats/errors","Eroare : " + self.video_source + " " + str(initial_box) + " " + "KCF+" + self.backup_tracker + "\n")
                cv2.putText(frame, "Tracking on " + self.backup_tracker + " failure detected", (0, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 2)

            fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
            cv2.putText(frame, "FPS : " + str(int(fps)), (0, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 170, 50), 2)

            try:
                cv2.imshow("Frame", frame)
            except:
                break

            k = cv2.waitKey(1) & 0xff
            if k == 27:
                break
        final_stop = time.time()
        self.log_message("./../stats/total_time.txt","Total time : " + str(final_stop - start) + "\n")
        self.log_bounding_box(initial_box[0], initial_box[1], kcf_box, self.video_source, video)
        cv2.destroyAllWindows()
