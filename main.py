from event_advertiser import EventAdvertiser
from chart_generator import ChartGenerator
from ast import literal_eval as make_tuple


def get_stats():
    print("Starting...")
    video_sources = []
    video_boxes = []
    with open("./../stats/video_boxes2.txt") as fp:
        line = fp.readline()
        while line:
            video_sources.append(line.split(' ',1)[0])
            video_boxes.append((line.split(' ',1)[1].rstrip()))
            line = fp.readline()

    parsed_video_boxes = [ ]
    for video_box in video_boxes:
        parsed_video_boxes.append(make_tuple(video_box))

    backup_trackers = ['CSRT','MIL','MEDIANFLOW']

    for backup_tracker in backup_trackers :
        for i in range(0,len(video_sources)):
            event_advertiser = EventAdvertiser(video_sources[i], False, parsed_video_boxes[i],backup_tracker)
            event_advertiser.find_parking_spot()

    #chart_generator = ChartGenerator('cataploty', 'WhW3fYZJLVlnFF0syU0m')
    #chart_generator.generate_chart()
    #print("Done!")

#get_stats()


def event_advertiser_test():
    print("1.Mil")
    print("2.Median")
    print("3.Csrt")
    backup_tracker_option = input("Choose backup tracker : ")


    use_camera = input("Do you want to use camera ? yes / no ")
    if use_camera == 'yes':
        use_camera = True
    elif use_camera == 'no':
        use_camera = False
        print("Available videos  :")
        for i in range(1,15):
            print("car"+str(i) + ".mp4")

        video_number = input("Select video number: ")
        video_source = "./../videos/car" + video_number + ".mp4"
    else:
        print("Ooups the options are yes or no!")

    if backup_tracker_option == '1':
        event_advertiser = EventAdvertiser(video_source, use_camera, None, 'MIL')
        event_advertiser.find_parking_spot()
    elif backup_tracker_option == '2':
        event_advertiser = EventAdvertiser(video_source, use_camera, None,'MEDIANFLOW')
        event_advertiser.find_parking_spot()
    elif backup_tracker_option == '3':
        event_advertiser = EventAdvertiser(video_source, use_camera, None, 'CSRT')
        event_advertiser.find_parking_spot()
    else:
        print("Ooups the options are 1  2 or 3 !")

event_advertiser_test()