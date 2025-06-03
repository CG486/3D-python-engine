#3D renderer version 0.12
#This project intended to display a 3D scene on a 2D screen.


#Imports modules
import time
import math
import tkinter as tk
import threading as t
import multiprocessing as SMT


class shape:
    def __init__(self, input):
        self.input = input
        __display__.root.bind("<<update>>", self.update)


    def update(self, event):
        __display__.coordinates += self.input


class display:
    def __init__(self, x = 0, y = 0, z = 1280, yaw = 0, pitch = 0, roll = 0, framerate_max = 1000, process_count = 1, x_res=1280, y_res=720):
        global __display__
        __display__ = self
        
        #Sets up variables
        self.coordinates = []
        self.process_count = process_count
        self.framerate_max = framerate_max


        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll
        self.x_res = x_res
        self.y_res = y_res
        self.camera_yaw = 0
        self.camera_pitch = 0
        self.camera_roll = 0


        self.count = 0
        self.Cycle_1 = True
        self.done = False


        #Creates shared spaces to send inputs to other threads
        self.output_queue = SMT.JoinableQueue()
        self.input_queue = SMT.JoinableQueue()


        #Creates the threads that plot the coordinates.
        A_0 = []
        for i in range(self.process_count): 
            A_0.append(SMT.Process(target=__worker__, args=(self.input_queue, self.output_queue), daemon=True, name="Worker"))
            A_0[i].start()


        self.Events = t.Thread(target=self.__events__, daemon=True)
        self.Events.start()


        while (self.done == False): time.sleep(1)


        self.Update = t.Thread(target=self.__refresh__, daemon=True)
        self.Update.start()


    def __events__(self):
        #Starts renderer
        self.root = tk.Tk()
        self.root.title("")
        self.root.bind("<Configure>", self.__resize__)
        self.root.bind('<Motion>', self.__mouse__)
        self.root.bind("<Key>", self.__wasd__)
        self.canvas = tk.Canvas(self.root, width=self.x_res, height=self.y_res)
        self.canvas.pack(fill="both", expand=True)
        self.done = True
        self.root.mainloop()
        
    def __refresh__(self):
        while True:
            self.coordinates = []
            self.root.event_generate("<<update>>")


            temp_2 = []
            for i in self.coordinates:
                temp_2.append([i, self.x, self.y, self.z, self.yaw, self.pitch, self.roll, self.camera_yaw, self.camera_pitch, self.camera_roll, self.x_res, self.y_res])
                
            for i in range(self.process_count):
                #Sends the coordinates
                self.input_queue.put(temp_2[6*i:6*(i+1)])


            self.input_queue.join()


            #Retrives the coordinates. Threading is asynchronous, so these are not necessarily the outputs of the coordinates above. 
            #Old image is only cleared after new image is finished drawing, to prevent flickering.


            for i in range(self.process_count):
                A = self.output_queue.get()
                if (self.Cycle_1): 
                    for i in A: 
                        if (len(i) > 0): self.canvas.create_polygon(i, width=10, tags=('__Cycle_1__'), fill=None)
                else: 
                    for i in A:
                        if (len(i) > 0): self.canvas.create_polygon(i, width=10, tags=('__Cycle_2__'), fill=None)
                self.output_queue.task_done()
            
            if (self.Cycle_1): 
                self.canvas.delete('__Cycle_2__')
                self.Cycle_1 = False
            
            else: 
                self.canvas.delete('__Cycle_1__')
                self.Cycle_1 = True
                
            self.count = 0
            time.sleep(1/self.framerate_max)


    def wait(self, input = 1): time.sleep(input)


    def __resize__(self, event):
        """Calculates the resolution if the window is resized"""
        self.x_res = self.root.winfo_width()
        self.y_res = self.root.winfo_height()


    def __mouse__(self, event):
        self.camera_yaw = event.x - 0.5*self.x_res
        self.camera_pitch = event.y - 0.5*self.y_res


    def __wasd__(self, event): # Handles keypress, this is the main user input.
        
        #Sets up variables
        key = event.char


        #Angle controls
        if "q" in key: self.roll-=10
        if "e" in key: self.roll+=10
        if "a" in key: self.yaw-=10
        if "d" in key: self.yaw+=10
        if "w" in key: self.pitch-=10
        if "s" in key: self.pitch+=10


        #Movement controls
        if "j" in key: self.x-=10
        if "l" in key: self.x+=10
        if "y" in key: self.y-=10
        if "h" in key: self.y+=10
        if "k" in key: self.z-=10
        if "i" in key: self.z+=10


        #Angle controls, capitalized in case caps lock is pressed
        if "Q" in key: self.roll-=10
        if "E" in key: self.roll+=10
        if "A" in key: self.yaw-=10
        if "D" in key: self.yaw+=10
        if "W" in key: self.pitch-=10
        if "S" in key: self.pitch+=10


        #Movement controls, capitalized in case caps lock is pressed
        if "J" in key: self.x-=10
        if "L" in key: self.x+=10
        if "Y" in key: self.y-=10
        if "H" in key: self.y+=10
        if "K" in key: self.z-=10
        if "I" in key: self.z+=10


        #Numpad controls, because I wanted it
        if "4" in key: self.x-=10
        if "6" in key: self.x+=10
        if "7" in key: self.y-=10
        if "1" in key: self.y+=10
        if "2" in key: self.z-=10
        if "8" in key: self.z+=10


