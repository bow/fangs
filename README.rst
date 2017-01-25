Rattle
======

|ci|

.. |ci| image:: https://travis-ci.org/bow/rattle.svg?branch=master
    :target: https://travis-ci.org/bow/rattle

Rattle is a collection of opinionated helper functions and classes for running
a `Snakemake <https://snakemake.readthedocs.io/en/latest/>`_ pipeline. It imposes a certain way of structuring input
information, with the goal making Snakefiles for next generation sequencing pipelines even more readable.


Conventions
-----------

Rattle was written with next-generation sequencing experiments in minds. As such, it expects that pipeline inputs be
organized in a tiered-level of ``samples`` (a single unit to be analyzed by the experiment) and ``read groups`` (a
single unit representing a sequencing run). This is similar to the organization used in
`BAM files <https://samtools.github.io/hts-specs/SAMv1.pdf>`_. There, the ``@RG SM`` tag corresponds to sample names
and ``@RG ID`` tag corresponds to read group names.

With that in mind, Rattle expects inputs for Snakemake runs to be organized in a config file with the following
pseudoschema:

.. code-block::

    settings:
        <setting-key-0-name>: <setting-key-0-value>
        <setting-key-n-name>: <setting-key-n-value>
    samples:
        <sample-0-name>:
            read_groups:
                <read-group-0-name>:
                    <input-0-name>: <path-to-input-0>
                    <input-n-name>: <path-to-input-n>
                    tags:
                        <key-0-name>: <key-0-value>
                        <key-n-name>: <key-n-value>
        <sample-n-name>:
            read_groups:
                <read-group-0-name>:
                    <input-0-name>: <path-to-input-0>
                    <input-n-name>: <path-to-input-n>
                    tags:
                        <key-0-name>: <key-0-value>
                        <key-n-name>: <key-n-value>

The ``settings`` entry as well as ``tags`` entry are optional.


Usage
-----

Take a look at the ``test`` directory to see how Rattle is used.
