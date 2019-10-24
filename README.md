# manga-downloader
A small python project for downloading manga from various sources.

To build the docker image run, replacing <image_name> by a name :

```docker build --rm -t <image_name> .```

Run it with, replacing <config_file> by the configuration file path, <library_dir> by the calibre libary path and <image_name> by a name : 

```docker run -it -v "<config_file>:/mangas-downloader/config.yml" -v "<library_dir>:/library" <image_name>```