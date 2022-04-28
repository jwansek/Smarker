.. _assessmentyaml:

Assessment configuration yaml
=============================

A yaml file defines how assessments work. Here's the `example configuration <https://github.com/jwansek/Smarker/blob/master/ExampleAssessments/example.yml>`_ on git:

.. literalinclude:: ../../ExampleAssessments/example.yml
    :linenos:
    :language: yaml

Configuration files must have a name, from which the assessment will be referred to from now often
Pay attention to the use of lists, even if there is only one file or class, it must still be in a list
Tests are put into pytest and must include the name of the module in functions and classes as shown,
for example it's ``example.MyDate()`` not just ``MyDate``. You must use exactly 4 spaces of indentation.

``run:`` blocks can analyse the output to stdout of a python file, or read any file. Add a
``monitor:`` block to monitor a specific file or omit to analyse stdout.

``dependencies:`` blocks add required files using ``files:`` and pypi dependencies using ``libraries:``.

``produced_files`` lists files that are produced by the code. To analyse files they must be in
this list. They will be deleted after the program runs.

Functions and methods have a number in their arguments. An error will be shown in the report
if not enough arguments are found.

Assessment configurations are added to the database:

.. code-block:: bash

    python3 Smarker/assessments.py -c ExampleAssessments/example.yml -e 1

The ``-e`` flag is the number of student enrolled and is optional. The assessments in the 
database are listed:

.. code-block:: bash

    python3 Smarker/assessments.py -l yes

Which returns a string in the yaml format. Assessments can be deleted (will also deleted
associated submissions)

.. code-block:: bash

    python3 Smarker/assessments.py -rm example

