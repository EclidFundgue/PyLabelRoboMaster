#ifndef __EFUTILS_H__
#define __EFUTILS_H__

#define PY_SSIZE_T_CLEAN
#include <Python.h>

long Ef_PySequence_GetItemAsLong(PyObject *seq, Py_ssize_t i);

int Ef_GetTwoIntsFromSequence(PyObject *seq, int *v1, int *v2);

PyObject *Ef_RelaviteImport(PyObject *module, const char *module_name,
                            const char *type_name, int level);

#endif // __EFUTILS_H__