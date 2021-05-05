#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# template: header.j2

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: vcenter_vm_guest_processes
short_description: Starts a program in the guest operating system
description: 'Starts a program in the guest operating system. <p> A process started
  this way can have its status queried with {@link #list} or {@link #get}. When the
  process completes, its exit code and end time will be available for 5 minutes after
  completion. <p>'
options:
  arguments:
    description:
    - 'The arguments to the program. Characters which must be escaped to the shell
      should also be escaped in {@name #arguments}. In Linux and Solaris guest operating
      systems, stdio redirection arguments may be used. For Windows, stdio redirection
      can be added to the argments if {@name #path} is prefixed with <code>c:\windows\system32\cmd.exe
      /c</code>.'
    type: str
  credentials:
    description:
    - The guest authentication data.  See {@link Credentials}. Required with I(state=['absent'])
    - 'Valid attributes are:'
    - ' - C(interactive_session) (bool): If {@term set}, the {@term operation} will
      interact with the logged-in desktop session in the guest. This requires that
      the logged-on user matches the user specified by the {@link Credentials}. This
      is currently only supported for {@link Type#USERNAME_PASSWORD}.'
    - ' - C(type) (str): Types of guest credentials'
    - '   - Accepted values:'
    - '     - USERNAME_PASSWORD'
    - '     - SAML_BEARER_TOKEN'
    - ' - C(user_name) (str): For {@link Type#SAML_BEARER_TOKEN}, this is the guest
      user to be associated with the credentials. For {@link Type#USERNAME_PASSWORD}
      this is the guest username.'
    - ' - C(password) (str): password'
    - ' - C(saml_token) (str): SAML Bearer Token'
    type: dict
  environment_variables:
    description:
    - A map of environment variables, specified using the guest OS rules (for example
      <code>PATH, c:\bin;c:\windows\system32</code> or <code>LD_LIBRARY_PATH,/usr/lib:/lib</code>),
      to be set for the program being run.  Note that these are not additions to the
      default environment variables; they define the complete set available to the
      program.
    type: dict
  path:
    description:
    - 'The absolute path to the program to start. For Linux guest operating systems,
      /bin/bash is used to start the program. For Solaris guest operating systems,
      if /bin/bash exists, its used to start the program, otherwise /bin/sh is used.
      If /bin/sh is used, then the process ID returned by {@link Processes#create}
      will be that of the shell used to start the program, rather than the program
      itself, due to the differences in how /bin/sh and /bin/bash work.  This PID
      will still be usable for watching the process with {@link Processes#list} to
      find its exit code and elapsed time. For Windows, no shell is used. Using a
      simple batch file instead by prepending <code>c:\windows\system32\cmd.exe /c</code>
      will allow stdio redirection to work if passed in the {@name #arguments} parameter.
      Required with I(state=[''present''])'
    type: str
  pid:
    description:
    - Process ID of the process to be terminated Required with I(state=['absent'])
    type: int
  start_minimized:
    description:
    - Makes any program window start minimized in Windows operating systems. Returns
      an error if {@term set} for non-Windows guests.
    type: bool
  state:
    choices:
    - absent
    - present
    default: present
    description: []
    type: str
  vcenter_hostname:
    description:
    - The hostname or IP address of the vSphere vCenter
    - If the value is not specified in the task, the value of environment variable
      C(VMWARE_HOST) will be used instead.
    required: true
    type: str
  vcenter_password:
    description:
    - The vSphere vCenter username
    - If the value is not specified in the task, the value of environment variable
      C(VMWARE_PASSWORD) will be used instead.
    required: true
    type: str
  vcenter_rest_log_file:
    description:
    - 'You can use this optional parameter to set the location of a log file. '
    - 'This file will be used to record the HTTP REST interaction. '
    - 'The file will be stored on the host that run the module. '
    - 'If the value is not specified in the task, the value of '
    - environment variable C(VMWARE_REST_LOG_FILE) will be used instead.
    type: str
  vcenter_username:
    description:
    - The vSphere vCenter username
    - If the value is not specified in the task, the value of environment variable
      C(VMWARE_USER) will be used instead.
    required: true
    type: str
  vcenter_validate_certs:
    default: true
    description:
    - Allows connection when SSL certificates are not valid. Set to C(false) when
      certificates are not trusted.
    - If the value is not specified in the task, the value of environment variable
      C(VMWARE_VALIDATE_CERTS) will be used instead.
    type: bool
  vm:
    description:
    - Virtual machine to perform the operation on. This parameter is mandatory.
    required: true
    type: str
  working_directory:
    description:
    - The absolute path of the working directory for the program to be run.  VMware
      recommends explicitly setting the working directory for the program to be run.
    type: str
author:
- Ansible Cloud Team (@ansible-collections)
version_added: 1.0.0
requirements:
- python >= 3.6
- aiohttp
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

# This structure describes the format of the data expected by the end-points
PAYLOAD_FORMAT = {
    "delete": {
        "query": {},
        "body": {"credentials": "credentials"},
        "path": {"pid": "pid", "vm": "vm"},
    },
    "get": {
        "query": {},
        "body": {"credentials": "credentials"},
        "path": {"pid": "pid", "vm": "vm"},
    },
    "create": {
        "query": {},
        "body": {
            "arguments": "spec/arguments",
            "environment_variables": "spec/environment_variables",
            "path": "spec/path",
            "start_minimized": "spec/start_minimized",
            "working_directory": "spec/working_directory",
        },
        "path": {"vm": "vm"},
    },
    "list": {"query": {}, "body": {"credentials": "credentials"}, "path": {"vm": "vm"}},
}  # pylint: disable=line-too-long

import json
import socket
from ansible.module_utils.basic import env_fallback

try:
    from ansible_collections.cloud.common.plugins.module_utils.turbo.exceptions import (
        EmbeddedModuleFailure,
    )
    from ansible_collections.cloud.common.plugins.module_utils.turbo.module import (
        AnsibleTurboModule as AnsibleModule,
    )

    AnsibleModule.collection_name = "vmware.vmware_rest"
except ImportError:
    from ansible.module_utils.basic import AnsibleModule
from ansible_collections.vmware.vmware_rest.plugins.module_utils.vmware_rest import (
    build_full_device_list,
    exists,
    gen_args,
    get_device_info,
    get_subdevice_type,
    list_devices,
    open_session,
    prepare_payload,
    update_changed_flag,
)


def prepare_argument_spec():
    argument_spec = {
        "vcenter_hostname": dict(
            type="str", required=True, fallback=(env_fallback, ["VMWARE_HOST"]),
        ),
        "vcenter_username": dict(
            type="str", required=True, fallback=(env_fallback, ["VMWARE_USER"]),
        ),
        "vcenter_password": dict(
            type="str",
            required=True,
            no_log=True,
            fallback=(env_fallback, ["VMWARE_PASSWORD"]),
        ),
        "vcenter_validate_certs": dict(
            type="bool",
            required=False,
            default=True,
            fallback=(env_fallback, ["VMWARE_VALIDATE_CERTS"]),
        ),
        "vcenter_rest_log_file": dict(
            type="str",
            required=False,
            fallback=(env_fallback, ["VMWARE_REST_LOG_FILE"]),
        ),
    }

    argument_spec["arguments"] = {"type": "str"}
    argument_spec["credentials"] = {"type": "dict"}
    argument_spec["environment_variables"] = {"type": "dict"}
    argument_spec["path"] = {"type": "str"}
    argument_spec["pid"] = {"type": "int"}
    argument_spec["start_minimized"] = {"type": "bool"}
    argument_spec["state"] = {
        "type": "str",
        "choices": ["absent", "present"],
        "default": "present",
    }
    argument_spec["vm"] = {"required": True, "type": "str"}
    argument_spec["working_directory"] = {"type": "str"}

    return argument_spec


async def main():
    required_if = list([])

    module_args = prepare_argument_spec()
    module = AnsibleModule(
        argument_spec=module_args, required_if=required_if, supports_check_mode=True
    )
    if not module.params["vcenter_hostname"]:
        module.fail_json("vcenter_hostname cannot be empty")
    if not module.params["vcenter_username"]:
        module.fail_json("vcenter_username cannot be empty")
    if not module.params["vcenter_password"]:
        module.fail_json("vcenter_password cannot be empty")
    try:
        session = await open_session(
            vcenter_hostname=module.params["vcenter_hostname"],
            vcenter_username=module.params["vcenter_username"],
            vcenter_password=module.params["vcenter_password"],
            validate_certs=module.params["vcenter_validate_certs"],
            log_file=module.params["vcenter_rest_log_file"],
        )
    except EmbeddedModuleFailure as err:
        module.fail_json(err.get_message())
    result = await entry_point(module, session)
    module.exit_json(**result)


# template: default_module.j2
def build_url(params):
    return (
        "https://{vcenter_hostname}"
        "/api/vcenter/vm/{vm}/guest/processes/{pid}?action=delete"
    ).format(**params)


async def entry_point(module, session):

    if module.params["state"] == "present":
        if "_create" in globals():
            operation = "create"
        else:
            operation = "update"
    elif module.params["state"] == "absent":
        operation = "delete"
    else:
        operation = module.params["state"]

    func = globals()["_" + operation]

    return await func(module.params, session)


async def _create(params, session):

    if params["None"]:
        _json = await get_device_info(session, build_url(params), params["None"])
    else:
        _json = await exists(params, session, build_url(params), ["None"])
    if _json:
        if "value" not in _json:  # 7.0.2+
            _json = {"value": _json}
        if "_update" in globals():
            params["None"] = _json["id"]
            return await globals()["_update"](params, session)
        return await update_changed_flag(_json, 200, "get")

    payload = prepare_payload(params, PAYLOAD_FORMAT["create"])
    _url = (
        "https://{vcenter_hostname}"
        "/api/vcenter/vm/{vm}/guest/processes?action=create"
    ).format(**params)
    async with session.post(_url, json=payload) as resp:
        if resp.status == 500:
            text = await resp.text()
            raise EmbeddedModuleFailure(
                f"Request has failed: status={resp.status}, {text}"
            )
        try:
            if resp.headers["Content-Type"] == "application/json":
                _json = await resp.json()
        except KeyError:
            _json = {}

        if resp.status in [200, 201]:
            if isinstance(_json, str):  # 7.0.2 and greater
                _id = _json  # TODO: fetch the object
            elif isinstance(_json, dict) and "value" not in _json:
                _id = list(_json["value"].values())[0]
            elif isinstance(_json, dict) and "value" in _json:
                _id = _json["value"]
            _json_device_info = await get_device_info(session, _url, _id)
            if _json_device_info:
                _json = _json_device_info

        return await update_changed_flag(_json, resp.status, "create")


async def _delete(params, session):
    _in_query_parameters = PAYLOAD_FORMAT["delete"]["query"].keys()
    payload = prepare_payload(params, PAYLOAD_FORMAT["delete"])
    subdevice_type = get_subdevice_type(
        "/api/vcenter/vm/{vm}/guest/processes/{pid}?action=delete"
    )
    if subdevice_type and not params[subdevice_type]:
        _json = await exists(params, session, build_url(params))
        if _json:
            params[subdevice_type] = _json["id"]
    _url = (
        "https://{vcenter_hostname}"
        "/api/vcenter/vm/{vm}/guest/processes/{pid}?action=delete"
    ).format(**params) + gen_args(params, _in_query_parameters)
    async with session.post(_url, json=payload) as resp:
        try:
            if resp.headers["Content-Type"] == "application/json":
                _json = await resp.json()
        except KeyError:
            _json = {}
        return await update_changed_flag(_json, resp.status, "delete")


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
