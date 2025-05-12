#include "_root.h"

#include "efimport.h"
#include "surface.h"

static void
EfRootWidget_dealloc(EfRootWidget *self) {
    // self
    // Py_XDECREF(self->_children);
    // Py_XDECREF(self->_keyboard_events);
    // Py_XDECREF(self->_keyboard_events_once);

    Py_TYPE(self)->tp_free((PyObject *)self);
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
    initproc base_init = EfBaseWidgetType.tp_init;
    if (base_init((PyObject *)self, Py_BuildValue("iiii", 0, 0, surf->w, surf->h), NULL) < 0) {
        return -1;
    }

    return 0;
}

static PyMemberDef EfRootWidget_members[] = {
    {"surface", T_OBJECT, offsetof(EfRootWidget, surface), READONLY,
     "screen surface"},
    {NULL}
};

PyTypeObject EfRootWidgetType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "widget.Root",
    .tp_doc = PyDoc_STR("Root widgets."),
    .tp_basicsize = sizeof(EfRootWidget),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_base = &EfBaseWidgetType,
    .tp_init = (initproc)EfRootWidget_init,
    .tp_dealloc = (destructor)EfRootWidget_dealloc,
    .tp_members = EfRootWidget_members,
};