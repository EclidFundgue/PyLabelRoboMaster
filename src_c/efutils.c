#include "efutils.h"

long Ef_PySequence_GetItemAsLong(PyObject *seq, Py_ssize_t i) {
    PyObject *tmp;
    long res;

    tmp = PySequence_GetItem(seq, i);
    if (!tmp) {
        return -1;
    }

    res = PyLong_AsLong(tmp);
    Py_DECREF(tmp);
    return res;
}

int Ef_GetTwoIntsFromSequence(PyObject *seq, int *v1, int *v2) {
    // handle neasted tuple
    while (PyTuple_Check(seq) && Py_SIZE(seq) == 1) {
        seq = PyTuple_GET_ITEM(seq, 0);
    }

    if (!PySequence_Check(seq) || PySequence_Length(seq) != 2) {
        return -1;
    }

    *v1 = (int)Ef_PySequence_GetItemAsLong(seq, 0);
    *v2 = (int)Ef_PySequence_GetItemAsLong(seq, 1);
    if (PyErr_Occurred()) {
        return -1;
    }
    return 0;
}

PyObject *Ef_RelaviteImport(
    PyObject *module,
    const char *module_name,
    const char *type_name,
    int level
) {
    PyObject* globals = PyModule_GetDict(module);
    if (!globals) {
        return NULL;
    }

    PyObject* py_module_name = PyUnicode_FromString(module_name);
    if (!py_module_name) {
        return NULL;
    }

    PyObject* imported_module = PyImport_ImportModuleLevelObject(
        py_module_name,
        globals,
        NULL, // locals
        NULL, // fromlist
        level
    );

    PyObject *type = PyObject_GetAttrString(imported_module, type_name);
    Py_DECREF(imported_module);
    if (!type) {
        return NULL;
    }
    return type;
}
