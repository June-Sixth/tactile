from matplotlib.gridspec import GridSpec #①
import matplotlib.pyplot as plt

fig = plt.figure()

gs = GridSpec(3, 3, figure=fig) #③
ax1 = fig.add_subplot(gs[0, :]) #④
ax2 = fig.add_subplot(gs[1, :-1])
ax3 = fig.add_subplot(gs[1:, -1])
ax4 = fig.add_subplot(gs[-1, 0])
ax5 = fig.add_subplot(gs[-1, -2])
ax5.set_title(5, pad=0, fontsize=6)

def format_axes(fig):    
    for i, ax in enumerate(fig.axes): #⑤
        ax.text(0.5, 0.5, "ax%d" % (i+1), va="center", ha="center")
        ax.tick_params(labelbottom=False, labelleft=False)

format_axes(fig)
plt.show()