"Module that provides a GUI for editing ballots."

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

__revision__ = "$Id: BFE.py 719 2010-03-01 03:43:54Z jeff.oneill $"

import wx
import os
import warnings
import wx.lib.mixins.listctrl as listmix

from openstv.STV import *
from openstv.ballots import Ballots
from openstv.utils import getHome

##################################################################

class BFEFrame(wx.Frame):

  def __init__(self, parent, mode):
    wx.Frame.__init__(self, parent, -1, "Ballot File Editor")

    warnings.showwarning = self.catchWarnings

    self.MakeMenu()
    self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
    self.logfName = ""

    fn = os.path.join(getHome(), "Icons", "blt.ico")
    icon = wx.Icon(fn, wx.BITMAP_TYPE_ICO)
    self.SetIcon(icon)

    # Edit a new ballot file
    if mode == "new":

      # Create an empty ballots class instance
      self.b = Ballots()

      # Get the candidate names from the user
      dlg = CandidatesDialog(parent, self.b)
      dlg.Center()
      if dlg.ShowModal() != wx.ID_OK:
        dlg.Destroy()
        self.Destroy()
        return
      dlg.Destroy()
        
    # Edit an existing ballot file
    elif mode == "old":
      dlg = wx.FileDialog(self, "Edit Ballot File",
                          style=wx.OPEN|wx.CHANGE_DIR)
      if dlg.ShowModal() != wx.ID_OK:
        dlg.Destroy()
        self.Destroy()
        return
      fName = dlg.GetPath()
      dlg.Destroy()

      # Open the file
      try:
        self.b = Ballots()
        self.b.loadUnknown(fName)
      except RuntimeError, msg:
        wx.MessageBox(str(msg), "Error", wx.OK|wx.ICON_ERROR)
        self.Destroy()
        return

    else:
      assert(0)

    # Set the window title to include the filename
    fn = self.b.getFileName()
    if fn is not None:
      title = "%s - Ballot File Editor" % os.path.basename(fn)
    else:
      title = "%s - Ballot File Editor" % "New File"
    self.SetTitle(title)

    # Create a notebook with an editing page and a log page
    nb = wx.Notebook(self, -1)

    self.panel = BallotsPanel(nb, self.b)
    nb.AddPage(self.panel, "Ballots")

    self.logN = 1 # counter for display purposes
    self.log = wx.TextCtrl(nb, -1,
                           style=wx.TE_MULTILINE|wx.TE_READONLY|\
                           wx.TE_WORDWRAP|wx.FIXED)
    self.log.SetMaxLength(0)
    nb.AddPage(self.log, "Log")

    # Initialize
    if mode == "new":
      self.panel.NeedToSaveBallots = True
      self.Log("Created a new ballot file.")
    elif mode == "old":
      self.panel.NeedToSaveBallots = False
      self.Log("Loaded %d ballots from file %s." %\
               (self.b.numBallots, os.path.basename(self.b.getFileName())))
    else:
      assert(0)

    # Set up the sizer
    sizer = wx.BoxSizer()
    sizer.Add(nb, 1, wx.EXPAND, 0)
    self.SetSizer(sizer)
    sizer.Fit(self)
    sizer.SetSizeHints(self)
    
  def catchWarnings(self, message, category, filename, lineno):
    "Catch any warnings and display them in a dialog box."
    
    wx.MessageBox(str(message), "Warning", wx.OK|wx.ICON_INFORMATION)

  def Log(self, txt):

    # create a prompt for each new line
    prompt = "%3d: " % self.logN
    self.log.AppendText(prompt + txt + "\n")
    self.logN += 1
    
  def MakeMenu(self):

    fileMenu = wx.Menu()

    append = fileMenu.Append(-1, "A&ppend ballots from file...")
    saveBallots = fileMenu.Append(-1, "&Save ballots")
    saveBallotsAs = fileMenu.Append(-1, "Save ballots &as...")
    saveLog = fileMenu.Append(-1, "Save &log")
    saveLogAs = fileMenu.Append(-1, "Save log as...")
    exitBFE = fileMenu.Append(wx.ID_EXIT, "E&xit")

    self.Bind(wx.EVT_MENU, self.OnAppendBF, append)
    self.Bind(wx.EVT_MENU, self.OnSaveBallots, saveBallots)
    self.Bind(wx.EVT_MENU, self.OnSaveBallotsAs, saveBallotsAs)
    self.Bind(wx.EVT_MENU, self.OnSaveLog, saveLog)
    self.Bind(wx.EVT_MENU, self.OnSaveLogAs, saveLogAs)
    self.Bind(wx.EVT_MENU, self.OnExit, exitBFE)

    if wx.Platform == "__WXMAC__":
      wx.App.SetMacExitMenuItemId(wx.ID_EXIT)

    menuBar = wx.MenuBar()
    menuBar.Append(fileMenu, "&File")
    self.SetMenuBar(menuBar)

  def OnAppendBF(self, event):

    # Get the filename of the ballots to be appended
    dlg = wx.FileDialog(self, "Select Ballot File",
                        style=wx.OPEN|wx.CHANGE_DIR)
    if dlg.ShowModal() != wx.ID_OK:
      dlg.Destroy()
      return
    fName = dlg.GetPath()
    dlg.Destroy()

    # Attempt to append the ballots
    try:
      oldNumBallots = self.b.numBallots
      self.b.appendFile(fName)
      self.b = self.b.getCleanBallots(removeEmpty=False, removeWithdrawn=False)
    except RuntimeError, msg:
      wx.MessageBox(str(msg), "Error", wx.OK|wx.ICON_ERROR)
    else:
      self.Log("Appended %d ballots from file %s." %\
               (self.b.numBallots - oldNumBallots, os.path.basename(fName)))

    self.panel.NeedToSaveBallots = True
    self.panel.NeedToSaveLog = True
    self.panel.UpdatePanel()
    
  def OnSaveBallots(self, event):

    if self.b.getFileName() is None:
      self.OnSaveBallotsAs(event)
      return

    try:
      self.b.save()
    except RuntimeError, msg:
      wx.MessageBox(str(msg), "Error", wx.OK|wx.ICON_ERROR)
      return
    self.panel.NeedToSaveBallots = False

  def OnSaveBallotsAs(self, event):

    # Ask the user to choose the filename.
    dlg = wx.FileDialog(self, "Save Ballot File",
                        style=wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
    if dlg.ShowModal() != wx.ID_OK:
      dlg.Destroy()
      return
    fName = dlg.GetPath()
    dlg.Destroy()

    # Save
    try:
      self.b.saveAs(fName)
    except RuntimeError, msg:
      wx.MessageBox(str(msg), "Error", wx.OK|wx.ICON_ERROR)
      return
    self.panel.NeedToSaveBallots = False

    # Set the window title to include the filename
    title = "%s - Ballot File Editor" % os.path.basename(fName)
    self.SetTitle(title)
    self.panel.fNameC.SetLabel(os.path.basename(fName))

  def OnSaveLog(self, event):

    if self.logfName == "":
      self.OnSaveLogAs(event)
      return

    try:
      self.log.SaveFile(self.logfName)
    except RuntimeError, msg:
      wx.MessageBox(str(msg), "Error", wx.OK|wx.ICON_ERROR)
      return

    self.panel.NeedToSaveLog = False

  def OnSaveLogAs(self, event):
    dlg = wx.FileDialog(self, "Save Log to a File",
                        style=wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
    if dlg.ShowModal() != wx.ID_OK:
      dlg.Destroy()
      return
    self.logfName = dlg.GetPath()
    dlg.Destroy()

    try:
      self.log.SaveFile(self.logfName)
    except RuntimeError, msg:
      wx.MessageBox(str(msg), "Error", wx.OK|wx.ICON_ERROR)
      return

    self.panel.NeedToSaveLog = False

  def OnExit(self, event):
    self.Close()

  def OnCloseWindow(self, event):

    # Check to see if the current ballot is empty and warn user
    if self.panel.currentBallot == []:
      txt = "The current ballot is empty.  Ok to close editor?"
      code = wx.MessageBox(txt, "Warning", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
      if code == wx.CANCEL:
        # Don't exit
        event.Veto()
        return

    # Ask user if we should save ballots.
    if self.panel.NeedToSaveBallots == True:
      if self.b.getFileName() is None:
        msg = "Do you want to save the ballots?"
      else:
        msg = "Do you want to save the ballots to %s?" % self.b.getFileName()
      saveBallots = wx.MessageBox(msg, "Warning",
                                  wx.YES_NO|wx.CANCEL|wx.ICON_INFORMATION)
      if saveBallots == wx.CANCEL:
        event.Veto() # Don't exit
        return
      elif saveBallots == wx.YES:
        self.OnSaveBallots(None) # Save ballots
      elif saveBallots == wx.NO:
        # If user is discarding ballot changes then don't ask to save the log
        self.panel.NeedToSaveLog = False

    # Ask user if we should also save the log.
    if self.panel.NeedToSaveLog == True:
      msg = "Do you want to save the log for ballot file %s?"\
            % os.path.basename(self.b.getFileName())
      saveLog = wx.MessageBox(msg, "Warning",
                                  wx.YES_NO|wx.CANCEL|wx.ICON_INFORMATION)
      if saveLog == wx.CANCEL:
        event.Veto() # Don't exit
        return
      elif saveLog == wx.YES:
        self.OnSaveLog(None) # Save log

    self.Destroy()

##################################################################

class BallotCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
  
  def __init__(self, parent, ID):
    style = wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES
    wx.ListCtrl.__init__(self, parent, ID, style=style)
    listmix.ListCtrlAutoWidthMixin.__init__(self)

  def computeColumnWidth(self):
    # This is another kluge to overcome a difficulty with ListCtrl.
    # You can easily set the column width to the largest entry or to
    # the width of the header, but not the largest of the two.
    # This hack does that.
    self.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
    w1 = self.GetColumnWidth(1)
    self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
    w2 = self.GetColumnWidth(1)
    w = max(w1, w2)
    return w

##   def GetMinSize(self):

##  # This is adapted from _doResize() in
##  #   /c/Python25/Lib/site-packages/wx-2.8-msw-ansi/wx/lib/mixins/listctrl.py
##     # but I couldn't get it to work.

##     w = self.GetColumnWidth(0) + self.GetColumnWidth(1)
##     if self.GetItemCount() > self.GetCountPerPage():
##       w = wx.SystemSettings_GetMetric(wx.SYS_VSCROLL_X)
##     return (w, -1)

##################################################################

class BallotsPanel(wx.Panel):

  def __init__(self, parent, b):
    wx.Panel.__init__(self, parent, -1)

    self.NeedToSaveBallots = False
    self.NeedToSaveLog = False
    self.b = b
    self.i = 0   # The number of the ballot being displayed
    if self.b.numBallots == 0:
      self.b.appendBallot([])
    self.currentBallot = self.b.getBallot(self.i)

    # Information box
    informationBox = wx.StaticBox(self, -1, "Information")
    fNameL = wx.StaticText(self, -1, "Filename:")
    fn = self.b.getFileName()
    if fn is None:
      fn = "New File"
    else:
      fn = os.path.basename(fn)
    self.fNameC = wx.StaticText(self, -1, fn)
    numBallotsL = wx.StaticText(self, -1, "No. of ballots:")
    self.numBallotsC = wx.StaticText(self, -1, "%d" % self.b.numBallots)
    numSeatsL = wx.StaticText(self, -1, "No. of seats:")
    numSeatsC = wx.StaticText(self, -1, "%d" % self.b.numSeats)
    numCandidatesL = wx.StaticText(self, -1, "No. of candidates:")
    numCandidatesC = wx.StaticText(self, -1, "%d" % self.b.numCandidates)
    titleL = wx.StaticText(self, -1, "Title:")
    title = ""
    if vars(self.b).has_key("title"): 
      title = self.b.title
    titleC = wx.TextCtrl(self, -1, title)
    self.Bind(wx.EVT_TEXT, self.OnTitle, titleC)

    # Rankings box
    rankingsBox = wx.StaticBox(self, -1, "Rankings")
    txt = """\
Click on a candidate's name to assign that candidate the next
available ranking, and double-click on a candidate's name to
remove the ranking and reorder the remaining candidates."""
    rankingsHelp = wx.StaticText(self, -1, txt)

    # Navigation box
    navigationBox = wx.StaticBox(self, -1, "Navigation")
    first = wx.Button(self, -1, "|<", style=wx.BU_EXACTFIT)
    prev = wx.Button(self, -1, "<", style=wx.BU_EXACTFIT)
    next = wx.Button(self, -1, ">", style=wx.BU_EXACTFIT)
    last = wx.Button(self, -1, ">|", style=wx.BU_EXACTFIT)
    self.spin = wx.SpinCtrl(self, -1, size=(60, -1))
    self.spin.SetRange(1, self.b.numBallots)
    self.spin.SetValue(1)
    go = wx.Button(self, -1, "Go", style=wx.BU_EXACTFIT)
    
    self.Bind(wx.EVT_BUTTON, self.OnNav, first)
    self.Bind(wx.EVT_BUTTON, self.OnNav, prev)
    self.Bind(wx.EVT_BUTTON, self.OnNav, next)
    self.Bind(wx.EVT_BUTTON, self.OnNav, last)
    self.Bind(wx.EVT_BUTTON, self.OnNav, go)

    # Operations box
    operationsBox = wx.StaticBox(self, -1, "Operations")
    clear = wx.Button(self, -1, "Clear This Ballot")
    delete = wx.Button(self, -1, "Delete This Ballot")
    append = wx.Button(self, -1, "Append New Ballot")
    exitBFE = wx.Button(self, -1, "Exit")

    self.Bind(wx.EVT_BUTTON, self.OnClear, clear)
    self.Bind(wx.EVT_BUTTON, self.OnDelete, delete)
    self.Bind(wx.EVT_BUTTON, self.OnAppend, append)
    self.Bind(wx.EVT_BUTTON, self.OnExit, exitBFE)

    # Ballot box
    self.ballotBox = wx.StaticBox(self, -1, "Ballot No. %d" % (self.i + 1))
    self.ballotC = BallotCtrl(self, -1)
    self.ballotC.InsertColumn(0, " R ", wx.LIST_FORMAT_RIGHT)
    self.ballotC.InsertColumn(1, "Candidate")
    self.ballotBox.SetLabel("Ballot No. %d" % (self.i+1))
    for c, name in enumerate(self.b.names):
      if c in self.currentBallot:
        r = self.currentBallot.index(c)
        self.ballotC.InsertStringItem(c, str(r+1))
      else:
        self.ballotC.InsertStringItem(c, "")
      self.ballotC.SetStringItem(c, 1, name)
    self.ballotC.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
    w = self.ballotC.computeColumnWidth()
    self.ballotC.SetColumnWidth(1, w)

    self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.OnColBeginDrag, self.ballotC)
    self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListClick, self.ballotC)
    self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListDClick, self.ballotC)

    # Sizers
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    leftSizer = wx.BoxSizer(wx.VERTICAL)

    # Information
    informationSizer = wx.StaticBoxSizer(informationBox, wx.VERTICAL)
    fgs = wx.FlexGridSizer(5, 2, 5, 5)
    fgs.Add(fNameL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(self.fNameC, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(numBallotsL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(self.numBallotsC, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(numSeatsL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(numSeatsC, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(numCandidatesL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(numCandidatesC, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(titleL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(titleC, 1, wx.EXPAND|wx.ALL)
    fgs.AddGrowableCol(1)
    informationSizer.Add(fgs, 0, wx.EXPAND|wx.ALL, 5)
    leftSizer.Add(informationSizer, 0, wx.EXPAND|wx.ALL, 5)

    # Rankings
    rankingsSizer = wx.StaticBoxSizer(rankingsBox, wx.VERTICAL)
    rankingsSizer.Add(rankingsHelp, 0, wx.ALIGN_CENTER|wx.ALL, 5)
    leftSizer.Add(rankingsSizer, 0, wx.EXPAND|wx.ALL, 5)

    # Navigation
    navigationSizer = wx.StaticBoxSizer(navigationBox, wx.VERTICAL)

    hSizer = wx.BoxSizer(wx.HORIZONTAL)
    hSizer.Add(first, 0, wx.ALIGN_CENTER|wx.ALL, 5)
    hSizer.Add(prev, 0, wx.ALIGN_CENTER|wx.ALL, 5)
    hSizer.Add(next, 0, wx.ALIGN_CENTER|wx.ALL, 5)
    hSizer.Add(last, 0, wx.ALIGN_CENTER|wx.ALL, 5)
    navigationSizer.Add(hSizer, 0, wx.ALIGN_CENTER, 0)

    hSizer = wx.BoxSizer(wx.HORIZONTAL)
    hSizer.Add(self.spin, 0, wx.ALIGN_CENTER|wx.ALL, 5)
    hSizer.Add(go, 0, wx.ALIGN_CENTER|wx.ALL, 5)
    navigationSizer.Add(hSizer, 0, wx.ALIGN_CENTER, 0)

    leftSizer.Add(navigationSizer, 0, wx.EXPAND|wx.ALL, 5)

    # Operations
    operationsSizer = wx.StaticBoxSizer(operationsBox, wx.VERTICAL)
    gs = wx.GridSizer(2, 2, 5, 5)
    gs.Add(clear, 0, wx.EXPAND)
    gs.Add(delete, 0, wx.EXPAND)
    gs.Add(append, 0, wx.EXPAND)
    gs.Add(exitBFE, 0, wx.EXPAND)
    operationsSizer.Add(gs, 0, wx.ALIGN_CENTER|wx.ALL, 5)
    leftSizer.Add(operationsSizer, 0, wx.EXPAND|wx.ALL, 5)

    # Ballot
    ballotSizer = wx.StaticBoxSizer(self.ballotBox, wx.VERTICAL)
    ballotSizer.Add(self.ballotC, 1, wx.EXPAND|wx.ALL, 5)
    # Need this ugly hack since wx.ListCtrl doesn't properly set its size
    w = self.ballotC.GetColumnWidth(0) + self.ballotC.GetColumnWidth(1)\
        + wx.SystemSettings_GetMetric(wx.SYS_VSCROLL_X) + 5
    ballotSizer.SetItemMinSize(self.ballotC, (w, -1))

    sizer.Add(leftSizer, 0, wx.EXPAND, 0)
    sizer.Add(ballotSizer, 0, wx.EXPAND|wx.ALL, 5)
    
    self.SetSizer(sizer)
    sizer.Fit(self)

  def OnExit(self, event):
    # Must be a cleaner way to do this?
    self.GetGrandParent().Close()

  def Log(self, txt):
    self.GetGrandParent().Log(txt)

  def OnColBeginDrag(self, event):
    # Don't allow column resizing
    event.Veto()

  def emptyBallotOK(self):
    #  Check if user is ok with navigating away from an empty ballot
    txt = "The current ballot is empty.  Ok to navigate to another ballot?"
    code = wx.MessageBox(txt, "Warning", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
    return code == wx.OK

  def storeCurrentBallot(self):
    # Store a copy of the current ballot to the ballots object
    self.b.setBallot(self.i, self.currentBallot)
    self.NeedToSaveBallots = True
    self.NeedToSaveLog = True
    
  def UpdatePanel(self):

    # Display the ballot number, and no. of ballots
    self.ballotBox.SetLabel("Ballot No. %d" % (self.i + 1))
    self.spin.SetValue(self.i + 1)
    self.spin.SetRange(1, self.b.numBallots)
    self.numBallotsC.SetLabel("%d" % self.b.numBallots)

    # Get rid of unsupported features
    if -1 in self.currentBallot:
      warnings.warn("Skipped rankings discarded from ballot %d." % (self.i+1))
    for ranking in self.currentBallot:
      if isinstance(ranking, list):
        warnings.warn("Duplicate rankings discarded from ballot %d" % (self.i+1))
        break
    self.currentBallot = [r for r in self.currentBallot 
                          if r != -1 and not isinstance(r, list)]
    
    # Update the list box to show the current ballot
    for c in xrange(self.b.numCandidates):
      if self.currentBallot.count(c) > 1:
        warnings.warn("Candidate %s appears on ballot %d more than once.  Later rankings ignored." % (self.b.names[c], self.i+1))
      if c in self.currentBallot:
        r = self.currentBallot.index(c)
        self.ballotC.SetStringItem(c, 0, str(r+1))
      else:
        self.ballotC.SetStringItem(c, 0, "")

  def OnClear(self, event):
    self.currentBallot = []
    self.storeCurrentBallot()
    self.UpdatePanel()
    self.Log("Cleared the rankings of ballot %d." % (self.i+1))

  def OnDelete(self, event):
    # Can't delete the last ballot
    if self.b.numBallots == 1:
      txt = "Can't delete.  Must have at least one ballot."
      wx.MessageBox(txt, "Error", wx.OK|wx.ICON_ERROR)
      return

    # Delete the current ballot
    self.b.deleteBallot(self.i)
    self.Log("Deleted ballot %d." % (self.i+1))
    self.NeedToSaveBallots = True
    self.NeedToSaveLog = True

    # Update the control
    self.i = min(self.i, self.b.numBallots - 1)
    self.currentBallot = self.b.getBallot(self.i)
    self.UpdatePanel()

  def OnAppend(self, event):

    if len(self.currentBallot) == 0 and not self.emptyBallotOK():
      return

    # Add blank ballot to end
    self.b.appendBallot([])
    self.Log("Appended ballot %d." % self.b.numBallots)
    self.NeedToSaveBallots = True
    self.NeedToSaveLog = True

    # Update the control
    self.i = self.b.numBallots - 1
    self.currentBallot = self.b.getBallot(self.i)
    self.UpdatePanel()
    
  def OnNav(self, event):

    if len(self.currentBallot) == 0 and not self.emptyBallotOK():
      return

    # Move to another ballot
    label = event.GetEventObject().GetLabel()
    if label == "|<":
      self.i = 0
    elif label == "<":
      self.i -= 1
    elif label == ">":
      self.i += 1
    elif label == ">|":
      self.i = self.b.numBallots - 1
    elif label == "Go":
      self.i = self.spin.GetValue() - 1
    else:
      assert(0)
    self.i = max(0, self.i)
    self.i = min(self.b.numBallots - 1, self.i)

    # Update the control
    self.currentBallot = self.b.getBallot(self.i)
    self.UpdatePanel()

  def OnListClick(self, event):
    c = event.m_itemIndex
    name = self.b.names[c]
    if c not in self.currentBallot:
      self.currentBallot.append(c)
      self.storeCurrentBallot()
      self.UpdatePanel()
      rank = len(self.currentBallot)
      self.Log("Added candidate %s to ballot %d with rank %d." %
               (name, self.i+1, rank))

    # Unselect the clicked item.  In some situations, the default behavior
    # is that an item of the list ctrl is selected, which prevents the user
    # from clicking directly on that item (the user must click elsewhere and
    # then click on the item).
    self.ballotC.SetItemState(c, 0, wx.LIST_STATE_SELECTED)    
    
  def OnListDClick(self, event):
    c = event.m_itemIndex
    name = self.b.names[c]
    if c in self.currentBallot:
      self.currentBallot.remove(c)
      self.storeCurrentBallot()
      self.UpdatePanel()
      self.Log("Removed candidate %s from ballot %d." %
               (name, self.i+1))

    # See comment in OnListClick
    self.ballotC.SetItemState(c, 0, wx.LIST_STATE_SELECTED)    

  def OnTitle(self, event):
    titleC = event.GetEventObject()
    self.b.title = titleC.GetValue().strip()
    self.NeedToSaveBallots = True

##################################################################

class CandidatesDialog(wx.Dialog):

  def __init__(self, parent, b):
    wx.Dialog.__init__(self, parent, -1, "New Ballot File")

    self.b = b
    self.names = []

    # Explanation
    txt = wx.StaticText(self, -1, """\
Enter the candidates' names one by one.  To remove a candidate
whose name has already been entered, double click on the candidate's
name below.""")

    # Candidate entry
    candidateL = wx.StaticText(self, -1, "Candidate to add:")
    self.candidateC = wx.TextCtrl(self, -1, "", style=wx.TE_PROCESS_ENTER)
    self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter, self.candidateC)
    candidateB = wx.Button(self, -1, "Add")
    self.Bind(wx.EVT_BUTTON, self.OnAdd, candidateB)

    # Candidate list
    listL = wx.StaticText(self, -1, "Candidates:")
    self.listC = wx.ListBox(self, -1, choices=self.b.names, size=(-1, 100))
    self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnListDClick, self.listC)
    blank = wx.StaticText(self, -1, "")

    # Buttons
    ok = wx.Button(self, wx.ID_OK)
    self.Bind(wx.EVT_BUTTON, self.OnOK, ok)
    cancel = wx.Button(self, wx.ID_CANCEL)

    # Sizers
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(txt, 0, wx.ALL, 5)
    sizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)

    fgs = wx.FlexGridSizer(2, 3, 5, 5)
    fgs.Add(candidateL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(self.candidateC, 0, wx.EXPAND)
    fgs.Add(candidateB, 0)
    fgs.Add(listL, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
    fgs.Add(self.listC, 0, wx.EXPAND)
    fgs.Add(blank, 0)
    fgs.AddGrowableCol(1)

    sizer.Add(fgs, 0, wx.EXPAND|wx.ALL, 5)
    bs = wx.StdDialogButtonSizer()
    bs.AddButton(ok)
    bs.AddButton(cancel)
    bs.Realize()
    sizer.Add(bs, 0, wx.EXPAND|wx.ALL, 5)

    self.SetSizer(sizer)
    sizer.Fit(self)

  def OnOK(self, event):
    # Check to see if name is entered and not added
    name = self.candidateC.GetValue().strip()
    if name == "":
      event.Skip()
    else:
      wx.MessageBox("Name entered but not added.  Please hit the 'Add' "
                    "button or clear the name in the text box to continue.",
                    "Message", wx.OK|wx.ICON_INFORMATION)
    self.b.names = self.names

  def OnEnter(self, event):
    self.OnAdd(event)
    
  def OnAdd(self, event):
    # Get the name in the text box
    name = self.candidateC.GetValue().strip()
    # Make sure the name is unique
    if name in self.names:
      wx.MessageBox("Can't have two candidates with the same name.",
                    "Error", wx.OK|wx.ICON_ERROR)
      self.candidateC.SetFocus()
      return
    # Make sure the name is not empty
    if name == "":
      wx.MessageBox("Candidate name cannot be blank.",
                    "Error", wx.OK|wx.ICON_ERROR)
      self.candidateC.SetFocus()
      return

    self.names.append(name)
    self.listC.Set(self.names)

    # Clear the text box to allow user to enter another name
    self.candidateC.Clear()
    self.candidateC.SetFocus()
    
  def OnListDClick(self, event):
    # Remove the candidate from the ballots instance and update the control
    c = self.listC.GetSelection()
    self.names.pop(c)
    self.listC.Set(self.names)
