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

- Need to process chunk-by-chunk
- To do this, think about mapping from output chunks to input chunks
- Run function to calculate a given output chunk in parallel

+++

## Processing categories

+++

### Element-wise operations (e.g., thresholding)

Element-wise operations are those where there's a 1:1 mapping from input chunks to output chunks.

```{mermaid}
    flowchart LR
        input_i --> output_i
        
        output_i["Output chunk i"]
        input_i["Input chunk i"]
```

This makes parallelising very simple - we can write a function that takes an array, and returns an array that has the same shape. For example, to do a simple thresholding operation:

```{code-cell} ipython3
import numpy as np

def threshold(array):
    return np.clip(array, 0, 1)

def apply_elementwise(f, *, input_array: zarr.Array, output_array: zarr.Array) -> None:
    """
    Apply a function to all chunks of a Zarr array.
    """
    
    
```

```{code-cell} ipython3
from data_helpers import load_heart_data, plot_slice

heart_image = load_heart_data(array_type='zarr')
```

### Downsampling

If we're downsampling by a factor of two, then our ouptut array will have half the shape of the input array. In 3D, eight input chunks will map to one output chunk.

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

If we're upsampling by a factor of two, then our ouptut array will have double the shape of the input array. In 3D, each input chunk will map to 8 output chunks.

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
