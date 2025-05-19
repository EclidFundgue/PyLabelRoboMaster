#ifndef __WIDGETS_BASE_INTERNAL_H__
#define __WIDGETS_BASE_INTERNAL_H__

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>

struct _EfBaseWidget {
    PyObject_HEAD
    int x;
    int y;
    int w;
    int h;
    int layer;
    int redraw_parent; // boolean
    int interactive_when_active; // boolean
    int alive; // boolean
    int active; // boolean

    // internal variables
    PyObject *_parent;
    PyObject *_children;
    PyObject *_keyboard_events;
    PyObject *_keyboard_events_once;

    int _need_redraw;
    int _in_redraw_path;
};
typedef struct _EfBaseWidget EfBaseWidget;

extern PyTypeObject EfBaseWidgetType;

#endif // __WIDGETS_BASE_INTERNAL_H__