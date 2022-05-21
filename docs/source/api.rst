.. _api:

Running as an API
=================

*Smarker* can be hosted on a server and accessed through an API. A valid docker-compose
file is in the ``API/`` directory. Since the API docker container accesses the host docker
daemon, you must pass set the host location of the ``.uploads/`` directory as the ``$UPLOADS_DIR``
environment variable.

.. autofunction:: app.helloworld

.. autofunction:: app.mark

An example CURL request could be:

.. code-block:: bash
    
    curl -X POST -H "Content-Type: multipart/form-data" \
        -F "zip=@../100301654.zip" \
        -F "key=2g_yU7n1SqTODGQmpuViIAwbdbownmVDpjUl9NKkRqz" \
        -F "assessment=example" \
        -F "filedep1=@../../dependency.txt" \
        -F "dependency.txt=/dependency.txt" \
        "localhost:6970/api/mark"

