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

# Parallel processing

+++

In this chapter we'll look at how to efficiently process Zarr arrays.
We'll do it with a focus on scalability.
Although the examples here below operate on small arrays, the theory and techniques described will scale to processing large datasets and machines with more resources (e.g., number of processing cores).

When we process an array, we are transforming it in some way and creating a new array - think of this as a mapping from one array to another.
Because a Zarr array is split into chunks, we can split up this mapping into many smaller jobs.
When writing a Zarr array whole chunks are compressed at written in one go, so it makes sense to break down the task into a mapping a mapping from the input array to each individual output chunk, and then create one job for each output chunk.
This will allow us to compute each output chunk independently, which has two large benefits:

- For each job we only need to load the data into memory needed to compute a single output chunk
- We can parallelise the computation of output chunks, speeding up the whole process.

To start with lets look at the simplest possible mapping from input chunks to output chunks - where the output array has the same shape and chunk size as the input array, and each output chunk depends only on the corresponding input chunk.

+++

## Element-wise operations

Element-wise operations are those where there's an exact one-to-one mapping from input chunks to output chunks.

```{mermaid}
    flowchart LR
        input_i --> output_i

        output_i["Chunk i, j, k"]
        input_i["Chunk i, j k"]
```

This makes parallelising very simple - we can write a function that takes one chunk (an array), and returns another chunk (another array) that has the same shape.

Before we get into this we'll setup a few helper functions.
First, a function that generates slices for every chunk in a Zarr array:

```{code-cell} ipython3
import itertools
from typing import Generator

import zarr


def all_chunk_slices(array: zarr.Array) -> Generator[tuple[slice, ...], None, None]:
    """
    Generate slices that represent all chunks in a Zarr Array.
    """
    ndim = len(array.shape)
    indices = [range(0, array.shape[i], array.chunks[i]) for i in range(ndim)]
    chunk_corners = itertools.product(*indices)
    yield from (
        tuple(
            slice(corner[i], min(corner[i] + array.chunks[i], array.shape[i]))
            for i in range(ndim)
        )
        for corner in chunk_corners
    )
```

```{code-cell} ipython3
from data_helpers import load_heart_data

heart_image = load_heart_data(array_type='zarr')
print(f"Array shape: {heart_image.shape}")
print(f"Chunk shape: {heart_image.chunks}")
print("Chunk slices:")
for slc in all_chunk_slices(heart_image):
    print(slc)
```

Second, a function to copy a slice of data from one array to another:

```{code-cell} ipython3
import itertools
from collections.abc import Callable
from typing import Any

import joblib
import numpy as np
import numpy.typing as npt
import zarr


def copy_slice(input_array: zarr.Array, output_array: zarr.Array, slc: slice) -> None:
    """
    Copy a specific slice of data from one array to another.
    """
    print(f"Copying slice {slc}...")
    output_array[slc] = input_array[slc]
```

And third, a function to double check two Zarr arrays have the same shape and chunks:

```{code-cell} ipython3
def check_same_shape(array_1: zarr.Array, array_2: zarr.Array) -> None:
    if input_array.shape != output_array.shape:
        raise ValueError(
            f"Input shape ({input_array.shape}) != output shape {output_array.shape}"
        )
    if input_array.chunks != output_array.chunks:
        raise ValueError(
            f"Input chunk ({input_array.chunks}) != output chunks {output_array.chunks}"
        )

```

```{code-cell} ipython3
def elementwise_jobs(
    f: Callable[..., npt.NDArray[Any]],
    *,
    input_array: zarr.Array,
    output_array: zarr.Array,
) -> list[joblib.delayed]:
    """
    Apply a function to all chunks of a Zarr array.
    """
    check_same_shape(input_array, output_array)
    return [
        joblib.delayed(copy_slice)(input_array, output_array, slc)
        for slc in all_chunk_slices(output_array)
    ]


def threshold(array):
    return np.clip(array, 0, 1)
```

```{code-cell} ipython3
from data_helpers import plot_slice
import matplotlib.pyplot as plt

heart_image = load_heart_data(array_type='zarr')
thresholded_image = zarr.empty_like(heart_image)

fig, axs = plt.subplots(ncols=2)
plot_slice(heart_image, z_idx=65, ax=axs[0])
plot_slice(thresholded_image, z_idx=65, ax=axs[1])
```

```{code-cell} ipython3
thresholded_image = zarr.empty_like(heart_image)
jobs = elementwise_jobs(threshold, input_array=heart_image, output_array=thresholded_image)
print(f"Number of jobs: {len(jobs)}")
print(jobs[0])
```

```{code-cell} ipython3
for job, args, kwargs in jobs:
    job(*args, **kwargs)
```

```{code-cell} ipython3
fig, axs = plt.subplots(ncols=2)
plot_slice(heart_image, z_idx=65, ax=axs[0])
plot_slice(thresholded_image, z_idx=65, ax=axs[1])
```

### Downsampling

If we're downsampling by a factor of two, then our output array will have half the shape of the input array. In 3D, eight input chunks will map to one output chunk.

```{mermaid}
    flowchart LR
        input_i --> output_i
        input_i --> output_i
        input_i --> output_i
        input_i --> output_i
        input_i --> output_i
        input_i --> output_i
        input_i --> output_i
        input_i --> output_i

        output_i["Output chunk i, j, k"]
        input_i["Input chunk 2i, 2j, 2k"]
```

+++

### Upsampling

If we're upsampling by a factor of two, then our output array will have double the shape of the input array. In 3D, each input chunk will map to 8 output chunks.

```{mermaid}
    flowchart LR
        input_i --> output_i
        input_i --> output_i
        input_i --> output_i
        input_i --> output_i
        input_i --> output_i
        input_i --> output_i
        input_i --> output_i
        input_i --> output_i

        input_i["Input chunk 2i, 2j, 2k"]
        output_i["Output chunk i, j, k"]
```

+++

### Convolution

```{code-cell} ipython3

```
