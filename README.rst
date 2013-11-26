=======================
sphinxcontrib-cqlengine
=======================

This package provides an extension for the `Sphinx <http://sphinx-doc.org/>`_
documentation system for automatically generating documentation for
`cqlengine <https://cqlengine.readthedocs.org>`_, a Python ORM for the
`Cassandra <http://cassandra.apache.org/>`_ database.

The extension depends on and compliments the
`autodoc <http://sphinx-doc.org/ext/autodoc.html#module-sphinx.ext.autodoc>`_
and `sphinxcontrib-blockdiag <http://blockdiag.com/en/blockdiag/sphinxcontrib.html>`_
extensions.


Installation
============

Add `sphinxcontrib-cqlengine` to your package dependencies or install it
separately::

    pip install sphinxcontrib-cqlengine

Enable the required Sphinx extensions in `conf.py`:

.. code-block:: python

    extensions = [
        # Intersphinx for linking directly into the cqlengine documentation
        'sphinx.ext.intersphinx',
        'sphinx.ext.autodoc',
        # blockdiag for rendering the diagrams
        'sphinxcontrib.blockdiag',
        'sphinxcontrib.cqlengine',
    ]

For linking directly into the cqlengine documentation update the intersphinx
mapping:

.. code-block:: python

    intersphinx_mapping = {
        'http://docs.python.org/': None,
        'cqlengine': ('https://cqlengine.readthedocs.org/en/latest', None),
    }


Usage
=====

The extension provides a single new directive called `cassandra` which takes a
single argument which is the module path to the cqlengine model to document::

    .. cassandra:: path.to.model

Example
=======

.. code-block:: python

    from cqlengine.models import model

    class MyModel(Model):
        """Normal documentation about the model.

        .. cassandra:: myapp.models.MyModel
        """
