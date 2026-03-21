import moderngl
import glfw

from .mglhelpers import HasMGLContext, create_simple_framebuffer
from .util import ChunkedNonBlockReader

class GLFWWindow(HasMGLContext):
    def __init__(self, width: int, height: int, title: str = "GLFW Window"):
        # Initialize GLFW
        if not glfw.init():
            raise Exception("glfw.init() failed")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        # Create a windowed mode window and its OpenGL context
        window_handle = glfw.create_window(width, height, title, None, None)
        if not window_handle:
            glfw.terminate()
            raise Exception("glfw.create_window() failed")

        # Make the window's context current
        glfw.make_context_current(window_handle)

        # Detect OpenGL context from GLFW
        gl = moderngl.create_context()

        # We'll deal with it from here using ModernGL

        framebuffer = create_simple_framebuffer(gl, width, height)

        super().__init__(gl)
        self._width = width
        self._height = height
        self._handle = window_handle
        self._framebuffer = framebuffer

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def handle(self):
        return self._handle

    @property
    def framebuffer(self):
        return self._framebuffer

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.terminate()

    def poll_events(self) -> None:
        glfw.poll_events()

    def swap_buffers(self) -> None:
        glfw.swap_buffers(self.handle)

    def should_close(self) -> bool:
        return glfw.window_should_close(self.handle)

    def raise_for_close(self) -> None:
        # Name inspired by urllib raise_for_status

        if self.should_close():
            raise KeyboardInterrupt

    def terminate(self) -> None:
        glfw.terminate()

    def read_frame(self, chunked_reader: ChunkedNonBlockReader):
        gl = self.gl

        # pixels = bytearray(floats_per_image)
        #
        # for row_idx in range(rows_per_image):
        #     for col_idx in range(pixels_per_row):
        #         pixel_offset = floats_per_row * row_idx + floats_per_pixel * col_idx
        #
        #         pixels[pixel_offset + 0] = 0
        #         pixels[pixel_offset + 1] = 0
        #         pixels[pixel_offset + 2] = 255
        #         pixels[pixel_offset + 3] = 128

        try:
            pixels = chunked_reader.read()
        except (BlockingIOError, EOFError):
            raise

        texture = self.framebuffer.color_attachments[0]

        texture.write(pixels)

        gl.copy_framebuffer(dst = gl.screen, src = self.framebuffer)

    def main(self, sock):
        floats_per_pixel = 4
        pixels_per_row = self.width
        rows_per_image = self.height

        floats_per_row = floats_per_pixel * pixels_per_row
        floats_per_image = floats_per_row * rows_per_image

        chunked_reader = ChunkedNonBlockReader(sock, floats_per_image)

        # Loop until the user closes the window
        while True:
            self.raise_for_close()

            try:
                self.read_frame(chunked_reader)
            except BlockingIOError:
                pass
            except EOFError:
                return
            else:
                self.swap_buffers()

            self.poll_events()
