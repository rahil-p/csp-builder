# csp-builder

[![docker-image][docker-image-badge]][docker-image]

A simple Docker executable for parsing Content Security Policies from YAML configuration files, including support 
for environment variables.

## Motivation

Content Security Policy serves to mitigate cross-site attacks by allowing web admins to declare the resources 
that their sites are permitted to access. Because websites often rely on several internal and third-party services,
maintaining CSP restrictions can become an elaborate task with ongoing accumulation and pruning. Furthermore, policies 
are serialized in a format that is challenging to maintain<sup id='fnr-1'>[1](#fn-1)</sup>, e.g.:

```
default-src 'none';frame-ancestors 'self';frame-src https://app.my-site.com https://bid.g.doubleclick.net;connect-src https://api.my-site.com wss://chat.my-site.com;script-src 'report-sample' 'self' https://tagmanager.google.com https://ssl.google-analytics.com https://www.google-analytics.com;img-src https://www.google.com https://ssl.gstatic.com https://www.gstatic.com;style-src https://tagmanager.google.com https://fonts.googleapis.com;font-src data: https://fonts.gstatic.com;manifest-src 'self';worker-src 'self';base-uri 'self';form-action 'none';report-to https://o0.ingest.sentry.io/api/0/security/?sentry_key=someKey
```

This Docker image serves as a tool to support YAML configurations for CSP ([example](#examples)). Furthermore, it can be used 
in multi-stage builds or CI pipelines to insert policies in server configs or HTML `meta` tags.

<sup id='fn-1'>[[1]](#fnr-1) Splitting policies into multiple headers is not equivalent as user agents are expected to 
enforce each policy independently ([details][w3#multiple-policies])</sup>

## Usage

```shell
python -m build-csp [options] in[:out] [in[:out] ...]
```

### Positional Arguments:

- `in[:out]`  
_input path of YAML file with an optional output path, which defaults to `stdout`_

### Optional Arguments:

- `-l`, `--lax`  
_disable exceptions for unset environment variables_

- `-p`, `--no-minify`  
_disable minification of policy outputs_

- `-k`, `--keep-ports`  
_disable stripping default p  orts for URI schemes_

- `-n`, `--nginx-format`  
_format the output as an nginx `add_header` directive_



## Examples
With a YAML configuration file `csp.yaml`:
```yaml
Content-Security-Policy:
  default-src: 
    - "'none'"
  script-src:
    - "'self'"
  connect-src:
    - "'self'"
    - https://${API_DOMAIN}:${API_PORT}
  font-src:
    - "'self'"
    - https://my-site.com
  base-uri:
    - "'self'"
  report-to:
    - ${CSP_REPORT_URI}
```
___

To run the image locally as an executable:

```shell
docker run --rm --volume $(pwd):/var/csp/ \
  rahilp/csp-builder:latest /var/csp/csp.yaml:/var/csp/csp.txt
```

Running this command will write the policy to `csp.txt` in the working directory.
___

To run in a multi-stage Dockerfile for NGINX:

```dockerfile
FROM rahilp/csp-builder:latest AS build-csp

COPY csp.yaml /var/csp/

RUN python -m csp-builder --nginx-format /var/csp/csp.yaml:/var/csp/csp.conf

FROM nginx:latest

COPY config/ /etc/nginx/
COPY --from=build-csp /var/csp/csp.conf /etc/nginx/partials
```

NGINX configs can add the header to contexts by reference with:

```nginx
include /etc/nginx/partials/csp.conf;
```

[w3#multiple-policies]: https://www.w3.org/TR/CSP3/#multiple-policies

[docker-image-badge]: https://img.shields.io/docker/v/rahilp/csp-builder?label=docker

[docker-image]: https://hub.docker.com/r/rahilp/csp-builder/tags

