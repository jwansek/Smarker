.. _docker:

Running in docker
=================

Running the system in docker has many advantages:

* Don't have to worry about getting dependencies- the system requires many libraries to be avaliable on the PATH

* Isolation: we are running remote code supplied by anyone, which can potentially be very dangerous. Docker isolates the dangerous code, a significant security concern

* Makes the system be able to be used in Windows- Smarker has been tested in docker for windows using WSL for the backend

Using docker
------------

We have a ``Dockerfile`` ready for use: ``sudo docker build -t smarker .``

To input files and get the output report we use docker volumes ``-v``. Unfortunately
docker seems to be rather buggy passing through single files, so we recommend making
a directory to pass through instead. 

Command line arguments can be replaced with environment variables, using the ``-e``
flag in a ``key=value`` format. There is the additional environment variable ``SMARKERDEPS``
which will pip install pypi modules at the start, deliminated with commas.

.. code-block:: bash
    
    sudo docker run \
        -v "$(pwd)/../wsData.txt":/wsData.txt \
        -v "$(pwd)/100301654.zip":/tmp/100301654.zip \
        -v "$(pwd)/out/":/out/ \
        -e submission=/tmp/100301654.zip \
        -e assessment=example \
        -e SMARKERDEPS=matplotlib \
        -e format=pdf \
        -e output=/out/100301654.pdf \
        --rm smarker

To list assessments in the database using docker:

.. code-block:: bash
    
    sudo docker run -it --entrypoint python --rm smarker assessments.py --list yes

.. code-block:: bash

    touch out/report.pickle && sudo docker run -v "$(pwd)/out/report.pickle":/Smarker/plagarism_report_details.pickle -it --entrypoint python --rm smarker assessments.py --plagarism_report example

If a file doesn't exist before it's passed through as a volume in docker, it will be created automatically as a *directory*- this causes issues if the docker image produces a file so we make a blank file first.