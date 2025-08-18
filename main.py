# --------------- DEPENDENCIES --------------- #
# showing the animation with matplotlib
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
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
        self.robot = Robot(self.ax)

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
                                                                  trail=self.trail), blit=True, cache_frame_data=False,interval=10)

        plt.show()


class Robot:
    def __init__(self, ax, x: float = 0, y: float = 0, heading: float = 0, MAX_VELOCITY: float = 0.1,
                 MAX_ACCELERATION: float = 1, MAX_TURN_VELOCITY: float = 3.35, MAX_TURN_ACCELERATION: float = 1,
                 scaling: float = 1, isdiffy: bool = True):
        """
        Initializes all of the positional, velocity, acceleration, maximum, and draw shape variables.
        Args:
            ax: the axis on which the robot is drawn
            x: inital x position of the robot
            y: inital y postition of the robot
            heading: inital heading of the robot
            MAX_VELOCITY: maximum linear velocity
            MAX_ACCELERATION: maximum linear acceleration
            MAX_TURN_VELOCITY: maximum rate of change in velocity angle
            scaling: how much bigger or smaller the robot is drawn
            isdiffy: if the robot is drawn with a differential swerve or holonomic drivetrain
        """
        # --- instance variables --- #
        # the plot axis
        self.ax = ax

        # positional variables
        self.x = x
        self.y = y
        self.heading = heading

        # I'm using polar coordinates for velocity for simplicity
        self.velocity = 0.1
        # how fast the velocity angle is changing
        self.turnVelocity = 3.35
        self.velocityAngle = 0

        # accelerations
        self.acceleration = 0
        self.turnAcceleration = 0

        # maximums
        self.MAX_VELOCITY = MAX_VELOCITY
        self.MAX_ACCELERATION = MAX_ACCELERATION
        self.MAX_TURN_VELOCITY = MAX_TURN_VELOCITY
        self.MAX_TURN_ACCELERATION = MAX_TURN_ACCELERATION

        # for drawing
        # to scale the robot shown by a factor of scaling
        self.scaling = scaling
        self.isdiffy = isdiffy

        # --- drawing variables --- #

        # (x, y) positions, widths, radius's, etc. are 0 because
        # they are going to be updated immediately in the update function anyway

        self.body = plt.Rectangle((0, 0), width=0, height=0, angle=self.heading,
                                  rotation_point='center', lw=None, color='darkslategrey')
        # r=right, l=left, f=front, b=back
        self.wheelfr = plt.Rectangle((0, 0), width=0, height=0, angle=self.heading,
                                     rotation_point='center', lw=None, color='black')
        self.wheelbr = plt.Rectangle((0, 0), width=0, height=0, angle=self.heading,
                                     rotation_point='center', lw=None, color='black')
        self.wheelfl = plt.Rectangle((0, 0), width=0, height=0, angle=self.heading,
                                     rotation_point='center', lw=None, color='black')
        self.wheelbl = plt.Rectangle((0, 0), width=0, height=0, angle=self.heading,
                                     rotation_point='center', lw=None, color='black')
        self.eyer = plt.Circle((0, 0), radius=0.05 * self.scaling, color='white', lw=None)
        self.eyel = plt.Circle((0, 0), radius=0.05 * self.scaling, color='white', lw=None)
        self.pupilr = plt.Circle((0, 0), radius=0.02 * self.scaling, color='black', lw=None)
        self.pupill = plt.Circle((0, 0), radius=0.02 * self.scaling, color='black', lw=None)

        self.centerPt = plt.Circle((self.x, self.y), radius=0.01 * self.scaling, color='black')

        self.frontTriangle = plt.Polygon(((0, 0), (0, 0)), fill=True, color='firebrick')

        # so the wheels can rotate
        self.wheelHolefr = plt.Circle((0, 0), radius=0.055, color='darkgrey')
        self.wheelHolebr = plt.Circle((0, 0), radius=0.055, color='darkgrey')
        self.wheelHolefl = plt.Circle((0, 0), radius=0.055, color='darkgrey')
        self.wheelHolebl = plt.Circle((0, 0), radius=0.055, color='darkgrey')

        # adding each shape to a patch so that it can be displayed
        self.ax.add_patch(self.body)
        self.ax.add_patch(self.centerPt)
        self.ax.add_patch(self.frontTriangle)
        self.ax.add_patch(self.wheelHolefr)
        self.ax.add_patch(self.wheelHolebr)
        self.ax.add_patch(self.wheelHolefl)
        self.ax.add_patch(self.wheelHolebl)
        self.ax.add_patch(self.wheelfr)
        self.ax.add_patch(self.wheelbr)
        self.ax.add_patch(self.wheelfl)
        self.ax.add_patch(self.wheelbl)
        self.ax.add_patch(self.eyer)
        self.ax.add_patch(self.eyel)
        self.ax.add_patch(self.pupilr)
        self.ax.add_patch(self.pupill)

        # if we are not showing a diffy swerve robot, the shapes
        # unique to the diffy are hidden
        if not self.isdiffy:
            self.frontTriangle.set_visible(False)
            self.wheelHolefr.set_visible(False)
            self.wheelHolebr.set_visible(False)
            self.wheelHolefl.set_visible(False)
            self.wheelHolebl.set_visible(False)

    # --- Helpers --- #
    # --- Drawing and Updates --- #
    def update(self):
        """
        Updates the position and heading, velocities, and accelerations
        This function does not draw the robot, the draw function does that.
        This function is called by the draw function before drawing the robot.
        """
        # idk what to do with acceleration, but there will probably be some acceleration function
        # based off of velocity or maybe its changed in a goTo function or something similar (?)
        self.acceleration = 0
        self.turnAcceleration = 0

        self.velocity = min(self.velocity + self.acceleration, self.MAX_VELOCITY)
        self.turnVelocity = math.copysign(min(abs(self.turnVelocity + self.turnAcceleration), self.MAX_TURN_VELOCITY),
                                          self.turnVelocity)
        # turn velocity is how much the velocity angle changes by
        self.velocityAngle += self.turnVelocity

        # changing the robot position
        self.x += self.velocity * math.sin(math.radians(-self.velocityAngle))
        self.y += self.velocity * math.cos(math.radians(self.velocityAngle))

        # going to add velocity and acceleration to this later
        self.heading += 0

    def draw(self, ax):
        """
        Calls the update function, and draws the robot, either with a holonomic or differential swerve drivetrain.
        It updates all the shapes positions and attributes.
        The isdiffy variable controls if a differential swerve or holonomic drivetrain is drawn.

        Args:
            ax: the axis to add patches to so the shapes can be drawn
        """
        self.update()

        # hopefully no one including me should have to go through this
        if not self.isdiffy:
            self.body.set(xy=(self.x - 0.15 * self.scaling, self.y - 0.25 * self.scaling),
                          width=0.30 * self.scaling,
                          height=0.5 * self.scaling, angle=self.heading)
            # r=right, l=left, f=front, b=back
            self.wheelfr.set(xy=(self.x + (0.25 * math.cos(math.radians(self.heading + 36.8698976)) - 0.05) *
                                 self.scaling,
                                 self.y + (0.25 * math.sin(math.radians(self.heading + 36.8698976)) - 0.1) *
                                 self.scaling),
                             width=0.1 * self.scaling,
                             height=0.2 * self.scaling, angle=self.heading, lw=0.1,
                             color='black', hatch='////////', fill=False)
            self.wheelbr.set(xy=(self.x + (0.25 * math.cos(math.radians(self.heading + 323.1301024)) - 0.05) *
                                 self.scaling,
                                 self.y + (0.25 * math.sin(math.radians(self.heading + 323.1301024)) - 0.1) *
                                 self.scaling),
                             width=0.1 * self.scaling,
                             height=0.2 * self.scaling, angle=self.heading, lw=0.1,
                             color='black', hatch='\\\\\\\\\\\\\\\\\\', fill=False)
            self.wheelfl.set(xy=(self.x + (0.25 * math.cos(math.radians(self.heading + 143.1301024)) - 0.05) *
                                 self.scaling,
                                 self.y + (0.25 * math.sin(math.radians(self.heading + 143.1301024)) - 0.1) *
                                 self.scaling),
                             width=0.1 * self.scaling,
                             height=0.2 * self.scaling, angle=self.heading, lw=0.1,
                             color='black', hatch='\\\\\\\\\\\\\\\\\\', fill=False)
            self.wheelbl.set(xy=(self.x + (0.25 * math.cos(math.radians(self.heading + 216.8698976)) - 0.05) *
                                 self.scaling,
                                 self.y + (0.25 * math.sin(math.radians(self.heading + 216.8698976)) - 0.1) *
                                 self.scaling),
                             width=0.1 * self.scaling,
                             height=0.2 * self.scaling, angle=self.heading, lw=0.1,
                             color='black', hatch='////////', fill=False)
            self.eyer.set(
                center=(self.x + 0.19235384061 * self.scaling * math.cos(math.radians(self.heading + 64)), self.y +
                        0.19235384061 * self.scaling *
                        math.sin(math.radians(self.heading + 64))), radius=0.05 * self.scaling)
            self.eyel.set(
                center=(self.x + 0.19235384061 * self.scaling * math.cos(math.radians(self.heading + 110)), self.y +
                        0.19235384061 * self.scaling *
                        math.sin(math.radians(self.heading + 110))), radius=0.05 * self.scaling)
            self.pupilr.set(
                center=(self.x + 0.19235384061 * self.scaling * math.cos(math.radians(self.heading + 64)), self.y +
                        0.19235384061 * self.scaling *
                        math.sin(math.radians(self.heading + 64))), radius=0.02 * self.scaling)
            self.pupill.set(
                center=(self.x + 0.19235384061 * self.scaling * math.cos(math.radians(self.heading + 110)), self.y +
                        0.19235384061 * self.scaling *
                        math.sin(math.radians(self.heading + 110))), radius=0.02 * self.scaling)
            self.centerPt.set(center=(self.x, self.y))

            if self.frontTriangle.get_visible():
                # setting parts of the diffy swerve to not be visible
                self.frontTriangle.set_visible(False)
                self.wheelHolefr.set_visible(False)
                self.wheelHolebr.set_visible(False)
                self.wheelHolefl.set_visible(False)
                self.wheelHolebl.set_visible(False)
                return self.body, self.wheelfr, self.wheelbr, self.wheelfl, self.wheelbl, self.eyer, self.eyel, self.pupilr, self.pupill, self.frontTriangle, self.wheelHolefr, self.wheelHolebr, self.wheelHolefl, self.wheelHolebl, self.centerPt
            return self.body, self.wheelfr, self.wheelbr, self.wheelfl, self.wheelbl, self.eyer, self.eyel, self.pupilr, self.pupill, self.centerPt

        else:
            self.body.set(xy=(self.x - 0.25 * self.scaling, self.y - 0.25 * self.scaling),
                          width=0.5 * self.scaling,
                          height=0.5 * self.scaling, angle=self.heading)
            # r=right, l=left, f=front, b=back
            self.wheelHolefr.set(
                center=(self.x + 0.24234531148 * math.cos(math.radians(self.heading + 45)) * self.scaling,
                        self.y + 0.24234531148 * math.sin(math.radians(self.heading + 45)) * self.scaling),
                radius=0.055 * self.scaling, visible=True)
            self.wheelHolebr.set(
                center=(self.x + 0.24234531148 * math.cos(math.radians(self.heading + 315)) * self.scaling,
                        self.y + 0.24234531148 * math.sin(math.radians(self.heading + 315)) * self.scaling),
                radius=0.055 * self.scaling, visible=True)
            self.wheelHolefl.set(
                center=(self.x + 0.23234531148 * math.cos(math.radians(self.heading + 133)) * self.scaling,
                        self.y + 0.23234531148 * math.sin(math.radians(self.heading + 133)) * self.scaling),
                radius=0.055 * self.scaling, visible=True)
            self.wheelHolebl.set(
                center=(self.x + 0.23234531148 * math.cos(math.radians(self.heading + 226)) * self.scaling,
                        self.y + 0.23234531148 * math.sin(math.radians(self.heading + 226)) * self.scaling),
                radius=0.055 * self.scaling, visible=True)
            self.wheelfr.set(xy=(self.x + (0.2351728088 * math.cos(math.radians(self.heading + 46.3)) - 0.018) * self.scaling,
                                 self.y + (0.2351728088 * math.sin(math.radians(self.heading + 46.3)) - 0.0475) * self.scaling),
                             width=0.05 * self.scaling, angle=self.velocityAngle,
                             height=0.1 * self.scaling, lw=None, fill=True, visible=True)
            self.wheelbr.set(xy=(self.x + (0.2351728088 * math.cos(math.radians(self.heading + 316.3)) - 0.025) * self.scaling,
                                 self.y + (0.2351728088 * math.sin(math.radians(self.heading + 316.3)) - 0.0575) * self.scaling),
                             width=0.05 * self.scaling, angle=self.velocityAngle,
                             height=0.1 * self.scaling, lw=None, fill=True)
            self.wheelfl.set(xy=(self.x + (0.2351728088 * math.cos(math.radians(self.heading + 133.7)) - 0.02425) * self.scaling,
                                 self.y + (0.2351728088 * math.sin(math.radians(self.heading + 133.7)) - 0.0475) * self.scaling),
                             width=0.05 * self.scaling, angle=self.velocityAngle,
                             height=0.1 * self.scaling, lw=None, fill=True)
            self.wheelbl.set(xy=(self.x + (0.2351728088 * math.cos(math.radians(self.heading + 226.3)) - 0.024725) * self.scaling,
                                 self.y + (0.2351728088 * math.sin(math.radians(self.heading + 226.3)) - 0.046) * self.scaling),
                             width=0.05 * self.scaling, angle=self.velocityAngle,
                             height=0.1 * self.scaling, lw=None, fill=True)
            self.eyer.set(
                center=(self.x + 0.09848857801 * self.scaling * math.cos(math.radians(self.heading + 24)), self.y +
                        0.09848857801 * self.scaling * math.sin(math.radians(self.heading + 24))),
                radius=0.05 * self.scaling)
            self.eyel.set(
                center=(self.x + 0.08762257748 * self.scaling * math.cos(math.radians(self.heading + 156)), self.y +
                        0.08762257748 * self.scaling * math.sin(math.radians(self.heading + 156))),
                radius=0.05 * self.scaling)
            self.pupilr.set(
                center=(self.x + 0.09848857801 * self.scaling * math.cos(math.radians(self.heading + 24)), self.y +
                        0.09848857801 * self.scaling * math.sin(math.radians(self.heading + 24))),
                radius=0.02 * self.scaling)
            self.pupill.set(
                center=(self.x + 0.08762257748 * self.scaling * math.cos(math.radians(self.heading + 156)), self.y +
                        0.08762257748 * self.scaling * math.sin(math.radians(self.heading + 156))),
                radius=0.02 * self.scaling)
            self.frontTriangle.set(xy=((self.x + 0.24 * math.cos(math.radians(self.heading + 90)) * self.scaling,
                                        self.y + 0.24 * math.sin(math.radians(self.heading + 90)) * self.scaling),
                                       (self.x + 0.18172781845 * math.cos(
                                           math.radians(self.heading + 82)) * self.scaling,
                                        self.y + 0.18172781845 * math.sin(
                                            math.radians(self.heading + 82)) * self.scaling),
                                       (self.x + 0.18172781845 * math.cos(
                                           math.radians(self.heading + 98)) * self.scaling,
                                        self.y + 0.18172781845 * math.sin(
                                            math.radians(self.heading + 98)) * self.scaling)), visible=True)
            self.centerPt.set(center=(self.x, self.y))

            return self.body, self.wheelHolefr, self.wheelHolebr, self.wheelHolefl, self.wheelHolebl, self.wheelfr, self.wheelbr, self.wheelfl, self.wheelbl, self.eyer, self.eyel, self.pupilr, self.pupill, self.frontTriangle, self.centerPt


# do I really need a comment?
def updateFrame(frame, ax, robot: Robot, trailX, trailY, trail):
    # updating the robot trail
    trailX.append(robot.x)
    trailY.append(robot.y)

    # combining the trail x and y to show the trail
    trail.set_data(trailX, trailY)

    # the robot draws itself
    return (trail,) + robot.draw(ax)


# --------------- MAIN --------------- #

# calls the functions which actually does stuff
# the function is literally useless, but I hold onto my c++ roots
def main():
    # kinda rhymes
    if __name__ == "__main__":
        animation = Animation()
        animation.display()
    else:
        exit("Not main Python file.")


# I do not embrace some python aspects
main()
plt.close()
