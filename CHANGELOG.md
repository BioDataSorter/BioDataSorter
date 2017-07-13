# Change Log
All notable changes will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [2.0.9] - 7-11-2017
### Added
- extra row get descriptions is selected to note Entrez_ID

### Fixed
- cannot connect to internet error modified to PubMed error

## [2.0.8] - 7-1-2017
### Changed
- log file is now called app.log instead of myapp.log
- progress info prints to stdout as well as app.log file

### Fixed
- blank first column in output caused by faulty None test
- descriptions checked first column which was blank

## [2.0.7] - 6-20-2017
### Changed
- changed print to console to logging to a .log file

## [2.0.6] - 5-11-2017
### Added
- displays amount of time the process takes in popup and console

## [2.0.5] - 5-6-2017
### Added
- sort options (high to low or low to high) (updated config saving for this)

### Changed
- GUI for advanced page has options

## [2.0.4] - 4-14-2017
### Changed
- window width 30 pixels wider to accommodate other operating systems
- add parenthesis around all synonyms (multiple words increase the number of citations)

### Fixed
- descriptions query now accesses the right column
- position of the output columns
- spacing on the title page should be fixed
- rounding in wordcloud which posed a problem for smaller sets of data
- hopefully fixed comment sizing (added "pt" to the end of the strings)

## [2.0.3] - 4-12-2017
### Changed
- symbol column is moved to first column in output
- updated word cloud samples

### Fixed
- symbol column and synonyms column headers are changed to standard headers
and are now compatible with the wordcloud feature
- progress bar correctly disappears after process runs

## [2.0.2] - 4-11-2017
### Added
- locate_columns method and col_nums global variable to consolidate information
- GUI_DEBUG global variable in layout.py to pass update_color during debugging
- key in the progress bar space
- key appears only when output page is selected

### Fixed
- error message about manual synonyms column input corrected
- status bar will always align with bottom of window (added anchor=s)
- ignores capitalization of column titles in Excel file
- openpyxl library updated to 2.4.5 for better compatibility with Excel

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
