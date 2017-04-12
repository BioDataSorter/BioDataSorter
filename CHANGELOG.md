# Change Log
All notable changes will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [2.0.2]
### Added
- locate_columns method and col_nums global variable to consolidate information
- GUI_DEBUG global variable in layout.py to pass update_color during debugging
- key in the progress bar space

### Fixed
- error message about manual synonyms column input corrected
- status bar will always align with bottom of window (added anchor=s)

### Removed
- wordcloud debugging print statements that locate DroidSansMono.ttf
- hovering key over wordcloud

## [2.0.1]
### Fixed
- Column Error message boxes no longer display the message as the title
- form_elements now contains manually inputted column names as a list of strings

### Removed
- extra exception catcher for columns because of existing test in remove_duplicates

## [1.0.2]
### Changed
- optimized imports for py2exe

### Fixed
- status bar

## [1.0.1]
### Changed
- layout on form is evened out

## Fixed
- all colors show up in wordcloud run from source (not just red)

## [1.0.0]
### Changed
- only includes nonzero values in the quartiles, but they remain in the wordcloud

### Fixed
- made notebook frame larger to accommodate previous Windows OSs
- fixed positioning of the start page for above reason

## [Unreleased]
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
