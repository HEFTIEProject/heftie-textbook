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

# Data formats

This chapter gives a brief overview of how data is stored on a computer.
This is intended as a quick primer to motivate the chunked next generation file formats that the rest of this book talks about.

For a more in-depth discussion of

## Storing data

All data in a computer is stored in binary - a string of 0s and 1s.
One binary digit is called a _bit_.
These are almost always grouped together in batches of 8 bits, which together make a single _byte_.

If we have $n$ bits, then we can store $2^{n}$ different numbers.
So for one byte (8 bits) we can store $2^{8}$ = 256 different numbers, or for two bytes (16 bits) we can store $2^{16}$ = 65,536 different numbers.

Images are made up of a number of different _pixels_.
In this book, for simplicity, we'll focus on grayscale, or single-channel images.
These are images where each pixel stores a single value.
Colour, or multi-channel images store multiple values per pixel (e.g., values for the red, green, and blue (RGB) components), and the same principles generally apply, just across multiple channels.

That's a lot of words without a single image yet!
Lets generate a random 8-bit 32 x 32 image as an example to take us through the rest of this chapter

```{code-cell} ipython3
import matplotlib.pyplot as plt
import numpy as np

image = np.random.randint(low=0, high=2**16, size=(32, 32), dtype=np.uint16)
print(image)

fig, ax = plt.subplots()
ax.imshow(image, cmap="Grays", vmin=0, vmax=2**16);
```

We can also look at what this looks like in binary, which is how the image is stored in memory:

```{code-cell} ipython3
image_bytes = image.tobytes()

print(f"{len(image_bytes)} bytes total")
print()
print("First ten bytes:")
for my_byte in image_bytes[:10]:
    print(f'{my_byte:0>8b}', end=' ')

print("...")
```

Because we have a 1024 pixel image, and each pixel is stored in 2 bytes (16 bits), we have a total of 1024$\times$2 = 2048 bytes.
Above you can see the bits written out for the first ten bytes of the image.
Saving these exact bits to a file is the simplest way of saving our image, but is also quite space-inefficient.
In the next sub-section we'll explore ways to reduce the size of our data by compressing it.

## Saving images

So far the image we've worked on has been stored in the random access memory (RAM) on our computer.
RAM is volatile, which means it's erased when it loses power, so if we want to save our image or send it to someone else we have to save it to a file that lives on persistent storage (e.g., a hard drive).

### 2D images

