# -*- coding: utf-8 -*-
import unittest

import pytest

from .utils import SnakemakeFiles, make_exp_commands


run_single_rg = SnakemakeFiles(
    contents="""from rattle import Run, ReadGroup

RUN = Run(config, output_dir="results")

rule all:
    input:
        [RUN.make_output_fname(
            "output-{sample}-{read_group}.txt",
            sample=unit_name.sample, read_group=unit_name.read_group)
        for unit_name in RUN.unit_names]

rule test:
    input:
        r1=RUN.make_input_func(ReadGroup, "r1"),
    output:
        r1=RUN.make_output_fname("output-{sample}-{read_group}.txt"),
    shell:
        "some_exe -i {input.r1} -o {output.r1}"
    """,
    config={
        "samples": {
            "sample01": {
                "read_groups": {
                    "rg01": {
                        "r1": "input-rg01.txt"
                    }
                }
            }
        }
    },
    input_fnames=["input-rg01.txt"]).to_fixture()


@pytest.mark.usefixtures("run_single_rg")
class TestSingleRG(unittest.TestCase):

    def test_exit_code(self):
        assert self.run_fixture.exit_code == 0

    def test_commands(self):
        exp_stdout = make_exp_commands(
            "some_exe -i input-rg01.txt -o results/output-sample01-rg01.txt")
        assert self.run_fixture.stdout == exp_stdout
