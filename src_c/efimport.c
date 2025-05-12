#include "efimport.h"

#include "efutils.h"

PyObject *imported_SurfaceType = NULL;
PyObject *imported_ScreenType = NULL;
PyObject *imported_RootWidgetType = NULL;

/**
 * \brief Import a type.
 * 
 * \param module Module object.
 * \param ret Import reult.
 * \param module_name Module name.
 * \param type_name Type name.
 * \return 0 on success, -1 on failure
 */
int Ef_ImportType(PyObject *module, PyObject **ret, const char *module_name, const char *type_name) {
    *ret = Ef_RelaviteImport(module, module_name, type_name, 1);
    if (!(*ret)) {
        return -1;
    }
    return 0;
}
