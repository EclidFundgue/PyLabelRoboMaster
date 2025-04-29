import os
import shutil
from distutils.core import Extension, setup


def get_ext(name: str, src_files: list[str]) -> Extension:
    return Extension(
        name=name,
        include_dirs=["src_c/sdl2/include/", "src_c/"],
        library_dirs=["src_c/sdl2"],
        libraries=["SDL2"],
        sources=[os.path.join("src_c", f) for f in src_files]
    )

def move_files(src_dir, dst_dir):
    for p in os.listdir(src_dir):
        shutil.copy(os.path.join(src_dir, p), dst_dir)

setup(
    name="efui-release",
    version="1.0",
    ext_modules=[
        get_ext("screen", ["screen.c", "efutils.c"]),
        get_ext("main", ["main.c", "screen.c", "efutils.c"])
    ]
)

build_dir = './build'
dst_dir = './src_py/efui'
lib_dir = None
for dir in os.listdir(build_dir):
    if dir.startswith('lib') and os.path.isdir(os.path.join(build_dir, dir)):
        lib_dir = os.path.join(build_dir, dir)

if lib_dir is not None:
    move_files(lib_dir, dst_dir)