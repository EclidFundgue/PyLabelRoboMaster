#include "_event.h"

PyObject *Ef_EventWidget_New(PyObject *type) {
    return ((PyTypeObject *)type)->tp_new((PyTypeObject *)type, NULL, NULL);
}

static void
EfEventWidget_dealloc(EfEventWidget *self) {
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *
EfEventWidget_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    EfEventWidget *self;
    self = (EfEventWidget *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->mouse_flags = 0;
        self->mouse_x = 0;
        self->mouse_y = 0;
        self->mouse_dx = 0;
        self->mouse_dy = 0;
        self->wheel = 0;
    }
    return (PyObject *)self;
}

static int
EfEventWidget_init(EfEventWidget *self, PyObject *args, PyObject *kwds) {
    return 0;
}

PyTypeObject EfEventWidgetType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "widgets.Event",
    .tp_doc = PyDoc_STR("Event widgets."),
    .tp_basicsize = sizeof(EfEventWidget),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = EfEventWidget_new,
    .tp_init = (initproc)EfEventWidget_init,
    .tp_dealloc = (destructor)EfEventWidget_dealloc,
};