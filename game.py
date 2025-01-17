import os
import json
import random
from typing import Optional


class FileUtil:

    @staticmethod
    def load_json(file, _encodings: list = 
                      ['utf8', 'utf-8', 'utf-8-sig', 
                       'Windows-1252', 'ASCII', 'UTF-16']) -> dict:
        """Attempts to load a json file from disk.

        Attempts to load a json file from disc using a range of different encodings.
        This can be useful if you don't know what encoding a json file is, recursivly
        attemptiong different encodings to find what is the correct encoding for that
        file.
        """
        codecs = _encodings.copy()
        if len(codecs) == 0:
            print(f'! Failed to find encodiung or json is invalid in file: {file}')
            return {}

        encoding = codecs.pop(0)
        try:
            with open(file, encoding = encoding) as f:
                info = json.load(f, strict=False)
                return info
        except:
            return FileUtil.load_json(file, codecs)


class NumberUtil:

    @staticmethod
    def extract_length_meters(text: str) -> float:
        text = text.replace(' ', '')
        try:
            if text.endswith('km'):
                km = float(text[:-2])
                return int(km * 1000)
            if text.endswith('m'):
                return int(float(text[:-1]))
            
            if '.' in text:
                # Assume km
                return int(float(text) * 1000)
            return int(text)
        except:
            return 0


class GameAsset:

    def __init__(self, folder_path: str = None):
        self.name: str = 'Undefined'
        self.preview_image: str = None
        self.folder_path: str = folder_path
        self.ui_file: str = None
        self._data: dict = None

        # Load the Assests data
        if folder_path:
            self.load_asset(folder_path)

    @property
    def _property_name(self) -> str:
        return 'name'
    
    @property
    def _path_ui_folder(self) -> str:
        # Defiens the relative path where the ui file is kept
        return 'ui'

    def is_valid(self) -> bool:
        if self.folder_path is None:
            return
        if not os.path.exists(self.folder_path):
            return False
        if self.ui_file is None or not os.path.exists(self.ui_file):
            return False
        return True
    
    def find_file(self, image_name: str, path: str = None) -> Optional[str]:
        """Attempts to file a file with the matching name
        """
        if not self.is_valid():
            return None
        
        if path is not None and not os.path.exists(path):
            return None

        compare = image_name.lower()
        files = os.listdir(self.folder_path if path is None else path)
        for file in files:
            name, ext = os.path.splitext(file)
            if name.lower() == compare:
                return os.path.join(self.folder_path if path is None else path, file)
        return None
    
    def load_ui_file(self):
        path = self.folder_path
        if self._path_ui_folder is not None and len(self._path_ui_folder) > 0:
            path = os.path.join(self.folder_path, self._path_ui_folder)

        if not os.path.exists(path):
            return
        files = os.listdir(path)

        for file in files:
            if file.startswith('ui_') and file.endswith('.json'):
                self.ui_file = os.path.join(path, file)
                break

    def load_asset(self, folder_path: str = None):
        if folder_path is not None:
            self.folder_path = folder_path
        self.load_ui_file()

        if not self.is_valid():
            return
        
        def _file(file_name) -> str:
            nonlocal folder_path
            return os.path.join(folder_path, file_name)

        files = os.listdir(self.folder_path)
        for file in files:
            full_file_path = os.path.join(self.folder_path, file)

            if os.path.isdir(full_file_path):
                continue

            name, ext = os.path.splitext(file)
            if name == 'preview':
                self.preview_image = _file(file)

        try:
            data = FileUtil.load_json(self.ui_file)
            self._data = data
            self.name = data.get(self._property_name, 'Undefined')
        except:
            asset_folder_name = os.path.basename(self.folder_path)
            print('Failed to load data for asset', asset_folder_name)

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return self.__str__()


class CarSkin(GameAsset):

    def __init__(self, folder_path: str = None):
        super(CarSkin, self).__init__(folder_path)

    @property
    def _property_name(self) -> str:
        return 'skinname'
    
    @property
    def _path_ui_folder(self) -> str:
        return None
    
    @property
    def priority(self) -> int:
        return self._data.get('priority', 0)


class Car(GameAsset):

    def __init__(self, folder_path: str = None):
        super(Car, self).__init__(folder_path)
        self.skins = []
        self.bhp = 0
        self.weight = 0

        self.load_skins()
        self.load_stats()

    def load_skins(self):
        skins_folder = os.path.join(self.folder_path, 'skins')
        if not os.path.exists(skins_folder):
            return
        self.skins.clear()

        skin_folders = os.listdir(skins_folder)
        for sf in skin_folders:
            skin = CarSkin(os.path.join(skins_folder, sf))
            if not skin.is_valid():
                continue
            self.skins.append(skin)

    def load_stats(self):
        if not self.is_valid():
            return
        
        specs: dict = self._data.get('specs', {})
        self.bhp = specs.get('bhp', 0)
        self.weight = specs.get('weight', 0)

    @property
    def brand(self):
        return self._data.get('brand', 'Unknown Brand')
    
    @property
    def catagory(self) -> str:
        return self._data.get('class', '')
    
    @property
    def description(self) -> str:
        return self._data.get('description', '')
    
    @property
    def country(self) -> str:
        return self._data.get('country', '')
    
    def random_skin(self) -> CarSkin:
        if len(self.skins) == 0:
            return None
        return self.skins[random.randint(0, len(self.skins) - 1)]
    
    def first_skin(self) -> CarSkin:
        if len(self.skins) == 0:
            return None
        return self.skins[0]

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return self.__str__()


