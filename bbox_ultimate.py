# -*- coding:utf-8 –*-

from tkinter import *
from tkinter.messagebox import *
from PIL import Image, ImageTk
import tkinter.filedialog
import imageio
import os
import shutil
import pickle


class MyApp:
    def __init__(self):
        self.root = Tk()
        self.root.title("BBOX GETTER")

        self.directory = ""
        self.submitflag = True
        self.frameflag = True
        self.lastframe = False
        self.videonum = 0
        self.frame = 0
        self.bboxnum = 0
        self.point = []
        self.currentvideo = -1
        self.videolist = []
        self.tags = []
        self._tags = []
        self.bboxdata = []
        self.rawsize = ()
        self.imageSize = (600, 400)
        self.imgInfo = NONE

        # 标题
        self.title = Label(self.root, text="BBOX GETTER", font=("Arial", 20), width=20)
        self.title.grid(row=0, column=0, columnspan=3, ipadx=160, ipady=25, sticky=N + W)

        # 保存按钮
        self.save = Button(self.root, text="Save Out", height=3, width=15)
        self.save.grid(row=0, column=3, padx=20, pady=10, sticky=W)
        self.save.bind("<Button-1>", self.saveButton)

        # 导入下一个视频按钮
        self.nextVideo = Button(self.root, text="Next Video", height=3, width=15)
        self.nextVideo.grid(row=2, column=3, padx=20, pady=20, sticky=W)
        self.nextVideo.bind("<Button-1>", self.VideoNext)

        # 导入下一帧按钮
        self.nextFrame = Button(self.root, text="Next Frame", height=3, width=15)
        self.nextFrame.grid(row=1, column=3, padx=20, pady=20, sticky=W)
        self.nextFrame.bind("<Button-1>", self.FrameNext)

        # 画布
        self.canvas = Canvas(self.root, width=600, height=400, bg="white")
        self.canvas.grid(row=1, rowspan=2, column=0, columnspan=3, padx=20, pady=10, sticky=W)
        self.canvas.bind("<Button-1>", self.getPointGraph)

        # 提交按钮
        self.submit = Button(self.root, text="Submit", height=3, width=15)
        self.submit.grid(row=3, column=3, padx=20, pady=20, sticky=E)
        self.submit.bind("<Button-1>", self.submitButton)

        # 清除所画的BBOX
        self.clear = Button(self.root, text="Clear Last BBOX", height=3, width=15)
        self.clear.grid(row=3, column=0, padx=20, pady=20, sticky=W)
        self.clear.bind("<Button-1>", self.removeLastbbox)

        # 选择文件夹
        self.openfile = Button(self.root, text="Open Folder", height=3, width=15)
        self.openfile.grid(row=3, column=1, padx=20, pady=20, sticky=W)
        self.openfile.bind("<Button-1>", self.fileChosen)

        # 退出
        self.exitbut = Button(self.root, text="Exit", height=3, width=15)
        self.exitbut.grid(row=3, column=2, padx=20, pady=20, sticky=W)
        self.exitbut.bind("<Button-1>", self.exitButton)

        self.root.mainloop()

    def exitButton(self, event):
        if askyesno("Reminder", "Are you sure to exit ?"):
            self.root.destroy()
        else:
            return

    def demoPic(self):
        # 导入视频图片

        self.rawsize = self.imgInfo.size
        newsize = self.imageSize
        self.imgInfo = self.imgInfo.resize(newsize)
        self.imgInfo = ImageTk.PhotoImage(self.imgInfo)
        self.canvas.create_image(0, 0, image=self.imgInfo, anchor=NW)

    def fileChosen(self, event):
        self.directory = tkinter.filedialog.askdirectory()

        self.getEachVideo()
        # print(self.directory)
        if os.path.exists(self.directory+"/pickledata.pkl"):
            pklfile = open(self.directory+"/pickledata.pkl", "rb")

            update = pickle.load(pklfile)

            # self.directory = update[0]
            self.submitflag = update[1]
            self.frameflag = update[2]
            self.videonum = update[3]
            self.frame = update[4]
            self.bboxnum = update[5]
            self.point = update[6]
            self.currentvideo = update[7]
            self.videolist = update[8]
            self.tags = update[9]
            self._tags = update[10]
            self.bboxdata = update[11]
            self.rawsize = update[12]
            self.imageSize = update[13]
            self.lastframe = update[14]

            pklfile.close()

    def transfer(self):
        newbbox = []

        for i in self.bboxdata:
            temp = []
            for j in i:
                temp.append((int(j[0] / float(self.imageSize[0]) * self.rawsize[0]), int(j[1] / float(self.imageSize[1]) * self.rawsize[1])))
            newbbox.append(tuple(temp))

        return newbbox

    def submitButton(self, event):
        if self.submitflag:
            showwarning(title="Reminder", message="Sorry. You have already submitted your bboxs.")
            return
        if self.bboxnum == 0 and self.lastframe == False:
            showwarning(title="Reminder", message="Sorry. You cannot submit since you have not mark the bboxs. "
                                                  "Submit if you have marked the bboxs or you have read all frames.")
            return
        outfile = open(self.directory+"/bboxdata.txt", "a")
        ansbbox = self.transfer()

        print(self.videolist[self.currentvideo][1], end=' ', file=outfile)
        print(self.frame + 1, end=' ', file=outfile)
        if len(ansbbox):
            for _item in ansbbox:
                for item in _item:
                    print("%d %d" % (item[0], item[1]), end=' ', file=outfile)
        else:
            print("%d %d %d %d" % (0, 0, 0, 0), end=' ', file=outfile)
        print("\n", end='', file=outfile)

        outfile.close()

        self.submitflag = True
        self.frameflag = False
        self.lastframe = False
        self.nextFrame.config(state="disabled")
        self.nextVideo.config(state="normal")
        self.submit.config(state="disabled")

        for element in self._tags:
            self.canvas.delete(self.canvas.find_withtag(element)[0])
        for element in self.tags:
            self.canvas.delete(self.canvas.find_withtag(element)[0])
        self._tags = []
        self.tags = []
        self.bboxnum = 0
        self.point = []
        self.bboxdata = []

        datapack = [self.directory, self.submitflag, self.frameflag, self.videonum, self.frame, self.bboxnum,
                    self.point, self.currentvideo, self.videolist, self.tags, self._tags, self.bboxdata,
                    self.rawsize, self.imageSize, self.lastframe]
        pickleoutfile = open(self.directory+"/pickledata.pkl", "wb")
        pickle.dump(datapack, pickleoutfile)
        pickleoutfile.close()

    def saveButton(self, event):
        subdirectory = tkinter.filedialog.askdirectory()
        shutil.copy(self.directory+"/bboxdata.txt", subdirectory)

    def graph1(self):
        self.tags.append('#' + str(self.bboxnum))
        self.bboxnum += 1
        self.canvas.create_rectangle(self.point[0], self.point[1], outline="red", width=3, tags=self.tags[-1])

    def graph2(self):
        radius = 1.5
        self._tags.append('*' + str(self.bboxnum))
        self.canvas.create_oval(self.point[0][0]-radius, self.point[0][1]-radius, self.point[0][0]+radius,
                                self.point[0][1]+radius, fill="red", outline="red", tags=self._tags[-1])

    def getPointGraph(self, event):
        if len(self.point) == 0:
            self.point.append((event.x, event.y))
            self.graph2()
        else:
            self.point.append((event.x, event.y))
            self.graph1()
            self.bboxdata.append(tuple(self.point))
            self.point = []

    def removeLastbbox(self, event):
        try:
            if len(self._tags) == len(self.tags)+1:
                self.canvas.delete(self.canvas.find_withtag(self._tags[-1])[0])
                del self._tags[-1]
                self.point = []
            self.canvas.delete(self.canvas.find_withtag(self._tags[-1])[0])
            self.canvas.delete(self.canvas.find_withtag(self.tags[-1])[0])
        except:
            showwarning(title="Reminder", message="All the BBoxs have been cleared!")
            return
        del self._tags[-1]
        del self.tags[-1]
        self.bboxnum -= 1
        del self.bboxdata[-1]

    def getEachVideo(self):
        path = self.directory

        lst = os.listdir(path)
        for videoname in lst:
            if videoname != "bboxdata.txt" and videoname != "pickledata.pkl":
                videopath = os.path.join(path, videoname)
                self.videolist.append((videopath, videoname))
        self.videonum = len(self.videolist)

    def VideoNext(self, event):
        if not self.submitflag:
            showwarning(title="Reminder", message="Sorry. You cannot click Next Video before submitting the bboxs!")
            return
        self.nextVideo.config(state="disabled")
        self.nextFrame.config(state="normal")
        self.submit.config(state="normal")
        self.submitflag = False
        self.frameflag = True
        self.frame = 0
        self.currentvideo += 1
        if self.currentvideo == self.videonum:
            showinfo(title="Reminder", message="You have completed all the videos. Thank you so much! Save out and Exit.")
            return
        vidpath = self.videolist[self.currentvideo][0]
        try:
            vid = imageio.get_reader(vidpath, "ffmpeg")
        except:
            showwarning(title="Reminder", message="The video is broken. Abandon it and Click Next Video.")
            return
        tempimg = vid.get_data(self.frame)
        self.imgInfo = Image.fromarray(tempimg)

        self.demoPic()

    def FrameNext(self, event):
        if not self.frameflag:
            showwarning(title="Reminder",
                        message="Sorry. You cannot click Next Frame since you have submitted the bboxs.")
            return
        if self.bboxnum != 0:
            if not askyesno("Reminder", "There are still bboxs remaining. Are you sure to clear them and "
                                        "step into the next frame ?"):
                return
        for element in self._tags:
            self.canvas.delete(self.canvas.find_withtag(element)[0])
        for element in self.tags:
            self.canvas.delete(self.canvas.find_withtag(element)[0])
        self._tags = []
        self.tags = []
        self.bboxnum = 0
        self.point = []
        self.bboxdata = []

        self.frame += 5

        vidpath = self.videolist[self.currentvideo][0]
        vid = imageio.get_reader(vidpath, "ffmpeg")
        try:
            tempimg = vid.get_data(self.frame)
        except:
            self.lastframe = True
            showwarning(title="Reminder",
                        message="The video has run out of all the frames. Abandon it and click Submit and Next Video.")
            return
        self.imgInfo = Image.fromarray(tempimg)

        self.demoPic()


app = MyApp()
