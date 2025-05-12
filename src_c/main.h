#ifndef __MAIN_H__
#define __MAIN_H__

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "SDL.h"

struct _EfMainObject {
    PyObject_HEAD
    PyObject *screen;
    PyObject *root;
};
typedef struct _EfMainObject EfMainObject;

#endif // __MAIN_H__