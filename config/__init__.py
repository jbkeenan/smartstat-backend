"""
Package initialisation for the config module.

Exposes the Celery application instance as ``celery_app`` for
conventional import patterns, e.g.::

    from config import celery_app

Having this here ensures Celery is loaded and autodiscovers tasks
whenever Django starts.
"""

from .celery import app as celery_app  # noqa: F401

__all__ = ('celery_app',)