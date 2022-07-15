from unittest.mock import DEFAULT
import numpy as np
from enum import Enum
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Slider
import matplotlib.patches as patches
from skimage import measure

# without tactile data: 
# wineglass 0 3 9;
# smallshaker 0 4;
# longneckbottle 7；
# largeshaker 8；

# threthord：
# longneckbottle 0 palm无接触 有响应
# longneckbottle 1 3 8 tip1接触瞬间阈值异常大
# largeshaker掌心没有接触 4 5反复横跳+阈值异常 

# good data:
# longneckbottle 2 4 5 6
# smallshaker 3！ 5 7 8 9！
# wineglass 2 4 
# largeshaker 2 9

data_dir = "/home/wuyi/data/20220511"
object_name = "wineglass" #     smallshaker  wineglass  largeshaker  longneckbottle
experiment_num = "4"

INNER_TAC_NUM = 6*6
PALM_TAC_NUM = 10*10
TIP_TAC_NUM = 12*12

THRETHOLD_PERSENT = 0.2
THRETHOLD_ORDER = 0.999
THRETHOLD_DEFAULT = 100

class TacDataSet():
  def __init__(self):
    self.image_names = []
    self.data_num = 0
    #changed to ndarray
    self.palm, self.f0inn,self.f0tip,  self.f1inn,self.f1tip,  self.f2inn,self.f2tip = [],[],[],[],[],[],[]

  def openfile(self, datadir, object_name, experiment_num):
    self.datapath = datadir + '/' + object_name + '/' + experiment_num + '/'
    self.file_name = self.datapath + 'data.txt'
    with open(self.file_name, 'r') as file:
      file_lines = file.readlines()
      for line in file_lines:
        if(line[:2]=='16'):
          self.image_names.append(line[:-1])
          self.data_num += 1
        if(line[:3]=='640'):
          data = list(map(int, line[4:-1].split()))
          temp_data = np.array(data[0 : PALM_TAC_NUM]).reshape(10,10)
          #palm丢弃底行噪声
          temp_data[9,:] = 0 
          self.palm.append(temp_data)
          current_index = PALM_TAC_NUM
          self.f0inn.append(np.array(data[current_index : current_index + INNER_TAC_NUM]).reshape(6,6))
          current_index += INNER_TAC_NUM
          self.f0tip.append(np.array(data[current_index : current_index + TIP_TAC_NUM]).reshape(12,12))
          current_index += TIP_TAC_NUM
          self.f1inn.append(np.array(data[current_index : current_index + INNER_TAC_NUM]).reshape(6,6))
          current_index += INNER_TAC_NUM
          self.f1tip.append(np.array(data[current_index : current_index + TIP_TAC_NUM]).reshape(12,12))
          current_index += TIP_TAC_NUM
          self.f2inn.append(np.array(data[current_index : current_index + INNER_TAC_NUM]).reshape(6,6))
          current_index += INNER_TAC_NUM
          self.f2tip.append(np.array(data[current_index : current_index + TIP_TAC_NUM]).reshape(12,12))
          current_index += TIP_TAC_NUM
      self.palm = np.array(self.palm)
      self.f0inn = np.array(self.f0inn)
      self.f0tip = np.array(self.f0tip)
      self.f1inn = np.array(self.f1inn)
      self.f1tip = np.array(self.f1tip)
      self.f2inn = np.array(self.f2inn)
      self.f2tip = np.array(self.f2tip)
    self.inns = [self.f0inn, self.f1inn, self.f2inn]#for read and plot
    self.tips = [self.f0tip, self.f1tip, self.f2tip]
    self.set_threshold_default()
    #changeable in percent or order
    # self.set_threshold_percent()
    # self.set_threshold_order()
    #print(self.thresholds)

  def set_threshold_default(self):
    # palm f0inner f0tip f1inner f1tip f2inner f2tip
    self.thresholds = [240, 180, 680, 300, 180, 280, 460]

  def set_threshold_percent(self):
    self.thresholds = [self.palm.max()]
    for i in range(3):
      self.thresholds.append(self.inns[i].max())
      self.thresholds.append(self.tips[i].max())
      a = self.tips[i]
      print("max val:%d position:" %np.max(a), np.where(a==np.max(a)))
    print("max")
    for index in range(len(self.thresholds)):
      if self.thresholds[index] < THRETHOLD_DEFAULT:
        self.thresholds[index] = THRETHOLD_DEFAULT
      print(self.thresholds[index])
      self.thresholds[index] *= THRETHOLD_PERSENT

  def set_threshold_order(self):
    list_temp = self.palm.reshape(-1,).tolist()
    list_temp.sort()
    self.thresholds = [list_temp[round(len(list_temp) * THRETHOLD_ORDER)]]
    for i in range(3):
      list_temp = self.inns[i].reshape(-1,).tolist()
      list_temp.sort()
      self.thresholds.append(list_temp[round(len(list_temp) * THRETHOLD_ORDER)])
      list_temp = self.tips[i].reshape(-1,).tolist()
      list_temp.sort()
      #print(int(len(list_temp) * THRETHOLD_ORDER),":",len(list_temp))
      #print(list_temp)
      self.thresholds.append(list_temp[round(len(list_temp) * THRETHOLD_ORDER)])
    print("order")
    for index in range(len(self.thresholds)):
      if self.thresholds[index] < THRETHOLD_DEFAULT:
        self.thresholds[index] = THRETHOLD_DEFAULT
      print(self.thresholds[index])
      self.thresholds[index] *= THRETHOLD_PERSENT
      

