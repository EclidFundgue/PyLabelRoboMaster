import json
import os
from typing import Any, Union

from .pygame_gui import BaseComponent, f_warning, singleton
from .utils.dataproc import getLabelPath, makeFolder

THEME_VAR_CHANGE = 'VAR_CHANGE'

class ObserveVar:
    def addObserver(self, observer) -> None:
        '''
        Add an observer to this theme. All observers will be noticed when Theme call
        `notify` function. Observer can receive notice by calling `onReceive` function.
        '''
        self.removeDead()

        if not observer.alive:
            f_warning(f'Operation on dead component {observer}.', self)
            return

        if observer in self.observers:
            f_warning(f'Observer {observer} has already attached to {self}.', self)
            return

        self.observers.append(observer)

    def removeObserver(self, observer) -> None:
        ''' Remove observer from this theme. '''
        self.removeDead()

        if not observer.alive:
            f_warning(f'Operation on dead component {observer}.', self)
            return

        if observer not in self.observers:
            f_warning(f'Observer {observer} has not attach to {self} yet.', self)
            return

        self.observers.remove(observer)

    def removeAllObservers(self) -> None:
        ''' Clear all observers. '''
        self.observers = []

    def notify(self, theme: str, message: Any = None) -> None:
        ''' Send message to all observers. '''
        self.removeDead()

        for observer in self.observers:
            observer.onReceive(id(self), theme, message)

    def onReceive(self, sender_id: int, theme: str, message: Any) -> None:
        ''' Receive a mesage. '''
        pass

@singleton
class VarArmorIconType(BaseComponent, ObserveVar):
    '''
    Methods:
    * setColor(idx) -> None
    * setType(idx) -> None
    * set(idx) -> None

    Theme -> Message:
    * THEME_VAR_CHANGE -> (color, type): Tuple[int, int]
    '''
    def __init__(self):
        super().__init__()
        self.color_idx = -1
        self.type_idx = -1
        self.theme = THEME_VAR_CHANGE

    def setColor(self, idx: int) -> None:
        self.color_idx = idx
        self.notify(self.theme, (self.color_idx, self.type_idx))

    def setType(self, idx: int) -> None:
        self.type_idx = idx
        self.notify(self.theme, (self.color_idx, self.type_idx))

    def set(self, idx: int) -> None:
        self.color_idx = idx // 8
        self.type_idx = idx % 8
        self.notify(self.theme, (self.color_idx, self.type_idx))

@singleton
class VarArmorLabels(BaseComponent, ObserveVar):
    '''
    This class is used to manage the image pairs and the deserted images, and
    provide methods to switch between the image folders and select/delete images.

    VarArmorLabels(image_folder, labels_folder, deserted_image_folder)

    Methods:
    * saveUserData() -> None
    * getCurrentImagePath() -> str | None
    * getCurrentLabelPath() -> str | None
    * setPage(page) -> None
    * select(file) -> None
    * delete(file) -> None
    * restore(file) -> None
    * setType(idx) -> None
    * setColor(idx) -> None
    '''

    def __init__(self,
            user_data_path: str,
            image_folder: str,
            label_folder: str,
            deserted_image_folder: str = None):
        super().__init__()

        self.user_data_path = user_data_path
        self.image_folder = image_folder
        self.label_folder = label_folder
        self.deserted_folder = deserted_image_folder

        self._buildOrLoadDeserted(self.deserted_folder)

        self.selected_image: str = None
        self.selected_label: str = None
        self.selected_deserted: str = None

        self.curr_page = 0
        self.curr_type = 0
        self.auto_labeling = False

        self._loadUserData()

    def _makeDefaultUserData(self, path: str) -> None:
        folder = os.path.dirname(path)
        # folder may not exist or be ''
        if folder and not os.path.exists(folder):
            makeFolder(folder)

        with open(path, 'w') as f:
            default_data = {
                'last_image_folder': None, # str
                'last_label_folder': None, # str
                'last_edit_image': None # str
            }
            json.dump(default_data, f)

    def _loadUserData(self) -> None:
        if not os.path.exists(self.user_data_path):
            self._makeDefaultUserData(self.user_data_path)

        with open(self.user_data_path, 'r') as f:
            user_data = json.load(f)
            last_image_folder = user_data['last_image_folder']
            last_label_folder = user_data['last_label_folder']
            last_edit_image = user_data['last_edit_image']

        if last_image_folder is None or last_image_folder != self.image_folder:
            return
        if last_label_folder is None or last_label_folder != self.label_folder:
            return
        if last_edit_image is None:
            return

        last_edit_image_path = os.path.join(self.image_folder, last_edit_image)
        if not os.path.exists(last_edit_image_path):
            return

        self.selected_image = last_edit_image
        self.selected_label = getLabelPath(last_edit_image, self.label_folder)

    def saveUserData(self) -> None:
        with open(self.user_data_path, 'w') as f:
            user_data = {
                'last_image_folder': self.image_folder,
                'last_label_folder': self.label_folder,
                'last_edit_image': self.selected_image
            }
            json.dump(user_data, f)

    def _buildOrLoadDeserted(self, deserted_folder: str) -> None:
        if deserted_folder is None:
            self.deserted_folder = os.path.join(self.image_folder, 'deserted')
        makeFolder(self.deserted_folder)

    def getCurrentImagePath(self) -> Union[str, None]:
        if self.curr_page == 0:
            if self.selected_image is None:
                return None
            return os.path.join(self.image_folder, self.selected_image)
        else:
            if self.selected_deserted is None:
                return None
            return os.path.join(self.deserted_folder, self.selected_deserted)

    def getCurrentLabelPath(self) -> Union[str, None]:
        if self.curr_page == 1:
            return None
        if self.selected_image is None:
            return None
        return getLabelPath(self.selected_image, self.label_folder)

    def setPage(self, page: int) -> None:
        self.curr_page = page

    def select(self, file: str) -> None:
        if self.curr_page == 0:
            self.selected_image = file
        else:
            self.selected_deserted = file

    def delete(self, file: str) -> None:
        '''
        delete the image from image folder and move it to deserted folder
        '''
        if self.selected_image == file:
            self.selected_image = None
        os.rename(
            os.path.join(self.image_folder, file),
            os.path.join(self.deserted_folder, file)
        )

    def restore(self, file: str) -> None:
        '''
        restore the image from deserted folder to image folder
        '''
        if self.selected_deserted == file:
            self.selected_deserted = None
        os.rename(
            os.path.join(self.deserted_folder, file),
            os.path.join(self.image_folder, file)
        )

    def setType(self, idx: int) -> None:
        self.curr_type = self.curr_type // 8 * 8 + idx

    def setColor(self, idx: int) -> None:
        self.curr_type = self.curr_type % 8 + idx * 8