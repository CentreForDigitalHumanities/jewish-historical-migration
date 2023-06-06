from pathlib import Path
import tempfile
import shutil

from django.test import TestCase

from .pleiades import PleiadesFetcher, PleiadesError


class PleiadesTest(TestCase):
    TESTDATA_FILE = Path(__file__).parent / 'testdata' / 'pleiades.json'

    def test_fetch(self):
        # Create a temporary directory for the external data dir and copy
        # the test data there to the location that PleiadesFetcher expects.
        # We are not testing downloading the file.
        with (
            tempfile.TemporaryDirectory() as datadir,
            self.settings(EXTERNAL_DATA_DIRECTORY=datadir)
        ):
            # Initialize the fetcher and prepare the test data
            fetcher = PleiadesFetcher()
            datafile = shutil.copy(self.TESTDATA_FILE, datadir)
            assert datafile == str(fetcher.pleiades_path)
            # Test fetching an existing ID
            place = fetcher.fetch(48210386)
            self.assertTrue('reprPoint' in place)
            # Test another one
            place = fetcher.fetch(48210385)
            self.assertTrue('reprPoint' in place)
            # Test if nonexisting ID raises error
            with self.assertRaises(PleiadesError):
                fetcher.fetch(5)
