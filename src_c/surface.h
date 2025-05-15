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

    // subsurface
    PyObject *owner;
    int x_offset;
    int y_offset;
};
typedef struct _EfSurfaceObject EfSurfaceObject;

PyObject *Ef_SurfaceObject_New(PyObject *type, int w, int h, SDL_Surface *surf);
PyObject *Ef_SurfaceObject_FromSurface(PyObject *type, SDL_Surface *surf);
PyObject *Ef_SurfaceObject_FromWindow(PyObject *type, SDL_Window *win);

PyObject *Ef_SurfaceObject_Subsurface(PyObject *owner, int x, int y, int w, int h);

#endif // __SURFACE_H__