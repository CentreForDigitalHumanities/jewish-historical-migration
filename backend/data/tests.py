from pathlib import Path
from os.path import join
import tempfile
import shutil

from django.test import TestCase

from .pleiades import PleiadesFetcher, PleiadesError
from .models import import_dataset, Record
from .utils import to_decimal

TESTDATA_LOCATION = join(Path(__file__).parent, 'testdata')

class PleiadesTest(TestCase):
    TESTDATA_FILE =  join(TESTDATA_LOCATION, 'pleiades.json')

    def test_fetch(self):
        # Create a temporary directory for the external data dir and copy
        # the test data there to the location that PleiadesFetcher expects.
        # We are not testing downloading the file.
        with tempfile.TemporaryDirectory() as datadir:
            with self.settings(EXTERNAL_DATA_DIRECTORY=datadir):
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


class RecordTest(TestCase):
    TESTDATA_FILE = join(TESTDATA_LOCATION, 'SampleData.xlsx')

    def test_data_import(self):
        import_dataset(self.TESTDATA_FILE)
        assert Record.objects.count() == 3


class DecimalConversionTest(TestCase):

    def test_conversion(self):
        test_cases = [
            "39˚39' 4''N",
            "39˚ 39' 4''N",
            "39˚ 15' N",
            "39˚ 39' 4'' N",
            "41.779˚N",
            "39˚ 10; N"
        ]
        for t in test_cases:
            assert to_decimal(t)

