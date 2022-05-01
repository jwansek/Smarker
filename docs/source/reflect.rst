``reflect.py``: Getting information about code
==============================================

Classes
*******

.. autoclass:: reflect.Reflect
    :members:

.. autoexception::  reflect.MonitoredFileNotInProducedFilesException

Thrown if the user has tried to monitor a file that isn't in the list of produced files in the :ref:`assessmentyaml`.

Functions
*********

.. autofunction:: reflect.gen_reflection_report

Generates a json file report. It is quite a complex structure, but it is made so users can add other rendering templates 
later on. For example, the :ref:`quickstart` looks like this:

.. literalinclude:: _static/simple.json
    :linenos:
    :language: yaml