#!/usr/bin/env python

import logging

from cleo.application import Application

from .commands import ReconcileCommand

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    application = Application()
    application.add(ReconcileCommand())

    application.run()
