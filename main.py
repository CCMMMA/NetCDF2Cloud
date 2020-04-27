import json

import prettyprint as pp

from netCDF4 import Dataset
from os import mkdir, path, remove
from NetCDF2JSON import NetCDF2JSON

from sys import exit


def calc_divisors(num):
    result = []
    for x in range(1, num + 1):
        if num % x == 0:
            result.append(x)
    return result


if __name__ == "__main__":
    #filename = "http://data.meteo.uniparthenope.it/opendap/opendap/rms3" \
    #           "/d03/history/2020/03/29/rms3_d03_20200329Z1200.nc"

    #filename = "http://data.meteo.uniparthenope.it/opendap/opendap/wrf5" \
    #            "/d01/archive/2020/03/29/wrf5_d01_20200329Z1200.nc"

    #filename = "http://data.meteo.uniparthenope.it/opendap/opendap/ww33" \
    #           "/d01/archive/2020/03/29/ww33_d01_20200329Z1200.nc"

    filename = "http://data.meteo.uniparthenope.it/opendap/opendap/rms3" \
               "/d03/archive/2020/03/29/rms3_d03_20200329Z1200.nc"

    #netCDF2JSON = NetCDF2JSON(filename)

    #item = netCDF2JSON.as_json()
    #print(json.dumps(item))

    rootgrp = Dataset(filename)

    dimensions_divisors = {}
    for dimension in rootgrp.dimensions.values():
        dimensions_divisors[str(dimension.name)] = calc_divisors(len(dimension))

    print (json.dumps(dimensions_divisors, indent=2, sort_keys=True))

    #center = 16384
    center = 8192
    #center = 4096
    #center = 2048
    time = 1
    level = 1
    dtype = 4
    sizes = []
    #X_DIM = "xi_rho"
    #Y_DIM = "eta_rho"
    X_DIM="longitude"
    Y_DIM="latitude"

    print(Y_DIM)
    print(dimensions_divisors[Y_DIM])
    print("--------")
    print(X_DIM)
    print(dimensions_divisors[X_DIM])
    print("--------")

    y_size = dimensions_divisors[Y_DIM][-1]
    x_size = dimensions_divisors[X_DIM][-1]
    xy_size = y_size * x_size * dtype
    print(y_size,x_size, xy_size)
    print("-------")
    for j in range(0, len(dimensions_divisors[Y_DIM])):
        new = []
        m = dimensions_divisors[Y_DIM][j]
        for i in range(0, len(dimensions_divisors[X_DIM])):

            n = dimensions_divisors[X_DIM][i]
            q = xy_size / (n*m)
            f=abs(center-q)
            print(m, n, q, f)

            new.append(f)

        sizes.append(new)
    print(sizes)

    minVal = 1E37
    j0 = -1
    i0 = -1
    for j in range(0, len(sizes)):
        for i in range(0, len(sizes[j])):
            print (sizes[j][i], minVal)
            if sizes[j][i] < minVal:
                minVal = sizes[j][i]
                j0 = j
                i0 = i
    print(minVal)
    print(j0, i0, dimensions_divisors[Y_DIM][j0], dimensions_divisors[X_DIM][i0])
    exit(0)

    variables = []
    for variable in rootgrp.variables.values():
        attributes = []
        for attribute in variable.ncattrs():
            attributes.append({"name": str(attribute), "value": str(variable.getncattr(attribute))})


        shapes = []
        for shape in variable.shape:
            shapes.append(shape)



        base_path = "data/"+path.splitext(path.basename(filename))[0]
        if not path.exists(base_path):
            mkdir(base_path)

        variable_file_name=base_path+"/"+variable.name+".nc"

        if path.exists(variable_file_name):
            remove(variable_file_name)

        dataset = Dataset(variable_file_name, "w", format="NETCDF4")

        dimension_names = ()
        for dimension_name in variable.dimensions:
            dimension_names = dimension_names + (dimension_name, )

        dimensions = {}
        for dimension in rootgrp.dimensions.values():
            if str(dimension.name) in dimension_names:
                print(dimension.name, dimension.size)
                dim = dataset.createDimension(str(dimension.name), dimension.size)
                dimensions[dimension.name] = dim

        print({
            "name": str(variable.name),
            "dtype": str(variable.dtype),
            "ndim": variable.ndim,
            "shape": shapes,
            "dimensions": dimension_names,
            "attributes": attributes
        })

        temp = dataset.createVariable(variable_file_name, variable.dtype, dimension_names)
        temp[:] = rootgrp.variables[variable.name][:]
        dataset.close()
