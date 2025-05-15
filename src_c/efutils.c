#include "efutils.h"

/**
 * \brief Get item from a sequence and convert it into an integer.
 * 
 * \param seq Input sequence.
 * \param i Item index.
 * \return -1 on error. Use `PyErr_Occurred()` to disambiguate.
 * 
 * \note This function will not set error string.
 */
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

/**
 * \brief Get two integers from sequence object.
 *
 * \param seq Sequence object. Borrowed reference.
 * \param v1 Converted value.
 * \param v2 Converted value.
 * \returns 0 on success, -1 on failure.
 * 
 * \note This function will not set error string.
 */
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

/**
 * \brief Get TypeObject from specific module.
 * 
 * \param module Module in current frame.
 * \param module_name Module to import.
 * \param type_name Type to import.
 * \param level 0: absolute, 1: current, 2: parent
 * \return New reference of TypeObject on success, NULL on failure.
 */
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
