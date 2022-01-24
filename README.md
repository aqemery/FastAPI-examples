# FastAPI Development Examples

This repository contains examples shown during the PyRVA meeting on January, 12th 2022.

## Slides

slides from the presentation are included as a file `slides.pdf`

## Requirements

The required packages are included with in a pipfile. You can use pipenv to install them. 

`pipenv install packages`
`pipenv shell`

This repo also makes use of a `justfile` you can get info on how to install just here: [GitHub - casey/just: 🤖 Just a command runner](https://github.com/casey/just)

Note: The justfile is a mix of bash and python code that you can execute manually

Docker is also used to stand up database and scaling examples.

## Running Examples

Example files in this repo are name `example-{name}` you can provide the name into the just command to run them. 

`just run 0`

`just run graphql`
