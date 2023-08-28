"""Contains the pyvista.Text class."""
from __future__ import annotations

import os
import pathlib
from typing import Sequence

import pyvista as pv
from pyvista.core.utilities.misc import _check_range, no_new_attr

from . import _vtk
from ._typing import ColorLike
from .colors import Color
from .themes import Theme
from .tools import FONTS


@no_new_attr
class CornerAnnotation(_vtk.vtkCornerAnnotation):
    """Text annotation in four corners.

    This is an annotation object that manages four text actors / mappers to provide annotation in the four corners of a viewport.

    Parameters
    ----------
    position : str | bool
        Position of the text.

    text : str
        Text input.

    prop : TextProperty
        Text property.

    linear_font_scale_factor : float
        Linear font scale factor.

    Examples
    --------
    Create text annotation in four corners.

    >>> from pyvista import CornerAnnotation
    >>> text = CornerAnnotation(0, 'text')
    >>> prop = text.prop
    """

    def __init__(self, position, text, prop=None, linear_font_scale_factor=None):
        """Initialize a new text annotation descriptor."""
        super().__init__()
        self.set_text(position, text)
        if prop is None:
            self.prop = TextProperty()
        if linear_font_scale_factor is not None:
            self.linear_font_scale_factor = linear_font_scale_factor

    def get_text(self, position):
        """Get the text to be displayed for each corner.

        Parameters
        ----------
        position : str | bool
            Position of the text.

        Returns
        -------
        str
            Text to be displayed for each corner.
        """
        return self.GetText(position)

    def set_text(self, position, text):
        """Set the text to be displayed for each corner.

        Parameters
        ----------
        position : str | bool
            Position of the text.

        text : str
            Text to be displayed for each corner.
        """
        corner_mappings = {
            'lower_left': self.LowerLeft,
            'lower_right': self.LowerRight,
            'upper_left': self.UpperLeft,
            'upper_right': self.UpperRight,
            'lower_edge': self.LowerEdge,
            'upper_edge': self.UpperEdge,
            'left_edge': self.LeftEdge,
            'right_edge': self.RightEdge,
        }
        corner_mappings['ll'] = corner_mappings['lower_left']
        corner_mappings['lr'] = corner_mappings['lower_right']
        corner_mappings['ul'] = corner_mappings['upper_left']
        corner_mappings['ur'] = corner_mappings['upper_right']
        corner_mappings['top'] = corner_mappings['upper_edge']
        corner_mappings['bottom'] = corner_mappings['lower_edge']
        corner_mappings['right'] = corner_mappings['right_edge']
        corner_mappings['r'] = corner_mappings['right_edge']
        corner_mappings['left'] = corner_mappings['left_edge']
        corner_mappings['l'] = corner_mappings['left_edge']
        if isinstance(position, str):
            position = corner_mappings[position]
        elif position is True:
            position = corner_mappings['upper_left']
        self.SetText(position, text)

    @property
    def prop(self):
        """Return or set the property of this actor.

        Returns
        -------
        TextProperty
            Property of this actor.
        """
        return self.GetTextProperty()

    @prop.setter
    def prop(self, prop: TextProperty):
        """Set the property of this actor.

        Parameters
        ----------
        prop : TextProperty
            Property of this actor.
        """
        self.SetTextProperty(prop)

    @property
    def linear_font_scale_factor(self):
        """Get font scaling factors.

        Returns
        -------
        float
            Font scaling factors.
        """
        return self.GetLinearFontScaleFactor()

    @linear_font_scale_factor.setter
    def linear_font_scale_factor(self, factor: float):
        """Set font scaling factors.

        Parameters
        ----------
        factor : float
            Font scaling factor.
        """
        self.SetLinearFontScaleFactor(factor)


