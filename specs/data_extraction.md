# Data Extraction Pipeline

**Objective** Given the company name, search the company directory in /assets/Company Data/ and extract all the document content except pitch Data and store it in /outputs/<company-name>/ref-data

## Implementation Details

1. After the questionnaire agent returns the questionnaire and stores it, the data extraction pipeline should start and search for the startup directory in /assets/Company Data/ . Try using regex because directory name could be of different form. Just check if the startup name is present in any of the directory.

2. If don't find the startup directory, terminate the process with log mentioning no reference data was avaialalbe.

However if you find the directory, check all the files inside it. Iterate over each file(except pitch deck file) and extract the information and store it in /outputs/<company-name>/ref-data/.

Ex. If there is any file that has 'Founders Checklist'(can be pdf or docx) in the name, extract the content and store it in /outputs/<company-name>/ref-data/ref-founders-checklist.md.
