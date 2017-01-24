# -*- coding: utf-8 -*-
"""Fangs test utilities"""

from collections import namedtuple

import yaml
from pytest_pipeline import PipelineRun, mark


class SnakemakeDryRun(PipelineRun):

    contents_fname = "Snakefile"
    config_fname = "config.yml"

    def __init__(self, *args, **kwargs):
        self.snakefile = kwargs.pop("snakefile")
        super().__init__(*args, **kwargs)

    @mark.before_run
    def write_snakefile_contents(self):
        with open(self.contents_fname, "w") as target:
            print(self.snakefile.contents, file=target)

    @mark.before_run
    def write_snakefile_config(self):
        with open(self.config_fname, "w") as target:
            print(yaml.dump(self.snakefile.config, default_flow_style=False),
                  file=target)

    @mark.before_run
    def write_fake_inputs(self):
        for input_fname in self.snakefile.input_fnames:
            # We just need the file to be present.
            with open(input_fname, "w"):
                pass


class SnakemakeFiles(namedtuple("SnakemakeFiles",
                                ["contents", "config", "input_fnames"])):

    """Helper class for creating fixtures."""

    def to_fixture(self):
        cmd = "snakemake -n --nocolor -pq --configfile config.yml"
        return SnakemakeDryRun\
            .make_fixture("class", snakefile=self,
                          cmd=cmd, stdout=True, stderr=True)


def make_exp_commands(*cmds):
    """Creates a raw string for expected commands test."""
    return ("\n".join(cmds) + "\n").encode("utf-8")
