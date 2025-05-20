#include "_root.h"

#include "efimport.h"
#include "surface.h"
#include "widgets/_event.h"
#include "widgets/_base.h"

#define EfObject_CallXY(obj, name, x, y) \
    PyObject_CallMethod((PyObject *)(obj), (name), "ii", (x), (y))

#define EfObject_CallXY_Return(obj, name, x, y, ret)    \
    do {                                                \
        if (EfObject_CallXY(obj, name, x, y) == NULL)   \
            return ret;                                 \
    } while (0)

#define EfObject_CallNoArgs(obj, name) \
    PyObject_CallMethodNoArgs((PyObject *)(obj), PyUnicode_FromString(name))

#define EfObject_CallNoArgs_Return(obj, name, ret)  \
    do {                                            \
        if (EfObject_CallNoArgs(obj, name) == NULL) \
            return ret;                             \
    } while (0)

static void
EfRootWidget_dealloc(EfRootWidget *self) {
    Py_XDECREF(self->surface);

    destructor base_dealloc = Py_TYPE(self)->tp_base->tp_dealloc;
    base_dealloc((PyObject *)self);
}

static int
EfRootWidget_init(EfRootWidget *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = {"surface", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &self->surface))
        return -1;

    if (!PyObject_TypeCheck(self->surface, (PyTypeObject *)imported_SurfaceType)) {
        PyErr_Format(PyExc_TypeError,
            "Wrong type of surface: %s (expect Surface)",
            Py_TYPE(self->surface)->tp_name
        );
        return -1;
    }

    EfSurfaceObject *surf = (EfSurfaceObject *)self->surface;
    initproc base_init = Py_TYPE(self)->tp_base->tp_init;
    if (base_init((PyObject *)self, Py_BuildValue("iiii", 0, 0, surf->w, surf->h), NULL) < 0) {
        return -1;
    }

    Py_INCREF(self->surface);
    return 0;
}

static PyMemberDef EfRootWidget_members[] = {
    {"surface", T_OBJECT, offsetof(EfRootWidget, surface), READONLY,
     "screen surface"},
    {NULL}
};

static void _clipRect(
    int x, int y, int w, int h,
    PyObject *surf,
    int *rx, int *ry, int *rw, int *rh
) {
    int x2 = x + w;
    int y2 = y + h;

    x = Py_MIN(x, ((EfSurfaceObject *)surf)->w);
    *rx = Py_MAX(0, x);

    y = Py_MIN(y, ((EfSurfaceObject *)surf)->h);
    *ry = Py_MAX(0, y);

    x2 = Py_MIN(x2, ((EfSurfaceObject *)surf)->w);
    *rw = Py_MAX(0, x2) - *rx;

    y2 = Py_MIN(y2, ((EfSurfaceObject *)surf)->h);
    *rh = Py_MAX(0, y2) - *ry;
}

/**
 * \brief Recursive update children.
 * 
 * \param obj The object and its children that need update.
 * \param contex_x X offset of the contex.
 * \param contex_y Y offset of the contex.
 * \param event Current event states.
 * \param interact Is the object needs mouse and keyboard interaction.
 * \return 0 on success, -1 on failure.
 */
static int _updateChildren(
    EfBaseWidget *obj,
    int contex_x,
    int contex_y,
    EfEventWidget *event,
    int interact
) {
    if (!obj->alive) {
        return 0;
    }

    Ef_BaseWidgetType_RemoveDeadChildren((PyObject *)obj);

    int x = event->mouse_x - contex_x - obj->x;
    int y = event->mouse_y - contex_y - obj->y;

    PyObject *active_obj = EfObject_CallXY(obj, "isHovered", x, y);
    if (!active_obj) {
        return -1;
    }

    if (PyObject_IsTrue(active_obj)) {
        if (!obj->active) {
            obj->active = 1;
            EfObject_CallNoArgs_Return(obj, "onMouseEnter", -1);
        }
    }
    else {
        if (obj->active) {
            obj->active = 0;
            EfObject_CallNoArgs_Return(obj, "onMouseLeave", -1);
        }
    }

    // Object may be killed after `onMouseEnter` or `onMouseLeave`.
    if (!obj->alive) {
        return 0;
    }

    interact = (obj->active || !obj->interactive_when_active) && interact;
    if (interact) {
        if (event->mouse_flags & EF_MOUSE_DOWN) {
            if (event->mouse_flags & EF_MOUSE_LEFT_DOWN)
                EfObject_CallXY_Return(obj, "onLeftClick", x, y, -1);
            if (event->mouse_flags & EF_MOUSE_MID_DOWN)
                EfObject_CallXY_Return(obj, "onMidClick", x, y, -1);
            if (event->mouse_flags & EF_MOUSE_RIGHT_DOWN)
                EfObject_CallXY_Return(obj, "onRightClick", x, y, -1);
        }

        if (event->mouse_flags & EF_MOUSE_PRESS) {
            if (event->mouse_flags & EF_MOUSE_LEFT_PRESS)
                EfObject_CallXY_Return(obj, "onLeftPress", x, y, -1);
            if (event->mouse_flags & EF_MOUSE_MID_PRESS)
                EfObject_CallXY_Return(obj, "onMidPress", x, y, -1);
            if (event->mouse_flags & EF_MOUSE_RIGHT_PRESS)
                EfObject_CallXY_Return(obj, "onRightPress", x, y, -1);
        }

        if ((event->mouse_flags & EF_MOUSE_PRESS) &&
            (event->mouse_flags & EF_MOUSE_MOTION)) {

            if (event->mouse_flags & EF_MOUSE_LEFT_PRESS)
                EfObject_CallXY_Return(obj, "onLeftDrag",
                    event->mouse_dx, event->mouse_dy, -1);

            if (event->mouse_flags & EF_MOUSE_MID_PRESS)
                EfObject_CallXY_Return(obj, "onMidDrag",
                    event->mouse_dx, event->mouse_dy, -1);

            if (event->mouse_flags & EF_MOUSE_RIGHT_PRESS)
                EfObject_CallXY_Return(obj, "onRightDrag",
                    event->mouse_dx, event->mouse_dy, -1);
        }

        if (event->mouse_flags & EF_MOUSE_UP) {
            if (event->mouse_flags & EF_MOUSE_LEFT_UP)
                EfObject_CallNoArgs_Return(obj, "onLeftRelease", -1);
            if (event->mouse_flags & EF_MOUSE_MID_UP)
                EfObject_CallNoArgs_Return(obj, "onMidRelease", -1);
            if (event->mouse_flags & EF_MOUSE_RIGHT_UP)
                EfObject_CallNoArgs_Return(obj, "onRightRelease", -1);
        }

        // Object may be killed when interact.
        if (!obj->alive) {
            return 0;
        }
    }

    if (PyObject_CallMethod((PyObject *)obj, "update", "iii", x, y, event->wheel) == NULL) {
        return -1;
    }

    // Object may be killed when update.
    if (!obj->alive) {
        return 0;
    }

    Py_ssize_t i;
    for (i = 0; i < PyList_GET_SIZE(obj->_children); i++) {
        EfBaseWidget *ch = (EfBaseWidget *)PyList_GET_ITEM(obj->_children, i);
        _updateChildren(ch, contex_x + obj->x, contex_y + obj->y, event, interact);
    }
    return 0;
}

