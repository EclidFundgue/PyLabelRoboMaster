#include "surface.h"

#include <structmember.h>

#include "SDL_image.h"
#include "efutils.h"

static PyTypeObject EfSurfaceType;

/**
 * \brief Create a new SurfaceObject.
 * 
 * \param type SurfaceObject Type.
 * \param w Surface width.
 * \param h Surface height.
 * \param surf SDL_Surface, can be NULL.
 * \return New reference to SurfaceObject, NULL on failure.
 */
PyObject *
Ef_SurfaceObject_New(PyObject *type, int w, int h, SDL_Surface *surf) {
    PyTypeObject *tp = (PyTypeObject *)type;

    EfSurfaceObject *ret = (EfSurfaceObject *)tp->tp_new(tp, NULL, NULL);
    if (!ret) {
        return NULL;
    }

    ret->w = w;
    ret->h = h;
    ret->sdl_surface = surf;
    return (PyObject *)ret;
}

/**
 * \brief Create SurfaceObject from SDL_Surface.
 * 
 * \param type SurfaceObject Type.
 * \param surf SDL_Surface.
 * 
 * \note SurfaceObject will take control of SDL_Surface and free it when dealloc.
 * \note `is_from_window` is default 0. Use `Ef_SurfaceObject_FromWindow` if you
 *       want to create object from SDL_Window.
 */
PyObject *
Ef_SurfaceObject_FromSurface(PyObject *type, SDL_Surface *surf) {
    return Ef_SurfaceObject_New(type, surf->w, surf->h, surf);
}

/**
 * \brief Create SurfaceObject from SDL_Surface.
 * 
 * \param type SurfaceObject Type.
 * \param win SDL_Window.
 */
PyObject *Ef_SurfaceObject_FromWindow(PyObject *type, SDL_Window *win) {
    SDL_Surface *surf = SDL_GetWindowSurface(win);
    if (!surf) {
        PyErr_Format(PyExc_RuntimeError,
            "Error getting surface!\n"
            "SDL Info: %s", SDL_GetError()
        );
        return NULL;
    }

    PyObject *ret = Ef_SurfaceObject_FromSurface(type, surf);
    ((EfSurfaceObject *)ret)->is_from_window = 1;
    return ret;
}

static SDL_Surface *_subsurfaceFrom(
    SDL_Surface *src,
    int x, int y, int w, int h
) {
    SDL_PixelFormat *f = src->format;
    char *data = (char *)src->pixels + x * f->BytesPerPixel + y * src->pitch;
    return SDL_CreateRGBSurfaceFrom(
        data, w, h, f->BitsPerPixel, src->pitch,
        f->Rmask, f->Gmask, f->Bmask, f->Amask
    );
}

/**
 * \brief Get a Subsurface from owner by certain rect.
 * 
 * \param x Rect X.
 * \param y Rect Y.
 * \param w Rect Width.
 * \param h Rect Height.
 * \return New reference to Subsurface on success, NULL on failure.
 */
PyObject *Ef_SurfaceObject_Subsurface(PyObject *owner, int x, int y, int w, int h) {
    EfSurfaceObject *owner_obj = (EfSurfaceObject *)owner;
    if (x < 0 || y < 0 || x + w > owner_obj->w || y + h > owner_obj->h) {
        PyErr_SetString(PyExc_ValueError,
            "Subsurface rect out of range."
        );
        return NULL;
    }

    SDL_Surface *sub = _subsurfaceFrom(owner_obj->sdl_surface, x, y, w, h);
    if (!sub) {
        PyErr_Format(PyExc_RuntimeError,
            "Error creating subsurface.\n"
            "SDL Info: %s", SDL_GetError()
        );
        return NULL;
    }

    EfSurfaceObject *ret = (EfSurfaceObject *)Ef_SurfaceObject_FromSurface((PyObject *)Py_TYPE(owner), sub);
    if (!ret) {
        return NULL;
    }

    Py_INCREF(owner_obj);
    ret->is_from_window = owner_obj->is_from_window;
    ret->owner = owner;
    ret->x_offset = x;
    ret->y_offset = y;
    return (PyObject *)ret;
}

