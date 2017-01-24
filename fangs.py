"""
Utilities for Snakemake.


This Snakefile requires a JSON/YAML file with the following layout as config:


"""
from collections import namedtuple
from os import path


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

    def __init__(self, sample, rg_name, rg_config):
        self.sample = sample
        self.name = rg_name
        self._raw = rg_config


class Sample(object):

    """Representation of a sample-level configuration."""

    def __init__(self, run, sample_name, sample_config):
        self.run = run
        self.name = sample_name
        self._raw = sample_config

    @cachedproperty
    def read_groups(self):
        return {rg_name: ReadGroup(self, rg_name, rg_config)
                for rg_name, rg_config in self._raw["read_groups"].items()}


class Run(object):

    """Representation of a run-level configuration.

    The input config must have the following layout:

        {
        "settings": {
            "workdir": <path_to_output_dir>,
        },
        "samples": {
            <sample_name>: {
            "read_groups": {
                <read_group_name>: {
                "R1": <path_to_R1>,
                "R2": <path_to_R2>
                }
            }
            }
        }
        }

    Notes:
        * <sample_name> can be any string; it is the sample name.
        * <read_group_name> can be any string; it is in practice the read group
          name.
        * <path_to_R1> and <path_to_R2> are *absolute* paths to each sequence
          file.
        * There must only be a single <read_group_name> for each sample.

    """

    def __init__(self, run_config, output_dir=None):
        self._raw = run_config
        self.output_dir = output_dir

    @cachedproperty
    def samples(self):
        return {sample_name: Sample(self, sample_name, sample_config)
                for sample_name, sample_config in self._raw["samples"].items()}

    @cachedproperty
    def unit_names(self):
        return [UnitName(sample.name, rg.name)
                for sample in self.samples.values()
                for rg in sample.read_groups.values()]

    def get_workdir(self, default=None):
        return getnattr(self._raw, ["settings", "workdir"], default)

    def make_input_func(self, rg_key, level):
        if level is Sample:
            return lambda wildcards: \
                getnattr(self._raw,
                         ["samples", wildcards.sample, rg_key])
        if level is ReadGroup:
            return lambda wildcards: \
                getnattr(self._raw,
                         ["samples", wildcards.sample, "read_groups",
                          wildcards.read_group, rg_key])

        raise ValueError("Invalid 'level' value.")

    def make_output_fname(self, fname, sample="{sample}",
                          read_group="{read_group}"):
        if self.output_dir is None:
            raise ValueError("'output_dir' is not defined.")
        return path\
            .join(self.output_dir, fname)\
            .format(sample=sample, read_group=read_group)
