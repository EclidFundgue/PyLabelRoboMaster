#include "_base.h"

#include "efimport.h"
#include "surface.h"

/**
 * \brief Submit redraw all the way to root.
 * 
 * \param obj Widget to redraw.
 */
static void
_submitRedraw(EfBaseWidget *obj) {
    obj->_in_redraw_path = 1;

    EfBaseWidget *p = (EfBaseWidget *)obj->_parent;
    if (p == NULL || p->_need_redraw) {
        return;
    }

    if (obj->_need_redraw && obj->redraw_parent) {
        p->_need_redraw = 1;
    }
    else if (p->_in_redraw_path) {
        return;
    }

    _submitRedraw(p);
}

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

        self->_need_redraw = 0;
        self->_in_redraw_path = 0;
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

/**
 * \brief Remove dead children and check if child already in list.
 * \return 0 on not in list, 1 on in list, -1 on failure.
 */
static int _removeDeadChildrenAndCheck(PyObject *list, EfBaseWidget *child) {
    Py_ssize_t i = 0;
    int in_list = 0;

    while (i < PyList_GET_SIZE(list)) {
        EfBaseWidget *ch = (EfBaseWidget *)PyList_GET_ITEM(list, i);
        if (ch->alive) {
            if (ch == child) {
                in_list = 1;
            }
            i++;
            continue;
        }

        if (PyList_SetSlice(list, i, i+1, NULL) != 0) {
            return -1;
        }
    }

    return in_list;
}

static PyObject *
EfBaseWidget_onXY(EfBaseWidget *self, PyObject *args, PyObject *kwds) {
    int x, y;
    static char *kwlist[] = {"x", "y", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "ii", kwlist, &x, &y))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
EfBaseWidget_onNoArgs(EfBaseWidget *self, PyObject *Py_UNUSED(ignore)) {
    Py_RETURN_NONE;
}

static PyObject *
EfBaseWidget_addChild(EfBaseWidget *self, PyObject *args, PyObject *kwds) {
    PyObject *child;
    EfBaseWidget *child_obj;
    static char *kwlist[] = {"child", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &child))
        return NULL;

    if (!PyObject_TypeCheck(child, &EfBaseWidgetType)) {
        PyErr_Format(PyExc_TypeError,
            "Expect 'Base' type, but received %s",
            Py_TYPE(child)->tp_name
        );
        return NULL;
    }

    child_obj = (EfBaseWidget *)child;
    if (!child_obj->alive) {
        PyErr_WarnFormat(PyExc_Warning, 1,
            "Operation not allowed on dead child: %s",
            PyUnicode_AsUTF8(PyObject_Str(child))
        );
        Py_RETURN_NONE;
    }

    switch (_removeDeadChildrenAndCheck(self->_children, child_obj)) {
    case 0:
        PyList_Append(self->_children, child);
        Py_INCREF(self);
        child_obj->_parent = (PyObject *)self;
        break;
    case 1:
        PyErr_WarnFormat(PyExc_Warning, 1,
            "%s is already added.",
            PyUnicode_AsUTF8(PyObject_Str(child))
        );
        break;
    case -1:
        return NULL;
    default:
        break;
    }

    Py_RETURN_NONE;
}

static int
_listRemove(PyObject *list, PyObject *v) {
    Py_ssize_t i;
    for (i = 0; i < Py_SIZE(list); i++) {
        PyObject *obj = PyList_GET_ITEM(list, i);
        if (obj != v) {
            continue;
        }

        if (PyList_SetSlice(list, i, i+1, NULL) != 0) {
            return -1;
        }
        return 0;
    }
    return 0;
}

