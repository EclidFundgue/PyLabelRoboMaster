#ifndef __WIDGETS_ROOT_INTERNAL_H__
#define __WIDGETS_ROOT_INTERNAL_H__

#include "widgets/_base.h"

struct _EfRootWidget {
    EfBaseWidget base;
    PyObject *surface;
};
typedef struct _EfRootWidget EfRootWidget;

extern PyTypeObject EfRootWidgetType;

#endif // __WIDGETS_ROOT_INTERNAL_H__