#include "surface.h"

#include <structmember.h>

#include "SDL_image.h"
#include "efutils.h"

static PyTypeObject EfSurfaceType;

/**
 * \brief Create SurfaceObject from SDL_Surface.
 * 
 * \param type SurfaceObject Type.
 * \param surface SDL_Surface.
 * \param is_from_window Is the SDL_Surface got from a SDL_Window.
 * 
 * \note SurfaceObject will take control of SDL_Surface and free it when dealloc.
 */
PyObject *Ef_SurfaceObject_FromSDLSurface(
    PyObject *type,
    SDL_Surface *surface,
    int is_from_window
) {
    EfSurfaceObject *ret = (EfSurfaceObject *)PyObject_CallFunction(
        type, "((ii))", surface->w, surface->h // (ii) will be considered as two arguments.
    );
    if (!ret) {
        return NULL;
    }

    ret->is_from_window = is_from_window;

    if (ret->sdl_surface) {
        SDL_FreeSurface(ret->sdl_surface);
    }
    ret->sdl_surface = surface;

    return (PyObject *)ret;
}

static void
EfSurfaceObject_dealloc(EfSurfaceObject *self) {
    // You can not free window surface.
    if (self->sdl_surface != NULL && !self->is_from_window) {
        SDL_FreeSurface(self->sdl_surface);
    }
    self->sdl_surface = NULL;
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *
EfSurfaceObject_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    EfSurfaceObject *self;
    self = (EfSurfaceObject *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->w = 0;
        self->h = 0;
        self->is_from_window = 0;
        self->sdl_surface = NULL;
    }
    return (PyObject *)self;
}

static int
EfSurfaceObject_init(EfSurfaceObject *self, PyObject *args, PyObject *kwds) {
    PyObject *size = NULL;
    static char *kwlist[] = {"size", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &size))
        return -1;

    if (Ef_GetTwoIntsFromSequence(size, &self->w, &self->h) < 0) {
        PyErr_SetString(PyExc_TypeError, "Size must be two numbers.");
        return -1;
    }

    self->sdl_surface = SDL_CreateRGBSurface(0, self->w, self->h, 32, 0, 0, 0, 0);
    if (!self->sdl_surface) {
        PyErr_Format(PyExc_RuntimeError,
            "Error creating SDL Surface!\n"
            "SDL Info: %s",
            SDL_GetError()
        );
        return -1;
    }

    return 0;
}

static PyObject *
EfSurfaceObject_repr(EfSurfaceObject *v) {
    return PyUnicode_FromFormat("<Surface %p {%dx%d}>", v, v->w, v->h);
}

static PyMemberDef EfSurfaceObject_members[] = {
    {"w", T_INT, offsetof(EfSurfaceObject, w), READONLY,
     "surface width"},
    {"h", T_INT, offsetof(EfSurfaceObject, h), READONLY,
     "surface height"},
    {"is_from_window", T_BOOL, offsetof(EfSurfaceObject, is_from_window), READONLY,
     "whether the surface got from a window"},
    {NULL}
};

static PyObject *
EfSurfaceObject_fill(EfSurfaceObject *self, PyObject *args, PyObject *kwds) {
    uint8_t r, g, b;
    static char *kwlist[] = {"color", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "(bbb)", kwlist, &r, &g, &b))
        return NULL;

    SDL_FillRect(
        self->sdl_surface, NULL,
        SDL_MapRGB(self->sdl_surface->format, r, g, b)
    );

    Py_RETURN_NONE;
}

static PyObject *
EfSurfaceObject_blit(EfSurfaceObject *self, PyObject *args, PyObject *kwds) {
    EfSurfaceObject *src = NULL;
    PyObject *src_obj = NULL;
    PyObject *pos = NULL;
    int x;
    int y;
    static char *kwlist[] = {"src", "pos", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", kwlist, &src_obj, &pos))
        return NULL;

    if (!PyObject_TypeCheck(src_obj, &EfSurfaceType)) {
        PyErr_Format(PyExc_TypeError,
            "Expect Surface type, but received: %s",
            Py_TYPE(src)->tp_name
        );
    }
    src = (EfSurfaceObject *)src_obj;

    if (Ef_GetTwoIntsFromSequence(pos, &x, &y) < 0) {
        return NULL;
    }

    if (src->sdl_surface == NULL || self->sdl_surface == NULL) {
        Py_RETURN_NONE;
    }

    SDL_Rect dst_rect;
    dst_rect.x = x;
    dst_rect.y = y;
    dst_rect.w = src->w;
    dst_rect.h = src->h;
    SDL_BlitSurface(src->sdl_surface, NULL, self->sdl_surface, &dst_rect);

    Py_RETURN_NONE;
}

static PyMethodDef EfSurfaceObject_methods[] = {
    {"fill", (PyCFunction)EfSurfaceObject_fill, METH_VARARGS | METH_KEYWORDS,
     "Fill the surface with a certain color."},
    {"blit", (PyCFunction)EfSurfaceObject_blit, METH_VARARGS | METH_KEYWORDS,
     "Blit anohter surface to self."},
    {NULL}
};

static PyTypeObject EfSurfaceType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "surface.Surface",
    .tp_doc = PyDoc_STR("Surface objects."),
    .tp_basicsize = sizeof(EfSurfaceObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = EfSurfaceObject_new,
    .tp_init = (initproc)EfSurfaceObject_init,
    .tp_dealloc = (destructor)EfSurfaceObject_dealloc,
    .tp_repr = (reprfunc)EfSurfaceObject_repr,
    .tp_members = EfSurfaceObject_members,
    .tp_methods = EfSurfaceObject_methods,
};

static PyObject *
Ef_Py_loadImage(PyObject *self, PyObject *args, PyObject *kwds) {
    const char *path = NULL;
    static char *kwlist[] = {"path", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "s", kwlist, &path))
        return NULL;

    SDL_Surface *image = IMG_Load(path);
    if (!image) {
        PyErr_Format(PyExc_ValueError,
            "Unable to load image %s!\n"
            "SDL_image Info: %s",
            path,
            IMG_GetError()
        );
        return NULL;
    }

    return Ef_SurfaceObject_FromSDLSurface((PyObject *)&EfSurfaceType, image, 0);
}

static PyMethodDef surface_methods[] = {
    {"loadImage", (PyCFunction)Ef_Py_loadImage, METH_VARARGS | METH_KEYWORDS,
     "Load image to Surface."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef surface_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "surface",
    .m_doc = "Control surfaces.",
    .m_size = -1,
    .m_methods = surface_methods
};

PyMODINIT_FUNC
PyInit_surface(void) {
    PyObject *m;
    if (PyType_Ready(&EfSurfaceType) < 0)
        return NULL;

    m = PyModule_Create(&surface_module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&EfSurfaceType);
    if (PyModule_AddObject(m, "Surface", (PyObject *)&EfSurfaceType) < 0) {
        Py_DECREF(&EfSurfaceType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}