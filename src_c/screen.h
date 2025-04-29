#ifndef __SCREEN_H__
#define __SCREEN_H__

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "SDL.h"

struct _EfScreenObject {
    PyObject_HEAD
    int w;
    int h;
    const char *title;
    SDL_Window *sdl_window;
};
typedef struct _EfScreenObject EfScreenObject;

PyObject *Ef_ScreenObject_FromPy(PyObject *type, PyObject *size, PyObject *title);
PyObject *Ef_ScreenObject_FromC(PyObject *type, int w, int h, const char *title);

int Ef_ScreenObject_CreateWindow(PyObject *screen, int x, int y);
void Ef_ScreenObject_DestroyWindow(PyObject *screen);
int Ef_ScreenObject_Fill(PyObject *screen, uint8_t r, uint8_t g, uint8_t b);
void Ef_ScreenObject_Update(PyObject *screen);

#endif // __SCREEN_H__