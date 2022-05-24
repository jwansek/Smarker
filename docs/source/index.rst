.. mdinclude:: readme.md

Read the :ref:`quickstart`.

Setting up
----------

* Set up a MySQL/MariaDB server. The database will be generated automatically.
* Add ``smarker.conf`` to the root directory of the code. See :ref:`configfile` for the structure of this file.
* Decide how you want to run the program: with or without docker.
* Add an assessment yaml- :ref:`assessmentyaml`.
* Enroll students: ``python3 Smarker/assessments.py -s 123456789,Eden,Attenborough,E.Attenborough@uea.ac.uk``

*Smarker* can be used inside docker, see :ref:`docker` (recommended for sandboxing client code)
and through an API- see :ref:`api`.

``smarker.py`` usage
********************

Now we are ready to make some reports! For which we use the main file ``smarker.py``:

.. argparse::
   :module: smarker
   :func: getparser
   :prog: python Smarker/smarker.py

Please note that the ``-o`` flag is required for rendering to PDFs.

``assessments.py`` usage
************************

``assessments.py`` contains many useful arguments for interacting with the database:

Also see :ref:`assessments`

.. argparse::
   :module: assessments
   :func: getparser
   :prog: python Smarker/assessments.py

.. toctree::
   :maxdepth: 2
   :caption: Setting up:

   quickstart.rst
   configfile.rst

.. toctree::
   :maxdepth: 3
   :caption: Docker:

   docker.rst
   assessmentyaml.rst
   api.rst

.. toctree::
   :maxdepth: 3
   :caption: Modules:
   
   reflect.rst
   database.rst
   assessments.rst
   api.rst

.. sidebar-links::
   :caption: Source code:   
   :github: 

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* `Source Code <https://git.eda.gay/Smarker/files.html>`_
* `License <https://git.eda.gay/Smarker/file/LICENSE.html>`_
