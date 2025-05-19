#include "widgets.h"

#include <structmember.h>

#include "efimport.h"
#include "efutils.h"

static struct PyModuleDef widgets_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "widgets",
    .m_doc = "Control widgets.",
    .m_size = -1,
};

PyMODINIT_FUNC
PyInit_widgets(void) {
    PyObject *m = NULL;

    if (PyType_Ready(&EfBaseWidgetType) < 0)
        return NULL;
    if (PyType_Ready(&EfRootWidgetType) < 0)
        return NULL;

    m = PyModule_Create(&widgets_module);
    if (m == NULL)
        goto err_exit;

    if (EF_IMPORT_Surface() < 0)
        goto err_exit;

    Py_INCREF(&EfBaseWidgetType);
    if (PyModule_AddObject(m, "Base", (PyObject *)&EfBaseWidgetType) < 0)
        goto err_exit;
    Py_INCREF(&EfRootWidgetType);
    if (PyModule_AddObject(m, "Root", (PyObject *)&EfRootWidgetType) < 0)
        goto err_exit;

    return m;

err_exit:
    Py_XDECREF(m);
    EF_IMPORT_DECREAF();
    Py_XDECREF(&EfBaseWidgetType);
    Py_XDECREF(&EfRootWidgetType);
    return NULL;
}