class TacPlotClass():
  def __init__(self, dataset):
    self.dataset = dataset
    self.time_index = 0
    self.fig = plt.figure(num=object_name + '-' + experiment_num,figsize=(12, 6))
    self.gs = GridSpec(4, 8, figure=self.fig)
    #tips and inners
    self.axtip, self.axinn = [],[]
    for i in range(3):
      self.axtip.append(self.fig.add_subplot(self.gs[0, i]))
      self.axtip[i].set_title(i+4, pad=0.5, fontsize=6)
      self.axinn.append(self.fig.add_subplot(self.gs[1, i]))
      self.axinn[i].set_title(i+1, pad=0.5, fontsize=6)
    #palm
    self.axpalm = self.fig.add_subplot(self.gs[2:, :3])
    self.axpalm.set_title(0, pad=0.5, fontsize=6)
    #valid
    #print("valid, max=%d, threshold=%d%%"%(np.max(self.dataset.palm),THRETHOLD_PERSENT*100))
    #image
    self.aximg = self.fig.add_subplot(self.gs[2:, 3:])
    self.format_axes(self.fig)
    self.axpoint = self.fig.add_subplot(self.gs[:2, 3:])
    self.axpoint.yaxis.set_ticks_position('right')
    self.pointdata = np.zeros(self.dataset.data_num)
    self.axtime = plt.axes([0, 0.02, 1, 0.05])#slider left bottom w h
    self.time_slider = Slider(self.axtime, 'Time', 0, self.dataset.data_num-1, valinit=0, valstep=1)
    self.time_slider.on_changed(self.update_time_slider)
    self.update_time_slider(0)
    self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
    plt.show()

  def format_axes(self, fig):
    for _,ax in enumerate(fig.axes):
        ax.tick_params(labelbottom=False, labelleft=False)
        ax.get_xaxis().set_visible(False)  
        ax.get_yaxis().set_visible(False)

  def clear_axes(self):
    self.axpoint.clear()
    self.axpalm.clear()
    for i in range(3):
      self.axtip[i].clear()
      self.axinn[i].clear()

#sensor_location: 0 for palm; 1 for f0i; 2 for f0t
  def draw_area(self, tac_img, ax, sensor_location):
    ax.imshow(tac_img,cmap='Greys')
    binary_img = np.int64(tac_img>self.dataset.thresholds[sensor_location])
    label_img = measure.label(binary_img,connectivity=1)  #1代表4邻接，2代表8邻接
    props = measure.regionprops(label_img)
    if(props):
      props = sorted(props, key = lambda props:props.area, reverse=True)
      if(props[0].area > 1 or sensor_location == 2 or sensor_location == 4 or sensor_location == 6):
        for coord in props[0].coords:
          rect=patches.Rectangle((coord[1]-0.5,coord[0]-0.5),1,1,linewidth=1,edgecolor='none',facecolor='b',alpha = 0.4)
          ax.add_patch(rect)

  def draw_one_element(self):
    self.clear_axes()
    self.draw_area(self.dataset.palm[self.time_index], self.axpalm, 0)
    for i in range(0,3):
      self.draw_area(self.dataset.inns[i][self.time_index], self.axinn[i], 2*i+1)
      self.draw_area(self.dataset.tips[i][self.time_index], self.axtip[i], 2*i+2)

  def draw_picked_point(self):
    pass

  def update_time_slider(self, val):#time slider callback
    self.time_index = int(self.time_slider.val)
    self.draw_one_element()
    #draw img
    img = plt.imread(self.dataset.datapath + self.dataset.image_names[self.time_index]+'.png')
    self.aximg.set_title(self.dataset.image_names[self.time_index],fontsize=6,color='r')
    self.aximg.imshow(img)
    plt.draw()

  def onclick(self, event):
    if(event.inaxes):
      if(event.inaxes == self.axpoint or event.inaxes == self.axtime):
        self.axpoint.clear()
      else:
        axes_x = round(event.ydata)
        axes_y = round(event.xdata)
        self.draw_one_element()
        rect=patches.Rectangle((axes_y-0.5, axes_x-0.5),1,1,linewidth=1,edgecolor='r',facecolor='none')
        if(event.inaxes==self.axpalm):
          self.axpalm.add_patch(rect)
          self.pointdata = self.dataset.palm[:,axes_x, axes_y]
        else:
          for i in range(0,3):
            if (event.inaxes==self.axinn[i]):
              self.axinn[i].add_patch(rect)
              self.pointdata = self.dataset.inns[i][:,axes_x, axes_y]
            elif(event.inaxes==self.axtip[i]):
              self.axtip[i].add_patch(rect)
              self.pointdata = self.dataset.tips[i][:,axes_x, axes_y]
      self.axpoint.plot(self.pointdata)
      self.axpoint.plot(self.time_index, self.pointdata[self.time_index],'r',marker="o", markersize=5)
    plt.draw()

if __name__=="__main__":
  tac_data_set = TacDataSet()
  tac_data_set.openfile(data_dir, object_name, experiment_num)
  tac_plotter = TacPlotClass(tac_data_set)