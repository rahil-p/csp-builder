import argparse

from .parse import serialize_csp

if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage=('python -m build-csp '
                                            '[options] '
                                            'in[:out] [in[:out] ...]'),
                                     description='Serialize Content Security Policy values from YAML configurations',
                                     epilog=('W3:  https://www.w3.org/TR/CSP3 | '
                                             'MDN: https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP'))
    parser.add_argument(dest='io_pairs', nargs='+',
                        type=lambda kv: kv.split(':', 1),
                        metavar='in[:out]',
                        help='input path (to YAML file) with an optional output path (defaults to `stdout`)')
    parser.add_argument('-l', '--lax',
                        dest='strict', action='store_false',
                        help='disable exceptions for unset environment variables')
    parser.add_argument('-p', '--no-minify',
                        dest='minify', action='store_false',
                        help='disable minification of policy outputs')
    parser.add_argument('-k', '--keep-ports',
                        dest='normalize_ports', action='store_false',
                        help='disable stripping default ports for URI schemes')
    parser.add_argument('-n', '--nginx-format',
                        dest='nginx_format', action='store_true',
                        help='format the output as an nginx `add_header` directive')

    args = parser.parse_args()
    kwargs = {k: v for k, v in vars(args).items() if k != 'io_pairs'}

    for in_path, *out in args.io_pairs:
        if not in_path:
            raise ValueError('Input path is missing in the argument')

        result = serialize_csp(in_path, **kwargs)

        if (out_path := next(iter(out), 'stdout')) and out_path != 'stdout':
            with open(out_path, 'a+') as f:
                f.write(f'{result}\n')
        else:
            print(result)
