"""
Goal: avoid duplicating partner name strings

@authors:
    Andrei Sura <sura.andrei@gmail.com>

Example usage:

>>> from onefl.partner_name import PartnerName
>>> print(PartnerName.HCN.value)
==> HCN
"""

import importlib
import sys

from enum import Enum, unique


@unique
class PartnerName(Enum):
    """
    3-letter partner names
    """
    HCN = 'HCN'     # Health Choice Network
    BND = 'BND'     # Bond Community Hospital
    UMI = 'UMI'     # University of Miami

    FLM = 'FLM'     # Florida Medicaid Claims (aka ICHP)
    CHP = 'CHP'     # Capital Health Plan Claims

    UFH = 'UFH'     # University of Florida Health
    TMC = 'TMC'     # Tallahassee Memorial Hospital - Cerner
    TMA = 'TMA'     # Tallahassee Memorial Hospital - Allscripts
    ORH = 'ORH'     # Orlando Health

    FLH = 'FLH'     # Florida Hospital
    MCH = 'MCH'     # Miami Children's Hospital


VALID_PARTNERS = [p.value for p in list(PartnerName)]
VALID_PARTNERS_LOWERCASE = [p.value.lower() for p in list(PartnerName)]
