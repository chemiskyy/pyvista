"""Affine widget module."""
import numpy as np

import pyvista as pv
from pyvista.core.errors import VTKVersionError
from pyvista.core.utilities.misc import try_callback

from . import _vtk

DARK_YELLOW = (0.9647058823529412, 0.7450980392156863, 0)
INDEX_MAPPER = {0: 1, 1: 2, 2: 0}
AXES = {
    0: np.array([1, 0, 0], dtype=float),
    1: np.array([0, 1, 0], dtype=float),
    2: np.array([0, 0, 1], dtype=float),
}


def _make_quarter_arc():
    """Make a quarter circle centered at the origin."""
    circ = pv.Circle(resolution=100)
    circ.faces = np.empty(0, dtype=int)
    circ.lines = np.hstack(([26], np.arange(0, 26)))
    return circ


def get_angle(v1, v2):
    """Compute the angle between two vectors in degrees.

    Parameters
    ----------
    v1 : numpy.ndarray
        First input vector.
    v2 : numpy.ndarray
        Second input vector.

    Returns
    -------
    float
        Angle between vectors in degrees.
    """
    theta = (np.arccos(np.clip(np.dot(v1, v2), -1.0, 1.0))) * (180 / np.pi)
    return theta


def ray_plane_intersection(start_point, direction, plane_point, normal):
    """Compute the intersection between a ray and a plane.

    Parameters
    ----------
    start_point : ndarray
        Starting point of the ray.
    direction : ndarray
        Direction of the ray.
    plane_point : ndarray
        A point on the plane.
    normal : ndarray
        Normal to the plane.

    Returns
    -------
    ndarray
        Intersection point.
    """
    t_value = np.dot(normal, (plane_point - start_point)) / np.dot(normal, direction)
    return start_point + t_value * direction


