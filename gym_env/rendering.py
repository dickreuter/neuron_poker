import numpy as np
import pyglet
from math import radians, cos, sin

__author__ = 'Nicolas Dickreuter'

WHITE = list(np.array([255, 255, 255, 255]))
GREEN = list(np.array([0, 255, 0, 123]))
BLUE = list(np.array([0, 0, 128, 255]))
BLACK = list(np.array([0, 0, 0, 0]) / 255)
RED = list(np.array([255, 0, 0, 123]))
LIGHT = list(np.array([255, 150, 150, 123]))


# pylint: skip-file

class PygletWindow:
    """Rendering class"""

    def __init__(self, X, Y):
        """Initialization"""
        self.active = True
        self.display_surface = pyglet.window.Window(width=X, height=Y + 50)
        self.top = Y

        # make OpenGL context current
        self.display_surface.switch_to()
        self.reset()

    def circle(self, x_pos, y_pos, radius, color, thickness, numPoints=100):
        """Draw a circle"""
        verts = []
        y_pos = self.top - y_pos
        from pyglet.gl import glColor4f
        glColor4f(*[int(c) for c in color])
        for i in range(numPoints):
            angle = radians(float(i) / numPoints * 360.0)
            x = radius * cos(angle) + x_pos
            y = radius * sin(angle) + y_pos
            verts += [x, y]
        circle = pyglet.graphics.vertex_list(numPoints, ('v2f', verts))
        from pyglet.gl import GL_LINE_LOOP
        circle.draw(GL_LINE_LOOP)

    def text(self, text, x, y, font_size=20, color=None):
        """Draw text"""
        y = self.top - y
        label = pyglet.text.Label(text, font_size=font_size,
                                  x=x, y=y, anchor_x='left', anchor_y='top',
                                  color=[int(c) for c in color])
        label.draw()

    def rectangle(self, x, y, dx, dy, color):
        """Draw a rectangle"""
        y = self.top - y
        x = int(round(x))
        y = int(round(y))
        from pyglet.gl import glColor4f
        glColor4f(*[int(c) for c in color])
        rect = pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', [x, y, x + dx, y, x + dx, y + dy, x, y + dy]))
        rect.draw()

    def reset(self):
        """New frame"""
        pyglet.clock.tick()
        self.display_surface.dispatch_events()
        from pyglet.gl import glClear
        glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)

    def update(self):
        """Draw the current state on screen"""
        self.display_surface.flip()


if __name__ == '__main__':
    pg = PygletWindow(400, 400)

    pg.reset()
    pg.circle(5, 5, 100, 1, 5)
    pg.text("Test", 10, 10)
    pg.text("Test2", 30, 30)
    pg.update()
    input()

    pg.circle(5, 5, 100, 1, 5)
    pg.text("Test3333", 10, 10)
    pg.text("Test2123123", 303, 30)
    pg.update()
    input()
