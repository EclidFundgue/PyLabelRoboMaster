#ifndef __EFIMPORT_H__
#define __EFIMPORT_H__

#include <Python.h>

extern PyObject *imported_SurfaceType;
extern PyObject *imported_ScreenType;
extern PyObject *imported_RootWidgetType;

int Ef_ImportType(PyObject *module, PyObject **ret, const char *module_name, const char *type_name);

#define EF_IMPORT_Surface() Ef_ImportType(m, &imported_SurfaceType, "surface", "Surface")
#define EF_IMPORT_Screen() Ef_ImportType(m, &imported_ScreenType, "screen", "Screen")
#define EF_IMPORT_RootWidget() Ef_ImportType(m, &imported_RootWidgetType, "widget", "Root")

#define EF_IMPORT_DECREAF() \
    do {\
        Py_XDECREF(imported_SurfaceType);\
        Py_XDECREF(imported_ScreenType);\
        Py_XDECREF(imported_RootWidgetType);\
    } while (0)

#endif // __EFIMPORT_H__