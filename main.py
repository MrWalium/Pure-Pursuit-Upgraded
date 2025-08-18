# --------------- DEPENDENCIES --------------- #
# showing the animation with matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button

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

    def get_coord(self) -> tuple[float, float]:
        """
        So you can get the coordinate of a Waypoint

        Return:
            tuple of the x and y positions of the waypoint (x, y)
        """
        return self.x, self.y


path = [Waypoint(0, 0), Waypoint(0.571194595265405, -0.4277145118491421), Waypoint(1.1417537280142898,
        -0.8531042347260006)]


def convert_to_list(list_waypoints: list[Waypoint] = path) -> list[tuple[float, float]]:
    """Converts the list of waypoints to a list of tuples with the waypoint coordinates."""
    return [waypoint.get_coord() for waypoint in list_waypoints]


# --------------- CLASSES --------------- #

class Buttons:
    def __init__(self):
        self.is_auto = False

    def auto_manual(self):
        if self.is_auto:
            pass


class Animation:
    def __init__(self):
        # --- displaying plot stuff --- #

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

        # --- drawing stuff --- #

        # the path the robot is following drawn
        path_for_graph = np.array(convert_to_list())
        self.drawn_path = plt.plot(path_for_graph[:, 0], path_for_graph[:, 1], animated=True, color='black',
                                   solid_capstyle='round', linewidth=1)

        # the robot -_-
        self.robot = Robot(self.ax)

        # The trail X and Y will be combined to draw the trail
        # the trig is so the trail comes out of the back of the robot
        self.trail_x = [self.robot.x - 0.25 * math.sin(math.radians(-self.robot.heading))]
        self.trail_y = [self.robot.y - 0.25 * math.cos(math.radians(-self.robot.heading))]

        # the trail of how the robot has moved
        self.trail, = plt.plot(self.trail_x, self.trail_y, "-", color=(1, 0.79, 0, 0.6), linewidth=4, zorder=1)

    def display(self):
        # This is how we display the animation, where it basically updates every frame
        anim = animation.FuncAnimation(fig=self.fig, func=partial(updateFrame, ax=self.ax, robot=self.robot,
                                       trailX=self.trail_x, trailY=self.trail_y, trail=self.trail), blit=True,
                                       cache_frame_data=False, interval=10)
        # showing the plot
        plt.show()


