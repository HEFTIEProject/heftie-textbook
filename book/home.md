# Handling Enormous Files from 3D Imaging Experiments

Welcome to the textbook for working with huge 3D imaging datasets using modern data formats!

## Introduction

Modern imaging datasets are big - really big!
As an example, the [Human Organ Atlas](https://human-organ-atlas.esrf.fr/) routinely generates datasets that are > 500 GB in size.
For the average scientist, these datasets are too big to load into the available memory on their computer at once, raising the question: **how can we analyse huge imaging datasets**?

The key to answering this question comes in two parts:

1. Breaking down images into smaller files, or 'chunks' that are small enough to individually fit in memory.
2. Creating a series of downsampled versions of datasets, so it's possible to view a low resolution version of the whole dataset, but still zoom in and load high resolution regions of interest.

## Using this textbook

### Pre-requisites

This textbook assumes some familiarity with images and basic Python programming.
The [Introduction to Bioimage Analysis textbook](https://bioimagebook.github.io) has a good primer on images in the context of both Python and Biology.

### Reading the textbook

Every chapter is designed to be read from start to end in one sitting.
Each chapter builds upon the previous ones, so they should be read in order.
It is not designed to have hands-on examples, and should complement other resources that provide interactive lessons, such as the [OME-Zarr lesson in the Bioimage Analysis Training Resources](https://neubias.github.io/training-resources/ome_zarr/index.html).

### Running code

It's not necessary to run the code while reading, but if you want to...

## Acknowledgements

This book is part of the Handling Enormous Files from Tomographic Imaging Experiments (HEFTIE) project.
HEFTIE is funded by the [OSCARS project](https://oscars-project.eu/), which has received funding from the European Commission’s Horizon Europe Research and Innovation programme under grant agreement No. 101129751.

![OSCARS and EU logos](images/OSCARS-logo-EUflag.png)
