import json

from NetCDF2JSON import NetCDF2JSON

if __name__ == "__main__":
    filename = "http://data.meteo.uniparthenope.it/opendap/opendap/wrf5" \
               "/d01/history/2020/03/29/wrf5_d01_20200329Z1200.nc"

    netCDF2JSON=NetCDF2JSON(filename)

    item = netCDF2JSON.as_json()
    print(json.dumps(item))