class Robot:
    """
    A Robot class which will hold all of the positional variables and
    other information about the robot, it also updates and drawing the robot

    """
    def __init__(self, ax, x: float = 0, y: float = 0, heading: float = 0, MAX_VELOCITY: float = 0.1,
                 MAX_ACCELERATION: float = 1, MAX_TURN_VELOCITY: float = 3.35, MAX_TURN_ACCELERATION: float = 1,
                 scaling: float = 1, isdiffy: bool = True):
        """
        Initializes all of the positional, velocity, acceleration, maximum, and draw shape variables.
        Args:
            ax: the axis on which the robot is drawn
            x: initial x position of the robot
            y: initial y position of the robot
            heading: initial heading of the robot
            MAX_VELOCITY: maximum linear velocity
            MAX_ACCELERATION: maximum linear acceleration
            MAX_TURN_VELOCITY: maximum rate of change in velocity angle
            scaling: how much bigger or smaller the robot is drawn
            isdiffy: if the robot is drawn with a differential swerve or mecanum drivetrain
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
        self.turn_velocity = 3.35
        self.velocity_angle = 0

        # accelerations
        self.acceleration = 0
        self.turn_acceleration = 0

        # maximums
        self.MAX_VELOCITY = MAX_VELOCITY
        self.MAX_ACCELERATION = MAX_ACCELERATION
        self.MAX_TURN_VELOCITY = MAX_TURN_VELOCITY
        self.MAX_TURN_ACCELERATION = MAX_TURN_ACCELERATION

        # for drawing
        # to scale the robot shown by a factor of scaling
        self.scaling = scaling
        self.is_diffy = isdiffy

        # --- drawing variables --- #
        # initializes the variables used to draw the robot
        self.init_ui()

    def init_ui(self):
        """
        Initializes the objects used to display the robot on the plot
        Only the main unchanging attributes are kept because things like
        position are going to be immediately updated anyway.
        """
        # (x, y) positions, widths, radius's, etc. are 0 because
        # they are going to be updated immediately in the update function anyway

        self.body = plt.Rectangle((0, 0), width=0, height=0, angle=self.heading,
                                  rotation_point='center', lw=None, color='darkslategrey', animated=True)
        # r=right, l=left, f=front, b=back
        self.wheel_fr = plt.Rectangle((0, 0), width=0, height=0, angle=self.heading,
                                      rotation_point='center', lw=None, color='black', animated=True)
        self.wheel_br = plt.Rectangle((0, 0), width=0, height=0, angle=self.heading,
                                      rotation_point='center', lw=None, color='black', animated=True)
        self.wheel_fl = plt.Rectangle((0, 0), width=0, height=0, angle=self.heading,
                                      rotation_point='center', lw=None, color='black', animated=True)
        self.wheel_bl = plt.Rectangle((0, 0), width=0, height=0, angle=self.heading,
                                      rotation_point='center', lw=None, color='black', animated=True)
        self.eye_r = plt.Circle((0, 0), radius=0.05 * self.scaling, color='white', lw=None, animated=True)
        self.eye_l = plt.Circle((0, 0), radius=0.05 * self.scaling, color='white', lw=None, animated=True)
        self.pupil_r = plt.Circle((0, 0), radius=0.02 * self.scaling, color='black', lw=None, animated=True)
        self.pupil_l = plt.Circle((0, 0), radius=0.02 * self.scaling, color='black', lw=None, animated=True)

        self.center_pt = plt.Circle((self.x, self.y), radius=0.01 * self.scaling, color='black', animated=True)

        self.front_triangle = plt.Polygon(((0, 0), (0, 0)), fill=True, color='firebrick', animated=True)

        # so the wheels can rotate
        self.wheel_hole_fr = plt.Circle((0, 0), radius=0.055, color='darkgrey', animated=True)
        self.wheel_hole_br = plt.Circle((0, 0), radius=0.055, color='darkgrey', animated=True)
        self.wheel_hole_fl = plt.Circle((0, 0), radius=0.055, color='darkgrey', animated=True)
        self.wheel_hole_bl = plt.Circle((0, 0), radius=0.055, color='darkgrey', animated=True)

        # adding each shape to a patch so that it can be displayed
        self.ax.add_patch(self.body)
        self.ax.add_patch(self.center_pt)
        self.ax.add_patch(self.front_triangle)
        self.ax.add_patch(self.wheel_hole_fr)
        self.ax.add_patch(self.wheel_hole_br)
        self.ax.add_patch(self.wheel_hole_fl)
        self.ax.add_patch(self.wheel_hole_bl)
        self.ax.add_patch(self.wheel_fr)
        self.ax.add_patch(self.wheel_br)
        self.ax.add_patch(self.wheel_fl)
        self.ax.add_patch(self.wheel_bl)
        self.ax.add_patch(self.eye_r)
        self.ax.add_patch(self.eye_l)
        self.ax.add_patch(self.pupil_r)
        self.ax.add_patch(self.pupil_l)

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
        self.turn_acceleration = 0

        self.velocity = min(self.velocity + self.acceleration, self.MAX_VELOCITY)
        self.turn_velocity = math.copysign(min(abs(self.turn_velocity + self.turn_acceleration),
                                           self.MAX_TURN_VELOCITY), self.turn_velocity)
        # turn velocity is how much the velocity angle changes by
        self.velocity_angle += self.turn_velocity

        # changing the robot position
        self.x += self.velocity * math.sin(math.radians(-self.velocity_angle))
        self.y += self.velocity * math.cos(math.radians(self.velocity_angle))

        # going to add velocity and acceleration to this later
        self.heading += 0

    def draw(self, ax):
        """
        Calls the update function, and draws the robot, either with a mecanum or differential swerve drivetrain.
        It updates all the shapes positions and attributes.
        The is_diffy variable controls if a differential swerve or mecanum drivetrain is drawn.

        Args:
            ax: the axis to add patches to so the shapes can be drawn
        """
        self.update()
        
        if not self.is_diffy:
            # draws the mecanum drivetrain
            return self.draw_mecanum()
        else:
            # draws the differential swerve drivetrain
            return self.draw_diffy()

    # hopefully no one including me should have to ever go through this code again
    def draw_mecanum(self):
        """
        Specifically draws the mecanum drivetrain
        This function is called by the general draw() function when the is_diffy variable is False.
        """
        self.body.set(xy=(self.x - 0.15 * self.scaling, self.y - 0.25 * self.scaling),
                      width=0.30 * self.scaling,
                      height=0.5 * self.scaling, angle=self.heading)
        # r=right, l=left, f=front, b=back
        self.wheel_fr.set(xy=(self.x + (0.25 * math.cos(math.radians(self.heading + 36.8698976)) - 0.05) *
                              self.scaling,
                              self.y + (0.25 * math.sin(math.radians(self.heading + 36.8698976)) - 0.1) *
                              self.scaling),
                          width=0.1 * self.scaling,
                          height=0.2 * self.scaling, angle=self.heading, lw=0.1,
                          color='black', hatch='////////', fill=False)
        self.wheel_br.set(xy=(self.x + (0.25 * math.cos(math.radians(self.heading + 323.1301024)) - 0.05) *
                              self.scaling,
                              self.y + (0.25 * math.sin(math.radians(self.heading + 323.1301024)) - 0.1) *
                              self.scaling),
                          width=0.1 * self.scaling,
                          height=0.2 * self.scaling, angle=self.heading, lw=0.1,
                          color='black', hatch='\\\\\\\\\\\\\\\\\\', fill=False)
        self.wheel_fl.set(xy=(self.x + (0.25 * math.cos(math.radians(self.heading + 143.1301024)) - 0.05) *
                              self.scaling,
                              self.y + (0.25 * math.sin(math.radians(self.heading + 143.1301024)) - 0.1) *
                              self.scaling),
                          width=0.1 * self.scaling,
                          height=0.2 * self.scaling, angle=self.heading, lw=0.1,
                          color='black', hatch='\\\\\\\\\\\\\\\\\\', fill=False)
        self.wheel_bl.set(xy=(self.x + (0.25 * math.cos(math.radians(self.heading + 216.8698976)) - 0.05) *
                              self.scaling,
                              self.y + (0.25 * math.sin(math.radians(self.heading + 216.8698976)) - 0.1) *
                              self.scaling),
                          width=0.1 * self.scaling,
                          height=0.2 * self.scaling, angle=self.heading, lw=0.1,
                          color='black', hatch='////////', fill=False)
        self.eye_r.set(
            center=(self.x + 0.19235384061 * self.scaling * math.cos(math.radians(self.heading + 64)), self.y +
                    0.19235384061 * self.scaling *
                    math.sin(math.radians(self.heading + 64))), radius=0.05 * self.scaling)
        self.eye_l.set(
            center=(self.x + 0.19235384061 * self.scaling * math.cos(math.radians(self.heading + 110)), self.y +
                    0.19235384061 * self.scaling *
                    math.sin(math.radians(self.heading + 110))), radius=0.05 * self.scaling)
        self.pupil_r.set(
            center=(self.x + 0.19235384061 * self.scaling * math.cos(math.radians(self.heading + 64)), self.y +
                    0.19235384061 * self.scaling *
                    math.sin(math.radians(self.heading + 64))), radius=0.02 * self.scaling)
        self.pupil_l.set(
            center=(self.x + 0.19235384061 * self.scaling * math.cos(math.radians(self.heading + 110)), self.y +
                    0.19235384061 * self.scaling *
                    math.sin(math.radians(self.heading + 110))), radius=0.02 * self.scaling)
        self.center_pt.set(center=(self.x, self.y))

        if self.front_triangle.get_visible():
            # setting parts of the diffy swerve to not be visible
            self.front_triangle.set_visible(False)
            self.wheel_hole_fr.set_visible(False)
            self.wheel_hole_br.set_visible(False)
            self.wheel_hole_fl.set_visible(False)
            self.wheel_hole_bl.set_visible(False)
            return self.body, self.wheel_fr, self.wheel_br, self.wheel_fl, self.wheel_bl, self.eye_r, self.eye_l, self.pupil_r, self.pupil_l, self.front_triangle, self.wheel_hole_fr, self.wheel_hole_br, self.wheel_hole_fl, self.wheel_hole_bl, self.center_pt
        return self.body, self.wheel_fr, self.wheel_br, self.wheel_fl, self.wheel_bl, self.eye_r, self.eye_l, self.pupil_r, self.pupil_l, self.center_pt
    
    # hopefully no one including me should have to ever go through this code again
    def draw_diffy(self):
        """
        Specifically draws the differential swerve drivetrain.
        This function is called by the general draw() function when the variable is_diffy is True.
        """
        self.body.set(xy=(self.x - 0.25 * self.scaling, self.y - 0.25 * self.scaling),
                      width=0.5 * self.scaling,
                      height=0.5 * self.scaling, angle=self.heading)
        # r=right, l=left, f=front, b=back
        self.wheel_hole_fr.set(
            center=(self.x + 0.24234531148 * math.cos(math.radians(self.heading + 45)) * self.scaling,
                    self.y + 0.24234531148 * math.sin(math.radians(self.heading + 45)) * self.scaling),
            radius=0.055 * self.scaling, visible=True)
        self.wheel_hole_br.set(
            center=(self.x + 0.24234531148 * math.cos(math.radians(self.heading + 315)) * self.scaling,
                    self.y + 0.24234531148 * math.sin(math.radians(self.heading + 315)) * self.scaling),
            radius=0.055 * self.scaling, visible=True)
        self.wheel_hole_fl.set(
            center=(self.x + 0.23234531148 * math.cos(math.radians(self.heading + 133)) * self.scaling,
                    self.y + 0.23234531148 * math.sin(math.radians(self.heading + 133)) * self.scaling),
            radius=0.055 * self.scaling, visible=True)
        self.wheel_hole_bl.set(
            center=(self.x + 0.23234531148 * math.cos(math.radians(self.heading + 226)) * self.scaling,
                    self.y + 0.23234531148 * math.sin(math.radians(self.heading + 226)) * self.scaling),
            radius=0.055 * self.scaling, visible=True)
        self.wheel_fr.set(
            xy=(self.x + (0.2351728088 * math.cos(math.radians(self.heading + 46.3)) - 0.018) * self.scaling,
                self.y + (0.2351728088 * math.sin(math.radians(self.heading + 46.3)) - 0.0475) * self.scaling),
            width=0.05 * self.scaling, angle=self.velocity_angle,
            height=0.1 * self.scaling, lw=None, fill=True)
        self.wheel_br.set(
            xy=(self.x + (0.2351728088 * math.cos(math.radians(self.heading + 316.3)) - 0.025) * self.scaling,
                self.y + (0.2351728088 * math.sin(math.radians(self.heading + 316.3)) - 0.0575) * self.scaling),
            width=0.05 * self.scaling, angle=self.velocity_angle,
            height=0.1 * self.scaling, lw=None, fill=True)
        self.wheel_fl.set(
            xy=(self.x + (0.2351728088 * math.cos(math.radians(self.heading + 133.7)) - 0.02425) * self.scaling,
                self.y + (0.2351728088 * math.sin(math.radians(self.heading + 133.7)) - 0.0475) * self.scaling),
            width=0.05 * self.scaling, angle=self.velocity_angle,
            height=0.1 * self.scaling, lw=None, fill=True)
        self.wheel_bl.set(
            xy=(self.x + (0.2351728088 * math.cos(math.radians(self.heading + 226.3)) - 0.024725) * self.scaling,
                self.y + (0.2351728088 * math.sin(math.radians(self.heading + 226.3)) - 0.046) * self.scaling),
            width=0.05 * self.scaling, angle=self.velocity_angle,
            height=0.1 * self.scaling, lw=None, fill=True)
        self.eye_r.set(
            center=(self.x + 0.09848857801 * self.scaling * math.cos(math.radians(self.heading + 24)), self.y +
                    0.09848857801 * self.scaling * math.sin(math.radians(self.heading + 24))),
            radius=0.05 * self.scaling)
        self.eye_l.set(
            center=(self.x + 0.08762257748 * self.scaling * math.cos(math.radians(self.heading + 156)), self.y +
                    0.08762257748 * self.scaling * math.sin(math.radians(self.heading + 156))),
            radius=0.05 * self.scaling)
        self.pupil_r.set(
            center=(self.x + 0.09848857801 * self.scaling * math.cos(math.radians(self.heading + 24)), self.y +
                    0.09848857801 * self.scaling * math.sin(math.radians(self.heading + 24))),
            radius=0.02 * self.scaling)
        self.pupil_l.set(
            center=(self.x + 0.08762257748 * self.scaling * math.cos(math.radians(self.heading + 156)), self.y +
                    0.08762257748 * self.scaling * math.sin(math.radians(self.heading + 156))),
            radius=0.02 * self.scaling)
        self.front_triangle.set(xy=((self.x + 0.24 * math.cos(math.radians(self.heading + 90)) * self.scaling,
                                     self.y + 0.24 * math.sin(math.radians(self.heading + 90)) * self.scaling),
                                    (self.x + 0.18172781845 * math.cos(
                                        math.radians(self.heading + 82)) * self.scaling,
                                     self.y + 0.18172781845 * math.sin(
                                         math.radians(self.heading + 82)) * self.scaling),
                                    (self.x + 0.18172781845 * math.cos(
                                        math.radians(self.heading + 98)) * self.scaling,
                                     self.y + 0.18172781845 * math.sin(
                                         math.radians(self.heading + 98)) * self.scaling)), visible=True)
        self.center_pt.set(center=(self.x, self.y))

        return self.body, self.wheel_hole_fr, self.wheel_hole_br, self.wheel_hole_fl, self.wheel_hole_bl, self.wheel_fr, self.wheel_br, self.wheel_fl, self.wheel_bl, self.eye_r, self.eye_l, self.pupil_r, self.pupil_l, self.front_triangle, self.center_pt


# do I really need a comment?
def updateFrame(frame, ax, robot: Robot, trailX: list[float], trailY: list[float], trail):
    # updating the robot trail
    # the trig is so that the trail comes out of the back of the robot
    trailX.append(robot.x - 0.25 * math.sin(math.radians(-robot.heading)))
    trailY.append(robot.y - 0.25 * math.cos(math.radians(-robot.heading)))

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
