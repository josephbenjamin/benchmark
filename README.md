# Benchmark

This program was written to determine the reference gilt that is consistent with the ICMA Primary Market Handbook: _Chapter 7 Pricing_ 
guidance for pricing of GBP public bond issuance. The guidance provides an algorithm for selecting the reference gilt to
be used as for pricing a specific new GBP bond. 

The objective is to explore and better understand the sensitivity that
an issuer may have to the timing of issuance and the state of the gilt market. For example, between now and expected date
of issuance, is the reference gilt likely to change? Could an upcoming gilt auction, syndication or re-opening
cause a change to the reference, or is that unlikely? Are there any upcoming cliff-edges? This may be relevant when
the market is constructed of gilts trading far from par, ideosyncratic yield curve, etc.

Links to relevant sites and documents
- [ICMA Primary Market Handbook Home](https://www.icmagroup.org/market-practice-and-regulatory-policy/primary-markets/ipma-handbook-home/)
- [Amendments Archive](https://www.icmagroup.org/market-practice-and-regulatory-policy/primary-markets/ipma-handbook-home/icma-primary-market-handbook-amendments-archive/)
- [Prior Version - Chapter 7 Pricing](https://www.icmagroup.org/assets/Chapter-7-Jan-2022-update.pdf)
- [**Dec 2023 Update:: Chapter 7 Pricing**](https://www.icmagroup.org/assets/Chapter7_2023-12-v2.pdf)

| rule     | description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|:---------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **R7.3** | All gilts with an aggregate nominal amount of £10 billion or more should be considered as benchmarks, unless there are exceptional circumstances which could encompass situations such as specific liquidity events.                                                                                                                                                                                                                                                                                                                                                                                                |
| **R7.4** | The credit benchmark to reference in pricing a specific new Sterling bond should be: (a) where there is only one benchmark maturing in the same calendar year as that bond, that benchmark; (b) where there is no benchmark maturing in that calendar year, the nearest shorter maturity benchmark; (c) where there is more than one benchmark maturing in that calendar year: (i) the benchmark maturing in the same month as that bond, or failing which; (ii) the nearest shorter maturity benchmark in that calendar year, or failing which; (iii) the nearest longer maturity benchmark in that calendar year. 


## Open Questions
- [ ] What exactly is grounds for considering a benchmark gilt not appropriate?
  - Prior to Dec 2023, the Handbook made reference in section 7.3A to two specific Gilts which were
  agreed to have been deemed 'Not Appropriate', and it seems these were due to having high coupons
  - If this was due to the fact that the delta of a bond trading far from par would be quite different
  to the delta of a newly issued public bond (which would by definition be trading at or very close to par)
  then could it also be possible that a very low coupon bond could be considered 'Not Appropriate'?
  - At any rate, this section 7.3A is now removed...
- [ ] Who decides if a Benchmark gilt is not sufficiently liquid so as to be considered 'Not Appropriate'?


## Implementation
The program is constructed such that it can be updated directly with the latest information
on the Gilt Market from the D1A Gilts in Issue data provided by the 
Debt Management Office (DMO), which can be accessed [here](https://www.dmo.gov.uk/data/).

| format                      | direct link                                                                                                           |
|:----------------------------|:----------------------------------------------------------------------------------------------------------------------|
| **Gilts In Issue (D1A)**    | [https://www.dmo.gov.uk/data/pdfdatareport?reportCode=D1A](https://www.dmo.gov.uk/data/pdfdatareport?reportCode=D1A)  |                                                                                                                                                                                                         |
| **Gilts IN issue D1A: XML** | [https://www.dmo.gov.uk/data/XmlDataReport?reportCode=D1A](https://www.dmo.gov.uk/data/XmlDataReport?reportCode=D1A) | 

This data is then processed and saved as a clean csv file, and loaded back in as a pandas DataFrame (df).
The df is filtered for Conventional gilts.

An assumed New Issue Maturity date can be passed into the function to determine what the ICMA Benchmark
would be as of the current dataset.


## Visualisation
The program produces a chart and integrated table showing the breakdown
of the rules engine.\
Here is an illustrative output:\
![Illustrative Chart Output](figures/plot.svg)

## What are Benchmark Gilts?
Benchmark stocks are those gilts of which a large quantity has been issued, which are actively traded, and which tend to pay interest at rates in line with the prevailing market level of yields. Benchmark stocks provide a reference for the market and are also used to price other instruments of corresponding maturity, such as corporate bonds. 
https://publications.parliament.uk/pa/cm199900/cmselect/cmtreasy/154/15407.htm