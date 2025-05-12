#include "main.h"

#include <structmember.h>

#include "efimport.h"
#include "screen.h"
#include "widget.h"
#include "efutils.h"
#include "SDL_image.h"

static PyTypeObject EfMainType;

static void
EfMainObject_dealloc(EfMainObject *self) {
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *
EfMainObject_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    EfMainObject *self;
    self = (EfMainObject *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->screen = NULL;
    }
    return (PyObject *)self;
}

static int
EfMainObject_init(EfMainObject *self, PyObject *args, PyObject *kwds) {
    PyObject *size = NULL;
    PyObject *title = NULL;
    static char *kwlist[] = {"size", "title", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", kwlist, &size, &title))
        return -1;

    self->screen = Ef_ScreenObject_FromPy(imported_ScreenType, size, title);
    if (!self->screen) {
        return -1;
    }

    if (Ef_ScreenObject_CreateWindow(self->screen, -1, -1) < 0) {
        return -1;
    }

    PyObject *surf = Ef_ScreenObject_GetSurface(self->screen);
    if (surf == NULL || surf == Py_None) {
        if (surf == Py_None) {
            Py_DECREF(Py_None);
        }
        return -1;
    }

    self->root = PyObject_CallFunction(imported_RootWidgetType, "O", surf);
    if (!self->root) {
        return -1;
    }

    return 0;
}

static PyObject *
EfMainObject_repr(EfMainObject *v) {
    EfScreenObject *s = (EfScreenObject *)v->screen;
    if (s != NULL) {
        return PyUnicode_FromFormat("<Main %p '%s' {%dx%d}>",
                                    v, s->title, s->w, s->h);
    }
    else {
        return PyUnicode_FromFormat("<Main %p (not initialized)>", v);
    }
}

static PyMemberDef EfMainObject_members[] = {
    {"screen", T_OBJECT, offsetof(EfMainObject, screen), READONLY,
     "main screen"},
    {"root", T_OBJECT, offsetof(EfMainObject, root), READONLY,
     "root widget"},
    {NULL}
};

// static PyObject *
// EfMainObject_getscreen(EfMainObject *self, void *closure) {
//     Py_INCREF(self->screen);
//     return self->screen;
// }

// static int
// EfMainObject_setscreen(EfMainObject *self, PyObject *value, void *closure) {
//     PyErr_SetString(PyExc_AttributeError, "readonly attribute");
//     return -1;
// }

// static PyGetSetDef EfMainObject_getsetters[] = {
//     {"screen", (getter)EfMainObject_getscreen, (setter)EfMainObject_setscreen,
//      "main screen", NULL},
//     {NULL}
// };

static PyObject *
EfMainObject_run(EfMainObject *self, PyObject *Py_UNUSED(ignore)) {
    int quit = 0;
    SDL_Event e;

    while (!quit) {
        // Handle events.
        while(SDL_PollEvent(&e) != 0) {
            switch (e.type) {
                case SDL_QUIT:
                    quit = 1;
                    break;
                case SDL_KEYDOWN:
                    break;
                case SDL_KEYUP:
                    break;
            }
        }

        Ef_ScreenObject_Update(self->screen);

        Py_BEGIN_ALLOW_THREADS
        SDL_Delay(16);
        Py_END_ALLOW_THREADS
    }

    Py_RETURN_NONE;
}

static PyMethodDef EfMainObject_methods[] = {
    {"run", (PyCFunction)EfMainObject_run, METH_NOARGS,
     "Start loop."},
    {NULL}
};

static PyTypeObject EfMainType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "main.Main",
    .tp_doc = PyDoc_STR("Main objects."),
    .tp_basicsize = sizeof(EfMainObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = EfMainObject_new,
    .tp_init = (initproc)EfMainObject_init,
    .tp_dealloc = (destructor)EfMainObject_dealloc,
    .tp_repr = (reprfunc)EfMainObject_repr,
    .tp_members = EfMainObject_members,
    .tp_methods = EfMainObject_methods,
};

static PyMethodDef main_methods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef main_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "main",
    .m_doc = "Main frame to run a gui window.",
    .m_size = -1,
    .m_methods = main_methods
};

PyMODINIT_FUNC
PyInit_main(void) {
    PyObject *m;
    if (PyType_Ready(&EfMainType) < 0)
        return NULL;

    m = PyModule_Create(&main_module);
    if (m == NULL)
        goto err_exit;

    if (EF_IMPORT_Surface() < 0 ||
        EF_IMPORT_Screen() < 0 ||
        EF_IMPORT_RootWidget() < 0)
        goto err_exit;

    Py_INCREF(&EfMainType);
    if (PyModule_AddObject(m, "Main", (PyObject *)&EfMainType) < 0)
        goto err_exit;

    return m;

err_exit:
    Py_XDECREF(m);
    EF_IMPORT_DECREAF();
    Py_XDECREF(&EfMainType);
    return NULL;
}