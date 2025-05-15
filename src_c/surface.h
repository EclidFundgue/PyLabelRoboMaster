#ifndef __SURFACE_H__
#define __SURFACE_H__

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "SDL.h"

struct _EfSurfaceObject {
    PyObject_HEAD
    int w;
    int h;
    int is_from_window;
    SDL_Surface *sdl_surface;
};
typedef struct _EfSurfaceObject EfSurfaceObject;

PyObject *Ef_SurfaceObject_FromSDLSurface(PyObject *type, SDL_Surface *surface, int is_from_window);
PyObject *Ef_SurfaceObject_New(PyObject *type, Py_ssize_t w, Py_ssize_t h);

#endif // __SURFACE_H__