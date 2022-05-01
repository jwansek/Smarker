.. _assessments:

``assessments.py``
==================

``assessments.py`` contains many useful arguments for interacting with the database:

.. argparse::
   :module: assessments
   :func: getparser
   :prog: python Smarker/assessments.py

Classes
*******

.. autoclass:: assessments.SimilarityMetric
    :members:

Functions
*********

.. autofunction:: assessments.visualise_matrix

.. autofunction:: assessments.generate_plagarism_report