"Plugin module for Scottish STV"

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

__revision__ = "$Id: ScottishSTV.py 715 2010-02-27 17:00:55Z jeff.oneill $"

from openstv.STV import WeightedInclusiveSTV
from openstv.plugins import MethodPlugin

##################################################################

class ScottishSTV(WeightedInclusiveSTV, MethodPlugin):
  "Scottish STV"

  methodName = "Scottish STV"
  longMethodName = "Scottish STV"
  status = 1

  htmlBody = """
<p>Scotland enacted these rules for local elections in 2007.  This is a
straightforward implementation of STV and recommended to
organizations using STV for the first time. </p>

<p>The complete set of rules can be found at
http://www.opsi.gov.uk/legislation/scotland/ssi2007/ssi_20070042_en.pdf.
The relevant portions of the these rules are included below.</p>

<p>OpenSTV's implementation of the Scottish STV rules has been
validated against the eSTV program.</p>

<hr>

<p align=center>SCOTTISH STATUTORY INSTRUMENTS</p>
<p align=center>2007 No. 42</p>
<p align=center>REPRESENTATION OF THE PEOPLE</p>
<p align=center>The Scottish Local Government Elections Order 2007</p>

<p><b>Citation, commencement and extent</b>

<p><b>1.</b>&mdash;(1) This Order may be cited as the Scottish Local
Government Elections Order 2007.

<p>(2) This Order shall come into force on 17th February 2007 except for
the purposes of any election to be held on or before 2nd May 2007.

<p>(3) This Order shall extend to Scotland only.

<p><b>Interpretation</b>

<p><b>2.</b> In this Order, unless the context otherwise requires&mdash;

<p>"anonymous entry" in relation to a register of electors, shall be construed
in accordance with section 9B of the 1983 Act and "the record of anonymous
entries" means the record prepared in pursuance of regulations made by virtue
of paragraph 8A of Schedule 2 to the 1983 Act;

<p>"ballot paper account" has the meaning given in rule 39(3);

<p>"companion" has the meaning given in rule 34(1);

<p>"corresponding number list" means the list prepared in accordance with rule 15;

<p>"completed corresponding number list" has the meaning given in rule 39(1);

<p>"continuing candidate" means any candidate not deemed to be elected as a
councillor and not excluded from the list of candidates under rule 50;

<p>"council" means a council constituted by section 2 of the Local Government etc.
(Scotland) Act 1994(b);

<p>"count" means all the operations involved in counting and crediting
votes, including the ascertainment of the quota, the transfer of
ballot papers and the exclusion of candidates;

<p>"election court" means the court constituted under the 1983 Act for
the trial of a petition questioning an election;

<p>"election petition" means a petition presented in pursuance of Part
III of the 1983 Act as that Act is applied by this Order;

<p>"election" means an election under the Local Governance (Scotland) Act
2004 and, for the purposes of articles 1(2) and 6(2), an election
under the Local Government etc. (Scotland) Act 1994;

<p>"elector" means a person who is registered in the register (or, in the
case of a person who has an anonymous entry in the register, in the
record of anonymous entries) to be used at the election as a local
government elector for the local government area in which the election
is held and includes a person shown in the register as below voting
age if (but only if) it appears from the register that such person
will be of voting age on the day fixed for the poll;

<p>"electoral registration officer" has the same meaning as in the 1983 Act;

<p>"electronic counting system" means such computer hardware and
software, other equipment, data and services as may be necessary in
order to&mdash;

<p>(a) maintain a list of the areas in relation to which an election is
being held by reference to ward barcodes on ballot papers issued to
voters in relation to that area;

<p>(b) read electronically the votes marked and the unique identifying
number on each ballot paper returned;

<p>(c) calculate the number of votes cast for each candidate at the
election otherwise than on any spoilt, tendered or rejected ballot
paper; and

<p>(d) ensure the retention of a record of the votes given for each
candidate, without identifying the elector by whom, or on whose
behalf, the votes were cast;

<p>"list of proxies" has the meaning given by paragraph 5(3) of Schedule
4 to the Representation of the People Act 2000;

<p>"local authority" means a council constituted by section 2 of the
Local Government etc.  (Scotland) Act 1994;

<p>"local government area" is to be construed in accordance with section 1
(local government areas) of the Local Government etc. (Scotland) Act
1994;

<p>"next available preference" means a preference which is the second or,
as the case may be, subsequent preference in consecutive order for a
continuing candidate (any preferences for any candidate who is deemed
to be elected or is excluded from the list of candidates under rule 50
being ignored);

<p>"non-transferable paper" means a ballot paper on which there is no
next available preference;

<p>"proper officer" has the same meaning as in section 235(3) of the
Local Government (Scotland) Act 1973(a);

<p>"postal voters list" means the list of persons kept in pursuance of
paragraph 5(2) (persons whose applications to vote by post have been
granted) of Schedule 4 to the Representation of the People Act
2000(b);

<p>"proxy postal voters list" means the list of persons kept in pursuance
of paragraph 7(8) (persons whose applications to vote by post as proxy
have been granted) of Schedule 4 to the Representation of the People
Act 2000;

<p>"qualifying address" in relation to a person registered in the
register of electors, is the address in respect of which that person
is entitled to be so registered;

<p>"quota" has the meaning given in rule 46;

<p>"registered political party" means a party registered under Part II of
the Political Parties, Elections and Referendums Act 2000(c);

<p>"returning officer" means, in relation to an election, the returning
officer appointed for the election under section 41(1) (duty of local
authority to appoint returning officer for each local authority
election) of the 1983 Act;

<p>"special lists" means the lists kept under paragraph 5 of schedule 4
to the Representation of the People Act 2000(d);

<p>"spoilt ballot paper" has the meaning given in rule 36;

<p>"stage of the count" means&mdash;

<p>(a) the determination of the number of votes for each candidate as
first preference;

<p>(b) the transfer of transferable papers from a candidate deemed to be
elected who has a surplus; or

<p>(c) the exclusion of a candidate at any given time;

<p>"surplus" means the number of votes, if any, by which the total number
of votes credited to a candidate deemed to be elected as a councillor
exceeds the quota;

<p>"tendered ballot paper" has the meaning given in rule 35(1);

<p>"tendered votes list" has the meaning given in rule 35(8);

<p>"transferable paper" means a ballot paper on which a next available
preference is given;

<p>"transfer value" means the value of a vote on a ballot paper
calculated in accordance with rule 48;

<p>"unique identifying mark" means the mark (for example, a bar code,
letter, number or numerical sequence) on a ballot paper which is
unique to that ballot paper and which identifies that ballot paper as
a ballot paper to be issued by the returning officer; and

<p>"voter" means a person voting at an election and includes a person
voting as proxy and "vote" (whether noun or verb) shall be construed
accordingly except that any
reference to an elector voting or an elector's vote shall include a
reference to an elector voting by proxy or an elector's vote given by
proxy.

<p align=center>* * *</p>

<p align=center>SCHEDULE 1</p>
<p align=center>PART III &mdash; CONTESTED ELECTIONS</p>

<p align=center>* * *</p>

<p align=center><b>Counting of votes</b></p>

<p align=center>* * *</p>

<p><i>First stage</i>

<p><b>45.</b>&mdash;(1) The returning officer shall sort the valid ballot
papers into parcels according to the candidates for whom first
preference votes are given.

<p>(2) The returning officer shall then&mdash;

<p>(a) count the number of ballot papers in each parcel;

<p>(b) credit the candidate receiving the first preference vote with one
vote for each ballot paper; and

<p>(c) record those numbers.

<p>(3) The returning officer shall also ascertain and record the total
number of valid ballot papers.

<p><i>The quota</i>

<p><b>46.</b>&mdash;(1) The returning officer shall divide the total
number of valid ballot papers for the electoral ward by a number
exceeding by one the number of councillors to be elected at the
election for that electoral ward.

<p>(2) The result of the division under paragraph (1) (ignoring any
decimal places), increased by one, is the number of votes needed to
secure the return of a candidate as a councillor (in these rules
referred to as the "quota").

<p><i>Return of councillors</i>

<p><b>47.</b>&mdash;(1) Where, at any stage of the count, the number of
votes for a candidate equals or exceeds the quota, the candidate is
deemed to be elected.

<p>(2) A candidate is returned as a councillor when declared to be
elected in accordance with rule 55(a).

<p><i>Transfer of ballot papers</i>

<p><b>48.</b>&mdash;(1) Where, at the end of any stage of the count, the
number of votes credited to any candidate exceeds the quota and,
subject to rules 49 and 52, one or more vacancies remain to be filled,
the returning officer shall sort the ballot papers received by that
candidate into further parcels so that they are grouped&mdash;

<p>(a) according to the next available preference given on those papers;
and

<p>(b) where no such preference is given, as a parcel of non-transferable
papers.

<p>(2) The returning officer shall, in accordance with this rule and rule
49, transfer each parcel of ballot papers referred to in paragraph
(1)(a) to the continuing candidate for whom the next available
preference is given on those papers and shall credit such continuing
candidates with an additional number of votes calculated in accordance
with paragraph (3).

<p>(3) The vote on each ballot paper transferred under paragraph (2)
shall have a value ("the transfer value") calculated as
follows&mdash;

<p>A divided by B

<p>Where

<p>A = the value which is calculated by multiplying the surplus of the
transferring candidate by the value of the ballot paper when received
by that candidate; and

<p>B = the total number of votes credited to that candidate,

<p>the calculation being made to five decimal places (any remainder being
ignored).

<p>(4) For the purposes of paragraph (3)&mdash;

<p>(a) "transferring candidate" means the candidate from whom the ballot
paper is being transferred; and

<p>(b) "the value of the ballot paper" means&mdash;

<p>(i) for a ballot paper on which a first preference vote is given for
the transferring candidate, one; and

<p>(ii) in all other cases, the transfer value of the ballot paper when
received by the transferring candidate.

<p><i>Transfer of ballot papers &mdash; supplementary provisions</i>

<p><b>49.</b>&mdash;(1) If, at the end of any stage of the count, the
number of votes credited to two or more candidates exceeds the quota
the returning officer shall&mdash;

<p>(a) first sort the ballot papers of the candidate with the highest
surplus; and

<p>(b) then transfer the transferable papers of that candidate.

<p>(2) If the surpluses determined in respect of two or more candidates
are equal, the transferable papers of the candidate who had the
highest number of votes at the end of the most recent preceding stage
at which they had unequal numbers of votes shall be transferred first.

<p>(3) If the numbers of votes credited to two or more candidates were
equal at all stages of the count, the returning officer shall decide,
by lot, which candidate's transferable papers are to be transferred
first.

<p><i>Exclusion of candidates</i>

<p><b>50.</b>&mdash;(1) If, one or more vacancies remain to be filled and&mdash;

<p>(a) the returning officer has transferred all ballot papers which are
required by rule 48 or this rule to be transferred; or

<p>(b) there are no ballot papers to be transferred under rule 48 or this
rule, the returning officer shall exclude from the election at that
stage the candidate with the then lowest number of votes.

<p>(2) The returning officer shall sort the ballot papers for the
candidate excluded under paragraph (1) into parcels so that they are
grouped&mdash;

<p>(a) according to the next available preference given on those papers; and

<p>(b) where no such preference is given, as a parcel of non-transferable
papers.

<p>(3) The returning officer shall, in accordance with this article,
transfer each parcel of ballot papers referred to in paragraph (2)(a)
to the continuing candidate for whom the next available preference is
given on those papers and shall credit such continuing candidates with
an additional number of votes calculated in accordance with paragraph
(4).

<p>(4) The vote on each ballot paper transferred under paragraph (3)
shall have a transfer value of one unless the vote was transferred to
the excluded candidate in which case it shall have the same transfer
value as when transferred to the candidate excluded under paragraph
(1).

<p>(5) This rule is subject to rule 52.

<p><i>Exclusion of candidates &mdash; supplementary provisions</i>

<p><b>51.</b>&mdash;(1) If, when a candidate has to be excluded under
rule 50&mdash;

<p>(a) two or more candidates each have the same number of votes; and

<p>(b) no other candidate has fewer votes,

<p>paragraph (2) applies.

<p>(2) Where this paragraph applies&mdash;

<p>(a) regard shall be had to the total number of votes credited to those
candidates at the end of the most recently preceding stage of the
count at which they had an unequal number of votes and the candidate
with the lowest number of votes at that stage shall be excluded; and

<p>(b) where the number of votes credited to those candidates was equal
at all stages, the returning officer shall decide, by lot, which of
those candidates is to be excluded.

<p><i>Filling of last vacancies</i>

<p><b>52.</b>&mdash;(1) Where the number of continuing candidates is equal to the
number of vacancies remaining unfilled, the continuing candidates are
deemed to be elected.

<p>(2) Where the last vacancies can be filled under this rule, no further
transfer shall be made.
"""
  
  htmlHelp = (MethodPlugin.htmlBegin % (longMethodName, longMethodName)) +\
             htmlBody + MethodPlugin.htmlEnd
  
  def __init__(self, b):
    WeightedInclusiveSTV.__init__(self, b)
    MethodPlugin.__init__(self)
    
    self.prec = 5
    self.threshName = ["Droop", "Static", "Whole"]
    self.delayedTransfer = "Off"
    self.batchElimination = "None"

