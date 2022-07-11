import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Slider, Button, RadioButtons

#without tactile data: wineglass 0 3 9; smallshaker 0;  longneckbottle 7
# wineglass ; longneckbottle 0:finger without palm
BASE_DIR = "/home/wuyi/data/20220511/"
object_name = "largeshaker" #     smallshaker  wineglass  largeshaker  longneckbottle
experiments = "1"
data_path = BASE_DIR + object_name + '/' + experiments +'/data.txt'

INNER_TAC_NUM = 6*6
PALM_TAC_NUM = 10*10
TIP_TAC_NUM = 12*12

tactile_data = []
image_names = []
time_index = 0

def openfile(file_name):
    file = open(file_name, 'r')
    file_lines = file.readlines()
    for line in file_lines:
        if(line[:2]=='16'):
            image_names.append(line[:-1])
        if(line[:3]=='640'):
            tactile_data.append(list(map(int, line[4:-1].split())))
    #return tactile_data[436:516], image_names[436:516]
    return tactile_data, image_names
    
def update(val):
    time_index = int(time.val)
    draw_one_element(tactile_data[time_index])
    #draw img
    img = plt.imread(BASE_DIR + object_name + '/' + experiments + '/' + image_names[time_index]+'.png')
    aximg.set_title(image_names[time_index],fontsize=12,color='r')
    aximg.imshow(img)

def btn_next_callback(event):
    time_index = int(time.val)
    if time_index < len(tactile_data)-2:
        time_index = time_index + 1
        time.set_val(time_index)

def btn_pre_callback(event):
    time_index = int(time.val)
    if time_index > 1:
        time_index = time_index - 1
        time.set_val(time_index)

def on_press(event):
    time_index = int(time.val)
    if event.key == 'n':
        if time_index < len(tactile_data)-2:
            time_index = time_index + 1
            time.set_val(time_index)
    if event.key == 'p':
        if time_index > 1:
            time_index = time_index - 1
            time.set_val(time_index)
    print(time_index)

def draw_one_element(tactile_element):

    #draw palm
    palm_data = np.array(tactile_element[0 : PALM_TAC_NUM]).reshape(10,10)
    axpalm.clear()
    sns.heatmap(palm_data, ax=axpalm, cbar=False, annot=True, annot_kws={'size':5},fmt='.20g', cmap='Greys')
    axpalm.set_title(0, pad=0, fontsize=6)

    #draw tips and inners
    x1,y1 = np.mgrid[0:12,0:12]
    x2,y2 = np.mgrid[0:6,0:6]
    for i in range(0,3):
        innner_data = tactile_element[PALM_TAC_NUM + i*(TIP_TAC_NUM+INNER_TAC_NUM) : PALM_TAC_NUM + i*(TIP_TAC_NUM+INNER_TAC_NUM) + INNER_TAC_NUM]
        innner_data = np.array(innner_data).reshape(6,6)
        c = axinner[i].pcolor(x2,y2,innner_data, cmap='Greys')

        tip = tactile_element[PALM_TAC_NUM + i*(TIP_TAC_NUM+INNER_TAC_NUM) + INNER_TAC_NUM : PALM_TAC_NUM + (i+1)*(TIP_TAC_NUM+INNER_TAC_NUM)]
        c = axtip[i].pcolor(x1,y1,np.array(tip).reshape(12,12), cmap='Greys')

    fig.colorbar(c, ax=axtip, cax=axtipscolorbar)
    fig.colorbar(c, ax=axinner, cax=axinnerscolorbar)

    # #draw tips
    # x,y = np.mgrid[0:12,0:12]
    # for i in range(0,3):
    #     tip = tactile_element[PALM_TAC_NUM + i*TIP_TAC_NUM : PALM_TAC_NUM + (i+1)*TIP_TAC_NUM]
    #     c = axtip[i].pcolor(x,y,np.array(tip).reshape(12,12), cmap='Greys')
    #     axtip[i].set_title(i+1, pad=0, fontsize=6)
    # fig.colorbar(c, ax=axtip, cax=axtipscolorbar)

    # #draw inners
    # x,y = np.mgrid[0:6,0:6]
    # for i in range(0,3):
    #     innner_data = tactile_element[PALM_TAC_NUM + 3*TIP_TAC_NUM + i*INNER_TAC_NUM : PALM_TAC_NUM + 3*TIP_TAC_NUM + (i+1)*INNER_TAC_NUM]
    #     innner_data = np.array(innner_data).reshape(6,6)
    #     c = axinner[i].pcolor(x,y,innner_data, cmap='Greys')
    #     axinner[i].set_title(i+4, pad=0, fontsize=6)
    # fig.colorbar(c, ax=axtip, cax=axinnerscolorbar)

def format_axes(fig):
    for _,ax in enumerate(fig.axes):
        ax.tick_params(labelbottom=False, labelleft=False)
        ax.get_xaxis().set_visible(False) 
        ax.get_yaxis().set_visible(False) 

if __name__=="__main__":

    tactile_data, image_names = openfile(data_path)
    #print(max(tactile_data))

    fig = plt.figure(num=object_name + '-' + experiments,figsize=(8, 4))
    gs = GridSpec(4, 8, figure=fig)
    axtip, axinner = [],[]
    for i in range(3):
        axtip.append(fig.add_subplot(gs[0, i]))
        axinner.append(fig.add_subplot(gs[1, i]))
    axpalm = fig.add_subplot(gs[2:, :3])
    aximg = fig.add_subplot(gs[:, 3:])
    format_axes(fig)
    axtipscolorbar = plt.axes([0.07, 0.72, 0.005, 0.16])
    axinnerscolorbar = plt.axes([0.07, 0.52, 0.005, 0.16])
    axtime = plt.axes([0, 0.02, 1, 0.05])#slider left bottom w h
    time = Slider(axtime, 'Time', 0, len(tactile_data)-1, valinit=0, valstep=1)
    time.on_changed(update)

    fig.canvas.mpl_connect('key_press_event', on_press)
    ax_pre = plt.axes([0.55, 0.1, 0.1, 0.075])
    btn_pre = Button(ax_pre, 'pre')
    btn_pre.on_clicked(btn_pre_callback)
    ax_next = plt.axes([0.7, 0.1, 0.1, 0.075])
    btn_next = Button(ax_next, 'next')
    btn_next.on_clicked(btn_next_callback)

    plt.show()