There are lots of different file formats we can save 2D images to.
Lets start by saving our image to a [TIFF file](https://www.adobe.com/creativecloud/file-types/image/raster/tiff-file.html), a commonly used image file format in bio-sciences.

```{code-cell} ipython3
import imageio.v3 as iio

iio.imwrite("image_file.tiff", image, plugin='tifffile')
```

This saves a single .tiff file to disk.
Because the TIFF file (in this case) doesn't compress the data, we should expect the file to be at least 2048 bytes big.
Lets check:

```{code-cell} ipython3
import os.path

print(f"File size: {os.path.getsize("image_file.tiff")} bytes")
```

The file is slightly bigger than 2048 bytes - the image itself takes up 2048 bytes, and then other file metadata takes up some extra space on top of that.

+++

## Compression

In the previous section we saved our image to a TIFF file, without any compression. This means the data stored in the file is exactly the same as the data in memory. This makes the TIFF file very quick to read and write from, as the data doesn't need to be processed or transformed at all.

```{mermaid}
    flowchart LR
        Memory --> TIFF
        TIFF --> Memory
```

If we have limited storage space however, we might want to compress the data before writing it to a file. In general there are two different types of compression:

- Lossless compression:
- Lossy compression:

A common example of lossless compression is PNG files:

```{code-cell} ipython3
iio.imwrite("image_file.png", image)
print(f"File size: {os.path.getsize("image_file.png")} bytes")
```

The PNG filesize is slightly smaller than the TIFF we saved with identical data. If we read the data back in from the PNG file, we still get exactly the same values back though:

```{code-cell} ipython3
image_png_data = iio.imread("image_file.png")
print("Recovered original data?", np.all(image_png_data == image))
```

The cost of compressing the data is adding another step when reading or writing the data to file

```{mermaid}
    flowchart LR
        Memory --> comp --> PNG
        PNG --> comp --> Memory


        comp["Compressor"]
        PNG["PNG file"]
        Memory["Data in memory"]
```

+++

If we want to compress the data further, we have to sacrifices some accuracy and use lossy compression. A common example of lossy compression is JPEG files. Here we'll save to a JPEG2000 file:

```{code-cell} ipython3
iio.imwrite("image_file.jp2", image, quality_layers=[2])
print(f"File size: {os.path.getsize("image_file.jp2")} B")

image_jp2_data = iio.imread("image_file.jp2")
print("Recovered original data?", np.all(image_jp2_data == image))
```

We can see above that the original data isn't recovered.
To illustrate that further, the next plot shows the difference between the original data and the data stored in the JPEG2000 file.

```{code-cell} ipython3
difference = image_jp2_data.astype(np.float32) - image.astype(np.float32)
fig, ax = plt.subplots()
im = ax.imshow(difference, cmap='RdBu')
fig.colorbar(im)
ax.set_title("Difference between original data and JPEG data");
```

## Storing large 3D data

### Motivating new file formats

The approaches described above to compressing and saving images work well for small to medium sized 2D images.
But what about large 3D data?
As an example, [one high resolution scan of a human heart](https://human-organ-atlas.esrf.fr/datasets/1659197537) from the Human Organ Atlas is 16 bit and has dimensions 7614 x 7614 x 8480.
That's 491,611,006,080 voxels (almost 500 billion), and 983 GB of data.

One way of storing 3D data is to save it as a stack of 2D images.
In the example above this would result in 8480 individual 2D images, each with size 7614 x 7614.
This is illustrated in the image below - each file is represented with a different colour.

```{code-cell} ipython3
:hide-input: true
fig = plt.figure()
ax = fig.add_subplot(projection='3d')

nz = 20
for i in range(nz):
    voxels = np.zeros((10, 10, nz))
    voxels[:, :, i] = 1
    ax.voxels(voxels, edgecolors='black', linewidths=0.5, alpha=0.4, shade=False);

ax.set_aspect("equal")
ax.axis('off');
```

A single full slice of this 3D dataset is much higher resolution than a typical computer display (I'm currently writing this on a 2560 x 1664 laptop screen).
This means when visualising large data, we either way to look at:

1. A zoomed in full-resolution view
2. A zoomed out lower resolution view

These two requirements have spawned new data formats specifically designed to address these challenges.
To start with, we'll look at how the `zarr` data format allows us to load small subsets of data at a time, speeding up data access when we only want to look at some of the data.

### The `zarr` data format

Consider 3D data stored as stacks of 2D images, and say we want to look at a small (32 x 32 x 32) cube of the data.
To get this data this we would have to all 32 2D images that contain the cube.
This is illustrated in the following diagram:

```{code-cell} ipython3
:hide-input: true

from matplotlib.lines import Line2D

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

x, y, z = np.indices((10, 10, 20))

voxels = np.ones(x.shape)
voxels_request = (x < 4) & (x >= 2) & (y < 5) & (y >= 3) & (z < 4) & (z >= 2)
voxels_read = (z < 4) & (z >= 2)

all_vox = ax.voxels(voxels, alpha=0.2, edgecolors='black', linewidths=0.05, shade=False)
req_vox = ax.voxels(voxels_request, edgecolors='black', linewidths=0.5, facecolors='tab:red', alpha=1, shade=False);
read_vox = ax.voxels(voxels_read, edgecolors='black', linewidths=0.5, facecolors='tab:orange', alpha=0.3, shade=False);

ax.axis('off')
ax.set_aspect('equal')

custom_lines = [
    list(all_vox.values())[0],
    list(req_vox.values())[0],
    list(read_vox.values())[0]]
ax.legend(custom_lines, [
    'All data',
    f'Requested data ({np.sum(voxels_request)} voxels)',
    f'Read data ({np.sum(voxels_read)} voxels)'])
```

For small datasets this isn't too much of an issue, but with huge datasets reading in whole 2D slices and then throwing away most of the data is very wasteful.

To solve this, zarr saves data in _chunks_ that can have an arbitrary shape.
