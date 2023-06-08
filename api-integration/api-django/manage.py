#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Django divide la funcionalidad de un proyecto en aplicaciones. Cada aplicación gestiona una parte distinta del proyecto.

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'countryapi.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
