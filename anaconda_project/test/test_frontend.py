# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © 2016, Continuum Analytics, Inc. All rights reserved.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------
from __future__ import absolute_import

from anaconda_project.internal.test.fake_frontend import FakeFrontend


def test_partial_messages():
    frontend = FakeFrontend()

    frontend.partial_info("a\nb\nc\nd")
    # d is stuck in the buffer
    assert frontend.logs == ['a', 'b', 'c']
    assert frontend._info_buf == 'd'

    frontend.partial_error("1")
    frontend.partial_error("2")
    frontend.partial_error("3")
    frontend.partial_error("456")
    assert frontend._error_buf == "123456"
    frontend.partial_error("\n")

    assert frontend._error_buf == ""
    assert frontend.errors == ['123456']

    frontend.partial_error("\n\n\n\n")
    assert frontend.errors == ['123456', '', '', '', '']


def test_partial_messages_with_windows_line_endings():
    frontend = FakeFrontend()

    frontend.partial_info("a\r\nb\r\nc\r\nd")
    # d is stuck in the buffer
    assert frontend.logs == ['a', 'b', 'c']
    assert frontend._info_buf == 'd'
