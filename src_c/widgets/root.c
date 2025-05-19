#include "_root.h"

#include "efimport.h"
#include "surface.h"
#include "widgets/_event.h"
#include "widgets/_base.h"

#define EfObject_CallXY(obj, name, x, y) PyObject_CallMethod((PyObject *)(obj), (name), "ii", (x), (y))
#define EfObject_CallNoArgs(obj, name) PyObject_CallMethodNoArgs((PyObject *)(obj), PyUnicode_FromString(name))

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

static int _updateChildren(
    EfBaseWidget *obj,
    int contex_x,
    int contex_y,
    EfEventWidget *event
) {
    if (!obj->alive) {
        return 0;
    }

    int x = event->mouse_x - contex_x - obj->x;
    int y = event->mouse_y - contex_y - obj->y;

    if (event->mouse_flags & EF_MOUSE_DOWN) {
        if (event->mouse_flags & EF_MOUSE_LEFT_DOWN) {
            if (EfObject_CallXY(obj, "onLeftClick", x, y) == NULL) {
                return -1;
            }
        }
        if (event->mouse_flags & EF_MOUSE_MID_DOWN) {
            if (EfObject_CallXY(obj, "onMidClick", x, y) == NULL) {
                return -1;
            }
        }
        if (event->mouse_flags & EF_MOUSE_RIGHT_DOWN) {
            if (EfObject_CallXY(obj, "onRightClick", x, y) == NULL) {
                return -1;
            }
        }
    }

    if (event->mouse_flags & EF_MOUSE_PRESS) {
        if (event->mouse_flags & EF_MOUSE_LEFT_PRESS) {
            if (EfObject_CallXY(obj, "onLeftPress", x, y) == NULL) {
                return -1;
            }
        }
        if (event->mouse_flags & EF_MOUSE_MID_PRESS) {
            if (EfObject_CallXY(obj, "onMidPress", x, y) == NULL) {
                return -1;
            }
        }
        if (event->mouse_flags & EF_MOUSE_RIGHT_PRESS) {
            if (EfObject_CallXY(obj, "onRightPress", x, y) == NULL) {
                return -1;
            }
        }
    }

    if ((event->mouse_flags & EF_MOUSE_PRESS) &&
        (event->mouse_flags & EF_MOUSE_MOTION)) {
        if (event->mouse_flags & EF_MOUSE_LEFT_PRESS) {
            if (EfObject_CallXY(obj, "onLeftDrag", event->mouse_dx, event->mouse_dy) == NULL) {
                return -1;
            }
        }
        if (event->mouse_flags & EF_MOUSE_MID_PRESS) {
            if (EfObject_CallXY(obj, "onMidDrag", event->mouse_dx, event->mouse_dy) == NULL) {
                return -1;
            }
        }
        if (event->mouse_flags & EF_MOUSE_RIGHT_PRESS) {
            if (EfObject_CallXY(obj, "onRightDrag", event->mouse_dx, event->mouse_dy) == NULL) {
                return -1;
            }
        }
    }

    if (event->mouse_flags & EF_MOUSE_UP) {
        if (event->mouse_flags & EF_MOUSE_LEFT_UP) {
            if (EfObject_CallNoArgs(obj, "onLeftRelease") == NULL) {
                return -1;
            }
        }
        if (event->mouse_flags & EF_MOUSE_MID_UP) {
            if (EfObject_CallNoArgs(obj, "onMidRelease") == NULL) {
                return -1;
            }
        }
        if (event->mouse_flags & EF_MOUSE_RIGHT_UP) {
            if (EfObject_CallNoArgs(obj, "onRightRelease") == NULL) {
                return -1;
            }
        }
    }

    Py_ssize_t i;
    for (i = 0; i < PyList_GET_SIZE(obj->_children); i++) {
        EfBaseWidget *ch = (EfBaseWidget *)PyList_GET_ITEM(obj->_children, i);
        _updateChildren(ch, contex_x + obj->x, contex_y + obj->y, event);
    }
    return 0;
}

static PyObject *
EfRootWidget_update(EfRootWidget *self, PyObject *args, PyObject *kwds) {
    EfEventWidget *event = NULL;
    static char *kwlist[] = {"event", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &event))
        return NULL;

    if (_updateChildren((EfBaseWidget *)self, 0, 0, event) < 0) {
        return NULL;
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