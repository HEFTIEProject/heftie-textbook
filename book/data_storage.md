---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---


# Data formats

This chapter gives a brief overview of how data is stored on a computer.
This is intended as a quick primer to motivate the chunked next generation file formats that the rest of this book talks about.

## Storing images

All data in a computer is stored in binary - a string of 0s and 1s.
One binary digit is called a *bit*.
These are almost always grouped together in batches of 8 bits, which together make a single *byte*.

If we have $n$ bits, then we can store $2^{n}$ different numbers.
So for one byte (8 bits) we can store $2^{8}$ = 256 different numbers, or for two bytes (16 bits) we can store $2^{16}$ = 65,536 different numbers.

For simplicity in this book we'll focus on grayscale, or single-channel images.
These are images where each pixel stores a single value.
Colour, or multi-channel images store multiple values per pixel (e.g., values for the red, green, and blue (RGB) components), and the same principles generally apply, just across multiple channels.


That's a lot of words without a single image yet!
Lets generate a random 16-bit 4 x 4 image as an example to take us through the rest of this chapter

```{code-cell}
import matplotlib.pyplot as plt
import numpy as np

image = np.random.randint(low=0, high=2**16, size=(4, 4), dtype=np.uint16)
print(image)

fig, ax = plt.subplots()
ax.imshow(image, cmap="Grays", vmin=0, vmax=2**16);
```

We can also look at what this looks like in computer memory:
```{code-cell}
image_bytes = image.tobytes()
print(image_bytes)
```

## Data compression
- Brief overview of lossless/lossy compression
- Include read/write benchmarks
- Talk about cost of read/write compression
