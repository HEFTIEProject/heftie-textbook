---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.4
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Creating chunked datasets

```{code-cell} ipython3
import matplotlib.pyplot as plt
import numpy as np
from rich import print

from data_helpers import load_heart_data
```

This chapter gives a brief overview of to create an OME-Zarr dataset.

## Creating Zarr datasets

```{code-cell} ipython3
heart_image = load_heart_data(array_type='numpy')
```

## Creating OME-Zarr datasets

[OME-Zarr](https://ngff.openmicroscopy.org/specifications/index.html) is a specification for storing bio-imaging data.
OME-Zarr data consists of two components:

1. Data stored in the Zarr file format
2. Metadata used to interpret the data

The OME-Zarr specification contains details for storing a number of different types of data.
For storing 3D imaging data we will use the multiscale specification.

## Writing OME-Zarr datasets

There are a number of different Python libraries available for writing OME-Zarr multiscale datasets.
A list of them at time of writing, along with their pros and cons is available in the [appendices](appendices.md).
For this textbook we'll be using [ngff-zarr](https://github.com/thewtex/ngff-zarr), which advertises itself as a "lean and kind Open Microscopy Environment (OME) Next Generation File Format (NGFF) Zarr implementation".

Lets start by generating some data to convert to OME-Zarr.

```{code-cell} ipython3
import numpy as np
from rich import print

image = np.random.randint(low=0, high=2**16, size=(128, 128, 128), dtype=np.uint16)
```

At this point we just have a single 3D image array, stored as a numpy array in the memory of our computer.

To save it as an OME-Zarr Image dataset, we will use the `ngff-zarr` library.
The first step is to convert our numpy array to a NgffImage:

```{code-cell} ipython3
import ngff_zarr

ngff_image = ngff_zarr.to_ngff_image(image)
print(ngff_image)
```

Where our numpy array just contained data values, the NgffImage object contains this array alongside some mnew metadata including:

- The dataset name
- The axis names
- The axis units
- Coordinate transformations

Because we didn't explicitly specify any of this metadata when we created the NgffImage object it was set to default values.
Lets try that again, but set some of the metadata to values more appropriate for our image:

```{code-cell} ipython3
ngff_image = ngff_zarr.to_ngff_image(
    image,
    name="my_image",
    dims=("z", "y", "x"),
    scale={"x": 4, "y": 4, "z": 4},
    axes_units="um"
)
print(ngff_image)
```

Much better!
In this first step, we have taken our data array that had no metadata attached, and made it into a NgffIamge object that contains the correct metadata.
At this point no data has been copied or converted.

The second step in creating an OME-Zarr image is to convert the NgffImage object to a multiscales object.
This stage again does not copy any data, but sets up a pipeline for creating several downsampled levels of our origina image array.

```{code-cell} ipython3
multiscales = ngff_zarr.to_multiscales(
    ngff_image,
    scale_factors=4,
    chunks=64
)
print(multiscales)
```

We can see that this new Multiscales object now contains several NgffImage objects.
At the top is the image at its original full resolution (128$^{3}$), and then successively downsampled versions.

The third and final step is to save this Multiscales object to a folder.

```{code-cell} ipython3
ngff_zarr.to_ngff_zarr('data/heftie_image.ome.zarr', multiscales, version='0.4', overwrite=True)
```

This code computes all the multiscale images and saves them to an OME-Zarr group on the local filesystem.

## Validating data
