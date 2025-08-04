# heftie-textbook

<img src="book/images/heftie_logo.svg" alt="HEFTIE logo" width="100"/>

A digital textbook for working with huge 3D imaging datasets

> [!WARNING]
> This book is still a work in progress - it might not make complete sense yet!
> Feedback is very welcome, by [opening an issue](https://github.com/HEFTIEProject/heftie-textbook/issues/new) on our GitHub issue tracker.

## Contributing

This book is built using [Jupyter Book](https://next.jupyterbook.org/).
To build the book locally run:

```bash
cd book
jupyter book start --execute
```

This command will print a link that can be opened in a web browser to preview the book locally.

To develop the book, it's recommended to use `uv`.
Run `uv run jupyter lab` to start Jupyter, and then navigate to the `book` directory.
Then right-click on one of the chapter's `.md` files and select "Open With" > "Jupytext Notebook". 
All cells can be edited / run directly in this interface.

## Funding

This project is funded by the [OSCARS project](https://oscars-project.eu/), which has received funding from the European Commission’s Horizon Europe Research and Innovation programme under grant agreement No. 101129751.

![OSCARS and EU logos](book/images/OSCARS-logo-EUflag.png)
