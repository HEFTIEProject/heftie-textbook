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
One way of storing 3D data is to save it as a stack of 2D images.
As an example, if we have an image that has shape (10, 10, 20), we could save it to 20 2D image files, each of which has shape (10, 10).
This is illustrated in the image below - each file is represented with a different colour.

```{code-cell} ipython3
import matplotlib.figure

def color_chunk_figure(*, image_shape: tuple[int, int, int], chunk_shape: tuple[int, int, int]) -> matplotlib.figure.Figure:
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    
    for x in range(0, image_shape[0], chunk_shape[0]):
        for y in range(0, image_shape[1], chunk_shape[1]):
            for z in range(0, image_shape[2], chunk_shape[2]):
                voxels = np.zeros(image_shape)
                voxels[x:x+chunk_shape[0], y:y+chunk_shape[1], z:z+chunk_shape[2]] = 1
                ax.voxels(voxels, edgecolors='black', linewidths=0.5, alpha=0.9, shade=False);
    
    ax.set_aspect("equal")
    ax.axis('off');
    ax.set_title(f'Image shape = {image_shape}\nChunk shape = {chunk_shape}')
```

```{code-cell} ipython3
color_chunk_figure(image_shape=(10, 10, 20), chunk_shape=(10, 10, 1))
```

One way of thinking about this is that we are splitting our 3D image up into *chunks*, and each chunk is saved to a single file.
In this case each chunk has shape `(nx, ny, 1)`, where `nx` and `ny` is the size of our 3D image in the x- and y- dimensions.


If we want to fetch a small cube of data, say shape `(2, 2, 2)`, then we have to read and de-compress the two files that contain this data, but then we end up throwing away most of the data we've read in.
This is illustrated below - to get the data values at just 8 voxels (the red cubes), we have to read in 200 voxels in total (the orange cubes).

```{code-cell} ipython3
:hide-input: true

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
ax.set_title("Chunk shape = (10, 10, 1)")
```

This approach described above to compressing and saving 3D images as stacks of 2D images works well for small to medium sized 2D images, when reading each 2D image is fast.
But what about large 3D data?
As an example, [one high resolution scan of a human heart](https://human-organ-atlas.esrf.fr/datasets/1659197537) from the Human Organ Atlas is 16 bit and has dimensions 7614 x 7614 x 8480.
That's 491,611,006,080 voxels (almost 500 billion), and 983 GB of data.

**Add timings for reading in a large JPEG2000 image**

As well as being slow to read in, slices of such large datasets are often much bigger than we ever want.
As an example, I'm currently writing this text on a laptop with a screen resolution of 2560 x 1664.
Even if I read in a full resolution 7164 x 7164 image, my computer can't display all the pixels.

So for a better data format we want the following features:

1. Less wasted effort when reading in small subsets of data
2. Some way of storing low-resolution copies of the original image, for faster loading when zooomed out

These two requirements have spawned new data formats specifically designed to address these challenges.
For 1., we'll look at how the `zarr` format allows us to load load small subsets of data at a time.
For 2., we'll look at how the `ome-zarr` format extends `zarr` to provide a way of storing multiple copies of the same image at different resolutions.

+++

### zarr

In the example above where we stored 3D data as a series of 2D image files, the *chunk shape* of our data was `(nx, ny, 1)`.
This just means each file that makes up the full dataset contains an array that has shape `(nx, ny, 1)`.
If we want to read a single voxel, this is the minimum amount of data we need to load and de-compress.

The key innovation of `zarr` is allowing the chunk size to be chosen when creating the data.
As an example, for a (10, 10, 20) shaped image, we could choose a chunk shape of (5, 5, 10).
This would split the original image up into 8 individual files, illustrated below with different colors:

```{code-cell} ipython3
color_chunk_figure(image_shape=(10, 10, 20), chunk_shape=(5, 5, 10))
```

Or we could choose a different shape, with smaller chunks:

```{code-cell} ipython3
color_chunk_figure(image_shape=(10, 10, 20), chunk_shape=(2, 2, 3))
```

Note that the chunk shape doesn't have to exactly divide the image shape - in the case where it doesn't, some of the chunks on the edge are just slightly smaller than the 'full sized' chunks.

+++

Now if we want to load the same 8 voxels of data, we need to load 8 chunks, but in total these contain far fewer voxels to read - 96, versus the previous 200 when we were storing the data in 2D images.

```{code-cell} ipython3
fig = plt.figure()
ax = fig.add_subplot(projection='3d')

x, y, z = np.indices((10, 10, 20))

voxels = np.ones(x.shape)
voxels_request = (x < 4) & (x >= 2) & (y < 5) & (y >= 3) & (z < 4) & (z >= 2)
voxels_read = (x < 6) & (x >= 2) & (y < 6) & (y >= 2) & (z < 6) & (z >= 0) 

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
ax.set_title("Chunk shape = (2, 2, 3)")
```

### OME-Zarr
