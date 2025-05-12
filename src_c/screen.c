#include "screen.h"

#include <structmember.h>

#include "efimport.h"
#include "surface.h"
#include "efutils.h"

#define MAX_W 65535
#define MAX_H 65535

static PyTypeObject EfScreenType;

/**
 * A global list to store references to screen object.
 * It will be updated when new object created or user
 * calls the getAllWindows function.
 */
static PyObject *_screen_objects_list = NULL;

/**
 * \brief Remove screen objects with refcount <= 1 and have no created window.
 * 
 * \param list List object.
 * \return 0 on success, -1 on failure.
 */
static int _filterScreenObjects(PyObject *list) {
    if (!PyList_Check(list)) {
        PyErr_SetString(PyExc_TypeError, "Expected a list object");
        return -1;
    }

    Py_ssize_t size = PyList_GET_SIZE(list);

    for (Py_ssize_t i = size - 1; i >= 0; i--) {
        PyObject *item = PyList_GET_ITEM(list, i);
        if (!PyObject_TypeCheck(item, &EfScreenType)) {
            PyErr_Format(PyExc_TypeError,
                "Unexpected type in screen list: %s",
                Py_TYPE(item)->tp_name
            );
            return -1;
        }

        // This function may be called in `tp_dealloc`. Consider refcnt = 0.
        if (Py_REFCNT(item) <= 1 && ((EfScreenObject *)item)->sdl_window == NULL) {
            if (PyList_SetSlice(list, i, i+1, NULL) < 0) {
                return -1;
            }
        }
    }

    return 0;
}

/**
 * \brief Raise PyExc_ValueError if window size is illegal.
 * 
 * \param w Window width.
 * \param h Window height.
 * \return 0 on success, -1 on failure.
 */
static int _assertWindowSize(int w, int h) {
    if (w <= 0 || w > MAX_W) {
        PyErr_Format(PyExc_ValueError, "Illegal screen width: %d (Expect 1 to %d)", w, MAX_W);
        return -1;
    }
    if (h <= 0 || h > MAX_H) {
        PyErr_Format(PyExc_ValueError, "Illegal screen height: %d (Expect 1 to %d)", h, MAX_H);
        return -1;
    }
    return 0;
}

/**
 * \brief Initialize media and create a window surface.
 * 
 * \param x Created x position. -1 for center.
 * \param y Created y position. -1 for center.
 * \param w Window width.
 * \param h Window height.
 * \param title Window title string.
 * \return Pointer to SDL_Window on success, NULL on failure.
*/
static SDL_Window *_createWindow(int x, int y, int w, int h, const char *title) {
    if (!SDL_WasInit(SDL_INIT_VIDEO)) {
        if (SDL_Init(SDL_INIT_VIDEO) < 0) {
            PyErr_Format(PyExc_RuntimeError,
                "Video system initialize failed!\n"
                "SDL Info: %s", SDL_GetError()
            );
            return NULL;
        }
    }

    if (_assertWindowSize(w, h) < 0) {
        return NULL;
    }

    SDL_Window *window = SDL_CreateWindow(
        title,
        (x == -1) ? (int)SDL_WINDOWPOS_UNDEFINED : x,
        (y == -1) ? (int)SDL_WINDOWPOS_UNDEFINED : y,
        w, h, SDL_WINDOW_SHOWN
    );
    if (!window) {
        PyErr_Format(PyExc_RuntimeError,
            "Window creating failed!\n"
            "SDL Info: %s", SDL_GetError()
        );
        return NULL;
    }
    return window;
}

/**
 * \brief Create an instance of EfScreenObject.
 * 
 * \param type ScreenObject Type.
 * \param size Tuple[int, int] of size. Should not be NULL.
 * \param title Unicode of title. Should not be NULL.
 * \return New reference. Pointer to EfScreenObject on success, or raise an exception and return NULL on failure.
 */
PyObject *Ef_ScreenObject_FromPy(PyObject *type, PyObject *size, PyObject *title) {
    return PyObject_CallFunctionObjArgs(type, size, title, NULL);
}

/**
 * \brief Create an instance of EfScreenObject.
 * 
 * \param type ScreenObject Type.
 * \param w Screen width.
 * \param h Screen height.
 * \param title Screen title.
 * \return New reference. Pointer to EfScreenObject on success, or raise an exception and return NULL on failure.
 */
PyObject *Ef_ScreenObject_FromC(PyObject *type, int w, int h, const char *title) {
    return PyObject_CallFunction(type, "(ii)s", w, h, title);
}

/**
 * \brief Create a new window by ScreenObject.
 * 
 * \param screen Instance of EfScreenObject.
 * \param x Screen pos X.
 * \param y Screen pos Y.
 * \return 0 on success, -1 on failure.
 */
