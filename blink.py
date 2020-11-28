# python blink.py
import cv2   # pip install opencv-python
import psutil
from win10toast import ToastNotifier # pip install win10toast psutil
from threading import Thread
import csv
from time import sleep as nap , time
import random

# wrapper
def in_thread(func):
    def wraper(*args,**kwargs):
        # print('running function in thread')
        Thread(target=lambda : func(*args,**kwargs),daemon=True).start()
    return wraper

class blink:
    def __init__(self,debug = False,time_limit = 2):
        global data_file
        self.debug = debug
        self.time_limit = time_limit*60   # in time_limit min program will stop

        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        # this line is specific for the windows else: self.cam = cv2.VideoCapture(0)
        self.cam = cv2.VideoCapture(0,cv2.CAP_DSHOW)

        self.eye_in_last_frame = False
        self.blink_count = 0
        self.data_saved  = False
        self.run_from_bg_function = False
        data_file = f'{round(time())}-data.csv'
        print(f'your data file is {data_file}')
        self.data_file_name = data_file
    
    def __enter__(self):
        # creating a file
        open(self.data_file_name,'w').close()
        self.data_file = open(self.data_file_name,'w+',newline='')
        # save with only two columns time and blinks
        self.fields = ['Time Taken','Blinks']
        self.file_writer = csv.DictWriter(self.data_file, fieldnames=self.fields)
        self.file_writer.writeheader()

        self.start = time()
        self.run_time = time()
        return self
    
    def __exit__(self, type, value, traceback):
        # save last value in the end of the file 
        # check if this data saved else save
        if not self.data_saved :
            try:
                self.save_data(self.time_spent,self.blink_count)
            except Exception as e :
                # not expecting error here if does just remove excetion as e add print e and add pass 
                print(e)
                
        self.data_file.close()
        self.cam.release()

        # show results
        self.analyse_collected_data()
        
    @staticmethod
    def analyse_collected_data():
        # return result for the program
        # analyse the data colleted 
        time_taken = 0
        blink = 0
        with open(data_file,'r',newline='') as f :
            file_data = csv.DictReader(f)
            # heads of the file use in later to extract data
            fields = file_data.fieldnames
            # adding all collected data 
            for dict_line in file_data :
                time_taken += float(dict_line[fields[0]])
                blink += int(dict_line[fields[1]])
            
        #  average results should be 15 to 20 times in a minute 
        # average blink rate in one minute by unitary method
        average_blink= round((blink/time_taken)*60)
        # print(time_taken,blink)
        print(f'your average blink is {average_blink} times in a minutes.')
        return average_blink

    @in_thread
    def show_notification(self,message,title='Blinker',icon_path = 'eye.ico',duration = 10 ):
        toaster = ToastNotifier()
        toaster.show_toast(title,message,icon_path = icon_path ,duration=duration)

    @property
    def time_spent(self):
        # return time in seconds 
        end = round(time() - self.start ,2)
        return end
    
    @in_thread
    def save_data(self,time_taken,blinks):
        # save data in csv file for later analysing
        self.file_writer.writerow({'Time Taken':time_taken,'Blinks':blinks})

    def face_coordinates(self,img):
        # compressed image by 4 times 
        compressed = cv2.resize(img,(int(img.shape[1]*0.5),int(img.shape[0]*0.5)))
        # convert into black and white image  
        grey = cv2.cvtColor(compressed,cv2.COLOR_BGR2GRAY)
        # filter to clear the noise
        filter_gray = cv2.bilateralFilter(grey,5,1,1)

        face_coordinates = self.face_cascade.detectMultiScale(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY))
        return face_coordinates
    
    def blink_collector(self) :
        while True:
            _,img = self.cam.read()
            coordinates = self.face_coordinates(img)
            self.data_saved  = False

            # work on only one face 
            if len(coordinates) == 1 :
                # ploting the cordinates if there is only one face is there
                x,y,w,h = coordinates[0]
                # drow rectangle on screen 
                if self.debug : cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                # cut the image only face to ninimise the processing 
                just_face = img[y:y+h,x:x+w]
                # detect eye possitions
                eye = self.eye_cascade.detectMultiScale(just_face,1.3,5)
                
                # eye will only detected when eye is open 
                # only if both eye are detected 
                # if ele is blink then one frame have no eye in it that mean eye blink
                # this method works good but if there is any interference between eye program can see it as no eye (ex- sometimes glasses)
                if len(eye) == 2:
                    # print('eyes dete  cted')
                    for (ex,ey,ew,eh) in eye:
                        # because eye is in face then the possiton can be face + eye_relative to face 
                        self.eye_in_last_frame = True
                        if self.debug:
                            cv2.rectangle(img,(x+ex,y+ey),(x+ex+ew,y+ey+eh),(255,0,0),2)
                            cv2.putText(img,f"blinks:{self.blink_count}",(50,50),cv2.FONT_HERSHEY_PLAIN, 3, (0,255,0),2) 
                            cv2.putText(img,f"time:{self.time_spent}",(300,50),cv2.FONT_HERSHEY_PLAIN, 3, (0,255,0),2) 
                else:
                    # if less or no eye found then consider it closed
                    # print('eye not found')
                    if self.eye_in_last_frame:
                        self.blink_count += 1
                        self.eye_in_last_frame = False
            
            else:
                self.save_data(self.time_spent,self.blink_count)
                self.data_saved  = True                
                # if no person or nore then 1 preson found -> sleep and restart the clock  
                if not self.debug:
                    nap(0.3)
                self.start = time()
                self.blink_count = 0
                # save the results here 

            # show image in cv2 take 2 arrg =window name , image
            if self.debug :
                cv2.imshow('stream',img)
                key = cv2.waitKey(1)
                if key == 81 or key == 27 :
                    cv2.destroyAllWindows()
                    self.closed  = True
                    break
            
            # close the program after self.time_limit if running in background
            if (time() - self.run_time) >= self.time_limit and (not self.debug ) and (not self.run_from_bg_function) : 
                # break the program if it runs more then 20 min 
                print(f'program run for last {round(time() - self.run_time)} seconds sufficiant data collected 😉')
                break 

    # #############################
    def bg_blink_collector(self) :
        while True:
            _,img = self.cam.read()
            coordinates = self.face_coordinates(img)

            # work on only one face 
            if len(coordinates) == 1 :
                print('face')
                # ploting the cordinates if there is only one face is there
                x,y,w,h = coordinates[0]
                # cut the image only face to ninimise the processing 
                just_face = img[y:y+h,x:x+w]
                # detect eye possitions
                eye = self.eye_cascade.detectMultiScale(just_face,1.3,5)
                
                if len(eye) == 2:
                    for _ in eye:
                        # because eye is in face then the possiton can be face + eye_relative to face 
                        self.eye_in_last_frame = True
                else:
                    # if less or no eye found then consider it closed
                    print('eye not found')
                    if self.eye_in_last_frame:
                        self.blink_count += 1
                        self.eye_in_last_frame = False
            
            else:
                self.save_data(self.time_spent,self.blink_count)
                
                self.data_saved  = True                
                # if no person or nore then 1 preson found -> sleep and restart the clock  
                if not self.debug:
                    nap(0.3)
                self.start = time()
                self.blink_count = 0
    
    # #############################

    def bg_thread(self):
        # run the Thread for bg blink collecter
        blink_time,blinks = [],[]   
        last_notification_sent_time = time()
        min_interval_in_each_notification = 20*60   # notification after every 20 mins
        self.show_notification(f'Stating Blink Recording...')

        # collect all time spent and blink_count 
        while not self.kill_thread :
            # first save the data in list
            blink_time.append(self.time_spent)
            blinks.append(self.blink_count)

            # clearing some space in list by checking the list elements
            while sum(blink_time) > 5:
                if sum(blink_time) - blink_time[0] >= 5:
                    blink_time.pop(0)
                    blinks.pop(0)
                else:
                    break

            # taking actions for the program
            # take actions - send notification to the user 
            if sum(blink_time) >= 5 :
                # if sum the blink is 0 in last 5s and prevent to send notification again and again
                if ( sum(blinks) == 0 ) and (time() - last_notification_sent_time >= min_interval_in_each_notification ):
                    self.show_notification(f'Blink, You didn\'t blink for about last {round(sum(blink_time))} seconds\nAlso stretch and straight your posture')
                    # update last_notification_sent_time value to current time of notification send  
                    last_notification_sent_time = time()
                    # sleep for next 15 mins to save some processing power
                    print('user notified sleep for next 15 min')
                    nap(15*60)

            # for testing
            # print(round(sum(blink_time)),sum(blinks),end='\n\n')

                            
    # there is 3 versions
    @classmethod
    def once(cls):
        # 1. run of only 20 min to check your eye status once only
        print('Running for the 2 min to test the average blink time')
        with cls() as blink:
            # this will run in background and collect data 
            print('starting the camere')
            blink.blink_collector()
            blink.show_notification('data collection completed \nstating analysing the data')

    @classmethod
    def debuging(cls):
        '''This is debuging mode use to debug the program by representing the all process'''
        # 2. run in debug mode 
        print('running the debuging mode')
        with cls(debug=True) as blink:
            blink.blink_collector()
        
    @classmethod
    def bg(cls):
        # 3. run in background for ever until you stop it by [ctrl+c]
        '''bg will run you program in background and notify you ragularly in intervals'''    
        # your camera should be of good quality for acurate results
        try:
            with cls() as blink:
                cls.kill_thread = False
                cls.run_from_bg_function = True
                Thread(target=blink.bg_thread).start()
                blink.blink_collector()

        except KeyboardInterrupt:
            cls.kill_thread = True
            print('Program Forced stoped 😗')



if __name__ == '__main__':
    # blink.debuging()
    blink.bg()



