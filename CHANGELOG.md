# Change Log
All notable changes will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

##[1.0.0]
### Added

### Changed
- only includes nonzero values in the quartiles, but they remain in the wordcloud

### Fixed
- made notebook frame larger to accommodate previous Windows OSs
- fixed positioning of the start page for above reason

##[Unreleased]
### Added
- Convert function (found under file menu) to convert .txt files
generated from GEO profile data to .xlsx files
- added auto or manual options for getting symbol/synonyms columns
- added word cloud feature
- tests internet connection before process starts
- status bar describes more features (such as the task the progress bar is up to)
- added run menu to menubar
- can change background color in settings

### Changed
- gets all form elements in the beginning and stores them globally to limit usage of root
- updated start page with actual link
- changed run arrow to run button and added more options button

### Fixed
- program is compatible with GEO files (eliminates empty rows / rows w/o gene symbol)
- fixed clearing Top X Genes
