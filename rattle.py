"""
    rattle
    ~~~~~~

    Opinionated utilities for Snakemake pipelines.


    :copyright: (c) 2017 Wibowo Arindrarto <bow@bow.web.id>
    :license: BSD

"""

from collections import namedtuple
from os import path

from snakemake.io import expand

RELEASE = False

__version_info__ = ("0", "1", "0")
__version__ = ".".join(__version_info__)
__version__ += "-dev" if not RELEASE else ""

__author__ = "Wibowo Arindrarto"
__contact__ = "bow@bow.web.id"
__homepage__ = "https://github.com/bow/rattle"

__all__ = ["Run", "Sample", "ReadGroup", "UnitName"]


def getnattr(obj, idxs, fallback=None):
    """Helper method for recursively fetching an item from the given object.

    :param obj: Object containing the item to retrieve.
    :type obj: object
    :param idxs: List of attribute names / indices / keys to retrieve the item.
    :type idxs: list(str, int)
    :returns: None or the item.

    """
    if len(idxs) == 0:
        return obj

    idx = idxs.pop(0)

    if isinstance(obj, dict):
        if idx in obj:
            return getnattr(obj[idx], idxs)
        return fallback
    elif isinstance(obj, (list, tuple)) and isinstance(idx, int):
        if idx < len(obj):
            return getnattr(obj[idx], idxs)
        return fallback
    else:
        return getnattr(getattr(obj, idx, fallback))


def cachedproperty(func):
    """Decorator for cached property loading of class instances."""
    attr_name = func.__name__

    @property
    def cached(self):
        if not hasattr(self, '_cache'):
            setattr(self, '_cache', {})
        try:
            return self._cache[attr_name]
        except KeyError:
            result = self._cache[attr_name] = func(self)
            return result

    return cached


UnitName = namedtuple("UnitName", ["sample", "read_group"])


class ReadGroup(object):

    """Representation of a read group-level configuration."""

    def __init__(self, sample, rg_name, rg_config,
                 output_dir="{sample_group}"):
        self.sample = sample
        self.name = rg_name
        self.output_dir = output_dir
        self._raw = rg_config


class Sample(object):

    """Representation of a sample-level configuration."""

    def __init__(self, run, sample_name, sample_config):
        self.run = run
        self.name = sample_name
        self._raw = sample_config

    @cachedproperty
    def read_groups(self):
        """Read groups belonging to the sample."""
        return {rg_name: ReadGroup(self, rg_name, rg_config)
                for rg_name, rg_config in self._raw["read_groups"].items()}


class Run(object):

    """Representation of a run-level configuration."""

    def __init__(self, run_config, output_dir=None):
        # TODO: validation of incoming config
        self._raw = run_config
        self.output_dir = output_dir or run_config.get("output_dir", None)

    @cachedproperty
    def samples(self):
        """Samples belonging to the run."""
        return {sample_name: Sample(self, sample_name, sample_config)
                for sample_name, sample_config in self._raw["samples"].items()}

    @cachedproperty
    def unit_names(self):
        """Tuples of (sample, read group) names."""
        return [UnitName(sample.name, rg.name)
                for sample in self.samples.values()
                for rg in sample.read_groups.values()]

    def get_workdir(self, default=None):
        """Returns the working directory of the run

        A default value can optionally be given if the ``settings.workdir`` key
        is not defined in the config.

        """
        return getnattr(self._raw, ["settings", "workdir"], default)

    def config_input_func(self, level, rg_key):
        """Creates an input function for use in the ``input`` directive.

        :param str rg_key: Key name of the config in the given level whose
            value will be used.
        :param level: Level of the config to retrieve the key name from.
        :type level: ``Sample`` or ``ReadGroup`` class.
        :returns: A function with Snakemake wildcards as the input.

        """
        if level is not Sample and level is not ReadGroup:
            raise ValueError("Invalid 'level' value.")

        def func(wildcards):
            rgv = rg_key

            if rg_key.startswith("{") and rg_key.endswith("}"):
                rgv = getattr(wildcards, rg_key[1:-1])

            if level is Sample:
                return getnattr(self._raw,
                                ["samples", wildcards.sample, rgv])

            elif level is ReadGroup:
                return getnattr(self._raw,
                                ["samples", wildcards.sample, "read_groups",
                                 wildcards.read_group, rgv])

        return func

    def rg_gather_func(self, pattern, **kwargs):
        return lambda wildcards: \
            expand(pattern,
                   sample=wildcards.sample,
                   read_group=self.samples[wildcards.sample].read_groups,
                   **kwargs)

    def output(self, fname, fmt=False, sample="{sample}",
               read_group="{read_group}", **kwargs):
        """Creates a path of a file in the output directory.

        :param str fname: Name of the file.
        :param str sample: Value used for extrapolating the
            '{sample}' specifier if present.
        :param str read_group: Value used for extrapolating the
            '{read_group}' specifier if present.

        """
        if self.output_dir is None:
            raise ValueError("'output_dir' is not defined.")
        p = path.join(self.output_dir, fname)
        if fmt:
            return p.format(sample=sample, read_group=read_group, **kwargs)
        return p
