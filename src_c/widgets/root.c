#include "_root.h"

#include "efimport.h"
#include "surface.h"
#include "widgets/_base.h"

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

/**
 * \brief Rraversal and draw the nodes that needs redraw.
 * 
 * \return 0 on success, -1 on failure.
 */
static int _updateDrawChildren(EfBaseWidget *parent, PyObject *surf) {
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

        EfSurfaceObject *sub = (EfSurfaceObject *)Ef_SurfaceObject_Subsurface(
            surf, ch->x, ch->y, ch->w, ch->h
        );
        if (!sub) {
            return -1;
        }

        if (ch->_need_redraw) {
            if (PyObject_CallMethod((PyObject *)ch, "draw", "Oii",
                                    (PyObject *)sub, 0, 0) == NULL) {
                return -1;
            }
        }

        if (_updateDrawChildren(ch, (PyObject *)sub) < 0) {
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

    if (_updateDrawChildren((EfBaseWidget *)self, self->surface) < 0) {
        return NULL;
    }
    Py_RETURN_NONE;
}

static PyMethodDef EfRootWidget_methods[] = {
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