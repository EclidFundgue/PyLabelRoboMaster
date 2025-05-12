#include "_base.h"


static void
EfBaseWidget_dealloc(EfBaseWidget *self) {
    Py_XDECREF(self->_children);
    Py_XDECREF(self->_keyboard_events);
    Py_XDECREF(self->_keyboard_events_once);

    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *
EfBaseWidget_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    EfBaseWidget *self;
    self = (EfBaseWidget *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->x = 0;
        self->y = 0;
        self->w = 0;
        self->h = 0;
        self->layer = 0;
        self->redraw_parent = 1;
        self->interactive_when_active = 1;
        self->alive = 1;
        self->active = 0;

        self->_parent = NULL;
        self->_children = NULL;
        self->_keyboard_events = NULL;
        self->_keyboard_events_once = NULL;
    }
    return (PyObject *)self;
}

static int
EfBaseWidget_init(EfBaseWidget *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = {"x", "y", "w", "h", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|iiii", kwlist,
                                     &self->x, &self->y, &self->w, &self->h))
        return -1;

    self->_children = PyList_New(0);
    if (!self->_children) {
        return -1;
    }
    self->_keyboard_events = PyDict_New();
    if (!self->_keyboard_events) {
        return -1;
    }
    self->_keyboard_events_once = PyList_New(0);
    if (!self->_keyboard_events_once) {
        return -1;
    }
    return 0;
}

static PyObject *
EfBaseWidget_repr(EfBaseWidget *v) {
    return PyUnicode_FromFormat("<%s %p {%d,%d,%d,%d}>",
        Py_TYPE(v)->tp_name, v, v->x, v->y, v->w, v->h);
}

static PyMemberDef EfBaseWidget_members[] = {
    {"x", T_INT, offsetof(EfBaseWidget, x), 0,
     "widget x"},
    {"y", T_INT, offsetof(EfBaseWidget, y), 0,
     "widget y"},
    {"w", T_INT, offsetof(EfBaseWidget, w), 0,
     "widget width"},
    {"h", T_INT, offsetof(EfBaseWidget, h), 0,
     "widget height"},
    {"layer", T_INT, offsetof(EfBaseWidget, layer), 0,
     "widget display layer"},
    {"redraw_parent", T_BOOL, offsetof(EfBaseWidget, redraw_parent), 0,
     "whether redraw parent"},
    {"interactive_when_active", T_BOOL, offsetof(EfBaseWidget, interactive_when_active), 0,
     "whether interactive when active"},
    {"alive", T_BOOL, offsetof(EfBaseWidget, alive), READONLY,
     "is widget alive"},
    {"active", T_BOOL, offsetof(EfBaseWidget, active), READONLY,
     "is widget active"},
    {NULL}
};

static PyMethodDef EfBaseWidget_methods[] = {
    {NULL}
};

PyTypeObject EfBaseWidgetType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "widget.Base",
    .tp_doc = PyDoc_STR("Base widgets."),
    .tp_basicsize = sizeof(EfBaseWidget),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = EfBaseWidget_new,
    .tp_init = (initproc)EfBaseWidget_init,
    .tp_dealloc = (destructor)EfBaseWidget_dealloc,
    .tp_repr = (reprfunc)EfBaseWidget_repr,
    .tp_members = EfBaseWidget_members,
    .tp_methods = EfBaseWidget_methods,
};