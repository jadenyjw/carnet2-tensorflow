import numpy as np
import tables

# Generate some data
x = np.random.random(([176, 144], [1, 2]))

# Store "x" in a chunked array...
f = tables.openFile('test.hdf', 'w')
atom = tables.Atom.from_dtype(x.dtype)
ds = f.createCArray(f.root, 'somename', atom, x.shape)
ds[:] = x
f.close()
