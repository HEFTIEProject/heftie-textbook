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

Because we have a 1024 pixel image, and each pixel is stored in 1 byte (8 bits), we have a total of 1024$\times$1 = 32 bytes. Above you can see the bits for each byte. This is the simplest but least space efficient way of storing data. In the next sub-section we'll explore ways to reduce the size of our data by compressing it.

## Saving images

So far the image we've worked on has been stored in the random access memory (RAM) on our computer.
RAM is volatile, which means it's erased when it loses power, so if we want to save our image or send it to someone else we have to write it to a file, or 'serialise' it.

### 2D images
Since images are 2D data, there are lots of different file formats we can save it to.
Lets save it to a [TIFF file](https://www.adobe.com/creativecloud/file-types/image/raster/tiff-file.html), a commonly used image file format in bio-sciences.

```{code-cell} ipython3
import imageio.v3 as iio

iio.imwrite("image_file.tiff", image, plugin='tifffile')
```

This saves a single .tiff file to disk.
Because TIFF doesn't compress the data at all, we should expect the file to be at least 1024 bytes big.
Lets check:

```{code-cell} ipython3
import os.path

print(f"File size: {os.path.getsize("image_file.tiff")} B")
```

The file is slightly bigger than 2048 bytes - the image itself takes up 2048 bytes, and then other file metadata takes up 4 extra bytes on top of that.

+++

## Data compression

In the previous section we saved data to TIFF files, without any compression. This means the data stored in the file is exactly the same as the data in memory. This makes TIFF files very quick to read and write from, as the data doesn't need to be processed or transformed at all. 

```{mermaid}
    flowchart LR
        Memory --> TIFF 
        TIFF --> Memory 
```

If we have limited storage space however, we might want to compress the data somehow before writing it to a file. There are two different types of compression:

- Lossless compression:
- Lossy compression:

A common example of lossless compression is PNG files:

```{code-cell} ipython3
iio.imwrite("image_file.png", image)
print(f"File size: {os.path.getsize("image_file.png")} B")
```

The PNG filesize is slightly smaller than the TIFF we saved with identical data. If we read the data back in from the PNG file, we still get exactly the same values back:

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

difference = image_jp2_data.astype(np.float32) - image.astype(np.float32)
fig, ax = plt.subplots()
im = ax.imshow(difference, cmap='RdBu')
fig.colorbar(im)
ax.set_title("Difference between original data and JPEG data");
```

TODO: add some simple timing benchmarks
