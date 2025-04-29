#ifndef __EFUTILS_H__
#define __EFUTILS_H__

#define PY_SSIZE_T_CLEAN
#include <Python.h>

/**
 * \brief Get item from a sequence and convert it into an integer.
 * 
 * \param seq Input sequence.
 * \param i Item index.
 * \return -1 on error. Use `PyErr_Occurred()` to disambiguate.
 * 
 * \note This function will not set error string.
 */
long Ef_PySequence_GetItemAsLong(PyObject *seq, Py_ssize_t i);

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
int Ef_GetTwoIntsFromSequence(PyObject *seq, int *v1, int *v2);

/**
 * \brief Get TypeObject from specific module.
 * 
 * \param module Module in current frame.
 * \param module_name Module to import.
 * \param type_name Type to import.
 * \param level 0: absolute, 1: current, 2: parent
 * \return New reference of TypeObject on success, NULL on failure.
 */
PyObject *Ef_RelaviteImport(PyObject *module, const char *module_name,
                            const char *type_name, int level);

#endif // __EFUTILS_H__