from pathlib import Path
import requests
import gzip
import ijson

from django.conf import settings


class PleiadesError(RuntimeError):
    pass


class PleiadesFetcher:
    PLEIADES_URL = 'https://atlantides.org/downloads/pleiades/json/' \
        'pleiades-places-latest.json.gz'
    _pleiades_data: dict = None
    pleiades_path: Path

    def __init__(self):
        try:
            self.pleiades_path = Path(settings.EXTERNAL_DATA_DIRECTORY) / \
                'pleiades.json'
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

    def read_data(self) -> None:
        '''Read Pleiades data into memory to allow efficient access. Download
        data if necessary.'''
        if not self.pleiades_path.exists():
            # Download if the file does not yet exist. In the future, perhaps
            # check if the data may need an update (the JSON file is updated
            # daily).
            self.download_dump()
        print('Reading Pleiades data into memory...')
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
        except (OSError, ijson.JSONERROR) as err:
            raise PleiadesError(
                'Error while reading Pleiades file: {}'.format(err)
            )

    def reset(self) -> None:
        '''Reset this object so that memory is freed from all Pleiades data'''
        self._pleiades_data = None

    def fetch(self, pleiades_id: int) -> dict:
        '''Fetch Pleiades data from one id. Download latest Pleiades JSON
        dump first if necessary.'''
        if self._pleiades_data is None:
            self.read_data()
        try:
            data = self._pleiades_data[pleiades_id]
        except KeyError:
            raise PleiadesError(
                'Pleiades key {} not found'.format(pleiades_id)
            )
        return data


pleiades_fetcher = PleiadesFetcher()
