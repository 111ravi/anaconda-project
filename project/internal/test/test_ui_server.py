from __future__ import absolute_import, print_function

from bs4 import BeautifulSoup
from tornado.ioloop import IOLoop

from project.internal.plugin_html import _BEAUTIFUL_SOUP_BACKEND
from project.prepare import ConfigurePrepareContext, _FunctionPrepareStage, PrepareSuccess
from project.internal.test.http_utils import http_get, http_post
from project.internal.test.multipart import MultipartEncoder
from project.internal.test.tmpfile_utils import with_directory_contents
from project.internal.ui_server import UIServer, UIServerDoneEvent
from project.local_state_file import LocalStateFile
from project.plugins.requirement import EnvVarRequirement
from project.plugins.registry import PluginRegistry


def _no_op_prepare(config_context):
    def _do_nothing(stage):
        stage._result = PrepareSuccess(logs=[], command_exec_info=None, environ=dict())
        return None

    return _FunctionPrepareStage("Do Nothing", _do_nothing, config_context)


def test_ui_server_empty():
    def do_test(dirname):
        io_loop = IOLoop()
        io_loop.make_current()

        events = []

        def event_handler(event):
            events.append(event)

        local_state_file = LocalStateFile.load_for_directory(dirname)
        context = ConfigurePrepareContext(dict(), local_state_file, [])
        server = UIServer(_no_op_prepare(context), event_handler, io_loop)

        get_response = http_get(io_loop, server.url)
        print(repr(get_response))
        post_response = http_post(io_loop, server.url, body="")
        print(repr(post_response))

        server.unlisten()

        assert len(events) == 1
        assert isinstance(events[0], UIServerDoneEvent)

    with_directory_contents(dict(), do_test)


def test_ui_server_with_form():
    def do_test(dirname):
        io_loop = IOLoop()
        io_loop.make_current()

        events = []

        def event_handler(event):
            events.append(event)

        local_state_file = LocalStateFile.load_for_directory(dirname)

        value = local_state_file.get_value(['variables', 'FOO'])
        assert value is None

        requirement = EnvVarRequirement(registry=PluginRegistry(), env_var="FOO")
        status = requirement.check_status(dict())
        context = ConfigurePrepareContext(dict(), local_state_file, [status])
        server = UIServer(_no_op_prepare(context), event_handler, io_loop)

        get_response = http_get(io_loop, server.url)
        print(repr(get_response))

        soup = BeautifulSoup(get_response.body, _BEAUTIFUL_SOUP_BACKEND)
        field = soup.find_all("input", attrs={'type': 'text'})[0]

        assert 'name' in field.attrs

        encoder = MultipartEncoder({field['name']: 'bloop'})
        body = encoder.to_string()
        headers = {'Content-Type': encoder.content_type}

        post_response = http_post(io_loop, server.url, body=body, headers=headers)
        print(repr(post_response))

        server.unlisten()

        assert len(events) == 1
        assert isinstance(events[0], UIServerDoneEvent)

        value = local_state_file.get_value(['variables', 'FOO'])
        assert 'bloop' == value

    with_directory_contents(dict(), do_test)


def _ui_server_bad_form_name_test(capsys, name_template, expected_err):
    def do_test(dirname):
        io_loop = IOLoop()
        io_loop.make_current()

        events = []

        def event_handler(event):
            events.append(event)

        local_state_file = LocalStateFile.load_for_directory(dirname)

        requirement = EnvVarRequirement(registry=PluginRegistry(), env_var="FOO")
        status = requirement.check_status(dict())
        context = ConfigurePrepareContext(dict(), local_state_file, [status])
        server = UIServer(_no_op_prepare(context), event_handler, io_loop)

        # do a get so that _requirements_by_id below exists
        get_response = http_get(io_loop, server.url)
        assert 200 == get_response.code

        req_id = list(server._application._requirements_by_id.keys())[0]
        if '%s' in name_template:
            name = name_template % req_id
        else:
            name = name_template

        encoder = MultipartEncoder({name: 'bloop'})
        body = encoder.to_string()
        headers = {'Content-Type': encoder.content_type}

        post_response = http_post(io_loop, server.url, body=body, headers=headers)
        # we just ignore bad form names, because they are assumed
        # to be some sort of hostile thing. we shouldn't ever
        # generate them on purpose.
        assert 200 == post_response.code

        server.unlisten()

        assert len(events) == 1
        assert isinstance(events[0], UIServerDoneEvent)

        out, err = capsys.readouterr()
        assert out == ""
        assert err == expected_err

    with_directory_contents(dict(), do_test)


def test_ui_server_not_enough_pieces_in_posted_name(capsys):
    _ui_server_bad_form_name_test(capsys, "nopieces", "not enough pieces in ['nopieces']\n")


def test_ui_server_invalid_req_id_in_posted_name(capsys):
    _ui_server_bad_form_name_test(capsys, "badid.EnvVarProvider.value", "badid not a known requirement id\n")


def test_ui_server_invalid_provider_key_in_posted_name(capsys):
    _ui_server_bad_form_name_test(capsys, "%s.BadProvider.value", "did not find provider BadProvider\n")
