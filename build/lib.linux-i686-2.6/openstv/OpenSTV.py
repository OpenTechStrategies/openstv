#!/usr/bin/env python

## OpenSTV Copyright (C) 2003-2010 Jeffrey O'Neill
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

__revision__ = "$Id: OpenSTV.py 821 2010-11-19 23:36:17Z jeff.oneill $"

import os
import sys
import warnings
from time import sleep
from threading import Thread
from Queue import Queue

import wx
import wx.html
import wx.lib.mixins.listctrl as listmix

from openstv.BFE import BFEFrame
from openstv.ballots import Ballots
from openstv.ReportPlugins.TextReport import TextReport
from openstv.ReportPlugins.HtmlReport import HtmlReport
from openstv.ReportPlugins.CsvReport import CsvReport
from openstv.plugins import getMethodPlugins
from openstv.utils import getHome

##################################################################

class Output:
  """This is used to capture stdout/stderr from STV.py and send it to a 
  wxPython window."""
  
  def __init__(self, nb):
    self.nb = nb
  def write(self, txt):
    self.nb.GetCurrentPage().AppendText(txt)

##################################################################

class Election():
  
  def __init__(self, frame, filename, methodClass):
    self.frame = frame
    self.filename = filename
    self.methodClass = methodClass
    self.dispWidth = 100
    self.dirtyBallots = None
    self.cleanBallots = None
    self.e = None

  def loadBallots(self):
    self.dirtyBallots = Ballots()
    self.dirtyBallots.exceptionQueue = Queue(1)
    loadThread = Thread(target=self.dirtyBallots.loadUnknown, args=(self.filename,))
    loadThread.start()
    
    # Display a progress dialog
    dlg = wx.ProgressDialog(\
      "Loading ballots",
      "Loading ballots from %s\nNumber of ballots: %d" % 
      (os.path.basename(self.filename), self.dirtyBallots.numBallots),
      parent=self.frame, style = wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME
    )
    while loadThread.isAlive():
      sleep(0.1)
      dlg.Pulse("Loading ballots from %s\nNumber of ballots: %d" %
                (os.path.basename(self.filename), self.dirtyBallots.numBallots))
    dlg.Destroy()
    
    if not self.dirtyBallots.exceptionQueue.empty():
      raise RuntimeError(self.dirtyBallots.exceptionQueue.get())

  def initializeElection(self, cleanType):

    self.cleanBallots = self.dirtyBallots.getCleanBallots(removeOvervotes=cleanType)
    self.e = self.methodClass(self.cleanBallots)
            
  def runElection(self):

    if not self.frame.breakTiesRandomly:
      self.e.strongTieBreakMethod = "manual"
    self.e.breakTieRequestQueue = Queue(1)
    self.e.breakTieResponseQueue = Queue(1)

    countThread = Thread(target=self.e.runElection)
    countThread.start()
    # Display a progress dialog
    dlg = wx.ProgressDialog(\
      "Counting votes",
      "Counting votes using %s\nInitializing..." % self.e.longMethodName,
      parent=self.frame, style = wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME
    )
    while countThread.isAlive():
      sleep(0.1)
      if not self.e.breakTieRequestQueue.empty():
        [tiedCandidates, names, what] = self.e.breakTieRequestQueue.get()
        c = self.askUserToBreakTie(tiedCandidates, names, what)
        self.e.breakTieResponseQueue.put(c)
      if "R" in vars(self.e):
        status = "Counting votes using %s\nRound: %d" % \
               (self.e.longMethodName, self.e.R+1)
      else:
        status = "Counting votes using %s\nInitializing..." % \
               self.e.longMethodName          
      dlg.Pulse(status)
    dlg.Destroy()

  def askUserToBreakTie(self, candidates, names, what):
    "Provide a window to ask the user to break a tie."
    
    instructions = """\
Tie when selecting %s.  
Break the tie by selecting a candidate or choose Cancel 
to break the tie randomly.""" % what
    dlg = wx.SingleChoiceDialog(self.frame, instructions, "Break Tie Manually",
                                names, wx.CHOICEDLG_STYLE)
    if dlg.ShowModal() == wx.ID_OK:
      selection = dlg.GetStringSelection()
      i = names.index(selection)
      return candidates[i]
    else:
      return None

  def generateReport(self, reportObj):
    reportObj.generateReport()
    
  def generateTextOutput(self, output):
    self.generateReport(TextReport(self.e, self.dispWidth, outputFile=output))

  def generateCsvOutput(self, output):
    self.generateReport(CsvReport(self.e, outputFile=output))

  def generateHtmlOutput(self, output):
    self.generateReport(HtmlReport(self.e, outputFile=output))
    
