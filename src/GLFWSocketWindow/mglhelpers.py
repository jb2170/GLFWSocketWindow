import moderngl

class HasMGLContext:
    """Has ModernGL Context"""

    def __init__(self, gl: moderngl.Context):
        self._gl = gl

    @property
    def gl(self):
        return self._gl

def create_simple_framebuffer(gl: moderngl.Context, width: int, height: int) -> moderngl.Framebuffer:
    """One RGBA color texture, no depth buffer"""

    texture = gl.texture((width, height), 4)
    texture.filter = (gl.NEAREST, gl.NEAREST)

    color_attachments = (texture,)
    framebuffer = gl.framebuffer(color_attachments)

    return framebuffer
