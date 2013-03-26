"Plugin module for N. Ireland STV"

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

__revision__ = "$Id: NIrelandSTV.py 715 2010-02-27 17:00:55Z jeff.oneill $"

from openstv.STV import GregorySTV
from openstv.plugins import MethodPlugin

##################################################################

class NIrelandSTV(GregorySTV, MethodPlugin):
  "N. Ireland STV"

  methodName = "N. Ireland STV"
  longMethodName = "N. Ireland STV"
  status = 1

  htmlBody = """
<p>The STV rules used for local elections in Northern Ireland are
similar to the ERS97 rules, but significantly simpler.</p>

<p>The Local Elections (Northern Ireland) Order 1985.
Statutory Instrument 1985 No. 454.
Not available online.</p>

<hr>

<p align=center><b>STATUTORY INSTRUMENTS</b></p>

<p align=center><b>1985 No. 454</b></p>

<p align=center><b>NORTHERN IRELAND</b></p>

<p align=center>The Local Elections (Northern Ireland) Order 1985</p>

<p align=center>PART IV &mdash; Counting Of Votes</p>

<p align=center><i>Interpretation</i></p>

<p><b>41.</b> In this Part of these rules&mdash;

<p>"continuing candidate" means any candidate not deemed to be elected
and not excluded;

<p>"count" means all the operations involved in the counting of the first
preferences recorded for candidates, the transfer of the surpluses of elected
candidates, and the transfer of the vote, of excluded candidates;

<p>"deemed to be elected" means deemed to be elected for the purpose of the
counting of the votes but without prejudice to the declaration of the result of
the poll;

<p>"mark" means a figure a word written in the English language or a mark
such as "X";

<p>"non-transferable vote" means a ballot paper&mdash;

<p>(a) on which no second or subsequent preference
is recorded for a continuing candidate, or

<p>(b) which is excluded by the returning officer
under rule 50(4);

<p>"preference" as used in the following contexts has the meaning assigned
below:&mdash;

<p>(a) "first preference" means the figure "1" or any
mark or word which clearly indicates a first (or only) preference;

<p>(b) "next available preference" means a preference
which is the second
or, as the case may be, subsequent preference recorded in
consecutive order for a continuing candidate (any candidate who is
deemed to be elected or is excluded thereby being ignored), and

<p>(c) in this context, a "second preference" is shown by
the figure "2" or
any mark or word which clearly indicates a second preference, a
third preference by the figure "3" or any mark or word which clearly
indicates a third preference, arid so on;

<p>"quota" means the number calculated in accordance with rule 48;

<p>"surplus" means the number of votes by which the total number of votes
for any candidate (whether first preference or transferred votes, or a
combination of both) exceeds the quota; but references in these rules to the
transfer of the surplus means the transfer (at a transfer value) of all
transferable papers from the candidate who has the surplus;

<p>"stage of the count" means&mdash;

<p>(a) the determination of the first preference vote for each candidate;

<p>(b) the transfer of a surplus of a candidate deemed to be elected; or

<p>(c) the exclusion of one or more candidates at any given time;

<p>"transferable paper" means a ballot paper on which, following a first
preference, a second or subsequent preference is recorded in consecutive
numerical order for a continuing candidate;

<p>"transferred vote" means a vote derived from a ballot paper on which a
second or subsequent preference is recorded for the candidate to whom that
paper has been transferred;

<p>"transfer value" means the value of a transferred vote calculated in
accordance with paragraph (4) or (7) of rule 49, as the case may be.

<p align=center>* * *</p>

<p align=center><i>Rejected ballot papers</i></p>

<p><b>46.</b>&mdash; (1) Any ballot paper&mdash;

<p>(a) which does not bear the official mark; or

<p>(b) on which the figure 1 standing alone is not placed so as to
indicate a first preference for some candidate; or

<p>(c) on which the figure 1 standing alone indicating a first preference is set
opposite the name of more than one candidate; or

<p>(d) on which anything (other than the printed number on the back) is
written or marked by which the voter can be identified; or

<p>(e) which is unmarked or void for uncertainty,

<p>shall be void and not counted, but the ballot paper shall not be void by reason
only of carrying the words "one", "two", "three", (and so on) or any other
mark instead of a figure if, in the opinion of the returning officer, the word or
mark clearly indicates a preference or preferences.

<p>(2) The returning officer shall endorse "rejected" on any ballot paper which
under this rule is not to be counted and if an election agent objects to his
decision shall add to the endorsement the words "rejection objected to".

<p>(3) The returning officer shall prepare a statement showing the number of
ballot papers rejected by him under each of sub-paragraphs (a), (b),
(c), (d), and (e) of paragraph (I) and shall, on request, allow any
candidate or agent of a candidate to copy such statement.

<p>(4) The decision of the returning officer on any question arising in respect of
a ballot paper shall be final but shall be subject to review on an
election petition.

<p align=center><i>First stage</i></p>

<p><b>47.</b>&mdash; (1) The returning officer shall sort the ballot papers into parcels
according to the candidates for whom first preference votes are given.

<p>(2) The returning officer shall then count the number of first preference
votes given on ballot papers for each candidate and shall record
those numbers.

<p>(3) The returning officer shall also ascertain and record the number of valid
ballot papers.

<p align=center><i>The quota</i></p>

<p><b>48.</b>&mdash; (1) The returning officer shall divide the number of valid ballot papers
by a number exceeding by one the number of members to be elected.

<p>(2) The result, increased by one, of the division under paragraph (1) (any
fraction being disregarded) shall be the number of votes sufficient to
secure the election of a candidate (in these rules referred to as "the quota").

<p>(3) At any stage of the count a candidate whose total vote equals or exceeds
the quota shall be deemed to be elected, except that at an election where there is
only one vacancy a candidate shall not be deemed to be elected until the
procedure set out in paragraphs (1) to (3) of rule 51 has been
complied with.


<p align=center><i>Transfer of votes</i></p>

<p><b>49.</b>&mdash; (1) Where the number of first preference votes for any candidate
exceeds the quota, the returning officer shall sort all the ballot papers on which
first preference votes are given for that candidate into sub-parcels so that they
are grouped&mdash;

<p>(a) according to the next available preference given on those papers for
any continuing candidate, or

<p>(b) where no such preference is given, as the sub-parcel of non-transferable votes.

<p>(2) The returning officer shall count the number of ballot papers in each
parcel referred to in paragraph (1)

<p>(3) The returning officer shall, in accordance with this rule and rule 50,
transfer each sub-parcel of ballot papers referred to in sub-paragraph (a) of
paragraph (1) to the candidate for whom the next available preference is given
on those papers.

<p>(4) The vote on each ballot paper transferred under paragraph (3) shall be at
a value ("the transfer value") which&mdash;

<p>(a) reduces the value of each vote transferred so that the total value
of all such votes does not exceed the surplus, and

<p>(b) is calculated by dividing the surplus of the candidate from whom the
votes arc being transferred by the total number of the ballot papers on
which those votes an given, the calculation being made to two decimal
places (ignoring the remainder if any).

<p>(5) Where, at the cad of any stage of the count involving the transfer of
ballot papers, the number of votes for any candidate exceeds the quota, the
returning officer shall sort the ballot papers in the sub-parcel of transferred
votes which was last received by that candidate into separate sub-parcels so
that they are grouped&mdash;

<p>(a) according to the next available preference given on those papers for
any continuing candidate, or

<p>(b) where no such preference is given, as the sub-parcel of non-transferable votes.

<p>(6) The returning officer shall, in accordance with this rule and and
rule 50, transfer each sub-parcel of ballot papers referred to in sub-paragraph (a) of
paragraph (5) to the candidate for whom the next available preference is given
on those papers.

<p>(7) The vote on each ballot paper transferred under paragraph (6) shall be
at&mdash;

<p>(a) a transfer value calculated as set out in sub-paragraph (b) of
paragraph (4), or

<p>(b) at the value at which that vote was received by the candidate from
whom it is now being transferred,

<p>whichever is the less.

<p>(8) Each transfer of a surplus constitutes a stage in the count.

<p>(9) Subject to paragraph (10), the returning officer shall proceed to transfer
transferable papers until no candidate who is deemed to be elected has a
surplus or all of the vacancies have been filled.

<p>(10) Transferable papers shall not be liable to be transferred where any
surplus or surpluses which, at a particular stage of the count, have not already
been transferred, are

<p>(a) less than the difference between the total vote then credited to the
continuing candidate with the lowest recorded vote and the vote of the
candidate with the next lowest recorded vote; or

<p>(b) less than the difference between the total votes of the two or more
continuing candidates, credited at that stage of the count with the
lowest recorded total numbers of votes and the candidate next above
such candidates.

<p>(11) This rule shall not apply at an election where there is only one vacancy.


<p align=center><i>Supplementary provisions on transfer</i></p>

<p><b>50.</b>&mdash; If at any stage of the count, two or more candidates have
surpluses, the transferable papers of the candidate with the largest
surplus shall be transferred first, and if&mdash;

<p>(a) the surplus determined in respect of two or more candidates are
equal, the transferable papers of the candidate who had the highest
recorded votes at the earliest preceding stage at which they had
unequal votes, shall be transferred first, and

<p>(b) the votes credited to two or more candidates were equal at all stages of
the count, the returning officer shall decide between those candidates
by lot and the transferable papers of the candidate on whom the lot
falls shall be transferred first.

<p>(2) The returning officer shall, on each transfer of transferable papers under
rule 49&mdash;

<p>(a) record the total transfer value of the votes transferred to each
candidate;

<p>(b) add that value to the previous total of votes recorded for each
candidate, and record the new total;

<p>(c) record as non-transferable votes the difference between the surplus
and the total transfer value of transferred votes and add that difference
to the previously recorded total of non-transferable votes, and

<p>(d) compare&mdash;

<p>(i) the total number of votes then recorded for all of the candidates,
together with total number of non-transferable votes, with

<p>(ii) the recorded total of valid first preference votes.

<p>(3) All ballot papers transferred under rule 49 or 51 shall be clearly marked,
either individually or as a sub-parcel, so as to indicate the transfer value
recorded at that time to each vote on that paper or, as the case may
be, all the papers in that sub-parcel.

<p>(4) Where a ballot paper is so marked that it is unclear to the returning
officer at any stage of the count under rule 49 or 51 for which candidate the
next preference is recorded, the returning officer shall treat any vote on that
ballot paper as a non-transferable vote; and votes on a ballot paper shall be so
treated where, for example, the names of two or more candidates (whether
continuing candidates or not) are so marked that, in the opinion of the
returning officer, the same order of preference is indicated or the numerical
sequence is broken.

<p align=center><i>Exhaustion of candidates</i></p>

<p><b>51.</b>&mdash;(1) if&mdash;

<p>(a) all transferable papers which under the provisions of rule 49
(including that rule as applied by paragraph (11)) and this rule are
required to be transferred, have been transferred, and

<p>(b) subject to rule 52 one or more vacancies remain to be filled,

<p>the returning officer shall exclude from the election at that stage the candidate
with the then lowest vote (or, where paragraph (12) applies, the candidates with
the then lowest votes).

<p>(2) The returning officer shall sort all the ballot papers on which first
preference votes are given for the candidate or candidates excluded under
paragraph (1) into two sub-parcels so that they are grouped as&mdash;

<p>(a) ballot papers on which a next available preference is given, and

<p>(b) ballot papers on which no such preference is given (thereby including
ballot papers on which preferences are given only for candidates who
are deemed to be elected or are excluded).

<p>(3) The returning officer shall,  in accordance with this rule and rule 50,
transfer each sub-parcel of ballot papers referred to in sub-paragraph (a) of
paragraph (2) to the candidate for whom the next available preference is given
on those papers.

<p>(4) The exclusion of a candidate, or of two or more candidates together,
constitutes a further stage of the count.

<p>(5) If, subject to rule 52, one or more vacancies still remain to be filled, the
returning officer shall then sort the transferable papers, if any, which had been
transferred to any candidate excluded under paragraph (1) into sub-parcels
according to their transfer values.

<p>(6) The returning officer shall transfer those papers in the sub-parcel of
transferable papers with the highest transfer value to the continuing candidates
in accordance with the next available preferences given on those papers
(thereby passing over candidates who are deemed to be elected or are
excluded).

<p>(7) The vote on each transferable paper transferred under paragraph (6)
shall be at the value at which that vote was received by the candidate
excluded under paragraph (1).

<p>(8) Any papers on which no next available preferences have been expressed
shall be set aside as non-transferable votes.

<p>(9) After the returning officer has completed the transfer of the ballot papers
in the sub-parcel of ballot papers with the highest transfer value he shall
proceed to transfer in the same way the sub-parcel of ballot papers with the
next highest value and so on until he has dealt with each sub-parcel of a
candidate excluded under paragraph (1).

<p>(10) The returning officer shall after each stage of the count completed
under this rule&mdash;

<p>(a)   record&mdash;

<p>(i) the total value of votes, or

<p>(ii) the total transfer value of votes transferred to each candidate;

<p>(b) add that total to the previous total of votes recorded for each candidate
and record the new total;

<p>(c) record the value of non-transferable votes and add that value to the
previous non-transferable votes total, and

<p>(d) compare&mdash;

<p>(i) the total number of votes then recorded for each candidate
together with the total number of non-transferable votes, with

<p>(ii) the recorded total of valid first preference votes.

<p>(11) If after a transfer of votes under any prevision of this rule, a candidate
has a surplus, that surplus shall be dealt with in accordance with paragraphs (5)
to (10) of rule 49 and rule 50.

<p>(12) Where the total of the votes of the two or more lowest candidates,
together with any surpluses not transferred is less than the number of votes
credited to the next lowest candidate, the returning officer shall in one
operation exclude such two or more candidates.

<p>(13) If where a candidate has to be excluded under this rule, two or more
candidates each have the same number of votes and are lowest&mdash;

<p>(a) regard shall be had to the total number of votes credited to those
candidates at the earliest stage of the count at which they had an
unequal number of votes and the candidate with the lowest number of
votes at that stage shall be excluded; and

<p>(b) where the number of votes credited to those candidates was equal at
all stages, the returning officer shall decide between the candidates by
lot and the candidate on whom the lot falls shall be excluded.


<p align=center><i>Filling last vacancies</i></p>

<p><b>52.</b>&mdash; (1) Where the number of continuing candidates is equal to the number
of vacancies remaining unfilled the continuing candidates shall thereupon be
deemed to be elected.

<p>(2) Where only one vacancy remains unfilled and the votes of any one
continuing candidate are equal to or greater than the total of votes credited to
another or other continuing candidates together with any surplus not
transferred, the candidate shall thereupon be deemed to be elected.

<p>(3) Where the last vacancies can be filled under this rule, no further transfer
of votes shall be made.

"""

  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd

  def __init__(self, b):
    GregorySTV.__init__(self, b)
    MethodPlugin.__init__(self)
    
    self.prec = 2
    self.weakTieBreakMethod = "forward"
    self.threshName = ["Droop", "Static", "Whole"]
    self.delayedTransfer = "On"
    self.batchElimination = "Losers"

  def sortVotesByTransferValue(self, cList):
    "Sort votes according to N. Ireland rules."

    self.votesByTransferValue = {}
    for loser in cList:
      for i in self.votes[loser]:
        v = self.transferValue[i]
        if i in self.batches[loser][0]:
          key = "first"
        else:
          key = v
        if key not in self.votesByTransferValue.keys():
          self.votesByTransferValue[key] = []
        self.votesByTransferValue[key].append(i)

    self.transferValues = self.votesByTransferValue.keys()
    if "first" in self.transferValues:
      self.transferValues.remove("first")
      self.transferValues.sort(reverse=True)
      self.transferValues.insert(0, "first")
    else:
      self.transferValues.sort(reverse=True)      

  def transferVotesFromCandidates(self, elimList):
    elimList.sort()
    nTransferValues = len(self.transferValues)
    if nTransferValues == 0:
      # This will happen when all eliminated candidates have 0 votes
      self.updateRound()
      self.updateWinners()
      self.roundInfo[self.R]["eliminate"] += \
          "Count after eliminating %s. No votes are "\
          "transferred since all eliminated candidates "\
          "have zero votes. " % self.b.joinList(elimList)
      self.describeRound()
    else:
      self.roundInfo[self.R]["eliminate"] += \
          "Count after eliminating %s and transferring "\
          "votes. " % self.b.joinList(elimList)
      for v in self.transferValues:
        self.transferVotesWithValue(v)
        self.updateRound()
        self.describeRound()
        if self.electionOver():
          break