static void
EfSurfaceObject_dealloc(EfSurfaceObject *self) {
    // You can not free window surface.
    if (self->sdl_surface != NULL && !self->is_from_window) {
        SDL_FreeSurface(self->sdl_surface);
    }

    // subsurface
    if (self->owner) {
        Py_DECREF(self->owner);
    }
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

        self->owner = NULL;
        self->x_offset = 0;
        self->y_offset = 0;
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
        PyErr_SetString(PyExc_RuntimeError, "Detected not initialized surface.");
        return NULL;
    }

    // subsurface
    EfSurfaceObject *owner = src;
    int x_offset = 0;
    int y_offset = 0;
    while (owner->owner) {
        x_offset += owner->x_offset;
        y_offset += owner->y_offset;
        owner = (EfSurfaceObject *)owner->owner;
    }

    if (owner == src) { // no subsurface
        if (SDL_BlitSurface(src->sdl_surface, NULL, self->sdl_surface, NULL) < 0) {
            PyErr_Format(PyExc_RuntimeError,
                "Error bliting surface.\n"
                "SDL Info: %s", SDL_GetError()
            );
            return NULL;
        }
    }
    else {
        SDL_Rect src_rect = {x_offset, y_offset, src->w, src->h};
        SDL_Rect dst_rect = {x, y, src->w, src->h};
        if (SDL_BlitSurface(owner->sdl_surface, &src_rect, self->sdl_surface, &dst_rect) < 0) {
            PyErr_Format(PyExc_RuntimeError,
                "Error bliting surface.\n"
                "SDL Info: %s", SDL_GetError()
            );
            return NULL;
        }
    }

    Py_RETURN_NONE;
}

static PyMethodDef EfSurfaceObject_methods[] = {
    {"fill", (PyCFunction)EfSurfaceObject_fill, METH_VARARGS | METH_KEYWORDS,
     "Fill the surface with a certain color."},
    {"blit", (PyCFunction)EfSurfaceObject_blit, METH_VARARGS | METH_KEYWORDS,
     "Blit anohter surface to self."},
    {NULL}
};

static PyObject *
EfSurfaceObject_subscript(EfSurfaceObject* self, PyObject* item) {
    Py_ssize_t _sy, _ey, _stepy;
    Py_ssize_t _sx, _ex, _stepx;
    int sy, ey, stepy;
    int sx, ex, stepx;

    if (!PyTuple_Check(item) || PyTuple_GET_SIZE(item) != 2 ||
        !PySlice_Check(PyTuple_GET_ITEM(item, 0)) ||
        !PySlice_Check(PyTuple_GET_ITEM(item, 1))) {
        PyErr_SetString(PyExc_TypeError, "Surface indices must be two slices.");
        return NULL;
    }

    if (PySlice_Unpack(PyTuple_GET_ITEM(item, 0), &_sy, &_ey, &_stepy) < 0 ||
        PySlice_Unpack(PyTuple_GET_ITEM(item, 1), &_sx, &_ex, &_stepx) < 0) {
        return NULL;
    }

    sy = (int)_sy; ey = (int)_ey; stepy = (int)_stepy;
    sx = (int)_sx; ex = (int)_ex; stepx = (int)_stepx;
    if (stepy != 1 || stepx != 1) {
        PyErr_Format(PyExc_TypeError,
            "Slice step must be 1, but received %d",
            (stepy != 1) ? stepy : stepx
        );
        return NULL;
    }

    if (ex < 0) {
        ex += self->w + 1;
    }
    if (ey < 0) {
        ey += self->h + 1;
    }

    if (sy < 0 || sx < 0 || ey < 0 || ex < 0 || ey > self->h || ex > self->w) {
        PyErr_SetString(PyExc_ValueError, "Subsurface outside surface area.");
        return NULL;
    }

    if (sy >= ey || sx >= ex) {
        PyErr_SetString(PyExc_ValueError, "Invalid slice range.");
        return NULL;
    }

    return Ef_SurfaceObject_Subsurface((PyObject *)self, sx, sy, ex - sx, ey - sy);
}

static PyMappingMethods EfSurfaceObject_mapping_methods = {
    .mp_subscript = (binaryfunc)EfSurfaceObject_subscript,
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
    .tp_as_mapping = &EfSurfaceObject_mapping_methods,
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

    return Ef_SurfaceObject_FromSurface((PyObject *)&EfSurfaceType, image);
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