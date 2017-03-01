# Change Log


## [0.0.4] - unreleased yet


## [0.0.3a] - 2017-03-01
### Changed
 * consider race=07 (refused to answer) the same as UN, thus not generating a hash for rules involving this race value (Jiang Bian)


## [0.0.3] - 2017-02-28 :)

### Fixed
 * [BUG]: used `ahash_1` instead of `ahash_2` variable

### Added
 * draft installation steps for restricted windows

### Changed
 * [hasher]: make it faster using mp + introduced dependency on `dill` package
 * [hasher]: implement the `missing values` rule for RACE and SEX if value in ['NI', 'UN', 'OT'] ==> no hash is generated

 * [linker]: create a UUID even for patients with zero hashes
 * Allow nulls in the `linkage_hash` column since some patients do not have all required data elements
 * [schema]: update linkage table with `rule_id` + `fk_linkage_rule_id`
 * [linker]: fix error with un-set flag + do not create tables using SQLAlchemy
 * [linker]: update example config file file
 * logging: search the config file under `cwd`
 * Split requirements into two to reduce dependencies for pypi installs
 * [linker]: add logic for logging hashes that resolve to two distinct UUIDs
 * [linker]: update schema definition for UUID use varchar(32) instead of binary(16)
 * [linker]: changed the model to use a `text` field for UUIDs instead of `binary` (for compatibility with the PCORI tables)
 * [linker]: when there is only one hash provided store the link object in the proper slot 
+ return a link when hashes resolve to two different UUID's

 * [linker]: implement 2 changes per Jiang - if only one of the two hashes is found re-use existing UUID
   (previously we were giving precedence to the `rule_1` hash by generating a new UUID)


## [0.0.2] - 2017-02-09
### Added
* hasher logic for validating `race` and `sex`
* linker `rule` and `flag` columns
* linker code for enforcing the dominant rule


## [0.0.1c] - 2017-01-11
## Added
* Tasks for `develop` installation/removal


## [0.0.1b] - 2017-01-10
### Added
* Scheleton file `run/deduper.py`

### Changed 
* Moved `onefl/run_*` scripts to `run/` folder


## [0.0.1a] - 2017-01-10
### Added
* Support for reading a dedicated config file
* Support for packaging


## [0.0.1] - 2017-01-09
### Added
* `gen_hashes.py` - script for generating hashes from PHI.csv files
