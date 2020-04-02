import json

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
    filename = "http://data.meteo.uniparthenope.it/opendap/opendap/rms3" \
               "/d03/history/2020/03/29/rms3_d03_20200329Z1200.nc"

    #netCDF2JSON = NetCDF2JSON(filename)

    #item = netCDF2JSON.as_json()
    #print(json.dumps(item))

    rootgrp = Dataset(filename)

    dimensions_divisors = {}
    for dimension in rootgrp.dimensions.values():
        dimensions_divisors[str(dimension.name)] = calc_divisors(len(dimension))

    centerM = 8.192
    time = 1
    level = 1
    dtype = 4
    sizes = []
    X_DIM = "xi_rho"
    Y_DIM = "eta_rho"
    print(dimensions_divisors[Y_DIM], dimensions_divisors[X_DIM])
    for j in range(1, len(dimensions_divisors[Y_DIM])-1):
        new = []
        for i in range(1, len(dimensions_divisors[X_DIM])-1):
            
            new.append(abs(centerM-float(
                dtype*time*level *
                (dimensions_divisors[Y_DIM][-1]/dimensions_divisors[Y_DIM][j]) *
                (dimensions_divisors[X_DIM][-1]/dimensions_divisors[X_DIM][i])
            )/1024000.0))

        sizes.append(new)
    print(sizes)

    minVal = 1E37
    j0 = -1
    i0 = -1
    for j in range(0, len(sizes)):
        for i in range(1, len(sizes[j])):
            if sizes[j][i] < minVal:
                minVal = sizes[j][i]
                j0 = j+1
                i0 = i+1
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
