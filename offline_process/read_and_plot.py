import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Slider, Button

#without tactile data: wineglass 3 9; smallshaker 0

BASE_DIR = "/home/wuyi/data/20220511/"
object_name = "longneckbottle" #    largeshaker smallshaker  wineglass
experiments = "4"
data_path = BASE_DIR + object_name + '/' + experiments +'/data.txt'

INNER_TAC_NUM = 6*6
PALM_TAC_NUM = 10*10
TIP_TAC_NUM = 12*12

tactile_data = []
image_names = []

def openfile(file_name):
    file = open(file_name, 'r')
    file_lines = file.readlines()
    for line in file_lines:
        if(line[:2]=='16'):
            image_names.append(line[:-1])
        if(line[:3]=='640'):
            tactile_data.append(list(map(int, line[4:-1].split())))
    return tactile_data, image_names
    
def update(val):
    time_index = int(time.val)
    draw_one_element(tactile_data[time_index])
    #draw img
    img = plt.imread(BASE_DIR + object_name + '/' + experiments + '/' + image_names[time_index]+'.png')
    aximg.set_title(image_names[time_index],fontsize=12,color='r')
    aximg.imshow(img)


def draw_one_element(tactile_element):

    # #draw palm
    palm_data = np.array(tactile_element[0 : PALM_TAC_NUM]).reshape(10,10)
    axpalm.imshow(palm_data,cmap='Greys')
    axpalm.set_title(0, pad=0, fontsize=6)

    for i in range(0,3):
        innner_data = tactile_element[PALM_TAC_NUM + i*(TIP_TAC_NUM+INNER_TAC_NUM) : PALM_TAC_NUM + i*(TIP_TAC_NUM+INNER_TAC_NUM) + INNER_TAC_NUM]
        innner_data = np.array(innner_data).reshape(6,6)
        axinner[i].imshow(innner_data,cmap='Greys')
        axinner[i].set_title(i+4, pad=0, fontsize=6)

        tip = tactile_element[PALM_TAC_NUM + i*(TIP_TAC_NUM+INNER_TAC_NUM) + INNER_TAC_NUM : PALM_TAC_NUM + (i+1)*(TIP_TAC_NUM+INNER_TAC_NUM)]
        axtip[i].imshow(np.array(tip).reshape(12,12),cmap='Greys')
        axtip[i].set_title(i+1, pad=0, fontsize=6)


def format_axes(fig):
    for _,ax in enumerate(fig.axes):
        ax.tick_params(labelbottom=False, labelleft=False)
        ax.get_xaxis().set_visible(False) 
        ax.get_yaxis().set_visible(False) 

def onclick(event):
    if (event.inaxes==aximg):
      print("img")
    elif(event.inaxes==axpalm):
      print("palm")
    
    print('button=%d, xdata=%d, ydata=%d' %
          (event.button, round(event.xdata), round(event.ydata)))#四舍五入取整


if __name__=="__main__":

    tactile_data, image_names = openfile(data_path)

    fig = plt.figure(num=object_name + '-' + experiments,figsize=(8, 4))
    gs = GridSpec(4, 8, figure=fig)
    axtip, axinner = [],[]
    for i in range(3):
      axtip.append(fig.add_subplot(gs[0, i]))
      axinner.append(fig.add_subplot(gs[1, i]))
    axpalm = fig.add_subplot(gs[2:, :3])
    aximg = fig.add_subplot(gs[:, 3:])
    format_axes(fig)
    axtime = plt.axes([0, 0.02, 1, 0.05])#slider left bottom w h
    time = Slider(axtime, 'Time', 0, len(tactile_data)-1, valinit=0, valstep=1)
    time.on_changed(update)

    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    plt.show()
