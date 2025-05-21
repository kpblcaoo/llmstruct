"""Utility functions for the sample project."""

import logging

def helper():
    """Help the main function."""
    log("Helper called")

def log(message: str):
    """Log a message."""
    logging.info(message)