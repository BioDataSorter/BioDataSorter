# BioDataSorter

<h2>Summary</h2>

This is a project that we are working on for Winthrop University Hospital for genes to study in diabetes and multiple sclerosis. The program takes data in the form of Excel spreadsheets that have a gene 'Symbol' column and 'Synonyms' column, like the spreadsheets that can be downloaded from NCBI's Gene Expression Omnibus (GEO), which is a public functional genomics data repository for array-based and sequence-based data. Please fork us and let us know what could be improved or fixed!

<h4>Sample Excel File Format</h4>
<img src='./images/readme/sampledata.PNG' />

<h2>How to Get NCBI GEO Data</h2>
<ol>
<li>Search a keyword in <a href="http://www.ncbi.nlm.nih.gov/geo">GEO</a></li>
<li>Click on the datasets results</li>
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
<li>Clone the repository to your computer</li>
<li>Make sure you have Python 3 installed on your computer as well as all of the dependencies
<ul>
<li>Biopython</li>
<li>Pillow</li>
<li>Openpyxl</li>
<li>Requests</li>
<li>Mygene</li>
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
<li>Click the arrow in FormPage or press Run from the AdvancedPage</li>
<li>Wait for the program to finish</li>
</ol>
