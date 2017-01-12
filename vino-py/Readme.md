Python API for Vino
===================

Vino-py is the python version of the (Vino API](https://sourcesup.renater.fr/wiki/vino/apispecifications). The sources are located in the vino-py subdirectory of the project.

Environment Installation
------------------------

The best way is to use virtualenv for working with python dependencies:
```
# init
virtualenv env
# activation - run "deactivate" for closing
source env/bin/activate
```

Then, you can install required dependencies with:
` env/bin/pip install -r pip-requires.txt`

On recent version of ubuntu and hdf5 library, you should specify the hdf5 path like `HDF5_DIR=/usr/lib/x86_64-linux-gnu/hdf5/serial/ pip install h5py`

Usage
-----

### Input/Ouput

```
from FileFormatLoader import Loader
loader = Loader()
# Load from a file in a supported format
kernel = loader.load('../samples/2D.txt')

from hdf5common import HDF5Manager
# Save in HDF5 Vino format
HDF5Manager.writeKernel(kernel, '2D.h5')
```
