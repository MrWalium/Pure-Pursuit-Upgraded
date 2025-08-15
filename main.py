# --------------- DEPENDENCIES --------------- #
# showing the animation with matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import matplotlib.ticker as plticker

# because we love numpy
import numpy as np

# For actions executed when a button is pressed
from functools import partial

# because I'll probably need it
import math


# this was in the previous version
# idk why
# might be useful ¯\_(ツ)_/¯
# I probably should have done comments
# plt.rcParams['animation.writer'] = 'ffmpeg'

# ---------------- PATH ----------------- #

class Waypoint:
    """
    This is the waypoint class which is what the robot will be using for its path.

    Each waypoint has its (x, y) pos and a goal heading and speed
    """

    def __init__(self, x: float = 0, y: float = 0, heading: float = 0, speed: float = -1):
        """
        Notes:                                                                        ^
            heading: goal heading in degrees (might change), 0 degrees is straight up |
            speed: goal speed, -1 means automatic speed based on the path
        """
        self.x = x
        self.y = y
        self.heading = heading
        self.speed = speed

    def getCoord(self):
        """
        So you can get the coordinate of a Waypoint

        Return:
            tuple of the x and y positions of the waypoint (x, y)
        """
        return self.x, self.y


path = [Waypoint(0, 0), ]


def convertToList(listWaypoints: list[Waypoint] = path) -> list[tuple[float, float]]:
    """Converts the list of waypoints to a list of tuples with the waypoint coordinates."""
    return [waypoint.getCoord() for waypoint in listWaypoints]


# --------------- CLASSES --------------- #

class Animation:
    def __init__(self):
        # display plot stuff
        self.fig, self.ax = plt.subplots(subplot_kw={'aspect': 1})

        # gets rid of the axis labeling
        plt.xticks([])
        plt.yticks([])

        # 'scaled' means its locked at that scale, and its 1 to 1 (cirlces are circles)
        plt.axis('scaled')
        plt.xlim(-6, 6)
        plt.ylim(-4, 4)

        # so that it fills the screen
        self.fig.tight_layout()

        # drawing stuff

        # the path the robot is following drawn
        pathForGraph = np.array(convertToList())
        self.drawnPath = plt.plot(pathForGraph[:, 0], pathForGraph[:, 1], animated=True, color='black',
                                  solid_capstyle='round', linewidth=1)

        # the robot -_-
        self.robot = Robot()

        # The trail X and Y will be combined to draw the trail
        self.trailX = [self.robot.x]
        self.trailY = [self.robot.y]

        # the trail of how the robot has moved
        self.trail = plt.plot(self.trailX, self.trailY, color=(1, 0.83, 0.20))[0]

    def display(self):
        # This is how we display the animation, where it basicly updates every frame
        # Remember to update the path
        anim = animation.FuncAnimation(fig=self.fig, func=partial(updateFrame, ax=self.ax, robot=self.robot,
                                                                  trailX=self.trailX, trailY=self.trailY,
                                                                  trail=self.trail))

        plt.show()


class Robot:
    def __init__(self, x: float = 0, y: float = 0, heading: float = 0, maxVelocity: float = 1,
                 maxAcceleration: float = 1, scaling: float = 1, isdiffy: bool = True):
        self.x = x
        self.y = y
        self.heading = heading
        self.maxVelocity = maxVelocity
        self.maxAcceleration = maxAcceleration
        # For drawing
        # To scale the robot shown by a factor of scaling
        self.scaling = scaling
        self.isdiffy = isdiffy

    def draw(self, ax):
        if not self.isdiffy:
            body = plt.Rectangle((self.x - 0.15 * self.scaling, self.y - 0.25 * self.scaling),
                             width=0.3 * self.scaling,
                             height=0.5 * self.scaling, angle=self.heading,
                             rotation_point='center', lw=None, color='darkslategrey')
            # r=right, l=left, f=front, b=back
            wheelfr = plt.Rectangle((self.x + 0.25 * self.scaling, self.y + 0.25 * self.scaling),
                                    width=-0.1 * self.scaling,
                                    height=-0.2 * self.scaling, angle=self.heading,
                                    rotation_point='center', lw=None, color='black')
            wheelbr = plt.Rectangle((self.x + 0.25 * self.scaling, self.y - 0.25 * self.scaling),
                                    width=-0.1 * self.scaling,
                                    height=0.2 * self.scaling, angle=self.heading,
                                    rotation_point='center', lw=None, color='black')
            wheelfl = plt.Rectangle((self.x - 0.25 * self.scaling, self.y + 0.25 * self.scaling),
                             width=0.1 * self.scaling,
                             height=-0.2 * self.scaling, angle=self.heading,
                             rotation_point='center', lw=None, color='black')
            wheelbl = plt.Rectangle((self.x - 0.25 * self.scaling, self.y - 0.25 * self.scaling),
                                    width=0.1 * self.scaling,
                                    height=0.2 * self.scaling, angle=self.heading,
                                    rotation_point='center', lw=None, color='black')

        else:
            body = plt.Rectangle((self.x - 0.25 * self.scaling, self.y - 0.25 * self.scaling),
                             width=0.5 * self.scaling,
                             height=0.5 * self.scaling, angle=self.heading,
                             rotation_point='center', lw=None, color='darkslategrey')
            # r=right, l=left, f=front, b=back
            wheelfr = plt.Rectangle((self.x + 0.1875 * self.scaling, self.y + (0.12) * self.scaling),
                                    width=-0.05 * self.scaling,
                                    height=0.1 * self.scaling, angle=self.heading,
                                    rotation_point='center', lw=None, color='black')
            wheelbr = plt.Rectangle((self.x + 0.1875 * self.scaling, self.y - (0.12) * self.scaling),
                                    width=-0.05 * self.scaling,
                                    height=-0.1 * self.scaling, angle=self.heading,
                                    rotation_point='center', lw=None, color='black')
            wheelfl = plt.Rectangle((self.x - 0.1875 * self.scaling, self.y + (0.12) * self.scaling),
                                    width=0.05 * self.scaling,
                                    height=0.1 * self.scaling, angle=self.heading,
                                    rotation_point='center', lw=None, color='black')
            wheelbl = plt.Rectangle((self.x - 0.1875 * self.scaling, self.y - (0.12) * self.scaling),
                                    width=0.05 * self.scaling,
                                    height=-0.1 * self.scaling, angle=self.heading,
                                    rotation_point='center', lw=None, color='black')
        ax.add_patch(body)
        ax.add_patch(wheelfr)
        ax.add_patch(wheelbr)
        ax.add_patch(wheelfl)
        ax.add_patch(wheelbl)




# do I really need a comment?
def updateFrame(frame, ax, robot: Robot, trailX, trailY, trail):
    # updating the robot trail
    trailX.append(robot.x)
    trailY.append(robot.y)

    # combining the trail x and y to show the trail
    trail.set_data(trailX, trailY)

    # the robot draws itself
    robot.draw(ax)


# --------------- MAIN --------------- #

# calls the functions which actually does stuff
# the function is literally useless, but I hold onto my c++ roots
def main():
    animation = Animation()
    animation.display()


# I do not embrace some python aspects
main()
plt.close()