static PyObject *
EfRootWidget_update(EfRootWidget *self, PyObject *args, PyObject *kwds) {
    EfEventWidget *event = NULL;
    static char *kwlist[] = {"event", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &event))
        return NULL;

    Py_ssize_t i;
    for (i = 0; i < PyList_GET_SIZE(self->base._children); i++) {
        EfBaseWidget *ch = (EfBaseWidget *)PyList_GET_ITEM(self->base._children, i);
        if (_updateChildren(ch, 0, 0, event, 1) < 0) {
            return NULL;
        }
    }

    Py_RETURN_NONE;
}

/**
 * \brief Rraversal and draw the nodes that needs redraw.
 * 
 * \return 0 on success, -1 on failure.
 */
static int _drawChildren(EfBaseWidget *parent, PyObject *surf) {
    Py_ssize_t i;
    for (i = 0; i < PyList_GET_SIZE(parent->_children); i++) {
        EfBaseWidget *ch = (EfBaseWidget *)PyList_GET_ITEM(parent->_children, i);
        if (parent->_need_redraw) {
            ch->_need_redraw = 1;
            ch->_in_redraw_path = 1;
        }

        if (!ch->_in_redraw_path) {
            continue;
        }

        int x, y, w, h;
        _clipRect(ch->x, ch->y, ch->w, ch->h, surf, &x, &y, &w, &h);
        EfSurfaceObject *sub = (EfSurfaceObject *)Ef_SurfaceObject_Subsurface(
            surf, x, y, w, h
        );
        if (!sub) {
            return -1;
        }

        int x_start = parent->x + Py_MIN(0, ch->x);
        int y_start = parent->y + Py_MIN(0, ch->y);
        x_start = Py_MIN(0, x_start);
        y_start = Py_MIN(0, y_start);
        if (ch->_need_redraw) {
            if (PyObject_CallMethod((PyObject *)ch, "draw", "Oii",
                                    (PyObject *)sub, x_start, y_start) == NULL) {
                return -1;
            }
        }

        if (_drawChildren(ch, (PyObject *)sub) < 0) {
            return -1;
        }
    }

    parent->_need_redraw = 0;
    parent->_in_redraw_path = 0;

    return 0;
}

static PyObject *
EfRootWidget_draw(EfRootWidget *self, PyObject *Py_UNUSED(ignore)) {
    if (!self->base._in_redraw_path) {
        Py_RETURN_NONE;
    }

    if (self->base._need_redraw) {
        SDL_Surface *sdl_surf = ((EfSurfaceObject *)self->surface)->sdl_surface;
        SDL_FillRect(sdl_surf, NULL, SDL_MapRGB(sdl_surf->format, 0, 0, 0));
    }

    if (_drawChildren((EfBaseWidget *)self, self->surface) < 0) {
        return NULL;
    }
    Py_RETURN_NONE;
}

static PyMethodDef EfRootWidget_methods[] = {
    {"update", (PyCFunction)EfRootWidget_update, METH_VARARGS | METH_KEYWORDS,
     "Update root widget."},
    {"draw", (PyCFunction)EfRootWidget_draw, METH_NOARGS,
     "Draw the widget."},
    {NULL}
};

PyTypeObject EfRootWidgetType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "widgets.Root",
    .tp_doc = PyDoc_STR("Root widgets."),
    .tp_basicsize = sizeof(EfRootWidget),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_base = &EfBaseWidgetType,
    .tp_init = (initproc)EfRootWidget_init,
    .tp_dealloc = (destructor)EfRootWidget_dealloc,
    .tp_members = EfRootWidget_members,
    .tp_methods = EfRootWidget_methods,
};