@no_new_attr
class Text(_vtk.vtkTextActor):
    r"""Define text by default theme.

    Parameters
    ----------
    text : str, optional
        Text string to be displayed.
        "\n" is recognized as a carriage return/linefeed (line separator).
        The characters must be in the UTF-8 encoding.

    position : Sequence[float], optional
        The position coordinate.

    prop : TextProperty, optional
        The property of this actor.

    Examples
    --------
    Create a text with text's property.

    >>> from pyvista import Text
    >>> text = Text()
    >>> prop = text.prop
    """

    def __init__(self, text=None, position=None, prop=None):
        """Initialize a new text descriptor."""
        super().__init__()
        if text is not None:
            self.input = text
        if position is not None:
            self.position = position
        if prop is None:
            self.prop = TextProperty()

    @property
    def input(self):
        """Get the text string to be displayed.

        Returns
        -------
        str
            Text string to be displayed.
        """
        return self.GetInput()

    @input.setter
    def input(self, text: str):
        r"""Set the text string to be displayed.

        Parameters
        ----------
        text : str
            Text string to be displayed.
            "\n" is recognized as a carriage return/linefeed (line separator).
            The characters must be in the UTF-8 encoding.
        """
        self.SetInput(text)

    @property
    def prop(self):
        """Return the property of this actor.

        Returns
        -------
        str
            The property of this actor.
        """
        return self.GetTextProperty()

    @prop.setter
    def prop(self, prop: TextProperty):
        """Set the property of this actor.

        Parameters
        ----------
        prop : TextProperty
            The property of this actor.
        """
        self.SetTextProperty(prop)

    @property
    def position(self):
        """Get the position coordinate.

        Returns
        -------
        Sequence[float]
            The position coordinate.
        """
        return self.GetPosition()

    @position.setter
    def position(self, position: Sequence[float]):
        """Set the position coordinate.

        Parameters
        ----------
        position : Sequence[float]
            The position coordinate.
        """
        self.SetPosition(position[0], position[1])


