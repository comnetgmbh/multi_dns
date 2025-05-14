# Check multiple local DNS servers
This package contains a Checkmk special agent which parses the locally configured `/etc/resolv.conf` to find configured DNS servers and then attempts to resolve a configured list of domains with each of them, reporting response time and whether resolution was successful.

The check fills a small niche left by the built in DNS Check and the Agent Plugin provided by Checkmk itself, by providing a transparent way to check all available DNS servers on the site and taking the mystery out of sporadic resolution failures or long resolution times.

Please keep in mind, this runs on a Checkmk site, it is not deployed to a host.
