#!/usr/bin/env python3  

from trx_tactile_msgs.msg import TrxTactileStates
import rospy
import numpy as np
import matplotlib as mpl
mpl.use('TkAgg')  # or whatever other backend that you want
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Slider
from matplotlib import animation
from time import sleep
#for fpt_hand control
from limb_core_msgs.msg import JointState
from limb_core_msgs.msg import JointCommand

#to subscribe tacdata
class TacDataClass():
    def __init__(self):
        self.data = []
        self.init_done = False #True after record the origin_bias
        self.origin_bias = []
        rospy.init_node('tactile_listener', anonymous=True)
        self.tac_size = [10, 12, 12, 12, 6, 6, 6]
        rospy.Subscriber("/tactile_states", TrxTactileStates, self.tac_callback, queue_size=1)
        #order: palm f0t f1t f2t f0i f1i f2i
        #self.thresholds = [240, 180, 180, 280, 680, 460, 300]
        self.thresholds = [0, 0, 0, 0, 0, 0, 0]
        self.data_counter = np.zeros([7,16384])#record the number of a max tactile value appears(the value range(0-16384))
        self.max_value = [0, 0, 0, 0, 0, 0, 0]  


    def tac_callback(self, tac_data_in):
        if self.init_done:
            for i in range(7):
                data_temp = np.reshape(tac_data_in.states[i].data, [self.tac_size[i], self.tac_size[i]]) - self.origin_bias[i]        #data_temp[data_temp < 0] = 0
                data_temp[data_temp < self.thresholds[i]] = 0
                for value in tac_data_in.states[i].data:
                    if(self.data_counter[i][value]<100):
                        self.data_counter[i][value] += 1
                self.data[i] = data_temp
        else:
            for i in range(7):
                self.origin_bias.append(np.reshape(tac_data_in.states[i].data, [self.tac_size[i], self.tac_size[i]]))
            self.data = self.origin_bias.copy()
            self.init_done = True

#Unit: degree
#Range: 0(0指近关节)-[-45.0, 45.0], 1(0指远关节)-[-45.0, 45.0],
#       2(1指舵机)-[-90.0, 0.0], 3(1指近关节)-[-45.0, 45.0], 4(1指远关节)-[-45.0, 45.0],
#       5(2指舵机)-[0.0, 90.0], 6(2指近关节)-[-45.0, 45.0], 7(2指远关节)-[-45.0, 45.0]

#finger angles in rad
#close [0.3,0.8,0,0.3,0.8,0,0.3,0.8]
#open [-0.3,-0.8,0,-0.3,-0.8,0,-0.3,-0.8]