@no_new_attr
class TextProperty(_vtk.vtkTextProperty):
    """Define text's property.

    Parameters
    ----------
    theme : pyvista.plotting.themes.Theme, optional
        Plot-specific theme.

    color : ColorLike, optional
        Either a string, RGB list, or hex color string.  For example:
        ``color='white'``, ``color='w'``, ``color=[1.0, 1.0, 1.0]``, or
        ``color='#FFFFFF'``. Color will be overridden if scalars are
        specified.

    font_family : str | None, optional
        Font family or None.

    orientation : float, optional
        Text's orientation (in degrees).

    font_size : int, optional
        Font size.

    font_file : str, optional
        Font file path.

    shadow : bool, optional
        If enable the shadow.

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

    _theme = Theme()
    _color_set = None
    _background_color_set = None
    _font_family = None

    def __init__(
        self,
        theme=None,
        color=None,
        font_family=None,
        orientation=None,
        font_size=None,
        font_file=None,
        shadow=False,
    ):
        """Initialize text's property."""
        super().__init__()
        if theme is None:
            # copy global theme to ensure local property theme is fixed
            # after creation.
            self._theme.load_theme(pv.global_theme)
        else:
            self._theme.load_theme(theme)
        self.color = color
        self.font_family = font_family
        if orientation is not None:
            self.orientation = orientation
        if font_size is not None:
            self.font_size = font_size
        if font_file is not None:
            self.set_font_file(font_file)
        if shadow:
            self.enable_shadow()

    @property
    def color(self) -> Color:
        """Return the color of text's property.

        Returns
        -------
        Color
            The color of text's property.

        """
        return Color(self.GetColor())

    @color.setter
    def color(self, colo: ColorLiker):
        """Set the color of text's property.

        Parameters
        ----------
        color : ColorLike
            Either a string, RGB list, or hex color string.  For example:
            ``color='white'``, ``color='w'``, ``color=[1.0, 1.0, 1.0]``, or
            ``color='#FFFFFF'``. Color will be overridden if scalars are
            specified.

        """
        self._color_set = color is not None
        rgb_color = Color(color, default_color=self._theme.font.color)
        self.SetColor(rgb_color.float_rgb)

    @property
    def opacity(self) -> float:
        """Return or set the opacity of text's property.

        Returns
        -------
        float
            Opacity of the text. A single float value that will be applied globally
            opacity of the text and uniformly applied everywhere. Between 0 and 1.

        """
        return self.GetOpacity()

    @opacity.setter
    def opacity(self, opacity: float):
        """Set the opacity of text's property.

        Parameters
        ----------
        opacity : float
            Opacity of the text. A single float value that will be applied globally
            opacity of the text and uniformly applied everywhere. Between 0 and 1.

        """
        _check_range(opacity, (0, 1), 'opacity')
        self.SetOpacity(opacity)

    @property
    def background_color(self) -> Color:
        """Return the background color of text's property.

        Returns
        -------
        Color
            The background color of text's property.

        """
        return Color(self.GetBackgroundColor())

    @background_color.setter
    def background_color(self, color: ColorLike):
        """Return or set the background color of text's property.

        Parameters
        ----------
        color : ColorLike
            Either a string, RGB list, or hex color string.  For example:
            ``color='white'``, ``color='w'``, ``color=[1.0, 1.0, 1.0]``, or
            ``color='#FFFFFF'``. Color will be overridden if scalars are
            specified.

        """
        self._background_color_set = color is not None
        rgb_color = Color(color)
        self.SetBackgroundColor(rgb_color.float_rgb)

    @property
    def background_opacity(self) -> float:
        """Return or set the background opacity of text's property.

        Returns
        -------
        float
            Background opacity of the text. A single float value that will be applied globally.
            background opacity of the text and uniformly applied everywhere. Between 0 and 1.

        """
        return self.GetBackgroundOpacity()

    @background_opacity.setter
    def background_opacity(self, opacity: float):
        """Set the background opacity of text's property.

        Parameters
        ----------
        opacity : float
            Background opacity of the text. A single float value that will be applied globally.
            background opacity of the text and uniformly applied everywhere. Between 0 and 1.

        """
        _check_range(opacity, (0, 1), 'background_opacity')
        self.SetBackgroundOpacity(opacity)

    @property
    def show_frame(self) -> bool:
        """Return the visibility of frame.

        Returns
        -------
        bool:
            If shows the frame.

        """
        return bool(self.GetFrame())

    @show_frame.setter
    def show_frame(self, frame: bool):
        """Set the visibility of frame.

        Parameters
        ----------
        frame : bool
            If shows the frame.

        """
        self.SetFrame(frame)

    @property
    def frame_color(self) -> Color:
        """Get the frame color of text property.

        Returns
        -------
        Color
            The frame color of text property.
        """
        return Color(self.GetFrameColor())

    @frame_color.setter
    def frame_color(self, color):
        """Set the frame color of text property.

        Parameters
        ----------
        color : str | Color
            Either a string, RGB list, or hex color string.  For example:
            ``color='white'``, ``color='w'``, ``color=[1.0, 1.0, 1.0]``, or
            ``color='#FFFFFF'``. Color will be overridden if scalars are
            specified.
        """
        self.SetFrameColor(Color(color).float_rgb)

    @property
    def frame_width(self) -> int:
        """Get the width of the frame.

        Returns
        -------
        int
            The width of the frame. The width is expressed in pixels.
            The default is 1 pixel.
        """
        return self.GetFrameWidth()

    @frame_width.setter
    def frame_width(self, width: int):
        """Set the width of the frame.

        Parameters
        ----------
        width : int
            The width of the frame. The width is expressed in pixels.
            The default is 1 pixel.
        """
        self.SetFrameWidth(width)

    @property
    def font_family(self) -> str | None:
        """Get the font family.

        Returns
        -------
        str | None
            Font family or None.
        """
        return self._font_family

    @font_family.setter
    def font_family(self, font_family: str | None):
        """Set the font family.

        Parameters
        ----------
        font_family : str | None
            Font family or None.
        """
        if font_family is None:
            font_family = self._theme.font.family
        self._font_family = font_family
        self.SetFontFamily(FONTS[self._font_family].value)

    @property
    def font_size(self) -> int:
        """Get the font size.

        Returns
        -------
        int
            Font size.
        """
        return self.GetFontSize()

    @font_size.setter
    def font_size(self, font_size: int):
        """Set the font size.

        Parameters
        ----------
        font_size : int
            Font size.
        """
        self.SetFontSize(font_size)

    def enable_shadow(self) -> None:
        """Enable the shadow."""
        self.SetShadow(True)

    @property
    def orientation(self) -> float:
        """Return the text's orientation (in degrees).

        Returns
        -------
        float
            Text's orientation (in degrees).
        """
        return self.GetOrientation()

    @orientation.setter
    def orientation(self, orientation: float):
        """Set the text's orientation (in degrees).

        Parameters
        ----------
        orientation : float
            Text's orientation (in degrees).

        """
        self.SetOrientation(orientation)

    def set_font_file(self, font_file: str):
        """Set the font file.

        Parameters
        ----------
        font_file : str
            Font file path.
        """
        path = pathlib.Path(font_file)
        path = path.resolve()
        if not os.path.isfile(path):
            raise FileNotFoundError(f'Unable to locate {path}')
        self.SetFontFamily(_vtk.VTK_FONT_FILE)
        self.SetFontFile(str(path))
