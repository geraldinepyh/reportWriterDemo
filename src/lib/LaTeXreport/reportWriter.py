import pickle
import pandas as pd
import matplotlib.pyplot as plt
import os
import shutil
import jsonref

import pylatex
import subprocess # to download arxiv.sty from GH
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
        # Helper function to make Directories
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)
            print('Created', dirPath)
        else: 
            print(dirPath, 'already exists.')
        return
        
    def initialize(self, fpath):
        ## Initialize a report project
        self.makeDirs(fpath)
        subs = list(self.objects) + ['output'] 
        for sub in subs:
            self.makeDirs(os.path.join(fpath,sub))
        self.resetDoc()

        print(f'>> {self.name} report structure has been initialized.')
        return 

    def resetDoc(self):
        self.doc=Document()
        pkgs_to_add = [ 'booktabs','hyperref','lipsum','microtype', \
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
        '''
        Given a pandas dataframe (data), save to (path) as a tex file with the same (name)
            if it doesn't yet exist. (Option to override even if it exists.)
            If (caption) is given, will be appended.
        '''
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
                if tbl_width > 10:
                    tf.write(r'\setlength{\tabcolsep}{2pt}')
                    tf.write(r'\resizebox{0.95\textwidth}{!}{')

                tf.write(dataOut.to_latex(multirow=True, float_format=lambda x: '%0.2f' % x)) 
                if caption != '': tf.write(r'\\\caption{' + caption + r'}')
                
                if tbl_width > 10:
                    tf.write(r'}')
            print(f'Written {name}.tex to {inPath}')

        elif os.path.exists(inPath) and data.empty:
            print(f'{name} already exists in {inPath}. No override instruction was given.')
        return

    def addTbl2Doc(self, tbl):
        '''
        Add a table by name to the latex document if it exists in the folder.
        '''
        inPath = os.path.join(self.fpath, 'tables', tbl)
        outPath = os.path.join('../tables', tbl)

        if not os.path.exists(inPath):
            print(f'Error: {inPath} does not exist. Please save first and try again.')
        else:
            self.doc.append(NoEscape(r'\input{' + outPath + r'}')) 
            print(f'Added {tbl} to the tex doc obj.')
        return
    
    
    ########################## ADDING FIGURES ###########################
    
    
    def saveFigure(self, name, fpath='', caption='', option='', override=False):
        '''
        Given an existing image file (fpath), save to Figures folder
            if it doesn't exist yet. (Option to override even if it exists.)
        If caption and option are given, will be added to the figures' configuration dictionary.
        '''
        savePath = os.path.join(self.fpath, 'figures')
        outPng = os.path.join(savePath, name + '.png')
        outTex = os.path.join(savePath, name + '.tex')
        
        if not os.path.exists(outPng) and fpath != '':
            print(f'Copying {name}.png to {savePath}.')
            shutil.copyfile(fpath, outPng)
        
        elif override==True:
            print(f'Overriding {name}.png at {savePath}')
            shutil.copyfile(fpath, outPng)

        elif fpath == '' and not os.path.exists(outPng):
            print('No input path provided. Image not found.')

        elif os.path.exists(outTex) and os.path.exists(outPng):
            print(f'{name} already exists in {savePath}. No override instruction was given.')
        
        # Add to dictionary. 
        self.figures[name+'.png'] = {
            'name' : name,
            'fpath' : fpath, 
            'caption' : caption,
            'option' : option
        }
        return
    
    def addFig2Doc(self, fig):
        inPath = os.path.join(self.fpath, 'figures', fig)
        outPath = os.path.join('../figures', fig)
        
        if not os.path.exists(inPath):
            print('Error: File does not exist!')
        else:
            # self.doc.append(NoEscape(r'\input{' + outPath + r'}')) 
            with self.doc.create(Figure(position='!ht')) as fig_:
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
    
    
    def addText2Doc(self, text):
        '''Add a raw string of text to the Document.'''
        self.doc.append(NoEscape(text))
        return 

    def sectionLevel(self, level, title):
        """ To identify and return different section-types based on a given (level)
        """
        if level == 1:
            return Section(title)
        elif level == 2:
            return Subsection(title)
        elif level == 3:
            return Subsubsection(title)
        else:
            print('Error: invalid section level given.')
        return
    
    def addSection(self, name, level=1, override=False):

        sectPath = os.path.join(self.fpath, 'sections',  name.replace(' ','_')+'.tex')
        if not os.path.exists(sectPath) or override==True:
            # Create a section
            sect = self.sectionLevel(level, name)
            sect.append('Insert your text here.')
            sect.append(LineBreak())

            # Dump the section 
            with open(sectPath, 'w') as tf:
                tf.write(sect.dumps())
            print(f'Created section {name} at {sectPath}')

        else:
            print(f'{sectPath} already exists. Did not override.')
        
        if not name in self.sections:
            self.sections[name.replace(' ', '_')] = {
                "fpath" : sectPath,
                "level" : level
            }
        return
    
    def addAppendix(self):
        """Adds mapping tables as an appendix to the report.
        For each csv file in the appendix folder, it will create either a 2/3-column
            table specifying the mapping values. 
        """
        appenPath = os.path.join(self.fpath, 'mappingTables')

        self.addText2Doc(r'\clearpage') # page break
        for apdx in os.listdir(appenPath): 
            if not apdx.startswith('.'):
                mappingTable = pd.read_csv(os.path.join(appenPath, apdx), header=None)
                colNum = len(mappingTable.columns)

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

                self.doc.append(bold(NoEscape(r'{} Mapping Table\\'.format(apdx.replace('_', ' ')))))

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
                self.doc.append(LineBreak())
                self.doc.append(LineBreak())
        
        return
    
    
    ########################## MAKING THE REPORT ##########################
        
        
    def makeReport(self, reportName = 'report', tex_only=False):
        '''Automated generation of report structure'''
        # Clear document 
        self.resetDoc()

        # For section inside the folder, add sections
        sectPath = os.path.join(self.fpath, 'sections')
        # for sect in os.listdir(sectPath): 
        for sect in self.sections:
            sectFile = os.path.join('../sections', sect)
            self.addText2Doc(r'\input{' + sectFile + r'}')
            self.doc.append(NewLine())
            self.doc.append(LineBreak())
            
        # For figures inside the folder, add figures
        figPath = os.path.join(self.fpath, 'figures')
        self.doc.create(Section('Figures'))
        for fig in os.listdir(figPath):
            if not fig.startswith('.'):
                self.addFig2Doc(fig)
                self.doc.append(NewLine())
                self.doc.append(LineBreak())
            
        # For tables inside the folder, add tables
        tblPath = os.path.join(self.fpath, 'tables')
        self.doc.create(Section('Tables'))
        for tbl in os.listdir(tblPath):
            if not tbl.startswith('.'):
                self.addTbl2Doc(tbl)
                self.doc.append(NewLine())
                self.doc.append(LineBreak())

        # For apx inside the folder, add apx
        self.addAppendix()
        
        ## generate tex/pdf
        if tex_only:
            self.doc.generate_tex(os.path.join(self.outputPath, self.name))
        else:
            try:
                self.doc.generate_pdf(os.path.join(self.outputPath, self.name), 
                                  clean_tex=False)
            except:
<<<<<<< HEAD
                print('Error!')
=======
                print('error!')
>>>>>>> d6fff3dd198519c136451ed0116bef518ad35aad

        return 