static PyObject *
EfBaseWidget_removeChild(EfBaseWidget *self, PyObject *args, PyObject *kwds) {
    PyObject *child;
    EfBaseWidget *child_obj;
    static char *kwlist[] = {"child", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &child))
        return NULL;

    if (!PyObject_TypeCheck(child, &EfBaseWidgetType)) {
        PyErr_Format(PyExc_TypeError,
            "Expect 'Base' type, but received %s",
            Py_TYPE(child)->tp_name
        );
        return NULL;
    }

    child_obj = (EfBaseWidget *)child;
    if (!child_obj->alive) {
        PyErr_WarnFormat(PyExc_Warning, 1,
            "Operation not allowed on dead child: %s",
            PyUnicode_AsUTF8(PyObject_Str(child))
        );
        Py_RETURN_NONE;
    }

    switch (_removeDeadChildrenAndCheck(self->_children, child_obj)) {
    case 0:
        PyErr_WarnFormat(PyExc_Warning, 1,
            "%s is not in children list.",
            PyUnicode_AsUTF8(PyObject_Str(child))
        );
        break;
    case 1:
        Py_XDECREF(child_obj->_parent);
        child_obj->_parent = NULL;
        if (_listRemove(self->_children, child) < 0) {
            return NULL;
        }
        break;
    case -1:
        return NULL;
    default:
        break;
    }

    Py_RETURN_NONE;
}

static PyObject *
EfBaseWidget_redraw(EfBaseWidget *self, PyObject *Py_UNUSED(ignore)) {
    self->_need_redraw = 1;
    _submitRedraw(self);
    Py_RETURN_NONE;
}

static PyObject *
EfBaseWidget_draw(EfBaseWidget *self, PyObject *args, PyObject *kwds) {
    PyObject *surface;
    int x;
    int y;
    static char *kwlist[] = {"surface", "x", "y", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "Oii", kwlist, &surface, &x, &y))
        return NULL;

    if (!PyObject_TypeCheck(surface, (PyTypeObject *)imported_SurfaceType)) {
        PyErr_Format(PyExc_TypeError,
            "Expect 'Surface' type, but received %s",
            Py_TYPE(surface)->tp_name
        );
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyMethodDef EfBaseWidget_methods[] = {
    {"addChild", (PyCFunction)EfBaseWidget_addChild, METH_VARARGS | METH_KEYWORDS,
     "Add a child to widget."},
    {"removeChild", (PyCFunction)EfBaseWidget_removeChild, METH_VARARGS | METH_KEYWORDS,
     "Remove the child from widget."},
    {"redraw", (PyCFunction)EfBaseWidget_redraw, METH_NOARGS,
     "Redraw the widget."},

    {"onLeftClick", (PyCFunction)EfBaseWidget_onXY, METH_VARARGS | METH_KEYWORDS,
     "On left click."},
    {"onMidClick", (PyCFunction)EfBaseWidget_onXY, METH_VARARGS | METH_KEYWORDS,
     "On mid click."},
    {"onRightClick", (PyCFunction)EfBaseWidget_onXY, METH_VARARGS | METH_KEYWORDS,
     "On right click."},

    {"onLeftPress", (PyCFunction)EfBaseWidget_onXY, METH_VARARGS | METH_KEYWORDS,
     "On left press."},
    {"onMidPress", (PyCFunction)EfBaseWidget_onXY, METH_VARARGS | METH_KEYWORDS,
     "On mid press."},
    {"onRightPress", (PyCFunction)EfBaseWidget_onXY, METH_VARARGS | METH_KEYWORDS,
     "On right press."},

    {"onLeftDrag", (PyCFunction)EfBaseWidget_onXY, METH_VARARGS | METH_KEYWORDS,
     "On left drag."},
    {"onMidDrag", (PyCFunction)EfBaseWidget_onXY, METH_VARARGS | METH_KEYWORDS,
     "On mid drag."},
    {"onRightDrag", (PyCFunction)EfBaseWidget_onXY, METH_VARARGS | METH_KEYWORDS,
     "On right drag."},

    {"onLeftRelease", (PyCFunction)EfBaseWidget_onNoArgs, METH_NOARGS,
     "On left release."},
    {"onMidRelease", (PyCFunction)EfBaseWidget_onNoArgs, METH_NOARGS,
     "On mid release."},
    {"onRightRelease", (PyCFunction)EfBaseWidget_onNoArgs, METH_NOARGS,
     "On right release."},

    {"draw", (PyCFunction)EfBaseWidget_draw, METH_VARARGS | METH_KEYWORDS,
     "Draw the widget."},
    {NULL}
};

PyTypeObject EfBaseWidgetType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "widgets.Base",
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