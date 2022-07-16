import os
import requests
import time
import zipfile
import re

from etl_utils import get_logger, write_file

timestamp = lambda: int(time.time())

Map = lambda fn, iter: list(map(fn, iter))
logger = get_logger(log_level='DEBUG')
product_name = lambda name: 'output/901E.{}.{}'.format(str(timestamp()),name)
manifest_filename = product_name('manifest.csv')


# Get environment variables
MANIFEST_ONLY = os.getenv('MANIFEST_ONLY')

def download(url, mask=None):
    output = None
    try:
        response = requests.get(url)
        if mask == None:
            output = response.content
        else:
            matches = re.findall(mask, response.text)
            output = list(set(matches))
    except Exception as e:
        logger.error('download failure', extra={
            "exception": str(e),
            "url": url,
            "timestamp": timestamp(),
        })
    return output

def download_manifest():
    url = 'https://www2.census.gov/geo/tiger/TIGER2020/'
    mask = r'alt=\"\[DIR\]\"></td><td><a href=\"([a-zA-Z0-9]+)\/\">([a-zA-Z0-9]+)\/<\/a><\/td>'
    records = download(url, mask)

    catalog = {}
    for record in records:
        mask = r'<a href=\"([\S]+\.zip)\">'
        archives = download('{}{}/'.format(url,record[1]), mask)
        catalog[record[1]] = archives if archives is not None else None

    survey = {}
    for key, files in catalog.items():
        for file in files:
            survey['{}-{}'.format(key, file)] = '{}{}/{}'.format(url,key,file)

    manifest = Map(lambda entry: '{},{}'.format(entry[0], entry[1]), survey.items())
    write_file(manifest_filename, '\n'.join(manifest))


def get_file_bytes_from_archive(archive, filename):
    f=archive.open(filename)
    contents=f.read()
    f.close()
    return contents

def load_manifest():
    f = open(manifest_filename, "r")
    output = f.readlines()
    f.close()

    def fn(line):
        chunks = line.replace('\n', '').split(',')
        return {'filename': chunks[0], 'url': chunks[1]}
        
    return Map(fn, output)


def write_data(filename, bytes):
    f = open(filename, "wb")
    f.write(bytes)
    f.close()


def process_manifest(records):
    logger.info('processing manifest', extra={
        "timestamp": timestamp(),
    })


    for record in records:
        filename = record['filename']
        url = record['url']

        logger.info('downloading zip file', extra={
            "timestamp": timestamp(),
            "zip_filename": filename
        })
        
        zip_file_binary = download(url)
        if zip_file_binary is not None:
            temp_filename = product_name(filename)

            write_data(temp_filename, zip_file_binary)

            # logger.info('surveying zip file for [.shp] files', extra={
            #     "timestamp": timestamp(),
            #     "zip_filename": filename
            # })

            # zip=zipfile.ZipFile(temp_filename)
            # for shapefile in filter(lambda name: name.endswith('.shp'), zip.namelist()):
            #     logger.info('extracting [.shp] file from zip file', extra={
            #         "timestamp": timestamp(),
            #         "zip_filename": filename,
            #         "shapefile": shapefile,
            #     })
            #     data = get_file_bytes_from_archive(zip, shapefile)
            #     shp_filename = '{}-{}'.format(filename,shapefile)
            #     write_data(product_name(shp_filename), data)

            # os.remove(temp_filename)
        else:
            logger.error('downloading zip file failed', extra={
                "timestamp": timestamp(),
                "zip_filename": filename
            })



if MANIFEST_ONLY is None and os.path.exists(manifest_filename):
    logger.info('using existing manifest', extra={
        "timestamp": timestamp(),
    })
else:
    logger.info('creating manifest', extra={
        "timestamp": timestamp(),
    })
    download_manifest()

if MANIFEST_ONLY is None:
    process_manifest(load_manifest())
