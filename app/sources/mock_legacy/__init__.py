"""Sous-module MockLegacy : adapter de source pour fixtures JSON legacy.

Démontre la stabilité du contrat exposé face à un format de stockage
volontairement divergent (camelCase, Unix timestamps, dotted metrics,
metadata imbriquée). Le mapping est isolé dans mapping.py pour testabilité.
"""