##################################################################

class Frame(wx.Frame):

  def __init__(self, parent):
    wx.Frame.__init__(self, parent, -1, "OpenSTV", size=(900, 600))

    warnings.showwarning = self.catchWarnings

    # Get method plugins and create dict for easy access
    plugins = getMethodPlugins("classes")
    self.methodClasses1 = {} # Methods enabled by default
    self.methodClasses2 = {} # All methods
    self.lastMethod = "Scottish STV"
    for p in plugins:
      if p.status == 1:
        self.methodClasses1[p.longMethodName] = p
      self.methodClasses2[p.longMethodName] = p
    self.methodClasses = self.methodClasses1 # Methods currently viewable to user

    self.breakTiesRandomly = False
    
    fn = os.path.join(getHome(), "Icons", "pie.ico")
    self.icon = wx.Icon(fn, wx.BITMAP_TYPE_ICO)
    self.SetIcon(self.icon)

    self.lastBallotFile = ""
    self.electionList = []
    self.menuBar = wx.MenuBar()
    self.MakeMenu()
    self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

    # create a notebook
    self.notebook = wx.Notebook(self, -1)

    # create a console window
    self.console = wx.TextCtrl(self.notebook, -1,
                               style=wx.TE_MULTILINE|wx.TE_READONLY|\
                               wx.TE_WORDWRAP|wx.FIXED|wx.TE_RICH2)
    self.console.SetMaxLength(0)
    ps = self.console.GetFont().GetPointSize()
    font = wx.Font(ps, wx.MODERN, wx.NORMAL, wx.NORMAL)
    self.console.SetFont(font)

    # add the console as the first page
    self.notebook.AddPage(self.console, "Console")
    self.output = Output(self.notebook)
    sys.stdout = self.output
    sys.stderr = self.output

    self.introText = """\
OpenSTV Copyright 2003-2010 Jeffrey O'Neill
GNU General Public License
See Help->License for more details.

To run an election with an existing ballot file, select "New Election" from
the File menu.

To create a new ballot file, select "Create New Ballot File" from the File
menu.  To edit an existing ballot file, select "Edit Ballot File" from the
File menu.

For more information about the operation of OpenSTV, see the Help menu, go
to www.OpenSTV.org, or send an email to OpenSTV@googlegroups.com.    
"""
    self.console.AppendText(self.introText)
    
  def catchWarnings(self, message, category, filename, lineno):
    "Catch any warnings and display them in a dialog box."
    wx.MessageBox(str(message), "Warning", wx.OK|wx.ICON_INFORMATION)

  def MakeMenu(self):

    # File menu
    FileMenu = wx.Menu()
    self.AddMenuItem(FileMenu, 'Run Election...\tCtrl+E',
                     'Run election...', self.OnRunElection)
    FileMenu.AppendSeparator()
    self.AddMenuItem(FileMenu, 'New Ballot File...\tCtrl+N',
                     'New ballot file...', self.OnNewBF)
    self.AddMenuItem(FileMenu, 'Edit Ballot File...\tCtrl+O',
                     'Edit ballot file...', self.OnEditBF)
    FileMenu.AppendSeparator()
    self.AddMenuItem(FileMenu, 'Close Tab\tCtrl+W', 'Close Tab',
                     self.OnCloseTab)
    FileMenu.AppendSeparator()
    self.AddMenuItem(FileMenu, 'Save Results As CSV...',
                     'Save results as CSV', self.OnSaveResultsCSV)
    self.AddMenuItem(FileMenu, 'Save Results As Text...',
                     'Save results as text', self.OnSaveResultsText)
    self.AddMenuItem(FileMenu, 'Save Results As HTML...',
                     'Save results as HTML', self.OnSaveResultsHTML)
    menuId = self.AddMenuItem(FileMenu, 'Exit',
                     'Exit the application', self.OnExit, "Exit")
    if wx.Platform == "__WXMAC__":
      wx.App.SetMacExitMenuItemId(menuId)
    self.menuBar.Append(FileMenu, '&File')

    # Edit menu
    EditMenu = wx.Menu()
    self.AddMenuItem(EditMenu, '&Copy\tCtrl+C', 'Copy', self.OnCopy)
    self.AddMenuItem(EditMenu, 'Select All\tCtrl+A', 'Select all', 
                     self.OnSelectAll)
    self.menuBar.Append(EditMenu, '&Edit')

    # Options menu
    OptionsMenu = wx.Menu()
    self.AddMenuItem(OptionsMenu, 'Show All Methods', 'Show all methods',
                     self.OnShowAll, "Check")
    self.AddMenuItem(OptionsMenu, 'Break Ties Randomly', 'Break Ties Randomly',
                     self.OnBreakTiesRandomly, "Check")
    subMenu = wx.Menu()
    self.AddMenuItem(subMenu, '6', '6', self.OnFontSize)
    self.AddMenuItem(subMenu, '7', '7', self.OnFontSize)
    self.AddMenuItem(subMenu, '8', '8', self.OnFontSize)
    self.AddMenuItem(subMenu, '9', '9', self.OnFontSize)
    self.AddMenuItem(subMenu, '10', '10', self.OnFontSize)
    self.AddMenuItem(subMenu, '11', '11', self.OnFontSize)
    self.AddMenuItem(subMenu, '12', '12', self.OnFontSize)
    self.AddMenuItem(subMenu, '13', '13', self.OnFontSize)
    self.AddMenuItem(subMenu, '14', '14', self.OnFontSize)
    OptionsMenu.AppendMenu(wx.NewId(), "Font Size", subMenu)

    self.menuBar.Append(OptionsMenu, '&Options')
    
    # Help menu
    HelpMenu = wx.Menu()
    
    self.AddMenuItem(HelpMenu, 'OpenSTV Help',
                     'OpenSTV Help', self.OnHelp, "Help")

    self.AddMenuItem(HelpMenu, 'License',
                     'GNU General Public License', self.OnLicense)
    
    # Help about methods
    # mac wxPython doesn't allow submenus in the help menu so need to do it
    # a different way
    methods = self.methodClasses2.keys()
    methods.sort()
    if wx.Platform == "__WXMAC__":
      HelpMenu.AppendSeparator()
      for m in methods:
        self.AddMenuItem(HelpMenu, m, m, self.OnMethodHelp)
    else:
      methodHelpMenu = wx.Menu()
      for m in methods:
        self.AddMenuItem(methodHelpMenu, m, m, self.OnMethodHelp)
      HelpMenu.AppendMenu(wx.NewId(), "Methods", methodHelpMenu)

    # About OpenSTV
    if wx.Platform != "__WXMAC__":
      HelpMenu.AppendSeparator()
    itemId = self.AddMenuItem(HelpMenu, '&About', 'About OpenSTV', self.OnAbout, 
                          "About")
    if wx.Platform == "__WXMAC__":
      wx.App.SetMacAboutMenuItemId(itemId)

    self.menuBar.Append(HelpMenu, '&Help')
    if wx.Platform == "__WXMAC__":
      wx.GetApp().SetMacHelpMenuTitleName('&Help')

    self.SetMenuBar(self.menuBar)

  
  def AddMenuItem(self, menu, itemText, itemDescription, itemHandler, opt=''):
    if (opt == "Exit"):
      menuId = wx.ID_EXIT
    elif (opt == "Help"):
      menuId = wx.ID_HELP
    elif (opt == "About"):
      menuId = wx.ID_ABOUT
    else:
      menuId = wx.ID_ANY

    if opt == "Radio":
      item = menu.Append(menuId, itemText, itemDescription, wx.ITEM_RADIO)
    elif opt == "Check":
      item = menu.Append(menuId, itemText, itemDescription, wx.ITEM_CHECK)
    else:
      item = menu.Append(menuId, itemText, itemDescription)
    self.Bind(wx.EVT_MENU, itemHandler, item)
    return item.GetId()

  ### File Menu
    
  def OnRunElection(self, event):

    # Get the ballot filename and election method
    dlg = ElectionMethodFileDialog(self)
    dlg.Center()
    if dlg.ShowModal() != wx.ID_OK:
      dlg.Destroy()
      return
    filename = dlg.filenameC.GetValue().strip()
    self.lastBallotFile = filename
    methodName = dlg.methodC.GetStringSelection()
    self.lastMethod = methodName
    withdawCandidates = dlg.withdrawC.GetValue()
    cleanType = dlg.cleanC.GetStringSelection()
    dlg.Destroy()

    # Create an election instance
    election = Election(self, filename, self.methodClasses[methodName])

    # Load ballots from the file.  These are dirty ballots.
    try:
      election.loadBallots()
    except RuntimeError, msg:
      wx.MessageBox(str(msg), "Error", wx.OK|wx.ICON_ERROR)
      return

    # Allow the user to specify withdrawn candidates.
    # Will set withdrawn candidates in election.dirtyBallots
    if withdawCandidates:
      dlg = WithdrawDialog(self, election.dirtyBallots)
      dlg.Center()
      if dlg.ShowModal() != wx.ID_OK:
        dlg.Destroy()
        return

    # Initialize the election instance and set default options
    election.initializeElection(cleanType)
    
    # Allow user to change election information and options
    dlg = ElectionOptionsDialog(self, election)
    dlg.Center()
    if dlg.ShowModal() != wx.ID_OK:
      dlg.Destroy()
      return
    dlg.Destroy()

    try:
      election.runElection()
    except RuntimeError, msg:
      wx.MessageBox(str(msg), "Error", wx.OK|wx.ICON_ERROR)
      return
      
    self.electionList.append(election)

    # create a new notebook page
    tc = wx.TextCtrl(self.notebook, -1,
                     style=wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL|wx.FIXED)
    tc.SetMaxLength(0)
    ps = tc.GetFont().GetPointSize()
    font = wx.Font(ps, wx.MODERN, wx.NORMAL, wx.NORMAL)
    tc.SetFont(font)
    tabTitle = election.e.title
    if len(tabTitle) > 30:
      tabTitle = tabTitle[:27] + "..."
    self.notebook.AddPage(tc, tabTitle)
    page = self.notebook.GetPageCount() - 1
    self.notebook.SetSelection(page)
    election.generateTextOutput(self.notebook.GetPage(page))
    
  def OnNewBF(self, event):
    BFE = BFEFrame(self, "new")
    BFE.Show(True)
  
  def OnEditBF(self, event):
    BFE = BFEFrame(self, "old")
    BFE.Show(True)
  
  def OnCloseTab(self, event):
    
    n = self.notebook.GetSelection()
    if n == 0:
      pages = self.notebook.GetPageCount()
      if pages > 1:
        return	     # don't close console if there are open results pages
      self.OnCloseWindow(event)		# otherwise close window
      return

    # The index into electionList is off by one because of the console tab
    self.notebook.DeletePage(n)
    self.electionList.pop(n-1)

  def OnSaveResultsCSV(self, event):

    n = self.notebook.GetSelection()
    if n == 0:
      wx.MessageBox("Please select a tab containing election results.",
                    "Message", wx.OK|wx.ICON_INFORMATION)
      return
    T = self.electionList[n-1]
    if T.e.methodName == "Condorcet":
      wx.MessageBox("CSV report not available for Condorcet elections.",
                    "Message", wx.OK|wx.ICON_INFORMATION)
      return

    if T.e.methodName == "Condorcet":
      wx.MessageBox("Not available for this method.",
                    "Message", wx.OK|wx.ICON_INFORMATION)
      return

    dlg = wx.FileDialog(self, "Save Results in CSV Format",
                        style=wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
    if dlg.ShowModal() != wx.ID_OK:
      dlg.Destroy()
      return
    fName = dlg.GetPath()
    dlg.Destroy()

    f = open(fName, 'w')
    T.generateCsvOutput(f)
    f.close()
    
  def OnSaveResultsText(self, event):

    n = self.notebook.GetSelection()
    if n == 0:
      wx.MessageBox("Please select a tab containing election results.",
                    "Message", wx.OK|wx.ICON_INFORMATION)
      return

    dlg = wx.FileDialog(self, "Save Results in Text Format",
                        style=wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
    if dlg.ShowModal() != wx.ID_OK:
      dlg.Destroy()
      return
    fName = dlg.GetPath()
    dlg.Destroy()

    n = self.notebook.GetSelection()
    self.notebook.GetPage(n).SaveFile(fName)

  def OnSaveResultsHTML(self, event):

    n = self.notebook.GetSelection()
    if n == 0:
      wx.MessageBox("Please select a tab containing election results.",
                    "Message", wx.OK|wx.ICON_INFORMATION)
      return
    T = self.electionList[n-1]
    if T.e.methodName == "Condorcet":
      wx.MessageBox("HTML report not available for Condorcet elections.",
                    "Message", wx.OK|wx.ICON_INFORMATION)
      return

    dlg = wx.FileDialog(self, "Save Results in HTML Format",
                        style=wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
    if dlg.ShowModal() != wx.ID_OK:
      dlg.Destroy()
      return
    fName = dlg.GetPath()
    dlg.Destroy()

    f = open(fName, 'w')
    T.generateHtmlOutput(f)
    f.close()
    
  def OnExit(self, event):
    self.Close()

  def OnCloseWindow(self, event):
    childrenList = self.GetChildren()
    for child in childrenList:
      # If the child is a frame, then it is a BFE
      if child.GetClassName() == "wxFrame":
        # Try to close the child, this will return true if the user selects
        # "yes" or "no" and false if the user selects "cancel"
        if not child.Close():
          break
    else:
      # This only happens if the user did not select cancel for any BFE
      self.Destroy()

  ### Edit Menu

  def OnCopy(self, event):
    n = self.notebook.GetSelection()
    text = self.notebook.GetPage(n).GetStringSelection()
    do = wx.TextDataObject()
    do.SetText(text)
    wx.TheClipboard.Open()
    wx.TheClipboard.SetData(do)
    wx.TheClipboard.Close()

  def OnSelectAll(self, event):
    n = self.notebook.GetSelection()
    self.notebook.GetPage(n).SetSelection(-1, -1)
    
  ### Options Menu Methods

  def OnShowAll(self, event):
    itemId = event.GetId()
    showAll = self.GetMenuBar().FindItemById(itemId).IsChecked()
    if showAll:
      self.methodClasses = self.methodClasses2
    else:
      self.methodClasses = self.methodClasses1

  def OnBreakTiesRandomly(self, event):
    itemId = event.GetId()
    self.breakTiesRandomly = self.GetMenuBar().FindItemById(itemId).IsChecked()

  def OnFontSize(self, event):
    itemId = event.GetId()
    fontSize = int(self.menuBar.FindItemById(itemId).GetLabel())
    n = self.notebook.GetSelection()
    font = self.notebook.GetPage(n).GetFont()
    font.SetPointSize(fontSize)
    self.notebook.GetPage(n).SetFont(font)

  ### Help Menu

  def OnAbout(self, event):
    dlg = AboutDialog(self)
    dlg.Center()
    dlg.ShowModal()
    dlg.Destroy()

  def OnMethodHelp(self, event):
    itemId = event.GetId()
    methodName = self.menuBar.FindItemById(itemId).GetLabel()
    html = self.methodClasses2[methodName].htmlHelp
    frame = HTMLFrame(self, methodName, html=html)
    frame.SetIcon(self.icon)
    frame.Show(True)

  def OnHelp(self, event):
    frame = HTMLFrame(self, "OpenSTV Help", fName="Help.html")
    frame.Show(True)

  def OnLicense(self, event):
    frame = HTMLFrame(self, "GNU General Public License",
                      fName="License.html")
    frame.Show(True)

##################################################################

class ElectionMethodFileDialog(wx.Dialog):

  def __init__(self, parent):
    wx.Dialog.__init__(self, parent, -1, "Run Election")

    # Explanation
    txt = wx.StaticText(self, -1, """\
To run an election, choose the input filename and the election method.
See the Help menu for more information about the available methods.""")

    # Controls
    filenameL = wx.StaticText(self, -1, "Filename:")
    self.filenameC = wx.TextCtrl(self, -1, "")
    self.filenameC.SetValue(parent.lastBallotFile)
    filenameB = wx.Button(self, -1, "Select...", (50, 50))
    self.Bind(wx.EVT_BUTTON, self.OnFilenameSelect, filenameB)

    methodL = wx.StaticText(self, -1, "Method:")
    choices = parent.methodClasses.keys()
    choices.sort()
    self.methodC = wx.Choice(self, -1, choices = choices)
    if parent.lastMethod in choices:
      self.methodC.SetStringSelection(parent.lastMethod)
    blank1 = wx.StaticText(self, -1, "")
    
    self.withdrawC = wx.CheckBox(self, -1, "Withdraw canddiates:", 
                            style=wx.ALIGN_RIGHT)
    self.withdrawC.SetValue(False)
    blank2 = wx.StaticText(self, -1, "")
    blank3 = wx.StaticText(self, -1, "")
    
    cleanL = wx.StaticText(self, -1, "Ballot Cleaning:")
    choices = ["Cambridge", "San Francisco"]
    self.cleanC = wx.Choice(self, -1, choices = choices)
    self.cleanC.SetStringSelection("San Francisco")
    blank4 = wx.StaticText(self, -1, "")

    # Buttons
    ok = wx.Button(self, wx.ID_OK)
    self.Bind(wx.EVT_BUTTON, self.OnOK, ok)
    cancel = wx.Button(self, wx.ID_CANCEL)

    # Sizers
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(txt, 0, wx.ALL, 5)
    sizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)

    fgs = wx.FlexGridSizer(4, 3, 5, 5)
    fgs.Add(filenameL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(self.filenameC, 0, wx.EXPAND)
    fgs.Add(filenameB, 0)
    fgs.Add(methodL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(self.methodC, 0, wx.EXPAND)
    fgs.Add(blank1, 0)
    fgs.Add(blank2, 0)
    fgs.Add(self.withdrawC, 0)
    fgs.Add(blank3, 0)
    fgs.Add(cleanL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(self.cleanC, 0, wx.EXPAND)
    fgs.Add(blank4, 0)
    fgs.AddGrowableCol(1)

    sizer.Add(fgs, 0, wx.EXPAND|wx.ALL, 5)
    bs = wx.StdDialogButtonSizer()
    bs.AddButton(ok)
    bs.AddButton(cancel)
    bs.Realize()
    sizer.Add(bs, 0, wx.EXPAND|wx.ALL, 5)

    self.SetSizer(sizer)
    sizer.Fit(self)

  def OnFilenameSelect(self, event):
    dlg = wx.FileDialog(self, "Select Input File", "",
                        style=wx.OPEN|wx.CHANGE_DIR)
    if dlg.ShowModal() != wx.ID_OK:
      dlg.Destroy()
      return
    filename = dlg.GetPath()
    dlg.Destroy()
    self.filenameC.ChangeValue(filename)

  def OnOK(self, event):

    filename = self.filenameC.GetValue().strip()
    if filename == "":
      wx.MessageBox("Please select a filename.", "Message",
                    wx.OK|wx.ICON_INFORMATION)
      return
    event.Skip() # do normal OK button processing

##################################################################

class WithdrawCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
  
  def __init__(self, parent, ID):
    style = wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES
    wx.ListCtrl.__init__(self, parent, ID, style=style, size=(-1, 200))
    listmix.ListCtrlAutoWidthMixin.__init__(self)

##################################################################

class WithdrawDialog(wx.Dialog):

  def __init__(self, parent, b):
    wx.Dialog.__init__(self, parent, -1, "Withdraw Candidates")

    self.b = b

    withdrawTxt = wx.StaticText(self, -1, """\
Candidates with "W" in the first column are withdrawn.  Double
click on a candidate's name to change the status of the candidate.\
""")
    self.withdrawC = WithdrawCtrl(self, -1)
    self.withdrawC.InsertColumn(0, "W")
    self.withdrawC.InsertColumn(1, "Candidate")
    for c, name in enumerate(self.b.names):
      if c in self.b.withdrawn:
        self.withdrawC.InsertStringItem(c, "W")
      else:
        self.withdrawC.InsertStringItem(c, "")
      self.withdrawC.SetStringItem(c, 1, name)
    self.withdrawC.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
    self.withdrawC.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)

    self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListDClick,
              self.withdrawC)

    # Buttons
    ok = wx.Button(self, wx.ID_OK)
    cancel = wx.Button(self, wx.ID_CANCEL)

    # Sizers
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(withdrawTxt, 0, wx.ALL, 5)
    sizer.Add(self.withdrawC, 0, wx.EXPAND|wx.ALL, 5)    
    
    # Buttons
    bs = wx.StdDialogButtonSizer()
    bs.AddButton(ok)
    bs.AddButton(cancel)
    bs.Realize()
    sizer.Add(bs, 0, wx.EXPAND|wx.ALL, 5)

    self.SetSizer(sizer)
    sizer.Fit(self)

  def OnListDClick(self, event):
    withdrawC = event.GetEventObject()
    c = event.m_itemIndex
    if c in self.b.withdrawn:
      self.b.withdrawn.remove(c)
      withdrawC.SetStringItem(c, 0, "")
    else:
      self.b.withdrawn.append(c)
      withdrawC.SetStringItem(c, 0, "W")
      
##################################################################

class ElectionOptionsDialog(wx.Dialog):

  def __init__(self, parent, election):
    wx.Dialog.__init__(self, parent, -1, "Election Options")

    self.e = election

    # Controls for all elections
    informationBox = wx.StaticBox(self, -1, "Election Information")

    method1L = wx.StaticText(self, -1, "Method:")
    method2L = wx.StaticText(self, -1, self.e.e.longMethodName)

    file1L = wx.StaticText(self, -1, "File:")
    file2L = wx.StaticText(self, -1, os.path.basename(
      self.e.dirtyBallots.getFileName()))

    nBallots1L = wx.StaticText(self, -1, "Number of ballots:")
    nBallots2L = wx.StaticText(self, -1, str(self.e.dirtyBallots.numBallots))

    titleL = wx.StaticText(self, -1, "Title:")
    self.titleC = wx.TextCtrl(self, -1, "", size=(200, -1))
    self.titleC.SetValue(self.e.e.title)

    dateL = wx.StaticText(self, -1, "Date:")
    self.dateC = wx.TextCtrl(self, -1, "")
    self.dateC.SetValue(self.e.e.date)

    seatsL = wx.StaticText(self, -1, "Seats:")
    self.seatsC = wx.SpinCtrl(self, -1)
    self.seatsC.SetRange(1, self.e.cleanBallots.numCandidates-1)
    self.seatsC.SetValue(self.e.e.numSeats)
    if self.e.e.onlySingleWinner:
      self.seatsC.SetValue(1)
      self.seatsC.Enable(False)

    widthL = wx.StaticText(self, -1, "Display Width:")
    self.widthC = wx.SpinCtrl(self, -1)
    self.widthC.SetRange(0, 200)
    self.widthC.SetValue(self.e.dispWidth)

    # Method options
    labelList = []
    self.ctrlList = []

    if len(self.e.e.guiOptions) > 0:
      optionsBox = wx.StaticBox(self, -1, "Method Options")

    for option in self.e.e.guiOptions:
      exec(option[0])  # this defines label and control
      labelList.append(label)
      self.ctrlList.append(control)
      
    # Buttons
    ok = wx.Button(self, wx.ID_OK)
    self.Bind(wx.EVT_BUTTON, self.OnOK, ok)
    cancel = wx.Button(self, wx.ID_CANCEL)

    # Sizers
    sizer = wx.BoxSizer(wx.VERTICAL)

    # Election information
    informationSizer = wx.StaticBoxSizer(informationBox, wx.VERTICAL)
    sizer.Add(informationSizer, 0, wx.EXPAND|wx.ALL, 5)

    fgs = wx.FlexGridSizer(7, 2, 5, 5)
    fgs.Add(method1L, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(method2L, 0, wx.EXPAND)
    fgs.Add(file1L, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(file2L, 0, wx.EXPAND)
    fgs.Add(nBallots1L, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(nBallots2L, 0, wx.EXPAND)
    fgs.Add(titleL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(self.titleC, 0, wx.EXPAND)
    fgs.Add(dateL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(self.dateC, 0, wx.EXPAND)
    fgs.Add(seatsL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(self.seatsC, 0, wx.EXPAND)
    fgs.Add(widthL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(self.widthC, 0, wx.EXPAND)
    fgs.AddGrowableCol(1)
    informationSizer.Add(fgs, 0, wx.EXPAND|wx.ALL, 5)

    # Method specific options
    n = len(labelList)
    if n > 0:
      optionsSizer = wx.StaticBoxSizer(optionsBox, wx.VERTICAL)
      sizer.Add(optionsSizer, 0, wx.EXPAND|wx.ALL, 5)

      fgs = wx.FlexGridSizer(n, 2, 5, 5)
      for i in range(n):
        fgs.Add(labelList[i], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.ctrlList[i], 0, wx.EXPAND)
      fgs.AddGrowableCol(1)
      optionsSizer.Add(fgs, 0, wx.EXPAND|wx.ALL, 5)

    # Buttons
    bs = wx.StdDialogButtonSizer()
    bs.AddButton(ok)
    bs.AddButton(cancel)
    bs.Realize()
    sizer.Add(bs, 0, wx.EXPAND|wx.ALL, 5)

    self.SetSizer(sizer)
    sizer.Fit(self)

  def OnOK(self, event):
    self.e.e.title = self.titleC.GetValue()
    self.e.e.date = self.dateC.GetValue()
    self.e.e.numSeats = self.seatsC.GetValue()
    self.e.dispWidth = self.widthC.GetValue()
    
    for i, option in enumerate(self.e.e.guiOptions):
      cmd = "self.e.e.%s = self.ctrlList[i].%s" % (option[2], option[1])
      exec(cmd)
      
    event.Skip() # do normal OK button processing
    
##################################################################

class AboutDialog(wx.Dialog):
  "Dialog for about OpenSTV box."

  def __init__(self, parent):
    wx.Dialog.__init__(self, parent, -1, "About OpenSTV")

    sizer = wx.BoxSizer(wx.VERTICAL)

    fn = os.path.join(getHome(), "Icons", "splash.png")
    bmp = wx.Image(fn, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
    bm = wx.StaticBitmap(self, -1, bmp)
    sizer.Add(bm)

    button = wx.Button(self, wx.ID_OK, "Close")
    button.SetDefault()
    sizer.Add(button, 0, wx.ALIGN_CENTER|wx.ALL, 5)

    sizer.Fit(self)
    self.SetAutoLayout(True)
    self.SetSizer(sizer)

##################################################################

class HTMLFrame(wx.Frame):
  def __init__(self, parent, title, fName=None, html=None):
    wx.Frame.__init__(self, parent, -1, title, size=(600, 400))
    assert(fName is None or html is None)
    self.win = wx.html.HtmlWindow(self, -1)
    if fName is not None:
      fn = os.path.join(getHome(), fName)
      self.win.LoadFile(fn)
    if html is not None:
      self.win.SetPage(html)

##################################################################

class App(wx.App):

  def OnInit(self):
    wx.InitAllImageHandlers()

    # Show a splash screen
    png = os.path.join(getHome(), "Icons", "splash.png")
    bmp = wx.Image(png).ConvertToBitmap()
    wx.SplashScreen(bmp,
                    wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT,
                    5000, None, -1)

    self.frame = Frame(None)
    self.frame.Show(True)
    self.frame.Center()
    self.frame.Raise()
    self.SetTopWindow(self.frame)
    return True

##################################################################

if __name__ == '__main__':
  app = App(0)
  app.MainLoop()
