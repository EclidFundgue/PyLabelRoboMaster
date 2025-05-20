#include "_base.h"

#include "efimport.h"
#include "surface.h"

/**
 * \brief Remove dead children in list.
 * 
 * \param base Base object that needs remove dead children.
 * \return 0 on success, -1 on failure.
 * 
 * \note This function will create a new list and DECREF the origin.
 * \note It is safe to use this function during iteration, but you
 *       must INCREF the origin _children list before iterating.
 */
int Ef_BaseWidgetType_RemoveDeadChildren(PyObject *base) {
    EfBaseWidget *base_widget = (EfBaseWidget *)base;
    PyObject *ls = base_widget->_children;

    Py_ssize_t alive_cnt = 0;
    PyObject **start = ((PyListObject *)ls)->ob_item;
    PyObject **end = ((PyListObject *)ls)->ob_item + PyList_GET_SIZE(ls);

    while (start != end) {
        EfBaseWidget *ch = (EfBaseWidget *)*start++;
        if (ch->alive) {
            alive_cnt++;
        }
    }

    PyObject *new = PyList_New(alive_cnt);
    if (!new) {
        return -1;
    }

    if (alive_cnt != 0) {
        Py_ssize_t i = 0;
        start = ((PyListObject *)ls)->ob_item;
        while (start != end) {
            EfBaseWidget *ch = (EfBaseWidget *)*start++;
            if (ch->alive) {
                Py_INCREF(ch);
                PyList_SET_ITEM(new, i++, (PyObject *)ch);
            }
        }
    }

    Py_SETREF(base_widget->_children, new);

    return 0;
}

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

/**
 * \brief Check item in list.
 * \return If item in list.
 */
static int _inList(PyObject *ls, PyObject *v) {
    Py_ssize_t i;
    for (i = 0; i < PyList_GET_SIZE(ls); i++) {
        if (v == PyList_GET_ITEM(ls, i)) {
            return 1;
        }
    }
    return 0;
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

    if (_inList(self->_children, child)) {
        PyErr_WarnFormat(PyExc_Warning, 1,
            "%s is already added.",
            PyUnicode_AsUTF8(PyObject_Str(child))
        );
    }
    else {
        PyList_Append(self->_children, child);
        Py_INCREF(self);
        child_obj->_parent = (PyObject *)self;
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

    if (!_inList(self->_children, child)) {
        PyErr_WarnFormat(PyExc_Warning, 1,
            "%s is not in children list.",
            PyUnicode_AsUTF8(PyObject_Str(child))
        );
    }
    else {
        if (_listRemove(self->_children, child) < 0) {
            return NULL;
        }
        Py_XDECREF(child_obj->_parent);
        child_obj->_parent = NULL;
    }

    Py_RETURN_NONE;
}

static PyObject *
EfBaseWidget_isHovered(EfBaseWidget *self, PyObject *args, PyObject *kwds) {
    int x, y;
    static char *kwlist[] = {"x", "y", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "ii", kwlist, &x, &y))
        return NULL;

    if (0 <= x && x <= self->w && 0 <= y && y <= self->h) {
        Py_RETURN_TRUE;
    }
    Py_RETURN_FALSE;
}

static PyObject *
EfBaseWidget_redraw(EfBaseWidget *self, PyObject *Py_UNUSED(ignore)) {
    self->_need_redraw = 1;
    _submitRedraw(self);
    Py_RETURN_NONE;
}

static PyObject *
EfBaseWidget_update(EfBaseWidget *self, PyObject *args, PyObject *kwds) {
    int x;
    int y;
    float wheel;
    static char *kwlist[] = {"x", "y", "wheel", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "iii", kwlist, &x, &y, &wheel))
        return NULL;

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
    {"isHovered", (PyCFunction)EfBaseWidget_isHovered, METH_VARARGS | METH_KEYWORDS,
     "Is mouse hovered."},
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

    {"onMouseEnter", (PyCFunction)EfBaseWidget_onNoArgs, METH_NOARGS,
     "On mouse enter."},
    {"onMouseLeave", (PyCFunction)EfBaseWidget_onNoArgs, METH_NOARGS,
     "On mouse enter."},

    {"update", (PyCFunction)EfBaseWidget_update, METH_VARARGS | METH_KEYWORDS,
     "Update the widget."},

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