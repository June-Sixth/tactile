import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Slider, Button, RadioButtons


#without tactile data: wineglass 3 9; smallshaker 0;  longneckbottle 7
#palm contact longneckbottle 1
BASE_DIR = "/data/20220511/"
object_name = "longneckbottle" #    largeshaker smallshaker  wineglass
experiments = "1"
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
    #draw palm
    palm_data = np.array(tactile_element[0 : PALM_TAC_NUM]).reshape(10,10)
    axpalm.clear()
    sns.heatmap(palm_data, ax=axpalm, cbar=False, annot=True, annot_kws={'size':5},fmt='.20g')
    axpalm.set_title(0)

    #draw tips
    x,y = np.mgrid[0:12,0:12]
    for i in range(0,3):
        tip_data = np.array(tactile_element[PALM_TAC_NUM + i*TIP_TAC_NUM : PALM_TAC_NUM + (i+1)*TIP_TAC_NUM]).reshape(12,12)
        axtip[i].clear()
        sns.heatmap(tip_data, ax=axtip[i], cbar=False, annot=True, annot_kws={'size':5},fmt='.20g')
        axtip[i].set_title(i+1)

    #draw inners
    for i in range(0,3):
        innner_data = tactile_element[PALM_TAC_NUM + 3*TIP_TAC_NUM + i*INNER_TAC_NUM : PALM_TAC_NUM + 3*TIP_TAC_NUM + (i+1)*INNER_TAC_NUM]
        innner_data = np.array(innner_data).reshape(6,6)
        axinner[i].clear()
        sns.heatmap(innner_data, ax=axinner[i], cbar=False, annot=True, annot_kws={'size':5},fmt='.20g')
        axinner[i].set_title(i+4)
        

#clear the axis
def format_axes(fig):
    for _,ax in enumerate(fig.axes):
        ax.tick_params(labelbottom=False, labelleft=False)

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
    plt.show()
