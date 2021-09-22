# csp-builder

[![docker-image][docker-image-badge]][docker-image]

A simple Docker executable for parsing Content Security Policies from YAML configuration files, including support 
for environment variables.

## Motivation

Content Security Policy is represented by a linefeed <a href='#fn-1'><sup id='fnr-1'>(1)</sup></a>, which 
can be inconvenient to maintain.

An example:

```
default-src 'none';frame-ancestors 'self';frame-src https://app.my-site.com https://bid.g.doubleclick.net;connect-src https://api.my-site.com wss://chat.my-site.com;script-src 'report-sample' 'self' https://tagmanager.google.com https://ssl.google-analytics.com https://www.google-analytics.com;img-src https://www.google.com https://ssl.gstatic.com https://www.gstatic.com;style-src https://tagmanager.google.com https://fonts.googleapis.com;font-src data: https://fonts.gstatic.com;manifest-src 'self';worker-src 'self';base-uri 'self';form-action 'none';report-to https://o0.ingest.sentry.io/api/0/security/?sentry_key=someKey
```

This Docker image provides support for configuring Content Security Policy in YAML ([example](#examples)). It can be 
used in multi-stage builds or CI pipelines to insert policies in server configurations. Furthermore, it
supports environment variables to allow configuration for different deployment environments.

<sup id='fn-1'>[1](#fnr-1) Splitting policies into multiple headers is not equivalent as user agents are expected to 
enforce comma-delimited policies independently (</sup><a href='https://www.w3.org/TR/CSP3/#multiple-policies'><sup>details</sup></a><sup>)</sup>

## Usage

Python module:

```shell
python -m build-csp [options] in[:out] [in[:out] ...]
```

### Positional Arguments:

- `in[:out]`

  > input path of YAML file with an optional output path, which defaults to `stdout`

### Optional Arguments:

- `-l` `--lax`

  > disable exceptions for unset environment variables

- `-p` `--no-minify`

  > disable minification of policy outputs

- `-k` `--keep-ports`

  > disable stripping default ports for URI schemes

- `-n` `--nginx-format`
  > format the output as an nginx `add_header` directive


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

### To run the image locally as an executable:

```shell
docker run --rm --volume $(pwd):/var/csp/ \
  rahilp/csp-builder:latest /var/csp/csp.yaml:/var/csp/csp.txt
```

Running this command will write the policy to `csp.txt` in the working directory.


### To run in a multi-stage Dockerfile for NGINX:

```dockerfile
# Stage 1: Serialize the policy (formatted as an NGINX `add_header` directive)
FROM rahilp/csp-builder:latest AS build-csp

COPY csp.yaml /var/csp/

RUN python -m csp-builder --nginx-format /var/csp/csp.yaml:/var/csp/csp.conf

# Stage 2: Configure the NGINX image with the built policy from Stage 0
FROM nginx:latest

COPY config/ /etc/nginx/
COPY --from=build-csp /var/csp/csp.conf /etc/nginx/partials
```

NGINX configs can add the header by reference with:

```nginx
include /etc/nginx/partials/csp.conf;
```

[docker-image-badge]: https://img.shields.io/docker/v/rahilp/csp-builder?label=docker

[docker-image]: https://hub.docker.com/r/rahilp/csp-builder/tags