#finger angles in degree
#Closes palm. {30.0, 30.0, 0.0, 30.0, 45.0, 0.0, 45.0, 45.0}
#Opens palm.{-45.0, -45.0, -90.0, -45.0, -45.0, 90.0, -45.0, -45.0}
class HandMoveClass():
    def __init__(self):
        self.pub = rospy.Publisher('/fpt_hand_left/controller', JointCommand, queue_size=10)
        self.pub_rate = rospy.Rate(5) # hz
        self.joint_angles = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.joint_angles_min = np.array([-45.0, -45.0, -90.0, -45.0, -45.0,  0.0, -45.0, -45.0])#min angle
        self.joint_angles_max = np.array([ 55.0,  85.0,   0.0,  55.0,  85.0, 90.0,  55.0,  85.0])#max angle

    def home(self):
        for i in range(3):
            self.pub.publish(mode=1, command=np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]))
            self.pub_rate.sleep()
        sleep(0.1)

    def open(self):
        self.pub.publish(mode=1, command=np.array([-0.3,-0.8,0,-0.3,-0.8,0,-0.3,-0.8]))
        self.pub_rate.sleep()
        sleep(0.1)

    def grasp(self):
        self.pub.publish(mode=1, command=np.array([0.3,0.8,0,0.3,0.8,0,0.3,0.8]))
        self.pub_rate.sleep()
        sleep(0.1)

    def check_cmd_range(self):
        np.clip(self.joint_angles, self.joint_angles_min, self.joint_angles_max, self.joint_angles)
        print(self.joint_angles)

    def go(self):
        self.pub.publish(mode=1, command=self.joint_angles)
        self.pub_rate.sleep()
        sleep(0.1)

    def premove(self, pre_move):
        for i in range(3):
            self.pub.publish(mode=1, command=pre_move)
            self.pub_rate.sleep()
        print("Pre_pos OK")

    def move_hold(self, tg, mode):
        for i in range(3):
            self.pub.publish(mode=1, command=tg)
            self.pub_rate.sleep()
        print("Target_pos OK")
        
        # Countinue to input current
        sleep(1)
        print("Start to push ...")
        print("="*30)
        if mode == 1:  # Mode 1: Two fins push
            d_joint_pos = np.array([0, 0, 0, 0.1, 0.1, 0, 0.1, 0.1])
        elif mode == 2:
            d_joint_pos = np.array([0, 0.1, 0, 0.1, 0.1, 0, 0.1, 0.1])
        else:
            d_joint_pos = np.array([0, 0, 0, 0, 0, 0, 0, 0])
            print("Please input right mode in 1 2")
        #push 
        for i in range(30):
            joint_states = rospy.wait_for_message("/fpt_hand_left/joint_states", JointState)
            joint_pos = np.array(joint_states.position)
            joint_pos_next = joint_pos + d_joint_pos
            self.pub.publish(mode=1, command=joint_pos_next)
            self.pub_rate.sleep()


