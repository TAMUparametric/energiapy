"""
Compatibility imports for Vaelchi's chronology-constrained clustering.

Clustering is maintained in Vaelchi. New callers should import ``ahc`` and
``AHCResult`` from ``vaelchi`` directly. This module preserves Energia's
existing public imports, including historical ``AHCResult`` pickle paths.
"""

from vaelchi import AHCResult, ahc

__all__ = ["AHCResult", "ahc"]
