# Vino

This project is mainly hosted at [SourceSup](https://sourcesup.renater.fr/projects/vino/).
Please, consult the [Wiki](https://sourcesup.renater.fr/wiki/vino/index) for more information.

## Working with Docker

A "Dockerfile" is provided for easily building your development environment. It is achieved in 3 steps:

 - [install](https://docs.docker.com/engine/installation/) docker on your computer
 - build the docker image: 
   `docker build -t vinosite`
 - run the docker image just created: 
 `docker run -p 8000:8000 --volume=$(pwd):/vino vinosite`

Then you can test the web application by opening a web browser on `http://localhost:8000/sharekernel`.

If you want to run the image in interactive mode, you can run:
 `docker run -i -t --volume=$(pwd):/vino vinosite ipython`
and then run in the console `%run shell.py`. Now you can import modules from vino-py and vinosite.

You can also get a `bash` console with this command:
  `docker run -i -t --volume=$(pwd):/vino vinosite bash`
  