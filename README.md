# BioDataSorter

Please fork us and let us know what could be improved or fixed!
<h2>Summary</h2>

This is a project that we are working on for Winthrop University Hospital for genes to study in diabetes and multiple sclerosis. The program takes data in the form of Excel spreadsheets that have a gene 'Symbol' column and 'Synonyms' column, like the spreadsheets that can be downloaded from NCBI's Gene Expression Omnibus (GEO), which is a public functional genomics data repository for array-based and sequence-based data. Sample data for input and output into the program can be found in the <a href='https://github.com/BioDataSorter/BioDataSorter/tree/master/Sample%20Data'>Sample Data folder</a>.

<h2>How to Get NCBI GEO Data</h2>
(Soon to be automated from program!)
<ol>
<li>Search a keyword in <a href="http://www.ncbi.nlm.nih.gov/geo">GEO</a></li>
<li>Click on the datasets results<br />
<img src='./images/readme/howtousegeo.PNG'/></li>
<li>Click on a result that interests you</li>
<li>Click on <i>Compare 2 sets of samples</i> and choose sample groups to analyze gene fluctuations</li>
<img src='./images/readme/data_analysis_tools.PNG' />
<li>Follow the link under <i>Step 3</i>, which will lead you to the profile data results</li>
<li>Change the <i>Items per page</i> to 500</li>
<img src='./images/readme/items_per_page.PNG' />
<li>Click the <i>Download profile data</i> button in the right margin.</li>
<li>Convert the .txt document to a .xlsx document</li>
</ol>

<h2>How to Use BioDataSorter</h2>
<ol>
<li>Clone or download the repository to your computer</li>
<li>Make sure you have Python 3 installed on your computer as well as all of the dependencies
<ul>
<li>Biopython- can be installed from <a href="https://github.com/biopython/DIST">Biopython on GitHub</a> for 32-bit versions or 
<a href="http://www.lfd.uci.edu/~gohlke/pythonlibs/#biopython">www.lfd.uci.edu</a> for a 64-bit version</li>
<li>
Use pip to install the rest of the requirements
<ol>
<li>Make sure pip is in your environment variables' PATH variable as C:\Python34\Scripts\pip</li>
<li>In command prompt, navigate to the BioDataSorter repository and run <code>python -m pip install -r requirements.txt</code></li>
<li>If this doesn't work, install each one separately (Pillow, openpyxl, requests, mygene) using <code>python -m pip install <i>requirement</i></code></li>
</ol>
</li>
</ul>
</li>
<li>Run main.py in command prompt by navigating to your local repository and typing <code>python main.py</code></li>
<li>The window will pop up</li>
<img src='./images/readme/window.png' width='500px' />
<li>Click new and input data</li>
<li>Right-click and select <i>More Options</i></li>
<li>Change the Symbol Column to the input's <i>Symbol</i> or <i>Gene Symbol</i> column letter</li>
<li>Change the Synonyms Column to the input's <i>Synonyms</i> or <i>Gene Title</i> column letter</li>
<li>Select any other options you wish to include in your output</li>
<li>Click run in the Form page or from the Run Menu</li>
<li>Wait for the program to finish</li>
</ol>

<h2>Contact Us</h2>
Email: caitlinchou@gmail.com
