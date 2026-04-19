import moderngl as mgl

class HasMGLContext:
    """Has ModernGL Context"""

    def __init__(self, gl: mgl.Context):
        self._gl = gl

    @property
    def gl(self):
        return self._gl

def create_simple_framebuffer(gl: mgl.Context, width: int, height: int) -> mgl.Framebuffer:
    """One RGBA color texture, no depth buffer"""

    texture = gl.texture((width, height), 4)
    texture.filter = (gl.NEAREST, gl.NEAREST)

    color_attachments = (texture,)
    framebuffer = gl.framebuffer(color_attachments)

    return framebuffer
