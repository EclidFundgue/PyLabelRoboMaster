#ifndef __WIDGETS_ROOT_INTERNAL_H__
#define __WIDGETS_ROOT_INTERNAL_H__

#include "widgets/_base.h"

typedef struct EfRootWidget {
    EfBaseWidget base;
    PyObject *surface;
} EfRootWidget;

extern PyTypeObject EfRootWidgetType;

#endif // __WIDGETS_ROOT_INTERNAL_H__