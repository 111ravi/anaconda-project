# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © 2016, Continuum Analytics, Inc. All rights reserved.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------
from __future__ import absolute_import, print_function

from anaconda_project.internal.cli.main import _parse_args_and_run_subcommand
from anaconda_project.internal.simple_status import SimpleStatus


def test_unarchive_command(capsys, monkeypatch):
    def mock_unarchive(filename, project_dir, parent_dir=None, frontend=None):
        assert frontend is not None
        frontend.info("a")
        frontend.info("b")
        return SimpleStatus(success=True, description="DESC")

    monkeypatch.setattr('anaconda_project.project_ops.unarchive', mock_unarchive)
    code = _parse_args_and_run_subcommand(['anaconda-project', 'unarchive', 'foo.tar.gz', 'bar'])
    assert code == 0

    out, err = capsys.readouterr()
    assert 'a\nb\nDESC\n' == out
    assert '' == err


def test_unarchive_command_error(capsys, monkeypatch):
    def mock_unarchive(filename, project_dir, parent_dir=None, frontend=None):
        assert frontend is not None
        frontend.info("a")
        frontend.info("b")
        frontend.error("c")
        frontend.error("d")
        return SimpleStatus(success=False, description="DESC", errors=['c', 'd'])

    monkeypatch.setattr('anaconda_project.project_ops.unarchive', mock_unarchive)
    code = _parse_args_and_run_subcommand(['anaconda-project', 'unarchive', 'foo.tar.gz', 'bar'])
    assert code == 1

    out, err = capsys.readouterr()
    assert 'a\nb\n' == out
    assert 'c\nd\nDESC\n' == err