class AffineWidget3D:
    """3D affine transform widget.

    This widget allows interactive transformations including translation and
    rotation using the left mouse button.

    Parameters
    ----------
    plotter : pyvista.Plotter
        The plotter object.
    actor : pyvista.Actor
        The actor to which the widget is attached to.
    origin : sequence[float], optional
        Origin of the widget. Default is the center of the main actor.
    start : bool, default: True
        If True, start the widget immediately.
    scale : float, default: 0.15
        Scale factor for the widget relative to the length of the actor.
    line_radius : float, default: 0.02
        Relative radius of the lines composing the widget.
    always_visible : bool, default: True
        Make the widget always visible. Setting this to ``False`` will cause
        the widget geometry to be hidden by other actors in the plotter.
    axes_colors : tuple[ColorLike], optional
        Uses the theme by default. Configure the individual axis colors by
        modifying either the theme with ``pv.global_theme.axes.x_color =
        <COLOR>`` or setting this with a ``tuple`` as in ``('r', 'g', 'b')``.
    callback : callable, optional
        Call this method when releasing the left mouse button. It is passed the
        ``user_matrix`` of the actor.

    Notes
    -----
    After interacting with the actor, the transform will be stored within
    :attr:`pyvista.Actor.user_matrix` but will not be applied to the
    dataset. Use this matrix in conjunction with
    :func:`pyvista.DataSetFilters.transform` to transform the dataset.

    Requires VTK >= v9.2

    Examples
    --------
    Create the affine widget outside of the plotter and add it.

    >>> import pyvista as pv
    >>> pl = pv.Plotter()
    >>> actor = pl.add_mesh(pv.Sphere())
    >>> widget = pv.AffineWidget3D(pl, actor)
    >>> pl.show()

    Access the transform from the actor.

    >>> actor.user_matrix
    array([[1., 0., 0., 0.],
           [0., 1., 0., 0.],
           [0., 0., 1., 0.],
           [0., 0., 0., 1.]])

    """

    def __init__(
        self,
        plotter,
        actor,
        origin=None,
        start=True,
        scale=0.15,
        line_radius=0.02,
        always_visible=True,
        axes_colors=None,
        callback=None,
    ):
        """Initialize the widget."""
        # needs VTK v9.2.0 due to the hardware picker
        if pv.vtk_version_info < (9, 2):
            VTKVersionError('AfflineWidget3D requires VTK v9.2.0 or newer.')

        self._pl = plotter
        self._main_actor = actor
        self._selected_actor = None
        self._init_position = None
        self._mouse_move_observer = None
        self._left_press_observer = None
        self._left_release_observer = None

        if self._main_actor.user_matrix is None:
            self._main_actor.user_matrix = np.eye(4)
        self._cached_matrix = self._main_actor.user_matrix

        self._arrows = []
        self._circles = []
        self._pressing_down = False
        origin = origin if origin else actor.center
        self._origin = np.array(origin)
        if axes_colors is None:
            axes_colors = (
                pv.global_theme.axes.x_color,
                pv.global_theme.axes.y_color,
                pv.global_theme.axes.z_color,
            )
        self._axes_colors = axes_colors
        self._circ = _make_quarter_arc()
        self._actor_length = self._main_actor.GetLength()
        self._line_radius = line_radius
        if callback:
            if not callable(callback):
                raise TypeError(f"`callback` must be a callable, not {type(callback)}.")
        self._callback = callback

        self._init_actors(scale, always_visible)

        if start:
            self.enable()

    def _init_actors(self, scale, always_visible):
        """Initialize the widget's actors."""
        for ii, color in zip(range(3), self._axes_colors):
            arrow = pv.Arrow(
                self._origin,
                direction=AXES[ii],
                scale=self._actor_length * scale * 1.15,
                tip_radius=0.05,
                shaft_radius=self._line_radius,
            )
            self._arrows.append(self._pl.add_mesh(arrow, color=color, lighting=False))
            axis_circ = self._circ.copy()
            if ii == 0:
                axis_circ = axis_circ.rotate_y(-90)
            elif ii == 1:
                axis_circ = axis_circ.rotate_x(90)
            axis_circ.points *= self._main_actor.GetLength() * (scale * 1.6)
            axis_circ.points += self._origin
            axis_circ = axis_circ.tube(
                radius=self._line_radius * self._actor_length * scale,
                absolute=True,
                radius_factor=1.0,
            )

            self._circles.append(
                self._pl.add_mesh(
                    axis_circ,
                    color=color,
                    lighting=False,
                    render_lines_as_tubes=True,
                )
            )

        if always_visible:
            for actor in self._arrows + self._circles:
                actor.mapper.SetResolveCoincidentTopologyToPolygonOffset()
                actor.mapper.SetRelativeCoincidentTopologyPolygonOffsetParameters(0, -20000)

    def _get_world_coord_rot(self, interactor):
        """Get the world coordinates given an interactor.

        Unlike ``_get_world_coord_trans``, these coordinates are physically
        accurate, but sensitive to the position of the camera. Rotation is zoom
        independent.

        """
        x, y = interactor.GetLastEventPosition()
        coordinate = _vtk.vtkCoordinate()
        coordinate.SetCoordinateSystemToDisplay()
        coordinate.SetValue(x, y, 0)
        ren = interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()
        point = np.array(coordinate.GetComputedWorldValue(ren))
        if self._selected_actor:
            index = self._circles.index(self._selected_actor)
            view_vec = np.array(ren.camera.direction)
            point = ray_plane_intersection(point, view_vec, self._origin, AXES[index])
        return point

    def _get_world_coord_trans(self, interactor):
        """Get the world coordinates given an interactor.

        This uses a modified scaled approach to get the world coordinates that
        are not physically accurate, but ignores zoom and works for
        translation.

        """
        x, y = interactor.GetLastEventPosition()
        ren = interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()

        # Get normalized view coordinates (-1, 1)
        width, height = ren.GetSize()
        ndc_x = 2 * (x / width) - 1
        ndc_y = 2 * (y / height) - 1
        ndc_z = 1

        # convert
        camera = ren.GetActiveCamera()
        projection_matrix = pv.array_from_vtkmatrix(
            camera.GetProjectionTransformMatrix(ren.GetTiledAspectRatio(), 0, 1)
        )
        inverse_projection_matrix = np.linalg.inv(projection_matrix)
        camera_coords = np.dot(inverse_projection_matrix, [ndc_x, ndc_y, ndc_z, 1])
        modelview_matrix = pv.array_from_vtkmatrix(camera.GetModelViewTransformMatrix())
        inverse_modelview_matrix = np.linalg.inv(modelview_matrix)
        world_coords = np.dot(inverse_modelview_matrix, camera_coords)
        point = world_coords[:3] * self._actor_length

        # map the axis to the next axis (wrap around)
        index = INDEX_MAPPER[self._arrows.index(self._selected_actor)]
        view_vec = np.array(ren.camera.direction)
        point = ray_plane_intersection(point, view_vec, self._origin, AXES[index])

        return point

    def _move_callback(self, interactor, event):
        """Process actions for the move mouse event."""
        click_x, click_y = interactor.GetEventPosition()
        click_z = 0
        picker = interactor.GetPicker()
        renderer = interactor.GetInteractorStyle()._parent()._plotter.iren.get_poked_renderer()
        picker.Pick(click_x, click_y, click_z, renderer)
        actor = picker.GetActor()

        if self._pressing_down:
            if self._selected_actor in self._arrows:
                current_pos = self._get_world_coord_trans(interactor)
                index = self._arrows.index(self._selected_actor)
                diff = current_pos - self.init_position
                matrix = self._cached_matrix.copy()
                matrix[index, -1] += diff[index]
            elif self._selected_actor in self._circles:
                current_pos = self._get_world_coord_rot(interactor)
                index = self._circles.index(self._selected_actor)
                vec_current = current_pos - self._origin
                vec_init = self.init_position - self._origin
                normal = AXES[index]
                vec_current = vec_current - np.dot(vec_current, normal) * normal
                vec_init = vec_init - np.dot(vec_init, normal) * normal
                vec_current /= np.linalg.norm(vec_current)
                vec_init /= np.linalg.norm(vec_init)
                angle = get_angle(vec_init, vec_current)
                cross = np.cross(vec_init, vec_current)
                if cross[index] < 0:
                    angle = -angle
                trans = _vtk.vtkTransform()
                trans.Translate(self._origin)
                if index == 0:
                    trans.RotateX(angle)
                elif index == 1:
                    trans.RotateY(angle)
                elif index == 2:
                    trans.RotateZ(angle)
                trans.Translate(-self._origin)
                trans.Update()
                rot_matrix = pv.array_from_vtkmatrix(trans.GetMatrix())
                matrix = np.dot(rot_matrix, self._cached_matrix)

            self._main_actor.user_matrix = matrix

        elif self._selected_actor and self._selected_actor is not actor:
            # Return the color of the currently selected actor to normal and
            # deselect it
            if self._selected_actor in self._arrows:
                index = self._arrows.index(self._selected_actor)
            elif self._selected_actor in self._circles:
                index = self._circles.index(self._selected_actor)
            self._selected_actor.prop.color = self._axes_colors[index]
            self._selected_actor = None

        # Highlight the actor if there is no selected actor
        if actor and not self._selected_actor:
            if actor in self._arrows:
                index = self._arrows.index(actor)
                self._arrows[index].prop.color = DARK_YELLOW
                actor.prop.color = DARK_YELLOW
                self._selected_actor = actor
            elif actor in self._circles:
                index = self._circles.index(actor)
                self._circles[index].prop.color = DARK_YELLOW
                actor.prop.color = DARK_YELLOW
                self._selected_actor = actor
        self._pl.render()

    def _press_callback(self, interactor, event):
        """Process actions for the mouse button press event."""
        if self._selected_actor:
            self._pl.enable_trackball_actor_style()
            self._pressing_down = True
            if self._selected_actor in self._circles:
                self.init_position = self._get_world_coord_rot(interactor)
            else:
                self.init_position = self._get_world_coord_trans(interactor)

    def _release_callback(self, interactor, event):
        """Process actions for the mouse button release event."""
        self._pl.enable_trackball_style()
        self._pressing_down = False
        self._cached_matrix = self._main_actor.user_matrix
        if self._callback:
            try_callback(self._callback, self._main_actor.user_matrix)

    def _reset(self):
        """Reset the actor and cached transform."""
        self._main_actor.user_matrix = np.eye(4)
        self._cached_matrix = np.eye(4)

    @property
    def origin(self) -> tuple:
        """Origin of the widget.

        This is where the origin of the widget will be located and where the
        actor will be rotated about.

        Returns
        -------
        numpy.ndarray
            Widget origin.

        """
        return tuple(self._origin)

    @origin.setter
    def origin(self, value):  # numpydoc ignore=GL08
        value = np.array(value)
        diff = value - self._origin

        for actor in self._circles + self._arrows:
            if actor.user_matrix is None:
                actor.user_matrix = np.eye(4)
            matrix = actor.user_matrix
            matrix[:3, -1] += diff
            actor.user_matrix = matrix

        self._origin = value

    def enable(self):
        """Enable the widget."""
        if not self._pl._picker_in_use:
            self._pl.enable_mesh_picking(show_message=False, show=False, picker='hardware')
        self._mouse_move_observer = self._pl.iren.add_observer(
            "MouseMoveEvent", self._move_callback
        )
        self._pl._left_press_observer = self._pl.iren.add_observer(
            "LeftButtonPressEvent", self._press_callback
        )
        self._pl._left_release_observer = self._pl.iren.add_observer(
            "LeftButtonReleaseEvent", self._release_callback
        )

    def disable(self):
        """Disable the widget."""
        self._pl.disable_picking()
        if self._mouse_move_observer:
            self._pl.iren.remove_observer(self._mouse_move_observer)
        if self._left_press_observer:
            self._pl.iren.remove_observer(self._left_press_observer)
        if self._left_release_observer:
            self._pl.iren.remove_observer(self._left_release_observer)

    def remove(self):
        """Disable and delete all actors of this widget."""
        self.disable()
        for actor in self._circles + self._arrows:
            self._pl.remove_actor(actor)