int Ef_ScreenObject_CreateWindow(PyObject *screen, int x, int y) {
    EfScreenObject *s = (EfScreenObject *)screen;

    if (s->sdl_window != NULL) {
        PyErr_Warn(PyExc_RuntimeWarning, "Window has been created!");
        return 0;
    }

    s->sdl_window = _createWindow(x, y, s->w, s->h, s->title);
    if (!s->sdl_window) {
        return -1;
    }

    s->sdl_renderer = SDL_CreateRenderer(s->sdl_window, -1, SDL_RENDERER_ACCELERATED);
    if (!s->sdl_renderer) {
        PyErr_Format(PyExc_RuntimeError,
            "Renderer creating failed!\n"
            "SDL Info: %s", SDL_GetError()
        );
        return -1;
    }

    return 0;
}

/**
 * \brief Destroy window by ScreenObject.
 * 
 * \param screen Instance of EfScreenObject.
 */
void Ef_ScreenObject_DestroyWindow(PyObject *screen) {
    EfScreenObject *s = (EfScreenObject *)screen;

    if (s->sdl_window == NULL) {
        PyErr_Warn(PyExc_RuntimeWarning, "Window has not been created!");
        return;
    }

    SDL_DestroyWindow(s->sdl_window);
    SDL_DestroyRenderer(s->sdl_renderer);
    s->sdl_window = NULL;
    s->sdl_renderer = NULL;
}

/**
 * \brief Update screen.
 * 
 * \param screen Instance of EfScreenObject.
 */
void Ef_ScreenObject_Update(PyObject *screen) {
    EfScreenObject *s = (EfScreenObject *)screen;

    if (s->sdl_window == NULL) {
        PyErr_Warn(PyExc_RuntimeWarning, "Window has not been created!");
        return;
    }

    SDL_UpdateWindowSurface(s->sdl_window);
}

/**
 * \brief Get Surface Object from screen.
 * 
 * \param screen Instance of EfScreenObject.
 * \return Surface Object on success, None on no window created, NULL on failure.
 */
PyObject *Ef_ScreenObject_GetSurface(PyObject *screen) {
    EfScreenObject *s = (EfScreenObject *)screen;
    if (s->sdl_window == NULL) {
        PyErr_Warn(PyExc_RuntimeWarning, "Window has not been created!");
        Py_RETURN_NONE;
    }

    SDL_Surface *surface = SDL_GetWindowSurface(s->sdl_window);
    if (!surface) {
        PyErr_Format(PyExc_RuntimeError,
            "Error getting surface!\n"
            "SDL Info: %s", SDL_GetError()
        );
        return NULL;
    }

    return Ef_SurfaceObject_FromSDLSurface(imported_SurfaceType, surface, 1);
}

static void
EfScreenObject_dealloc(EfScreenObject *self) {
    if (self->sdl_window != NULL) {
        SDL_DestroyWindow(self->sdl_window);
        self->sdl_window = NULL;
    }
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *
EfScreenObject_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    EfScreenObject *self;
    self = (EfScreenObject *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->w = 0;
        self->h = 0;
        self->title = "";
        self->sdl_window = NULL;

        // Add screen object to global list.
        if (_filterScreenObjects(_screen_objects_list) < 0) {
            return NULL;
        }
        PyList_Append(_screen_objects_list, (PyObject *)self);
    }
    return (PyObject *)self;
}

static int
EfScreenObject_init(EfScreenObject *self, PyObject *args, PyObject *kwds) {
    PyObject *size = NULL;
    const char *title = NULL;
    static char *kwlist[] = {"size", "title", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "Os", kwlist, &size, &title))
        return -1;

    if (Ef_GetTwoIntsFromSequence(size, &self->w, &self->h) < 0) {
        PyErr_SetString(PyExc_TypeError, "Size must be two numbers.");
        return -1;
    }
    if (_assertWindowSize(self->w, self->h) < 0) {
        return -1;
    }

    self->title = strdup(title);

    return 0;
}

static PyObject *
EfScreenObject_repr(EfScreenObject *v) {
    return PyUnicode_FromFormat("<Screen %p '%s' {%dx%d}>",
                                v, v->title, v->w, v->h);
}

static PyMemberDef EfScreenObject_members[] = {
    {"w", T_INT, offsetof(EfScreenObject, w), 0,
     "screen width"},
    {"h", T_INT, offsetof(EfScreenObject, h), 0,
     "screen height"},
    {"title", T_STRING, offsetof(EfScreenObject, title), 0,
     "screen title"},
    {NULL}
};

