#!/usr/bin/env python3
#2024 Comnet GmbH, Andreas Decker

import re

from cmk.agent_based.v2 import AgentSection, CheckPlugin, Service, Result, State, Metric, check_levels


def _check_result(result):
    pattern_ip = re.compile(r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$")
    pattern_fqdn = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    if pattern_ip.match(result) or all(pattern_fqdn.match(domain) for domain in result.rstrip(".").split(".")):
        return "SUCCESS"
    elif result.startswith("communications error"):
        return "ERROR"
    else:
        return "TIMEOUT"


def _check_response_time(resp_time, timeout_param):
    return float(resp_time) < float(timeout_param) * 1000


def _evaluate_result(dns, test_domain, response_time_ms, timeout_param, result):
    if not _check_response_time(response_time_ms, timeout_param):
        return State.WARN, f"DNS server {dns} took {response_time_ms}ms to resolve {test_domain}"
    elif _check_result(result) == "TIMEOUT":
        return State.CRIT, f"DNS server {dns} did not resolve or timed out resolving {test_domain}"
    elif _check_result(result) == "ERROR":
        return State.CRIT, f"DNS server {dns} not reachable. Cannot resolve {test_domain}"
    else:
        return State.OK, f"DNS server {dns} resolved  {test_domain} successfully"


def _simplify_url(test_domain):
    # clean problematic characters for metric name
    # i.e. "https://docs.checkmk.com/2.2.0/en/devel_check_plugins.html#extend" becomes "docs-checkmk-com"
    test_domain_clean = test_domain
    if test_domain_clean.startswith("http"):
        test_domain_clean = test_domain_clean.split("//")[-1]
    if "/" in test_domain_clean:
        test_domain_clean = test_domain_clean.split("/")[0]
    if "." in test_domain_clean:
        test_domain_clean = test_domain_clean.replace(".", "-")
    return test_domain_clean


def parse_multi_dns(string_table):
    """
    # Example agent output
    127.0.0.53|google.com|.148412670|5|communications error to 127.0.0.53#53: connection refused
    127.0.0.53|microsoft.com|.028631868|5|
    127.0.0.53|comnet-solutions.de|.026186997|5|123.123.123.123

    # Parser output:
    {'127.0.0.53': {
         'google.com': {
             'response_time_ms': 148.41,
             'timeout_param': 5.0,
             'result': 'communications error to 127.0.0.53#53: connection refused'
            },
         'microsoft.com': {
             'response_time_ms': 28.63,
             'timeout_param': 5.0,
             'result': ''
             },
         'comnet-solutions.de': {
             'response_time_ms': 26.19,
             'timeout_param': 5.0,
             'result': '123.123.123.123'
             },
         }
    """
    parsed = {}
    for line in string_table:
        if parsed.get(line[0]):
            parsed[line[0]][line[1]] = {  # test domain
                "response_time_ms": round(float(line[2]) * 1000, 2),
                "timeout_param": float(line[3]),
                "result": line[4]
            }
        else:
            parsed[line[0]] = {
                line[1]: {  # test domain
                    "response_time_ms": round(float(line[2]) * 1000, 2),
                    "timeout_param": float(line[3]),
                    "result": line[4]
                }, }
    return parsed


def discover_multi_dns(section):
    for dns_server in section.keys():
        yield Service(item=dns_server)


def check_multi_dns(item, params, section):
    res_time_upper = params.get("res_time_upper")
    attrs = section.get(item)  # item == dns address
    total_response_time = 0.0
    number_of_domains = 0
    for test_domain in section[item].keys():
        result = section[item][test_domain]["result"]
        timeout_param = section[item][test_domain]["timeout_param"]
        response_time_ms = section[item][test_domain]["response_time_ms"]
        total_response_time += response_time_ms
        number_of_domains += 1
        state, summary = _evaluate_result(item, test_domain, response_time_ms, timeout_param, result)
        yield Result(state=state, summary=summary)

        clean_test_domain = _simplify_url(test_domain)
        yield Metric(
            name=f"response_time_{clean_test_domain}",
            value=response_time_ms,
            boundaries=(0.0, None)
        )

    avg_response_time = total_response_time / number_of_domains
    yield from check_levels(
        avg_response_time,
        levels_upper=res_time_upper,
        metric_name="avg_dns_resolution_time",
        label="Average resolution time",
        render_func=lambda avg_time: f"{avg_time:.2f}ms",
        boundaries=(0.0, None),
    )


agent_section_multi_dns = AgentSection(
    name="multi_dns",
    parse_function=parse_multi_dns,
)

check_plugin_multi_dns = CheckPlugin(
    name="multi_dns_check_params",
    sections=["multi_dns"],
    service_name="DNS resolver %s",
    discovery_function=discover_multi_dns,
    check_function=check_multi_dns,
    check_default_parameters={"res_time_upper": ("fixed", (500.0, 1000.0))},
    check_ruleset_name="multi_dns_check_params",
)
