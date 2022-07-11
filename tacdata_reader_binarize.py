import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Slider
import matplotlib.patches as patches
from skimage import measure


data_dir = "/home/wuyi/data/20220511"
object_name = "longneckbottle" #     smallshaker  wineglass  largeshaker  longneckbottle
experiment_num = "5"

INNER_TAC_NUM = 6*6
PALM_TAC_NUM = 10*10
TIP_TAC_NUM = 12*12

THRETHOLD_PERSENT = 0.1

class TacDataSet():
  def __init__(self):
    self.tactile_data = []
    self.image_names = []
    self.data_num = 0
    #changed to nparray
    self.palm,  self.f0inn,self.f0tip,  self.f1inn,self.f1tip,  self.f2inn,self.f2tip = [],[],[],[],[],[],[]

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
          self.tactile_data.append(data)
          self.palm.append(np.array(data[0 : PALM_TAC_NUM]).reshape(10,10))
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

    self.set_threshold()
    self.binarize()
    #self.f0tip_valid = self.binarize_threshold(self.f0tip, np.max(self.f0tip) * THRETHOLD_PERSENT)
    #print("f0tip threshold = " , self.f0tip_valid.size())

  def set_threshold(self):
    self.palm_threshold = np.max(self.palm) * THRETHOLD_PERSENT
    #print("palm threshold = " , self.palm_threshold)
    self.f1tip_threshold = np.max(self.f1tip) * THRETHOLD_PERSENT
    #print("f1tip threshold = " , self.f1tip_threshold)

  def binarize(self):
    self.palm_valid = np.int64(self.palm>self.palm_threshold)
    self.f1tip_valid = np.int64(self.f1tip>self.f1tip_threshold)

  def binarize_threshold(self, mat, threshold):
    return np.int64(mat>threshold)

  def connected_component(self, input_mat):
    return 

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
    self.axpalm = self.fig.add_subplot(self.gs[2:, :2])
    self.axpalm.set_title(0, pad=0.5, fontsize=6)
    #valid
    self.axpalm_valid = self.fig.add_subplot(self.gs[2:, 2:4])
    self.axpalm_valid.set_title("valid, max=%d, threshold=%d%%"%(np.max(self.dataset.palm),THRETHOLD_PERSENT*100), pad=0.5, fontsize=6)
    #image
    self.aximg = self.fig.add_subplot(self.gs[2:, 4:])
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

  def draw_one_element(self, time_index):
    self.axpalm.imshow(self.dataset.palm[time_index],cmap='Greys')
    #self.axpalm_valid.imshow(self.dataset.palm_valid[time_index],cmap='Greys')
    ##test connected component
    binary_img = self.dataset.palm_valid[time_index]
    #print(binary_img)
    label_img = measure.label(binary_img,connectivity=1)  #1代表4邻接，2代表8邻接
    props = measure.regionprops(label_img)
    if(props):
      props = sorted(props, key = lambda props:props.area, reverse=True)
      if(props[0].area > 1):
        binary_img = np.int64(label_img == props[0].label)
      else:
        binary_img = np.zeros_like(binary_img)
    self.axpalm_valid.imshow(binary_img,cmap='Greys')
    for i in range(0,3):
      self.axinn[i].imshow(self.dataset.inns[i][time_index],cmap='Greys')
      self.axtip[i].imshow(self.dataset.tips[i][time_index],cmap='Greys')

  def update_time_slider(self, val):#time slider callback
    self.time_index = int(self.time_slider.val)
    self.draw_one_element(self.time_index)
    #draw img
    img = plt.imread(self.dataset.datapath + self.dataset.image_names[self.time_index]+'.png')
    self.aximg.set_title(self.dataset.image_names[self.time_index],fontsize=6,color='r')
    self.aximg.imshow(img)
    #self.axpoint.plot(self.time_index, self.pointdata[self.time_index],'r',marker="o", markersize=5)
    #print(self.time_index, self.pointdata[self.time_index])
    plt.draw()

  def onclick(self, event):
    if(event.inaxes):
      if(event.inaxes == self.axpoint or event.inaxes == self.axtime):
        self.axpoint.clear()
      else:
        axes_x = round(event.ydata)
        axes_y = round(event.xdata)
        self.clear_axes()
        self.draw_one_element(self.time_index)
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