DEG2RAD = 0.0174532
class TacPlotClass():
    
    def __init__(self, dataClass, hand):
        self._dataClass = dataClass
        self.fig = plt.figure(figsize=(16, 18),num='tactile plot & hand ctrl')
        #for realtime tacimg plot
        self.anim = animation.FuncAnimation(self.fig, func = self.animate, frames=None, save_count=0, interval=1, blit = False, repeat = False)
        self.fig_gs = GridSpec(4, 3)
        self.sld_gs = GridSpec(65, 3)#for slider position
        #fig axes
        self.tip_fig_axes, self.inn_fig_axes = [],[]
        #slider axes
        self.tip_sld_axes, self.inn_sld_axes = [],[]
        #sliders
        self.tip_sld, self.inn_sld = [],[]
        for i in range(3):
            self.tip_fig_axes.append(self.fig.add_subplot(self.fig_gs[0, i]))
            # self.tip_fig_axes[i].set_title(i+1, fontsize=6)
            self.tip_sld_axes.append(self.fig.add_subplot(self.sld_gs[15, i]))#for position
            self.tip_sld.append(Slider(self.tip_sld_axes[i], 'f%dt'%(i), -45.0, 85.0, valinit = 0.0, valstep = 0.01))
            self.tip_sld[i].on_changed(self.sliders_on_change)

            self.inn_fig_axes.append(self.fig.add_subplot(self.fig_gs[1, i]))
            # self.inn_fig_axes[i].set_title(i+4, fontsize=6)
            self.inn_sld_axes.append(self.fig.add_subplot(self.sld_gs[32, i]))#for position
            self.inn_sld.append(Slider(self.inn_sld_axes[i], 'f%di'%(i), -45.0, 55.0, valinit = 0.0, valstep = 0.01))
            self.inn_sld[i].on_changed(self.sliders_on_change)

        #palm axes
        self.palm_fig_axes = self.fig.add_subplot(self.fig_gs[2:, :3])
        self.palm_fig_axes.set_title(0, fontsize=6)
        self.format_axes(self.fig)

        #for keypress callback
        self.fig.canvas.mpl_connect('key_press_event', self.on_press)
        #for hand control
        self.hand = hand

        #2 palm joint angle control
        self.palm_sld_axes1 = plt.axes([0, 0.02, 0.5, 0.02])#slider left bottom w h
        self.palm_sld1 = Slider(self.palm_sld_axes1, 'f1', -90.0, 0.0, valinit = 0.0, valstep = 0.01)
        self.palm_sld1.on_changed(self.sliders_on_change)
        self.palm_sld_axes2 = plt.axes([0.5, 0.02, 0.5, 0.02])#slider left bottom w h
        self.palm_sld2 = Slider(self.palm_sld_axes2, 'f2', 0.0, 90.0, valinit = 0.0, valstep = 0.01)
        self.palm_sld2.on_changed(self.sliders_on_change)
        plt.show()

    def draw_area(self, tac_img, ax):
        ax.clear()
        ax.imshow(tac_img,cmap='Greys')
        #sns.heatmap(tac_img, ax = ax, cbar=False, cbar_kws={}, cmap="YlGnBu", annot=True, annot_kws={"fontsize":12}, fmt='g', yticklabels=False, xticklabels=False)

    def animate(self, i):
        self.draw_area(self._dataClass.data[0],self.palm_fig_axes)
        for i in range(0,3):
            self.draw_area(self._dataClass.data[i+1], self.tip_fig_axes[i])
            self.draw_area(self._dataClass.data[i+4], self.inn_fig_axes[i])

    def format_axes(self, fig):
        for _,ax in enumerate(fig.axes):
            ax.tick_params(labelbottom=False, labelleft=False)
            ax.get_xaxis().set_visible(False)  
            ax.get_yaxis().set_visible(False)

    def on_press(self, event):
        print('pressing', event.key)
        if event.key == 'control':
            print('press ctrl+g for hand grasp, press ctrl+o for hand open, press ctrl+h for hand home, press ctrl+p for print tacdata record, press q to quit')
        elif event.key == 'ctrl+g':
            # self.hand.grasp()
            self.sliders_set_val([17.2, 45.8,  0.0, 17.2, 45.8,  0.0, 17.2, 45.8])
        elif event.key == 'ctrl+o':
            # self.hand.open()
            self.sliders_set_val([-17.2, -45.8,  0.0, -17.2, -45.8,  0.0, -17.2, -45.8])
        elif event.key == 'ctrl+h':
            # self.hand.home()
            self.sliders_set_val([0.0, 0.0,  0.0, 0.0, 0.0,  0.0, 0.0, 0.0])
        elif event.key == 'ctrl+d':#f1 f2 face to face
            self.sliders_set_val([0.0, 0.0,  -90.0, 0.0, 0.0,  90.0, 0.0, 0.0])
        elif event.key == 'ctrl+p':
            for i in range(7):
                index = self._dataClass.data_counter[i] > 2
                index = np.where(index)
                self._dataClass.max_value[i] = np.array(index).max()    
            print(self._dataClass.max_value)#to test the data_counter

    def sliders_on_change(self, val):#all sliders callback
        self.hand.joint_angles = self.sliders_get_val()
        self.hand.check_cmd_range()
        self.hand.joint_angles *= DEG2RAD
        print(self.hand.joint_angles)
        self.hand.go()

    def slider_update_val(self, slider, val):#update val but not activate the event
        slider.eventson = False
        slider.set_val(val)
        slider.eventson = True

    def sliders_set_val(self, vals):#vals in degrees
        self.slider_update_val(self.inn_sld[0], vals[0])
        self.slider_update_val(self.tip_sld[0], vals[1])
        self.slider_update_val(self.palm_sld1, vals[2])
        self.slider_update_val(self.inn_sld[1], vals[3])
        self.slider_update_val(self.tip_sld[1], vals[4])
        self.slider_update_val(self.palm_sld2, vals[5])
        self.slider_update_val(self.inn_sld[2], vals[6])
        self.slider_update_val(self.tip_sld[2], vals[7])
        self.sliders_on_change(0)

    def sliders_get_val(self):
        return np.array([self.inn_sld[0].val, self.tip_sld[0].val, 
                        self.palm_sld1.val, self.inn_sld[1].val, self.tip_sld[1].val, 
                        self.palm_sld2.val, self.inn_sld[2].val, self.tip_sld[2].val])
                        
def main():
    tac_data = TacDataClass()
    hand = HandMoveClass()
    plotter = TacPlotClass(tac_data, hand)
    
if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass