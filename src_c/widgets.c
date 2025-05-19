#include "widgets.h"

#include <structmember.h>

#include "efimport.h"
#include "efutils.h"

#define AddWidget(module, name, type)                                   \
    do {                                                                \
        if (PyType_Ready(&type) < 0)                                    \
            goto err_exit;                                              \
        Py_INCREF(&type);                                               \
        if (PyModule_AddObject(module, name, (PyObject *)&type) < 0)    \
            goto err_exit;                                              \
    } while (0)

static struct PyModuleDef widgets_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "widgets",
    .m_doc = "Control widgets.",
    .m_size = -1,
};

PyMODINIT_FUNC
PyInit_widgets(void) {
    PyObject *m = NULL;

    m = PyModule_Create(&widgets_module);
    if (m == NULL)
        goto err_exit;

    if (EF_IMPORT_Surface() < 0)
        goto err_exit;
    
    AddWidget(m, "Event", EfEventWidgetType);
    AddWidget(m, "Base", EfBaseWidgetType);
    AddWidget(m, "Root", EfRootWidgetType);

    return m;

err_exit:
    Py_XDECREF(m);
    EF_IMPORT_DECREAF();
    Py_XDECREF(&EfEventWidgetType);
    Py_XDECREF(&EfBaseWidgetType);
    Py_XDECREF(&EfRootWidgetType);
    return NULL;
}