static PyObject *
EfScreenObject_createWindow(EfScreenObject *self, PyObject *args, PyObject *kwds) {
    int x = -1;
    int y = -1;
    PyObject *pos = NULL;
    static char *kwlist[] = {"pos", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O", kwlist, &pos))
        return NULL;

    if (pos != NULL && Ef_GetTwoIntsFromSequence(pos, &x, &y) < 0) {
        PyErr_SetString(PyExc_TypeError, "Pos must be two numbers.");
        return NULL;
    }

    if (Ef_ScreenObject_CreateWindow((PyObject *)self, x, y) < 0) {
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject *
EfScreenObject_destroyWindow(EfScreenObject *self, PyObject *Py_UNUSED(ignore)) {
    Ef_ScreenObject_DestroyWindow((PyObject *)self);
    Py_RETURN_NONE;
}

static PyObject *
EfScreenObject_isCreated(EfScreenObject *self, PyObject *Py_UNUSED(ignore)) {
    if (self->sdl_window == NULL) {
        Py_RETURN_FALSE;
    }
    Py_RETURN_TRUE;
}

static PyObject *
EfScreenObject_getSurface(EfScreenObject *self, PyObject *Py_UNUSED(ignore)) {
    return Ef_ScreenObject_GetSurface((PyObject *)self);
}

static PyObject *
EfScreenObject_update(EfScreenObject *self, PyObject *Py_UNUSED(ignore)) {
    Ef_ScreenObject_Update((PyObject *)self);
    Py_RETURN_NONE;
}

static PyMethodDef EfScreenObject_methods[] = {
    {"createWindow", (PyCFunction)EfScreenObject_createWindow, METH_VARARGS | METH_KEYWORDS,
     "Create a new window."},
    {"destroyWindow", (PyCFunction)EfScreenObject_destroyWindow, METH_NOARGS,
     "Destroy the window."},
    {"isCreated", (PyCFunction)EfScreenObject_isCreated, METH_NOARGS,
     "Return is window created."},
    {"getSurface", (PyCFunction)EfScreenObject_getSurface, METH_NOARGS,
     "Get surface of the screen."},
    {"update", (PyCFunction)EfScreenObject_update, METH_NOARGS,
     "Update screen."},
    {NULL}
};

static PyTypeObject EfScreenType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "screen.Screen",
    .tp_doc = PyDoc_STR("Screen objects."),
    .tp_basicsize = sizeof(EfScreenObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = EfScreenObject_new,
    .tp_init = (initproc)EfScreenObject_init,
    .tp_dealloc = (destructor)EfScreenObject_dealloc,
    .tp_repr = (reprfunc)EfScreenObject_repr,
    .tp_members = EfScreenObject_members,
    .tp_methods = EfScreenObject_methods,
};

static PyObject *
Ef_Py_createWindow(PyObject *self, PyObject *args, PyObject *kwds) {
    int x = -1;
    int y = -1;
    PyObject *size = NULL;
    PyObject *title = NULL;
    PyObject *pos = NULL;
    PyObject *screen;

    static char *kwlist[] = {"size", "title", "pos", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO|O", kwlist,
                                     &size, &title, &pos))
        return NULL;

    screen = Ef_ScreenObject_FromPy((PyObject *)&EfScreenType, size, title);
    if (screen == NULL) {
        return NULL;
    }

    if (pos != NULL && Ef_GetTwoIntsFromSequence(pos, &x, &y) < 0) {
        PyErr_SetString(PyExc_TypeError, "Pos must be two numbers.");
        return NULL;
    }
    if (Ef_ScreenObject_CreateWindow((PyObject *)screen, x, y) < 0) {
        return NULL;
    }
    return screen;
}

static PyObject *
Ef_Py_getAllWindows(PyObject *self, PyObject *Py_UNUSED(ignore)) {
    if (_filterScreenObjects(_screen_objects_list) < 0) {
        return NULL;
    }
    return PySequence_List(_screen_objects_list);
}

static PyObject *
Ef_Py_destroyAllWindows(PyObject *self, PyObject *Py_UNUSED(ignore)) {
    if (_filterScreenObjects(_screen_objects_list) < 0) {
        return NULL;
    }

    for (Py_ssize_t i = 0; i < PyList_GET_SIZE(_screen_objects_list); i++) {
        Ef_ScreenObject_DestroyWindow(
            PyList_GET_ITEM(_screen_objects_list, i)
        );
    }

    if (_filterScreenObjects(_screen_objects_list) < 0) {
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyMethodDef screen_methods[] = {
    {"createWindow", (PyCFunction)Ef_Py_createWindow, METH_VARARGS | METH_KEYWORDS,
     "Create a new window."},
    {"getAllWindows", (PyCFunction)Ef_Py_getAllWindows, METH_NOARGS,
     "Returns a list copy to all exists windows."},
    {"destroyAllWindows", (PyCFunction)Ef_Py_destroyAllWindows, METH_NOARGS,
     "Destroy all exists windows."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef screen_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "screen",
    .m_doc = "A python extension depend on SDL2, support game frame in windows system.",
    .m_size = -1,
    .m_methods = screen_methods
};

PyMODINIT_FUNC
PyInit_screen(void) {
    PyObject *m = NULL;
    if (PyType_Ready(&EfScreenType) < 0)
        return NULL;

    m = PyModule_Create(&screen_module);
    if (!m)
        goto err_exit;

    if (EF_IMPORT_Surface() < 0)
        goto err_exit;

    Py_INCREF(&EfScreenType);
    if (PyModule_AddObject(m, "Screen", (PyObject *)&EfScreenType) < 0)
        goto err_exit;

    _screen_objects_list = PyList_New(0);
    if (!_screen_objects_list)
        goto err_exit;

    return m;

err_exit:
    Py_XDECREF(m);
    EF_IMPORT_DECREAF();
    Py_XDECREF(&EfScreenType);
    Py_XDECREF(_screen_objects_list);
    return NULL;
}