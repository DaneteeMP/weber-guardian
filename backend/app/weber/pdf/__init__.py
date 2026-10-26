"""Offer PDF generator (WeasyPrint + Jinja2).

Public entry point for the composition root (app.main): ``build_offer_pdf``
is the renderer's ``render_document`` under the stable domain name the API
has always imported. Internals (token values, executor blocks) live in
app.weber.pdf.values and are imported directly by their tests.
"""
from app.weber.pdf.renderer import render_document as build_offer_pdf

__all__ = ["build_offer_pdf"]
