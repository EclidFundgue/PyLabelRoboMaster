#ifndef __WIDGETS_EVENT_INTERNAL_H__
#define __WIDGETS_EVENT_INTERNAL_H__

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>

#define EF_BUTTON_FLAG(X) (1 << (X))

#define EF_MOUSE_LEFT_DOWN      EF_BUTTON_FLAG(0)
#define EF_MOUSE_LEFT_PRESS     EF_BUTTON_FLAG(1)
#define EF_MOUSE_LEFT_UP        EF_BUTTON_FLAG(2)

#define EF_MOUSE_MID_DOWN       EF_BUTTON_FLAG(3)
#define EF_MOUSE_MID_PRESS      EF_BUTTON_FLAG(4)
#define EF_MOUSE_MID_UP         EF_BUTTON_FLAG(5)

#define EF_MOUSE_RIGHT_DOWN     EF_BUTTON_FLAG(6)
#define EF_MOUSE_RIGHT_PRESS    EF_BUTTON_FLAG(7)
#define EF_MOUSE_RIGHT_UP       EF_BUTTON_FLAG(8)

#define EF_MOUSE_MOTION         EF_BUTTON_FLAG(9)

#define EF_MOUSE_DOWN (EF_MOUSE_LEFT_DOWN | EF_MOUSE_MID_DOWN | EF_MOUSE_RIGHT_DOWN)
#define EF_MOUSE_PRESS (EF_MOUSE_LEFT_PRESS | EF_MOUSE_MID_PRESS | EF_MOUSE_RIGHT_PRESS)
#define EF_MOUSE_UP (EF_MOUSE_LEFT_UP | EF_MOUSE_MID_UP | EF_MOUSE_RIGHT_UP)

typedef struct EfEventWidget {
    PyObject_HEAD
    uint16_t mouse_flags;
    int mouse_x;
    int mouse_y;
    int mouse_dx;
    int mouse_dy;
    int wheel;
} EfEventWidget;

extern PyTypeObject EfEventWidgetType;

PyObject *Ef_EventWidget_New(PyObject *type);

#endif // __WIDGETS_EVENT_INTERNAL_H__