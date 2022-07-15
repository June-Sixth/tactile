import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.patches as patches
from skimage import measure

INNER_TAC_NUM = 6*6
PALM_TAC_NUM = 10*10
TIP_TAC_NUM = 12*12

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

  def set_threshold_default(self):
    # palm f0inner f0tip f1inner f1tip f2inner f2tip
    self.thresholds = [240, 180, 680, 300, 180, 280, 460]

class TacPlotClass():
  def __init__(self, dataset):
    self.dataset = dataset
    self.time_index = int(dataset.data_num*0.99)#取最后时刻的数据
    self.fig = plt.figure(num=object_name + '-' + str(experiment_num),figsize=(12, 6))
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
    #image
    self.aximg = self.fig.add_subplot(self.gs[2:, 3:])

  def format_axes(self, fig):
    for _,ax in enumerate(fig.axes):
        ax.tick_params(labelbottom=False, labelleft=False)
        ax.get_xaxis().set_visible(False)  
        ax.get_yaxis().set_visible(False)

  def clear_axes(self):
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
    img = plt.imread(self.dataset.datapath + self.dataset.image_names[self.time_index]+'.png')
    self.aximg.set_title(self.dataset.image_names[self.time_index],fontsize=6,color='r')
    self.aximg.imshow(img)

    plt.show()

data_dir = "/home/wuyi/data/20220511"

if __name__=="__main__":
  objects = ['largeshaker','smallshaker','longneckbottle','wineglass']
  samples = [[0,1,2,3,4,5,6,7,9], [1,2,3,5,6,7,8,9], [0,1,2,3,4,5,6,8,9], [1,2,4,5,6,7,8]]
  for i in range(len(objects)):##select object
    object_name = objects[i]
    experiments = samples[i]
    for experiment_num in experiments:

      tac_data_set = TacDataSet()
      tac_data_set.openfile(data_dir, object_name, str(experiment_num))
      #print(object_name+":", tac_data_set.data_num)
      tac_plotter = TacPlotClass(tac_data_set)
      tac_plotter.draw_one_element()
