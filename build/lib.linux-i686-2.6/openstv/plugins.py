"Module to load plugins."

## Copyright (C) 2003-2010 Jeffrey O'Neill
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

__revision__ = "$Id: plugins.py 776 2010-06-05 17:35:35Z jeff.oneill $"

import sys
import os.path
import textwrap
import pkgutil

from openstv.utils import getHome

##################################################################

class MethodPlugin(object):
  "Base class used to identify method plugins."

  status = 0 # 0 is disabled; 1 is level 1; 2 is level 2
  
  htmlBegin = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>%s</title>
</head>
<body>

<h2>%s</h2>

"""

  htmlEnd = """
</body>
</html>
"""
  def __init__(self):
    self.guiOptions = []
  
  def createGuiOptions(self, options):

    for option in options:

      if option == "prec":
        self.guiOptions.append( ("""
label = wx.StaticText(self, -1, "Precision:")
control = wx.SpinCtrl(self, -1)
control.SetRange(0, 20)
control.SetValue(%d)""" % self.prec,
                           "GetValue()",
                           "prec") )
      
      elif option == "thresh0":
        self.guiOptions.append( ("""
label = wx.StaticText(self, -1, "Threshold:")
control = wx.Choice(self, -1, choices = ["Droop", "Hare"])
control.SetStringSelection("%s")""" % self.threshName[0],
                                "GetStringSelection()",
                                "threshName[0]") )

      elif option == "thresh1":
        self.guiOptions.append( ("""
label = wx.StaticText(self, -1, "")
control = wx.Choice(self, -1, choices = ["Dynamic", "Static"])
control.SetStringSelection("%s")""" % self.threshName[1],
                                "GetStringSelection()",
                                "threshName[1]") )
      
      elif option == "thresh2":
        self.guiOptions.append( ("""
label = wx.StaticText(self, -1, "")
control = wx.Choice(self, -1, choices = ["Whole", "Fractional"])
control.SetStringSelection("%s")""" % self.threshName[2],
                                "GetStringSelection()",
                                "threshName[2]") )

      elif option == "ballotCompletion":
        self.guiOptions.append( ("""
label = wx.StaticText(self, -1, "Ballot completion:")
control = wx.Choice(self, -1, choices = ["Off", "On"])
control.SetStringSelection("%s")""" % (self.ballotCompletion),
                                "GetStringSelection()",
                                "ballotCompletion") )

      elif option == "completionMethod":
        self.guiOptions.append( ("""
label = wx.StaticText(self, -1, "Completion method:")
choices = ["Borda on Smith Set",
           "IRV on Smith Set",
           "Schwartz Sequential Dropping"]
control = wx.Choice(self, -1, choices = choices)
control.SetStringSelection("%s")""" % self.completion,
                                "GetStringSelection()",
                                "completion") )

      elif option == "delayedTransfer":
        self.guiOptions.append( ("""
label = wx.StaticText(self, -1, "Delay Surplus Transfer:")
control = wx.Choice(self, -1, choices = ["Off", "On"])
control.SetStringSelection("%s")""" % self.delayedTransfer,
                                "GetStringSelection()",
                                "delayedTransfer") )

      elif option == "batchElimination":
        self.guiOptions.append( ("""
label = wx.StaticText(self, -1, "Candidate elimination:")
control = wx.Choice(self, -1, choices = ["None", "Zero", "Losers", "Cutoff"])
control.SetStringSelection("%s")""" % self.batchElimination,
                                "GetStringSelection()",
                                "batchElimination") )

      elif option == "batchCutoff":
        self.guiOptions.append( ("""
label = wx.StaticText(self, -1, "Batch cutoff:")
control = wx.SpinCtrl(self, -1)
control.SetRange(0, 10000)
control.SetValue(%d)""" % self.batchCutoff,
                                "GetValue()",
                                "batchCutoff") )

      elif option == "saveWinnersBallots":
        self.guiOptions.append( ("""
