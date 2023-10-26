from pathlib import Path
from typing import Optional
import requests
import gzip
import ijson
import pickle

from django.conf import settings


class PleiadesError(RuntimeError):
    pass


class PleiadesFetcher:
    PLEIADES_URL = 'https://atlantides.org/downloads/pleiades/json/' \
        'pleiades-places-latest.json.gz'
    _pleiades_data: Optional[dict] = None
    pleiades_path: Path

    def __init__(self):
        try:
            self.pleiades_path = Path(settings.EXTERNAL_DATA_DIRECTORY) / \
                'pleiades.json'
            self.pleiades_pickle_path = \
                Path(settings.EXTERNAL_DATA_DIRECTORY) / 'pleiades.pickle'
        except AttributeError:
            raise PleiadesError(
                'EXTERNAL_DATA_DIRECTORY setting must be set in settings.py'
            )

    def download_dump(self) -> None:
        '''Download the latest version of the Pleiades dump and put it in
        the EXTERNAL_DATA_DIRECTORY directory of settings.py'''
        try:
            self.pleiades_path.parent.mkdir(exist_ok=True, parents=True)
        except OSError as err:
            raise PleiadesError(
                'Could not create external data directory: {}'.format(err)
            )
        print(
            'Downloading latest Pleiades data from {}...'
            .format(self.PLEIADES_URL)
        )
        try:
            request = requests.get(self.PLEIADES_URL, allow_redirects=True)
        except requests.RequestException as err:
            raise PleiadesError(
                'Error while downloading Pleiades file: {}'.format(err)
            )
        try:
            with open(self.pleiades_path, 'wb') as f:
                f.write(gzip.decompress(request.content))
        except OSError as err:
            # This also catches gzip.BadGzipFile
            raise PleiadesError(
                'Error while decompressing Pleiades file: {}'.format(err)
            )

    def pickle_data(self) -> None:
        '''Read Pleiades data into memory to allow efficient access. Download
        data if necessary. Save as Pickle file.'''
        if not self.pleiades_path.exists():
            # Download if the file does not yet exist. In the future, perhaps
            # check if the data may need an update (the JSON file is updated
            # daily).
            self.download_dump()
        print('Converting all Pleiades data...')
        try:
            with open(self.pleiades_path, 'rb') as f:  # IJSON needs bin data
                self._pleiades_data = {}
                places = ijson.items(f, '@graph.item')
                for place in places:
                    pl_id = int(place['id'])
                    # Only retrieve the data we need, because otherwise
                    # we would need a lot of memory
                    self._pleiades_data[pl_id] = {
                        'reprPoint': place['reprPoint']
                    }
            with open(self.pleiades_pickle_path, 'wb') as f:
                pickle.dump(self._pleiades_data, f)
        except (OSError, ijson.JSONERROR) as err:
            raise PleiadesError(
                'Error while converting Pleiades file: {}'.format(err)
            )

    def get_data(self) -> None:
        '''Read Pleiades pickle file into memory; create it if it does not yet
        exist'''
        if self.pleiades_pickle_path.exists():
            with open(self.pleiades_pickle_path, 'rb') as f:
                self._pleiades_data = pickle.load(f)
        else:
            self.pickle_data()

    def reset(self) -> None:
        '''Reset this object so that memory is freed from all Pleiades data'''
        self._pleiades_data = None

    def fetch(self, pleiades_id: int) -> Optional[dict]:
        '''Fetch Pleiades data from one id. Download latest Pleiades JSON
        dump first if necessary. Return None if not found.'''
        if self._pleiades_data is None:
            self.get_data()
        assert self._pleiades_data is not None
        try:
            data = self._pleiades_data[pleiades_id]
        except KeyError:
            return None
        return data


pleiades_fetcher = PleiadesFetcher()
