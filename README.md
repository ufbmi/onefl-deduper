
# OneFL Deduper

| Branch | [Travis-CI] | [Coveralls] |
| :----- | :---------------------------: | :-------: |
| Master | [![Build Status](https://travis-ci.org/ufbmi/onefl-deduper.svg?branch=master)](https://travis-ci.org/ufbmi/onefl-deduper?branch=master) | [![Coverage Status](https://coveralls.io/repos/github/ufbmi/onefl-deduper/badge.svg?branch=master)](https://coveralls.io/github/ufbmi/onefl-deduper?branch=master) |
| Develop | [![Build Status](https://travis-ci.org/ufbmi/onefl-deduper.svg?branch=develop)](https://travis-ci.org/ufbmi/onefl-deduper?branch=develop) | [![Coverage Status](https://coveralls.io/repos/github/ufbmi/onefl-deduper/badge.svg?branch=develop)](https://coveralls.io/github/ufbmi/onefl-deduper?branch=develop) |

# Intro

Welcome to the OneFlorida "De-Duper" tool.

This tool genereates "Linkage Unique Identifiers" (LUID's)
used for patient de-duplication (aka "Entity Resolution", aka "Record Linkage").


The current plan is to have a CSV files as input for two separate scripts
as in the diagram below:

<pre>

    +- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    |   Partner Domain
    |
    |    (CSV file with PHI)                                (CSV file with no PHI)
    |   +--------------------------+                       +--------------------------+
    |   |   PHI_DATA.csv           | ----> hasher.py ----> |    HASHES.csv            |
    |   | patid, first, last,      |                       | patid, F_L_D_G, F_L_D_R  |
    |   | dob, sex, race           |                       |                          |
    |   +--------------------------+                       +--------------------------+
    |                                                            ||
    +- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - || - - - - - -
    |   OneFlorida Domain                                        \/
    |                                                       +--------------------------+
    |                                                       | OneFlorida SFTP Server   |
    |                                                       +--------------------------+
    |                                                            ||
    |                                                            ||
    |                                                            \/
    |                                                       +--------------------------+
    |                                                       |   HASHES.csv             |
    |                                                       | patid, F_L_D_G, F_L_D_R  |
    |                                                       +--------------------------+
    |                                                            |
    |      ____________                                          |
    |    /              \                                        |
    |   |               /|                                      /
    |   |\_____________/ |                                     /
    |   |              | |  <------------- linker.py <--------
    |   |  UF Database | |
    |   |              |/
    |    \_____________/
    |
    |       (Links between hashes -> UUID's)
    |                                                             _____   O
    |       patid, partner_code, linkage_uuid, linkage_hash      / /     -+-
    |         123,          UFH,       abc...,       def...   <-- /       |
    |         456,          FLM,       abc...,       def...   <--        / \
    |         789,          FLM,       987...,       012...
    |
    |    (generate OF_ID from hashes)
    |
    + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
</pre>

# Installation

The two components of the application
([hasher](run/hasher.py), [linker](run/linker.py)) need proper configuration in
order to function. For more details please refer to the
[docs/installation.md](docs/installation.md)

The format for the input file for the `hasher` component is described in the 
[input-specs.md](docs/input-specs.md) document.


# References

- CAPriCORN: Chicago Area Patient-Centered Outcomes Research Network - https://www.ncbi.nlm.nih.gov/pubmed/24821736
- http://infolab.stanford.edu/serf/
- "Swoosh: A Generic Approach to Entity Resolution" - http://link.springer.com/article/10.1007%2Fs00778-008-0098-x

