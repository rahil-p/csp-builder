# csp-builder

[![docker-image][docker-image-badge]][docker-image]
[![github-workflow][github-workflow-badge]][github-workflow]

A simple Docker executable for parsing Content Security Policies from YAML configuration files, including support for 
environment variables.

## Motivation

Content Security Policy is represented by a linefeed <a id='fnr-1' href='#fn-1'><sup>(1)</sup></a>, which can become
inconvenient to maintain. This is especially the case when several backing services require access from varying 
deployment environments.

This Docker image provides support for configuring Content Security Policy in YAML.

For example, instead of maintaining CSP in this kind of format:
```
default-src 'none';frame-ancestors 'self';frame-src https://app.third-party.com:8080;connect-src https://qa-api.my-site.com wss://qa-chat.my-site.com:*;script-src 'self' 'report-sample';style-src 'self' https://fonts.googleapis.com;font-src data: https://fonts.gstatic.com;report-to https://o0.ingest.sentry.io/api/0/security/?sentry_key=examplekey
```

...it can be managed with more structure and readability in YAML like:
```yaml
Content-Security-Policy:
  default-src:
    - 'none'
  frame-ancestors:
    - 'self'
  frame-src:
    - https://${WEBAPP_DOMAIN}:8080
  connect-src:
    - https://${API_SUBDOMAIN}.my-site.com
    - wss://${CHAT_SUBDOMAIN}.my-site.com:*
  script-src:
    - "'self'"
    - "'report-sample'"
  style-src:
    - "'self'"
    - https://fonts.googleapis.com # Google Fonts
  font-src:
    - 'data:'
    - https://fonts.gstatic.com # Google Fonts
  report-to:
    - https://o0.ingest.sentry.io/api/0/security/?sentry_key=${SENTRY_PUBLIC_KEY}
```

This image can be used in multi-stage builds or CI pipelines to insert CSP headers in server configurations or `meta`
tag equivalents in HTML. Furthermore, it supports environment variables to allow configuration for different deployment 
environments.

<a id='fn-1' href='fnr-1'><sup>1</sup></a>
<sup>
  Splitting policies into multiple headers is not equivalent as user agents are expected to enforce comma-delimited 
  policies independently | 
</sup>
<a href='https://www.w3.org/TR/CSP3/#multiple-policies'><sup>details</sup></a>

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

#### To run the image locally as an executable:

```shell
docker run --rm \
  --volume $(pwd):/var/csp/ \
  --env-file ./.env
  rahilp/csp-builder:latest /var/csp/csp.yaml:/var/csp/csp.txt
```

Running this command will write the policy to `csp.txt` in the working directory.

#### To run in a multi-stage Dockerfile for NGINX:

```dockerfile
# Stage 1: Serialize the policy (formatted as an NGINX `add_header` directive)

FROM rahilp/csp-builder:latest AS build-csp

# Define build arguments
ARG API_SUBDOMAIN
ARG CHAT_SUBDOMAIN
ARG WEBAPP_DOMAIN
ARG SENTRY_PUBLIC_KEY

# Export build arguments to environment variables
ENV API_SUBDOMAIN ${API_SUBDOMAIN}
ENV CHAT_SUBDOMAIN ${CHAT_SUBDOMAIN}
ENV WEBAPP_DOMAIN ${WEBAPP_DOMAIN}
ENV SENTRY_PUBLIC_KEY ${SENTRY_PUBLIC_KEY}

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

[docker-image-badge]: https://img.shields.io/docker/v/rahilp/csp-builder?logo=docker
[github-workflow-badge]: https://img.shields.io/github/workflow/status/rahil-p/csp-builder/ci?logo=github

[docker-image]: https://hub.docker.com/r/rahilp/csp-builder/tags
[github-workflow]: https://github.com/rahil-p/csp-builder/actions

