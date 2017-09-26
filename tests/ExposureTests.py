import io
import os
import inspect
import sys
import unittest
import shutil
import tarfile
import time

from flask import json
from random import randint

TEST_DIRECTORY = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
TEST_DATA_DIRECTORY = os.path.abspath(os.path.join(TEST_DIRECTORY, 'data'))
LIB_PATH = os.path.abspath(os.path.join(TEST_DIRECTORY, '..', 'src'))
sys.path.append(LIB_PATH)

from server import app
from common import data

class Test_ExposureTests(unittest.TestCase):
    ''' 
    Exposure API tests
    '''

    def touch(self, path):
        with open(path, 'a'):
            os.utime(path, None)

    def create_file(self, path, size_in_bytes):
        with open(path, "wb") as outfile:
            # Write 1 MB of random data
            for x in xrange(size_in_bytes):
                outfile.write(chr(randint(0,255)))

    def clean_directories(self):
        if os.path.exists(app.INPUTS_DATA_DIRECTORY):
            shutil.rmtree(app.INPUTS_DATA_DIRECTORY)
        os.makedirs(app.INPUTS_DATA_DIRECTORY)
        
        if os.path.exists(TEST_DATA_DIRECTORY):
            shutil.rmtree(TEST_DATA_DIRECTORY)
        os.makedirs(TEST_DATA_DIRECTORY)

    def setUp(self):
        app.DO_GZIP_RESPONSE = False
        INPUTS_DATA_DIRECTORY = os.path.join(TEST_DIRECTORY, 'exposure_data')
        app.INPUTS_DATA_DIRECTORY = INPUTS_DATA_DIRECTORY
        app.APP.config['TESTING'] = True
        self.app = app.APP.test_client()

    def test_get_exposure_summary_1(self):
        self.clean_directories()
        self.create_file(os.path.join(app.INPUTS_DATA_DIRECTORY, 'test1.tar'), 100)
        self.create_file(os.path.join(app.INPUTS_DATA_DIRECTORY, 'test2.tar'), 200)
        self.create_file(os.path.join(app.INPUTS_DATA_DIRECTORY, 'test3.tar'), 300)
        self.create_file(os.path.join(app.INPUTS_DATA_DIRECTORY, 'test4.tar'), 400)
        response = self.app.get("/exposure_summary")
        assert response._status_code == 200
        exposures = json.loads(response.data.decode('utf-8'))['exposures']
        assert len(exposures) == 4
        assert sum(1 for exposure in exposures if exposure['location'] == 'test1') == 1
        assert sum(1 for exposure in exposures if exposure['location'] == 'test2') == 1
        assert sum(1 for exposure in exposures if exposure['location'] == 'test3') == 1
        assert sum(1 for exposure in exposures if exposure['location'] == 'test4') == 1
        assert sum(1 for exposure in exposures if exposure['size'] == 100) == 1
        assert sum(1 for exposure in exposures if exposure['size'] == 200) == 1
        assert sum(1 for exposure in exposures if exposure['size'] == 300) == 1
        assert sum(1 for exposure in exposures if exposure['size'] == 400) == 1

    def test_get_exposure_summary_by_location_1(self):
        self.clean_directories()
        self.create_file(os.path.join(app.INPUTS_DATA_DIRECTORY, 'test1.tar'), 100)
        response = self.app.get("/exposure_summary/test1")
        assert response._status_code == 200
        exposures = json.loads(response.data.decode('utf-8'))['exposures']
        assert len(exposures) == 1
        assert sum(1 for exposure in exposures if exposure['location'] == 'test1') == 1
        assert sum(1 for exposure in exposures if exposure['size'] == 100) == 1

    def test_get_exposure_by_location_1(self):
        self.clean_directories()
        self.create_file(os.path.join(app.INPUTS_DATA_DIRECTORY, 'test1.tar'), 100)
        response = self.app.get("/exposure/test1")
        
        assert response._status_code == 200
  
        exposure_file =  "temp_exposure_data" 
        with open(exposure_file, "wb") as outfile:
            outfile.write(response.data) 
        assert(os.path.exists(exposure_file))
        assert(os.path.getsize(exposure_file) == 100)

    def test_get_exposure_summary_by_location_2(self):
        self.clean_directories()
        self.touch(os.path.join(app.INPUTS_DATA_DIRECTORY, 'test1.tar'))
        response = self.app.get("/exposure_summary/test2")
        assert response._status_code == 404

    def test_get_exposure_by_location_2(self):
        self.clean_directories()
        self.touch(os.path.join(app.INPUTS_DATA_DIRECTORY, 'test1.tar'))
        response = self.app.get("/exposure/test2")
        assert response._status_code == 404

    def test_post_exposure_1(self):
        self.clean_directories()
        filepath = os.path.join(TEST_DIRECTORY, 'post1.tar')
        self.touch(filepath)
        with io.open(filepath, 'rb') as file_to_upload:
            response = self.app.post(
                "/exposure", 
                data = {
                    'file': (file_to_upload, filepath),
                }, 
                content_type='multipart/form-data')
        assert response._status_code == 200
        exposures = json.loads(response.data.decode('utf-8'))['exposures']
        assert len(exposures) == 1

    def test_delete_exposure_1(self):
        self.clean_directories()
        filepath1 = os.path.join(app.INPUTS_DATA_DIRECTORY, 'test1.tar')
        filepath2 = os.path.join(app.INPUTS_DATA_DIRECTORY, 'test2.tar')
        self.touch(filepath1)
        self.touch(filepath2)
        response = self.app.delete("/exposure")
        assert response._status_code == 200
        assert not os.path.exists(filepath1)
        assert not os.path.exists(filepath2)

    def test_delete_exposure_by_location_1(self):
        self.clean_directories()
        filepath1 = os.path.join(app.INPUTS_DATA_DIRECTORY, 'test1.tar')
        filepath2 = os.path.join(app.INPUTS_DATA_DIRECTORY, 'test2.tar')
        self.touch(filepath1)
        self.touch(filepath2)
        response = self.app.delete("/exposure/test1")
        assert response._status_code == 200
        assert not os.path.exists(filepath1)
        assert os.path.exists(filepath2)

    def test_exposure_roundtrip_1(self):
        self.clean_directories()
        filepath = os.path.join(TEST_DIRECTORY, 'post1.tar')
        self.touch(filepath)
        with io.open(filepath, 'rb') as file_to_upload:
            response = self.app.post(
                "/exposure", 
                data = {
                    'file': (file_to_upload, filepath),
                }, 
                content_type='multipart/form-data')
        assert response._status_code == 200
        exposures = json.loads(response.data.decode('utf-8'))['exposures']
        assert len(exposures) == 1
        location = exposures[0]['location']
        response = self.app.get("/exposure_summary/" + location)
        assert response._status_code == 200
        exposures = json.loads(response.data.decode('utf-8'))['exposures']
        assert len(exposures) == 1
        assert sum(1 for exposure in exposures if exposure['location'] == location) == 1
        response = self.app.delete("/exposure/" + location)
        assert response._status_code == 200
        response = self.app.get("/exposure_summary/" + location)
        assert response._status_code == 404

    def test_check_exposure_1(self):
        self.clean_directories()
        os.chdir(TEST_DATA_DIRECTORY)
        filepath = 'items.bin'
        self.touch(filepath)
        filepath = 'coverages.bin'
        self.touch(filepath)
        filepath = 'summaryxref.bin'
        self.touch(filepath)
        filepath = 'fm_programme.bin'
        self.touch(filepath)
        filepath = 'fm_policytc.bin'
        self.touch(filepath)
        filepath = 'fm_profile.bin'
        self.touch(filepath)
        filepath = 'fm_summaryxref.bin'
        self.touch(filepath)
        tarpath = 'exposure.tar'
        tar = tarfile.open(tarpath, 'w')
        for name in [
            'items.bin', 'coverages.bin', 'summaryxref.bin',
            'fm_programme.bin', 'fm_policytc.bin', 'fm_profile.bin', 'fm_summaryxref.bin']:
            tar.add(name)
        tar.close()
        os.chdir(TEST_DIRECTORY)
        assert(app.validate_exposure_tar(
            os.path.join(TEST_DATA_DIRECTORY, tarpath)))

if __name__ == '__main__':
    unittest.main()