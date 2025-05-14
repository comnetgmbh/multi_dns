#!/usr/bin/env python3
#2024 Comnet GmbH, Andreas Decker

from cmk.rulesets.v1.form_specs import Dictionary, DictElement, Float, Integer, List, String, SimpleLevels, \
    LevelDirection, DefaultValue
from cmk.rulesets.v1.rule_specs import SpecialAgent, CheckParameters, Topic, Help, Title, HostCondition


def _formspec_special_agent():
    return Dictionary(
        title=Title("Check multiple local DNS servers (Linux)"),
        elements={
            "target_domains": DictElement(
                required=True,
                parameter_form=List(
                    title=Title("Domains which are resolved with all configured DNS servers."),
                    element_template=String(),
                    editable_order=True,
                    help_text=Help(
                        "Each domain listed here will be resolved with all DNS servers configured in '/etc/resolv.conf'.")
                )
            ),
            "timeout": DictElement(
                required=True,
                parameter_form=Integer(
                    title=Title("Timeout (seconds) until agent stops trying to resolve each domain."),
                    unit_symbol="seconds",
                    prefill=DefaultValue(value=5),
                    help_text=Help(
                        "Values less than 1 quietly default to 1. Be wary of large values and many domains slowing the check in timeout scenarios.")
                )
            ),
        }
    )


def _formspec_check_params():
    return Dictionary(
        title=Title("Check multiple local DNS servers (Linux)"),
        elements={
            "res_time_upper": DictElement(
                required=True,
                parameter_form=SimpleLevels(
                    title=Title("The average upper response time (ms) to determine check status."),
                    form_spec_template=Float(),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=DefaultValue(value=(500.0, 1000.0)),
                )
            ),
        }
    )


rule_spec_multi_dns = SpecialAgent(
    topic=Topic.NETWORKING,
    name="multi_dns",
    title=Title("Check DNS for locally set resolvers"),
    parameter_form=_formspec_special_agent
)

rule_spec_check_params = CheckParameters(
    topic=Topic.NETWORKING,
    name="multi_dns_check_params",
    title=Title("Check DNS for locally set resolvers"),
    condition=HostCondition(),
    parameter_form=_formspec_check_params
)
