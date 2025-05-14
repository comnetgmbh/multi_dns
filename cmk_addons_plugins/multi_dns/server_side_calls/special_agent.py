#!/usr/bin/env python3
#2024 Comnet GmbH, Andreas Decker

from cmk.server_side_calls.v1 import (
    noop_parser,
    SpecialAgentCommand,
    SpecialAgentConfig,
)


def _agent_arguments(params, host_config):
    args = [str(params['timeout'])]
    for domain in params["target_domains"]:
        if domain:  # ignore accidentally added empty fields and prevent confusing CRIT states
            args.append(domain)
    yield SpecialAgentCommand(command_arguments=args)


special_agent_multi_dns = SpecialAgentConfig(
    name="multi_dns",
    parameter_parser=noop_parser,
    commands_function=_agent_arguments
)
