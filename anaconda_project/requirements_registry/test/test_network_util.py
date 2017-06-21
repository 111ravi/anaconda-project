# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © 2016, Continuum Analytics, Inc. All rights reserved.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------
import anaconda_project.requirements_registry.network_util as network_util

import socket


def test_can_connect_to_socket():
    # create a listening socket just to get a port number
    # that (probably) won't be in use after we close it
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    s.listen(1)
    port = s.getsockname()[1]

    try:
        assert network_util.can_connect_to_socket("127.0.0.1", port)
    finally:
        s.close()


def test_cannot_connect_to_socket():
    # create a listening socket just to get a port number
    # that (probably) won't be in use after we close it
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()

    assert not network_util.can_connect_to_socket("127.0.0.1", port)
