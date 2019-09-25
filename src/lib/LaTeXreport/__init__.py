"""LaTeX library

Functions to programmatically generate a LaTeX/PDF document through Python.
Upon initialization of the report project, a directory will be created, 
containing all the different tpyes of objects/sections that you can add to 
to populate your report. 

The actual report document generated will be a very rough skeleton, 
to allow you more flexibility in your writing while still providing some 
initial structure to keep your files in order. 

## Report Style 
Documents generated can be specified to be in a standard arxiv report template.
To generate this template, the `arxiv.sty` file must be located in the same file path
as the `*.tex` file. 
For the default style, remove "arxiv" from the packages list in the json config file.

## Figures 
Figures added with the addFigure function will be added to the end of the report. 

The default setting is for images to be stretched to fill the page width.
Options can be specified to configure otherwise. 
For example, small images can be scaled down ("options" : "scale=0.8") 
or images too large for the page can have reduced height ("options" : "height=0.8\textheight")

## Tables
All Tables listed in the 'tables' section will be generated into tex files.
Filename(s) of the actual data must be provided under 'files'.
If multiple files are specified, they will be concatenated together.
A single tex file will be generated and stored in the tables directory.

## Appendix 
Mapping/LookUp tables in the form of csv files can be added to the end of the report. 
List the file names under the 'appendix' list of the jsonConfig. 
Accepts csv files with 2 or 3 columns and performs different operations. 

## Sections 
Report sections can be added using the addSections function. 
A tex file will be created for each section you add, under the sections directory.
You can also add subsections and subsubsections by defining the level. 

The sections will later be added to the report in order.
"""