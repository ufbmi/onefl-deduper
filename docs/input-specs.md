# Specification for the input file

As described in the [installation-redhat.md](installation-redhat.md) document,
the `hasher` component requires the input csv file to conform to a specific
format.

The expected column headers need to be:
`patid`, `first`, `last`, `dob`, `sex`, `race`

The `patid` column should match the values sent to our SFTP server in the
demographics file during the regular data submissions. The date of birth 
column must be in the `YYYY-MM-DD` format.

In addition to that, the `sex` and `race` columns **must have values**
from the list specified in the PCORI Common Data Model 3.0 
[official document](http://www.pcornet.org/wp-content/uploads/2014/07/2015-07-29-PCORnet-Common-Data-Model-v3dot0-RELEASE.pdf)

- `sex`

    Allowed values:

    * A  = Ambiguous
    * F  = Female
    * M  = Male
    * NI = No information
    * UN = Unknown
    * OT = Other

- `race`

    Allowed values:

	* 01 = American Indian or Alaska Native
	* 02 = Asian
	* 03 = Black or African American
	* 04 = Native Hawaiian or Other Pacific Islander
	* 05 = White
	* 06 = Multiple race
	* 07 = Refuse to answer
	* NI = No information
	* UN = Unknown
	* OT = Other

Note: The current version of the software is not checking for conformance to the
rules above but it will do so in the next version.