class __worker__:
    def __init__(self, input_queue, output_queue):
        while True:
            output = []
            temp = input_queue.get()
            for i in temp:
                output.append(self.__draw_shape__(i))
            output_queue.put(output)
            input_queue.task_done()
            output_queue.join()
                


    def __draw_shape__(self, input):
        #Sets up variables, (some need to be retrived from the main thread)
        temp = input[0]
        x = input[1]
        y = input[2]
        z = input[3]
        yaw = -math.pi*(input[4]/180)
        pitch = math.pi*(input[5]/180)
        roll = math.pi*(input[6]/180)
        camera_yaw = math.pi*(input[7]/180)
        camera_pitch = -math.pi*(input[8]/180)
        camera_roll = math.pi*(input[9]/180)
        x_res = input[10]
        y_res = input[11]


        temp = self.__yaw__(temp, yaw)
        temp = self.__pitch__(temp, pitch)
        temp = self.__roll__(temp, roll)
        temp = self.__translate__(temp, x, y, z)
        temp = self.__yaw__(temp, camera_yaw)
        temp = self.__pitch__(temp, camera_pitch)
        temp = self.__roll__(temp, camera_roll)
        temp = self.__draw__(temp, x_res, y_res)


        return temp


    def __draw__(self, input = [], x_res = 1280, y_res = 720):
        output = []
        for i in input:
            if (i[2] > 0):
                yaw_2 = math.atan2(i[0], i[2])
                pitch_2 = math.atan2(i[1], i[2])
                x_2 = i[0]/(i[2]/x_res)
                y_2 = i[1]/(i[2]/x_res)


                x_temp=(
                    math.cos(pitch_2)
                    *math.sin(yaw_2)
                ) #Calculates x position from angle


                y_temp=(
                    math.sin(pitch_2)
                    *math.cos(yaw_2)
                ) #Calculates y position from angle


                output.append([
                        x_temp + (x_res / 2) + x_2,
                        y_temp + (y_res / 2) + y_2,
                ])


        return output


    def __translate__(self, input = [], x = 0, y = 0, z = 0):
        output = []
        for i in input:
            output.append([i[0] + x, i[1] + y, i[2] + z])
        return output


    def __yaw__(self, input = [], angle = 0):
        output = []
        for i in input:
            output.append([
                i[0] * math.cos(angle) - i[2] * math.sin(angle),
                i[1],
                i[2] * math.cos(angle) + i[0] * math.sin(angle)
            ])
        return output


    def __pitch__(self, input = [], angle = 0):
        output = []
        for i in input:
            output.append([
                i[0],
                i[1] * math.cos(angle) - i[2] * math.sin(angle),
                i[2] * math.cos(angle) + i[1] * math.sin(angle)
            ])
        return output


    def __roll__(self, input = [], angle = 0):
        output = []
        for i in input:
            output.append([
                i[0] * math.cos(angle) - i[1] * math.sin(angle),
                i[1] * math.cos(angle) + i[0] * math.sin(angle),
                i[2]
            ])
        return output