label = wx.StaticText(self, -1, "Save Winners Ballots:")
control = wx.CheckBox(self, -1, "")
control.SetValue(%s)""" % self.saveWinnersBallots,
                                "GetValue()",
                                "saveWinnersBallots") )

      else:
        assert(0)

##################################################################

class LoaderPlugin(object):
  "Base class used to identify ballot loader plugins."
  
  status = 0
  extensions = ["blt"]
  formatName = None
  
  def __init__(self):
    self.fName = ""

  def reportLoadError(self, msg):
    msg = "Error when loading %s format ballots.  %s"\
        % (self.formatName, msg)
    raise RuntimeError(msg)
    
  def normalizeFileName(self, fName):
    if fName == "": 
      raise RuntimeError, "No file name given for saving ballots."
    ext = os.path.splitext(fName)[1]
    if ('' == ext):
      fName += "." + self.extensions[0]
    return fName

  def load(self, ballotList, fName):
    """Load a file from a filename"""
    self.fName = fName
    f = open(self.fName, "r")
    self.loadFromObject(ballotList, f)
    f.close()

##################################################################

class ReportPlugin(object):
  "Base class used to identify report loader plugins."

  status = 0
  
  def __init__(self, e, outputFile=None, test=False):

    self.e = e
    self.cleanB = self.e.b
    self.dirtyB = self.e.b.dirtyBallots
    if self.dirtyB == None:
      self.dirtyB = self.cleanB
    self.outputFile = outputFile
    self.test = test

  def output(self, output):
    """Stream output to destination file-like object."""
    print >> self.outputFile, output,
    
  def generateReport(self):
    "Selector for major categories of methods."
    if self.e.methodName == "Condorcet":
      self.generateReportCondorcet()
    elif self.e.iterative:
      self.generateReportIterative()
    else:
      self.generateReportNonIterative()

  def getWinnerText(self, winners, width=0):
    """Get the text for the declaration of winners."""
    winners = list(winners)
    winners.sort()
    if len(winners) == 0:
      winTxt = "No winners."
    elif len(winners) == 1:
      winTxt = "Winner is %s." % self.cleanB.joinList(winners)
    else:
      winTxt = "Winners are %s." % self.cleanB.joinList(winners)
    if width > 0:
      winTxt = textwrap.fill(winTxt, width)
    return winTxt

  def getValuesForRound(self, round):
    """Get a list of values to print out for one round."""
    values = []
    display = self.e.displayValue

    #Round / Stage Number
    roundStage = round
    if self.e.methodName == "ERS97 STV":
      roundStage = self.e.roundToStage(round)
    values.append("%2d" % (roundStage+1))
    
    # Candidate vote totals for the round
    for candidate in range(self.cleanB.numCandidates):
      numVotes = self.e.count[round][candidate]
      # If candidate has lost and has no votes, leave blank
      if candidate in self.e.losers and \
         self.e.lostAtRound[candidate] <= round and numVotes == 0:
        values.append("") 
      # otherwise print the total.
      else:
        values.append( display(numVotes) )
    # Exhausted ballots
    values.append( display( self.e.exhausted[round] ))

    # Surplus and Threshold if dynamic
    if self.e.threshMethod:
      values.append(display( self.e.surplus[round] ))
      values.append(display( self.e.thresh[round]))
    return values

##################################################################

def getPlugins(package, baseClass, format, exclude0):
  """Find plugins of a specified type.
  
  Each plugin has a status value that may be 0, 1, or 2.  For status=0, the 
  plugin is excluded by default, but will be included if exclude0 is set to
  False.  For Method plugins, status=1 or 2 indicates whether the method
  appears in the fist tier list or second tier list.  For Loader and Report
  plugins there is only one tier.
  """

  assert(format in ["byName", "classes"])
  
  # Import all modules in package
  ppath = package.__path__
  pname = package.__name__ + "."
  for importer, modname, ispkg in pkgutil.iter_modules(ppath, pname):
    module = __import__(modname, fromlist = "dummy")
  
  # Look for user-installed plugins
  externalPluginDir = os.path.join(getHome(), "Plugins")
  if os.path.exists(externalPluginDir):
    if externalPluginDir not in sys.path:
      sys.path.append(externalPluginDir)
    externalPlugins = [x[:-3] for x in os.listdir(externalPluginDir) 
                       if x.endswith(".py")]
    for plugin in externalPlugins:
      __import__(plugin)
  
  # Get plugin list from subclasses of baseClass
  pluginClasses = []
  for m in baseClass.__subclasses__():
    if exclude0 and m.status == 0:
      del m
    else:
      pluginClasses.append(m)

  if format == "classes":
    return pluginClasses
  elif format == "byName":
    pluginClass = {}
    for p in pluginClasses:
      pluginClass[p.__name__] = p
    return pluginClass
  else:
    assert(0)

def getMethodPlugins(format, exclude0 = True):
  import openstv.MethodPlugins
  return getPlugins(openstv.MethodPlugins, MethodPlugin, format, exclude0)
  
def getReportPlugins(format, exclude0 = True):
  import openstv.ReportPlugins
  return getPlugins(openstv.ReportPlugins, ReportPlugin, format, exclude0)
  
def getLoaderPlugins(format, exclude0 = True):
  import openstv.LoaderPlugins
  return getPlugins(openstv.LoaderPlugins, LoaderPlugin, format, exclude0)

def getLoaderPluginClass(extension, exclude0 = True):
  "Return the most appropriate loader for a given file extension."
  plugins = getLoaderPlugins("classes", exclude0)
  for p in plugins:
    if extension.lower() in p.extensions:
      return p
  return None # No loader for this extension
