# Introduction

Modern imaging datasets are big - really big!
As an example, the [Human Organ Atlas](https://human-organ-atlas.esrf.fr/) [^inspired] routinely generates datasets that are > 500 GB in size.
For the average scientist, these datasets are too big to load into the available memory on their computer at once, raising the question: **how can we analyse huge imaging datasets**?

The key to answering this question comes in two parts:

1. Breaking down images into smaller files, or 'chunks' that are small enough to individually fit in memory.
2. Creating a series of downsampled versions of datasets, so it's possible to view a low resolution version of the whole dataset, but still zoom in and load high resolution regions of interest.[^google_maps]

[^inspired]: the project that inspired this textbook
[^google_maps]: kind of like starting with the whole world and zooming in to your town on Google Maps