class TrackLayout(GameAsset):

    def __init__(self, folder_path):
        super(TrackLayout, self).__init__(folder_path)

    @property
    def _path_ui_folder(self) -> str:
        return None
    
    @property
    def description(self) -> str:
        return self._data.get('description', '')
    
    @property
    def country(self) -> str:
        return self._data.get('country', '')
    
    @property
    def city(self) -> str:
        return self._data.get('city', '')
    
    @property
    def length(self) -> int:
        return NumberUtil.extract_length_meters(self._data.get('length', ''))
    
    @property
    def length_km(self) -> float:
        return float(f'{self.length * 0.001:.2f}')
    
    @property
    def pitboxes(self) -> str:
        return self._data.get('pitboxes', '')
    
    @property
    def direction(self) -> str:
        return self._data.get('run', 'clockwise')

    @property
    def outline_file(self) -> Optional[str]:
        return self.find_file('outline')


class Track:

    def __init__(self, folder_path: str = None):
        self.tracks = []
        self.folder_path = folder_path

    def load_layouts(self, folder_path: str = None):
        if folder_path:
            self.folder_path = folder_path
        if not os.path.exists(self.folder_path):
            return
        
        ui_folder = os.path.join(self.folder_path, 'ui')
        ui_file_single = os.path.join(ui_folder, 'ui_track.json')

        if os.path.exists(ui_file_single):
            # This is a single layout track.
            layout = TrackLayout(ui_folder)
            if layout.is_valid():
                self.add_layout(layout)
        else:
            # Multi layout track. Look for and add all layouts
            files = os.listdir(ui_folder)
            for f in files:
                file_path = os.path.join(ui_folder, f)
                if not os.path.isdir(file_path):
                    continue
                layout = TrackLayout(file_path)
                if layout.is_valid():
                    self.add_layout(layout)

    def get_layouts(self) -> list:
        return self.tracks
    
    def add_layout(self, layout: TrackLayout):
        self.tracks.append(layout)

    def random_layout(self) -> TrackLayout:
        if len(self.tracks) == 0:
            return None
        return self.tracks[random.randint(0, len(self.tracks) - 1)]

    def is_valid(self) -> bool:
        return len(self.tracks) > 0


class AsettoCorsaManager:

    def __init__(self):
        self._install_path = None
        self._cars = []
        self._tracks = []
        self._valid = False
        self.set_install_path(r'C:\Program Files (x86)\Steam\steamapps\common\assettocorsa')

    def set_install_path(self, path: str) -> bool:
        self._install_path = path
        if path is None or not os.path.exists(path):
            self._valid = False
            return False
        
        files = os.listdir(self._install_path)
        if 'AssettoCorsa.exe' not in files:
            self._valid = False
            return False
        self._valid = True
        return True
    
    def is_valid(self) -> bool:
        return self._valid
        
    @property
    def _cars_path(self) -> str:
        return os.path.join(self._install_path, 'content', 'cars')

    @property
    def _tracks_path(self) -> str:
        return os.path.join(self._install_path, 'content', 'tracks')

    def refresh_cache(self):
        self._refresh_car_cache()
        self._refresh_track_cache()

    def _refresh_car_cache(self):
        if not self.is_valid():
            return
        self._cars.clear()

        car_folders = os.listdir(self._cars_path)

        for car_folder in car_folders:
            car = Car(os.path.join(self._cars_path, car_folder))

            if car.is_valid():
                self._cars.append(car)

            # car_path = os.path.join(self._cars_path, car_folder)
            # ui_car_file = os.path.join(car_path, 'ui', 'ui_car.json')

            # if not os.path.exists(ui_car_file):
            #     continue
            
            # with open(ui_car_file, encoding='utf8') as file:
            #     car_info = json.load(file, strict=False)
            #     self._cars.append(Car(car_info))


    def _refresh_track_cache(self):
        if not self.is_valid():
            return
        self._tracks.clear()
        track_folders = os.listdir(self._tracks_path)

        for track_folder in track_folders:
            track_path = os.path.join(self._tracks_path, track_folder)
            track_ui_file = os.path.join(track_path, 'ui', 'ui_tack.json')

            track = Track(track_path)
            track.load_layouts()

            if not os.path.exists(track_ui_file):
                # Look for any folders that might contain variations
                internal_files = os.listdir(os.path.join(track_path, 'ui'))

                for folder in internal_files:
                    pass
                    # folder_path = os.path.join(track_path, 'ui', folder)
                    # if not os.path.isdir(folder_path):
                    #     continue
                    
                    # ui_file = os.path.join(folder_path, 'ui_track.json')

                    # if not os.path.exists(ui_file):
                    #     continue

                    # layout = TrackLayout(FileUtil.load_json(ui_file))
                    # track.add_layout(layout)
            else:
                layout = TrackLayout(FileUtil.load_json(track_ui_file))
                track.add_layout(layout)
            
            if track.is_valid():
                self._tracks.append(track)
                
    def get_cars(self) -> list:
        return self._cars
    
    def pick_random_car(self) -> Car:
        if len(self._cars) == 0:
            return None
        return self._cars[random.randint(0, len(self._cars) - 1)]
    
    def pick_random_track(self) -> TrackLayout:
        if len(self._tracks) == 0:
            return None
        
        track: Track = self._tracks[random.randint(0, len(self._tracks) - 1)]
        return track.random_layout()


    def get_tracks(self) -> list:
        return self._tracks


def main():
    game = AsettoCorsaManager()
    game.refresh_cache()
    car = game.pick_random_car()
    track = game.pick_random_track()
    print(f'Car:', car, '-', car.brand, '-', car.random_skin())
    print(f'Track:', track)
    print(f'   Length: {track.length * 0.001:.2f}km')

    # print('\nTracks List')
    # print('-' * 60)
    # track: Track
    # for track in game.get_tracks():
    #     for t in track.tracks:
    #         print(t)

if __name__ == '__main__':
    main()