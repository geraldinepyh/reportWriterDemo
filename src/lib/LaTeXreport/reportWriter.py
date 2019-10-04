import pickle
import pandas as pd
import matplotlib.pyplot as plt
import os, glob
import shutil
import jsonref

import pylatex
from pylatex import Document, Section, Subsection, Tabular,  Tabularx, LongTabularx, MultiColumn, NoEscape, Figure, Package, Command, LineBreak, NewLine
from pylatex.utils import bold

class Report():
    def __init__(self, name):
        self.name = name
        self.title = 'Insert Report Title Here'
        self.author = 'Insert Author Name'
        self.date = '01/07/2020'
        self.fpath = os.path.join('../report', self.name)
        self.outputPath = os.path.join(self.fpath, 'output')
        self.doc = Document()
        self.objects = ['sections', 'tables', 'figures', 'mappingTables']
        self.figures = {}
        self.tables = {}
        self.sections = {}
        return 
    
    def makeDirs(self, dirPath):
        """Helper function to make Directories given a specified (dirPath)
        If the sub-directories do not exist, they will be created as well. 
        """
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)
            print('Created', dirPath)
        else: 
            print(dirPath, 'already exists.')
        return
        
    def initialize(self, fpath):
        """Initialize a report project. 
        
        Keyword Arguments:
            fpath {str} -- File path where the report project is to be generated. (default: {'../results'})
        """
        self.makeDirs(fpath)
        subs = list(self.objects) + ['output'] 
        for sub in subs:
            self.makeDirs(os.path.join(fpath,sub))
        self.resetDoc()

        print(f'>> {self.name} report structure has been initialized.')
        return 

    def resetDoc(self):
        """Adds packages and preamble to the document
        when it is to be regenerated. Clears previous entries.
        """
        self.doc=Document()
        pkgs_to_add = [ 'booktabs','hyperref','lipsum','microtype', 'graphicx',\
                        'nicefrac','url','bookmark','tabularx', 'svg']
        pream_to_add = {
                        'title'  : f'{self.title}',
                        'author' : f'{self.author}',
                        'date'   : f'{self.date}'
        }
        for pkg in pkgs_to_add:
            self.doc.packages.append(Package(pkg))
        for pa in pream_to_add:
            self.doc.preamble.append(Command(pa, pream_to_add[pa]))
        self.doc.append(NoEscape(r'\maketitle'))
        return
   
    ########################### ADDING TABLES ########################
    
    def saveTable(self, name, data, path='../tables/', caption='', override=False):
        """Given a pandas dataframe, save to a specified file path 
            as a tex file with the same name, if it doesn't yet exist. 

        Arguments:
            name {str} -- Name of the table of which the tex file will be saved as. 
            data {pandas dataframe or list of dataframes} -- table data that is to be saved. If a list of dataframes is provided as (data), 
            they will be concatenated columnwise (inner join). Hence the tables in the same list must have matching indices. 
        
        Keyword Arguments:
            path {str} -- File path location where the table is to be saved as a tex file. (default: {'../tables/'})
            caption {str} -- Optional caption that will be appended to the next line after the table. (default: {''})
            override {bool} -- Specify whether to override an existing tex file. (default: {False})
        """
        inPath = os.path.join(self.fpath, 'tables', name+'.tex') # to write the tex file in
        outPath = os.path.join(path, name+'.tex') # to point to the tex file? ## Why do i need this

        if not os.path.exists(inPath) or override==True:
            if isinstance(data, list): # concat multiple dataframes 
                dataOut = pd.concat(data, axis=1, sort=False)
                dataOut.fillna(0, inplace=True)
            else: 
                dataOut = data.copy()

            tbl_width = len(dataOut) # handle wide tables 
            with open(inPath,'w') as tf:
                if tbl_width >= 10:
                    tf.write(r'\setlength{\tabcolsep}{2pt}')
                    tf.write(r'\resizebox{0.95\textwidth}{!}{')

                tf.write(r'\begin{center}')
                tf.write(dataOut.to_latex(multirow=True, float_format=lambda x: '%0.2f' % x)) 
                tf.write(r'\end{center}')
                if caption != '': tf.write(r'\\\centerline{\caption{' + caption + r'}}')
                
                if tbl_width >= 10:
                    tf.write(r'}')
            print(f'Written {name}.tex to {inPath}')

        elif os.path.exists(inPath) and data.empty:
            print(f'{name} already exists in {inPath}. No override instruction was given.')
        return

    def addTbl2Doc(self, tbl):
        """Add a table by name to the latex document, if it exists in the folder.
        
        Arguments:
            tblpath {str} -- file path where the tex file will be retrieved from
        """
        inPath = os.path.join(self.fpath, 'tables', tbl)
        outPath = os.path.join('../tables', tbl)

        if not os.path.exists(tblpath):
            print(f'Error: {tblpath} does not exist. Please save first and try again.')
        else:
            self.doc.append(NoEscape(r'\input{' + outPath + r'}')) 
            print(f'Added {tblpath} to the tex doc obj.')
        return
    
    
    ########################## ADDING FIGURES ###########################
    
    
    def saveFigure(self, name, fpath='', caption='', option='', override=False):
        """Given an existing image file (fpath), save to Figures folder 
            as a png file with the same (name), if it doesn't yet exist. 
            Optional to (override) even if it exists.

        If (caption) and (option) are given, will be added to the 
            figures' configuration dictionary. 
            The (Option) is any extra tex formatting of the image. 
    
        Arguments:
            name {str} -- Name of the figure that will be saved into the savePath 
        
        Keyword Arguments:
            fpath {str} -- Location of the original file. Optional; if not provided, will just use files in the savePath (default: {''})
            savePath {str} -- file path where the png will be copied to if fpath provided or override instruction given. (default: {''})
            caption {str} -- Caption that will be added to the bottom of the figure. (default: {''})
            option {str} -- Special tex configurations/formatting for the image. It must be a raw tex string, such as option='r'0.8\textheight'' or option='scale=0.5'. (default: {''})
            override {bool} -- Specify whether to override a png file in savePath even if it exists. (default: {False})

        Returns:
            [type] -- [description]
        """
        savePath = os.path.join(self.fpath, 'figures')
        outPng = os.path.join(savePath, name + '.png')
        
        if not os.path.exists(outPng) and fpath != '':
            print(f'Copying {name}.png to {savePath}.')
            shutil.copyfile(fpath, outPng)
        
        elif override==True:
            print(f'Overriding {name}.png at {savePath}')
            shutil.copyfile(fpath, outPng)

        elif fpath == '' and not os.path.exists(outPng):
            print('No input path provided. Image not found.')

        elif os.path.exists(outPng):
            print(f'{name} already exists in {savePath}. No override instruction was given.')
        
        # Add to dictionary. 
        self.figures[name+'.png'] = {
            'name': name,
            'fpath': fpath,
            'caption': caption,
            'option': option
        }
        return
    
    def addFig2Doc(self, figpath):
        """Add a figure by name to the end of the latex document, 
            if it exists in the folder, by referencing the configurations
            of the figure as described in the self.figures dictionary.
        
        Arguments:
            figpath {str} -- file path of the figure to be added to the document.
        """ 
        fig = os.path.basename(figpath)
        inPath = os.path.join(self.fpath, 'figures', fig)
        outPath = os.path.join('../figures', fig)
        
        if not os.path.exists(figpath):
            print('Error: File does not exist!')
        else:
            # self.doc.append(NoEscape(r'\input{' + outPath + r'}')) 
            with self.doc.create(Figure(position='ht')) as fig_:
                ## To adjust image size given specified options: 
                if fig in self.figures: # added via saveFigure():
                    if 'option' in self.figures[fig]:
                        fig_.append(NoEscape(r'\centering'))
                        fig_.append(Command('includegraphics', 
                                        options=NoEscape(self.figures[fig]['option']), 
                                        arguments=outPath))
                    else:
                        fig_.add_image(outPath) # default uses 0.8\textwidth 
                    if 'caption' in self.figures[fig]:
                        fig_.append(LineBreak())
                        fig_.add_caption(self.figures[fig]['caption'])
                else:
                    fig_.add_image(outPath)
            print(f'Added {fig} to the tex doc obj')
        return
  
    ######################## ADDING STUFF ############################
    
    def addNewLine2Doc(self):
        """To add a new line to the document. If use NewLine() without
        the \leavevmode command, pdflatex will throw a 'no line to break' error.
        """
        self.doc.append(NoEscape(r'\leavevmode'))
        self.doc.append(NewLine())
        return
    
    def addText2Doc(self, text):
        """Add a raw string of text to the Document.
        
        Arguments:
            text {str} -- Text to be added to the document. 
            Include an 'r' in front of the string if there are 
            special characters you want to include as tex.
            e.g. use r'\textbf'
        """
        self.doc.append(NoEscape(text))
        return 

    def sectionLevel(self, level, title):
        """ To identify and return different section-types 
            based on a given (level). 
        
        Returns:
            pylatex Container -- Section/Subsection/Subsubsection container.
        """
        if level == 1:
            return Section(title)
        elif level == 2:
            return Subsection(title)
        elif level == 3:
            return Subsubsection(title)
        else:
            print('Error: invalid section level given.')
    
    def addSection(self, name, level=1, override=False):
        """Adds sections to the document in the order that they
        exist in the self.sections dictionary.

        Arguments:
            name {str} -- Name/Title of the section which will be printed.
            Avoid using special characters like '_'. 

        Keyword Arguments:
            level {int} -- The level of the seciton to be created. For example, level=2 gives a subsection. (default: {1})
            override {bool} -- Whether to override existing Figures on subsequent runs. (default: {False})
        """
        sectPath = os.path.join(self.fpath, 'sections',  name.replace(' ','_')+'.tex')
        if not os.path.exists(sectPath) or override==True:
            # Create a section
            sect = self.sectionLevel(level, name)
            sect.append('Insert your text here.')
            sect.append(NoEscape(r'\lipsum[1]'))
            sect.append(LineBreak())

            # Dump the section 
            with open(sectPath, 'w') as tf:
                tf.write(sect.dumps())
            print(f'Created section {name} at {sectPath}')

        else:
            print(f'{sectPath} already exists. Did not override.')
        
        if not name in self.sections:
            # avoid tex errors with any _ in the section name
            self.sections[name.replace(' ', '_')] = {
                "fpath" : sectPath,
                "level" : level
            }
        return
    
    def addAppendix(self, apdx):
        """Adds mapping tables as an appendix to the report.
        For the specified (apdx) csv file in the appendix folder, 
            it will create a table with either 2/3-columns
            specifying the mapping values. 
        Note that this might not work well with extremely long mapping tables.
        """
        mappingTable = pd.read_csv(apdx, header=None)
        colNum = len(mappingTable.columns)
        apdx_name = os.path.basename(apdx) # for printing

        if colNum == 2:
            hdr_format = 'l X[l]'
            col_names = ['Original', 'Category']
            mappingTable.columns = col_names
            mappingTable = mappingTable.groupby('Category')['Original'].apply(list).reset_index()
            tbl_type = LongTabularx(hdr_format, width_argument=NoEscape(r'0.9\textwidth'))

        elif colNum == 3:
            hdr_format = 'l l l'
            col_names = ['Lower','Upper','Category']
            tbl_type = Tabular(hdr_format)

        self.doc.append(Subsection('{}'.format(apdx_name.replace('_', ' '))))

        with self.doc.create(tbl_type) as appendix:
            appendix.add_hline()
            appendix.add_row(col_names) 
            appendix.add_hline()

            if colNum == 2: 
                appendix.end_table_header()
                appendix.add_hline()
                appendix.add_row((MultiColumn(colNum, align='r',
                                            data='Continued on Next Page'),))
                appendix.end_table_footer()
                appendix.add_hline()
                appendix.add_row((MultiColumn(colNum, align='r',
                                data='Not Continued on Next Page'),))
                appendix.end_table_last_footer()

            # Iterate through each row in the csv. 
            for i, rw in mappingTable.iterrows():
                row = [rw[j] for j in range(colNum)]
                appendix.add_row(row)

            appendix.add_hline()

        self.doc.append(LineBreak())
        
        return
    
    
    ########################## MAKING THE REPORT ##########################
        
        
    def makeReport(self, sectionOnly=False, tex_only=False):
        """Automated generation of the report. 

        Keyword Arguments:
            sectionOnly {bool} -- Specify whether the report should only generate
            the sections and appendix, or if the figures and tables tex should be
            regenerated as well. 
            
            Generally, use sectionOnly=True if you have moved the figures/tables tex 
            into your sections. Otherwise, anything in the figures/tables folders 
            will be regenerated at the end of your main tex document,
            even if you have already moved a copy out into the sections. 
            (default: {False})
            texOnly {bool} -- Specify whether you would like a PDF document to be generated,
            or if you only want to generate as tex for previewing. (default: {False})
        """
        # Clear document 
        self.resetDoc()

        # For section inside the folder, add sections
        sectPath = os.path.join(self.fpath, 'sections')
        # for sect in os.listdir(sectPath): 
        for sect in self.sections: 
            sectFile = os.path.join('../sections', sect)
            self.addText2Doc(r'\input{' + sectFile + r'}')

        if not sectionOnly: # figures and tables tex will be pushed to main doc    
            # For figures inside the folder, add figures
            figPath = os.path.join(self.fpath, 'figures')
            self.doc.create(Section('Figures'))
            for fig in glob.glob(figPath+'/*.png'):
                self.addFig2Doc(fig)
                
            # For tables inside the folder, add tables
            tblPath = os.path.join(self.fpath, 'tables')
            self.doc.create(Section('Tables'))
            for tbl in glob.glob(tblPath+'/*.tex'):
                self.addTbl2Doc(tbl)

        # For apx inside the folder, add appendix
        appenPath = os.path.join(self.fpath, 'mappingTables')
        apdxs = glob.glob(appenPath+'/*.csv')
        if apdxs != []:
            self.addText2Doc(r'\clearpage') # page break
            self.doc.append(Section('Appendix - Mapping Tables'))
            for apdx in apdxs:
                self.addAppendix(apdx)
        
        ## generate tex/pdf
        if texOnly:
            self.doc.generate_tex(os.path.join(self.outputPath, self.name))
        else:
            try:
                self.doc.generate_pdf(os.path.join(self.outputPath, self.name), 
                                  clean_tex=False) #,compiler='pdflatex',compiler_args='-interaction=batchmode')
            except:
                print('error!')

        return 
