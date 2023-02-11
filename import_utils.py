import zipfile, urllib
from io import BytesIO
import json
from preprocessing import preprocess_data

rows = []
max_file = 5
filtering_string = "2019 Q4"
info_download = json.load(open("info_download.json"))


def get_multiple_files(info_download:dict, max_file:int, filtering_string: str) -> list[dict]:
    for info in info_download['results']['drug']['event']['partitions']:
        if filtering_string in info['display_name'] and max_file != 0:
            max_file -= 1
            url = info['file']
            resp = urllib.request.urlopen(url)
            myzip = zipfile.ZipFile(BytesIO(resp.read()))
            with myzip.open(myzip.namelist()[0]) as f:
                data = f.read()
                data_json = json.loads(data.decode('utf-8'))
            rows.extend(preprocess_data(data_json))
    return rows
