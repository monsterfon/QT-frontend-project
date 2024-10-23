import os
import logging
import logging.config


# Log levels
_LOG_LEVELS = ('TRACE', 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')


def parser_add_logging_arguments(parser):
    parser.add_argument(
        '--log-level',
        choices=_LOG_LEVELS,
        metavar='level',
        default=None,
        help="Log level (one of: {})".format(', '.join(_LOG_LEVELS), ),
    )
    parser.add_argument(
        '--log-config',
        type=str,
        metavar='file',
        default=None,
        help="Log config file (defaults to logging.conf if it exists).",
    )


def setup_logging(args, default_level='WARN', default_config='logging.conf'):
    if args.log_config:
        # Config file is explicitly given
        assert os.path.isfile(args.log_config), f"Logging config file {args.log_config} does not exist!"
        logging.config.fileConfig(args.log_config)
    elif args.log_level:
        # Log level is explicitly given
        logging.basicConfig(level=args.log_level)
    else:
        # Neither is given; check if default logging conf file exists
        if default_config and os.path.isfile(default_config):
            logging.config.fileConfig(default_config)
        else:
            logging.basicConfig(level=default_level)
