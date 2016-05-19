OpenSTV: Introduction & Historical Notes
========================================

This is OpenSTV 1.7.  OpenSTV is open source voting software that implements the single transferable vote (STV) election method.

The canonical home for this archived version of OpenSTV is actually https://github.com/Conservatory/openstv/ (however, that tree is the same as the one here.) 
The software is not being maintained; 
at the very least, no one is maintaining the versions here or in the Conservatory. 

If you're looking for voting software, as of May 2016 the places to start are probably:

* Agora Voting: https://github.com/agoravoting
* Helios Voting: https://vote.heliosvoting.org/
* Condorcet Internet Voting Service: http://civs.cs.cornell.edu/
* Apache STeVe (https://steve.apache.org/)
* https://github.com/conservancy/voting (lists a bunch of other software too)
* https://github.com/mdipierro/evote
* https://github.com/Conservatory/openstv (including here so you have a complete list)

One of the first 4 is probably your best bet. 

Choice of voting system is a complex question, and the right choice depends on what kinds of outcomes you're going for.

OpenSTV History
---------------

OpenSTV was released under the GNU General Public License version 2 (or later) until around mid-2011.  At that point its main author, Jeff O'Neill, took future versions proprietary.  As of this writing, the latest version along the proprietary line is 2.1.0 and it is available for purchase from http://www.openstv.org/.  It looks like O'Neill also offers an online web app at http://www.opavote.org/, in case you don't want to set up OpenSTV 2.x yourself.

The last open source version of OpenSTV he released was 1.7, which is available here.  If this were ever to become the root of a new open source development line, good manners would dictate that we change the name to something other than "OpenSTV" (unless O'Neill prefers it stay the same).  However, that's not an issue at this point, as what's here is exactly what was released as "OpenSTV 1.7" back in 2011.

For more information about OpenSTV's history, the temporary disappearance of the 1.7 source code from the public Internet, and its eventual restoration, see:

  * http://groups.google.com/group/openstv-announce/browse_frm/month/2011-06?pli=1
  * http://meta.stackoverflow.com/questions/125579/downloading-openstv-doesnt-work
  * http://meta.stackoverflow.com/questions/78203/is-it-legal-for-stack-overflow-to-redistribute-openstv-binaries
  * https://github.com/OpenTechStrategies/openstv/commit/32df12393eae3f1ce8c00ac99d07e4045a3fbda6

Below is the original README.txt from Jeff O'Neill (just reformatted to Markdown for consistency with the rest of this file):

Original README.txt from OpenSTV 1.7
====================================

`Revision $Id: README.txt 578 2009-08-26 01:13:50Z jeff.oneill $`

Overview
--------

OpenSTV is a program for implementing the single transferable vote (STV).  STV is used for electing a group of people (e.g. council, committee, legislature) and it provides for proportional representation of the electorate.  The idea behind proportional representation is that the demographics of the elected group should, at least roughly, match the demographics of the electorate.  The beauty of STV is that there are no reserved seats and the proportional representation arises naturally.  For more information see

  * http://www.fairvote.org/
  * http://www.electoral-reform.org.uk/

In an STV election, each voter simply ranks the candidates in order of preference.  The rules for counting the votes with STV are more complicated than winner-take-all elections.  The votes can be counted by hand, but it is useful to have a computer program to speed up the process.  There are several variations of STV, but most users should use the default options.

Installation
------------

See http://www.OpenSTV.org/ for more information.

Jeff O'Neill
jeff.oneill at openstv.org
