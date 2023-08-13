"""Contains the pyvista.Text class."""
from __future__ import annotations

import pyvista as pv
from pyvista.core.utilities.misc import _check_range, no_new_attr

from . import _vtk
from .colors import Color


@no_new_attr
class Text(_vtk.vtkTextActor):
    """Define text by default theme.

    Examples
    --------
    Create a text with text's property.

    >>> from pyvista import Text
    >>> text = Text()
    >>> prop = text.prop
    """

    def __init__(self, prop=None):
        """Initialize a new text descriptor."""
        if prop is None:
            self.prop = TextProperty()

    @property
    def input(self):
        r"""Set the text string to be displayed.

        "\n" is recognized as a carriage return/linefeed (line separator).
        The characters must be in the UTF-8 encoding.
        """
        return self.GetInput()

    @input.setter
    def input(self, obj: str):
        self.SetInput(obj)

    @property
    def prop(self):
        """Return or set the property of this actor."""
        return self.GetTextProperty()

    @prop.setter
    def prop(self, obj: TextProperty):
        self.SetTextProperty(obj)


@no_new_attr
class TextProperty(_vtk.vtkTextProperty):
    """Define text's property.

    Examples
    --------
    Create a text's property.

    >>> from pyvista import TextProperty
    >>> prop = TextProperty()
    >>> prop.opacity = 0.5
    >>> prop.background_color = "b"
    >>> prop.background_opacity = 0.5
    >>> prop.show_frame = True
    >>> prop.frame_color = "b"
    >>> prop.frame_width = 10
    >>> prop.frame_color
    Color(name='blue', hex='#0000ffff', opacity=255)

    """

    _theme = None
    _color_set = None
    _background_color_set = None

    def __init__(self, theme=None):
        """Initialize text's property."""
        self._theme = pv.themes.Theme()
        if theme is None:
            # copy global theme to ensure local property theme is fixed
            # after creation.
            self._theme.load_theme(pv.global_theme)
        else:
            self._theme.load_theme(theme)

    @property
    def color(self) -> Color:
        """Return or set the color of text's property.

        Either a string, RGB list, or hex color string.  For example:
        ``color='white'``, ``color='w'``, ``color=[1.0, 1.0, 1.0]``, or
        ``color='#FFFFFF'``. Color will be overridden if scalars are
        specified.

        Examples
        --------
        Set the color to blue.

        >>> import pyvista as pv
        >>> prop = pv.TextProperty()
        >>> prop.color = 'b'
        >>> prop.color
        Color(name='blue', hex='#0000ffff', opacity=255)

        """
        return Color(self.GetColor())

    @color.setter
    def color(self, value):
        self._color_set = value is not None
        rgb_color = Color(value, default_color=self._theme.color)
        self.SetColor(rgb_color.float_rgb)

    @property
    def opacity(self) -> float:
        """Return or set the opacity of text's property.

        Opacity of the text. A single float value that will be applied globally
        opacity of the text and uniformly applied everywhere. Between 0 and 1.

        Examples
        --------
        Set opacity to ``0.5``.

        >>> import pyvista as pv
        >>> prop = pv.TextProperty()
        >>> prop.opacity = 0.5
        >>> prop.opacity
        0.5

        """
        return self.GetOpacity()

    @opacity.setter
    def opacity(self, value: float):
        _check_range(value, (0, 1), 'opacity')
        self.SetOpacity(value)

    @property
    def background_color(self):
        """Return or set the background color of text's property.

        Either a string, RGB list, or hex color string.  For example:
        ``color='white'``, ``color='w'``, ``color=[1.0, 1.0, 1.0]``, or
        ``color='#FFFFFF'``. Color will be overridden if scalars are
        specified.

        Examples
        --------
        Set the background color to blue.

        >>> import pyvista as pv
        >>> prop = pv.TextProperty()
        >>> prop.background_color = 'b'
        >>> prop.background_color
        Color(name='blue', hex='#0000ffff', opacity=255)

        """
        return Color(self.GetBackgroundColor())

    @background_color.setter
    def background_color(self, value):
        self._background_color_set = value is not None
        rgb_color = Color(value, default_color=self._theme.background)
        self.SetBackgroundColor(rgb_color.float_rgb)

    @property
    def background_opacity(self):
        """Return or set the background opacity of text's property.

        Background opacity of the text. A single float value that will be applied globally
        background opacity of the text and uniformly applied everywhere. Between 0 and 1.

        Examples
        --------
        Set background opacity to ``0.5``.

        >>> import pyvista as pv
        >>> prop = pv.TextProperty()
        >>> prop.background_opacity = 0.5
        >>> prop.background_opacity
        0.5

        """
        return self.GetBackgroundOpacity()

    @background_opacity.setter
    def background_opacity(self, value: float):
        _check_range(value, (0, 1), 'background_opacity')
        self.SetBackgroundOpacity(value)

    @property
    def show_frame(self) -> bool:
        """Return or set the visibility of frame.

        Shows or hides the frame.

        Examples
        --------
        >>> import pyvista as pv
        >>> prop = pv.TextProperty()
        >>> prop.show_frame = True
        >>> prop.show_frame
        True

        """
        return bool(self.GetFrame())

    @show_frame.setter
    def show_frame(self, value: bool):
        self.SetFrame(value)

    @property
    def frame_color(self) -> Color:
        """Return or set the frame color of this property.

        Either a string, RGB list, or hex color string.  For example:
        ``color='white'``, ``color='w'``, ``color=[1.0, 1.0, 1.0]``, or
        ``color='#FFFFFF'``. Color will be overridden if scalars are
        specified.

        Examples
        --------
        Set the frame color to blue.

        >>> import pyvista as pv
        >>> prop = pv.TextProperty()
        >>> prop.frame_color = 'b'
        >>> prop.frame_color
        Color(name='blue', hex='#0000ffff', opacity=255)

        """
        return Color(self.GetFrameColor())

    @frame_color.setter
    def frame_color(self, value):
        self.SetFrameColor(Color(value).float_rgb)

    @property
    def frame_width(self) -> int:
        """Set/Get the width of the frame.

        The width is expressed in pixels. The default is 1 pixel.

        Examples
        --------
        Change the frame width to ``10``.

        >>> import pyvista as pv
        >>> prop = pv.TextProperty()
        >>> prop.frame_width = 10
        >>> prop.frame_width
        10

        """
        return self.GetFrameWidth()

    @frame_width.setter
    def frame_width(self, value: int):
        self.SetFrameWidth(value)
