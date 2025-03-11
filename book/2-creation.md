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
from bokeh.plotting import figure, show, output_notebook

output_notebook()
```

```{code-cell} ipython3
from data_helpers import load_heart_data

heart_image = load_heart_data(array_type='numpy')
```

```{code-cell} ipython3
p = figure()
p.x_range.range_padding = p.y_range.range_padding = 0
p.image(image=[heart_image[:, :, 70]], x=0, y=0, dw=heart_image.shape[0], dh=heart_image.shape[1], palette='Greys256'
       )
show(p)
```

```{code-cell} ipython3

```
