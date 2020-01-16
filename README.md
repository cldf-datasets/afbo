# AfBo: A world-wide survey of affix borrowing

[![Build Status](https://travis-ci.org/cldf-datasets/afbo.svg?branch=master)](https://travis-ci.org/cldf-datasets/afbo)

Cite the source dataset as

> Seifart, Frank. 2013. AfBo: A world-wide survey of affix borrowing. Leipzig: Max Planck Institute for Evolutionary Anthropology.

This dataset is licensed under a CC-BY-4.0 license

Available online at https://afbo.info/


# About AfBo

## Data sources

Information on borrowed affixes was compiled by Frank Seifart from a variety of sources, as explicitly indicated for each case. Most information comes from published sources, especially descriptive grammars and other descriptive studies on, e.g., language contact or morphology. Different sources on the same language were consulted wherever possible. In many cases important additional information (and in some cases, all information) comes from personal communications from experts on the languages in question.


## Language sample

The sample of languages includes in principle all cases of affix borrowing that have come to my attention between 2007 and 2013, i.e. no attempt has been made to make the sample genealogically or areally balanced. If two or more pairs of languages (or dialects) are very similar in the aspects relevant here, only one pair has been included in the database, namely the language pair with the higher number of borrowed affixes. For instance, Chuvash (Turkic) affixes in Mari (Uralic) are included in the database, but excluded is the similar set of Chuvash affixes that the Mordvinian languages borrowed, which are closely related to Mari.

There is a clear bias in the language sample towards those language families and areas that are linguistically best described, especially European/Western Eurasian and Oriental languages. This is because detecting affix borrowing requires relatively detailed information not only on the recipient and donor language but crucially also comparative evidence from both of these languages for the proof of borrowing and determining the direction of borrowing.

Included in the sample are two languages that are often considered as "mixed languages", Gurindji Kriol from Northern Australia and Copper Island Aleut from the Commander Islands in the Bering Strait. Unlike other mixed languages, it is possible for these two to clearly identify one language as the matrix language (Myers-Scotton 2002; Myers-Scotton 2007), which contributes the morphosyntactic framework as well as a substantial portion of the vocabulary. This language is identified as the recipient language (English for Gurindji Kriol and Aleut for Copper Island Aleut) and the other contributing languages as the donor language (Gurindji for Gurindji Kriol and Russian for Copper Island Aleut), following Meakins' (2011) analysis of (English-based) Gurindji Kriol as having borrowed Gurindji case markers. Note that in AfBo, Gurindji Kriol and Copper Island Aleut do not appear as borrowing exceptionally many affixes: Gurindji Kriol is the sixth most heavily affix-borrowing language in the sample, Copper Island Aleut the ninth.


## What counts as an affix?

Any morphologically bound form from a closed class that fulfills a derivational or inflectional function counts as an affix in AfBo. By this definition, clitics are included as instances of affix borrowing, as long as they fulfill a derivational or inflectional function, e.g. tense, evidentiality, or topic marking. Potential doubts whether a given form is a bound or a free are explicitly noted in the descriptions and often a reason to consider such a case as less reliable (see below).

Some forms are included here that might be considered morphologically conditioned allomorphs because they fulfill the same function in different environments. For instance, a plural marker used with animate nouns and a plural marker used with inanimate nouns are counted as two borrowed affixes.


## Proof of borrowing

An affix is considered as effectively borrowed only if it is used on at least some native stems, i.e. it is not considered as borrowed if it only combines with equally borrowed stems, forming complex loanwords. In addition, a complete proof that a given affix is borrowed would ideally include (i) evidence that the borrowed affix was not present in the recipient language before contact, (ii) evidence that the source form was present in the donor language at the time of contact, and (iii) evidence that the similarity between source form and borrowed form is not coincidental. Even though the sources consulted for AfBo rarely if ever explicitly provide such complete information, the authors of these sources are often authorities in the language families concerned, which gives credibility to their judgments that a given form is borrowed.


## Data coding

Data are coded for a number of properties for comparative analyses (note that parts of this information are included in the web interface, while other parts are included in the downloadable database). Information on recipient languages involved in affix borrowing include:

1. language name
2. genealogical affiliation
3. iso 639-3 language identification code
4. an approximate geographic location
5. affiliation with a geographic macro area

For each recipient language, additionally the following information is provided:

1. the total number of borrowed affixes
2. the total number of interrelated borrowed affixes in the sense of Seifart (2012)
3. reliability of borrowed status/affixhood

The information provided for each borrowed affix consists of the following:

1. form of the borrowed affix
2. approximate function (e.g. agent nominalizer) and distribution (e.g. forming nouns from adjectives)
3. examples of hybrid formations, i.e. combinations of borrowed affixes with native stems, for over 500 borrowed affixes. In the remaining cases, the original sources explicitly state that the form is used on native stems.
4. based on the approximate functions and distributions of borrowed affixes, these are grouped into morphosyntactic subsystems and the overall number of borrowed affixes per subsystem is given (e.g. three nominalizer that form nouns from adjectives, two case markers, and one number marker)
5. Where possible, the overall number of forms in recipient language subsystems into which affixes were borrowed is given (e.g., three out of a total of five case markers are borrowed)

## Reliability of borrowed status and affixhood

The information on individual cases of affix borrowing varies in terms of reliability, either because information is lacking in available descriptions or the descriptions themselves acknowledge uncertainties. The reliability of data is coded as high (66 cases), mid (31 cases), or low (4 cases) in the database. Most often this refers to uncertainty of the borrowed status, due to lack of comparative evidence or to uncertainty with respect to its status as an affix (vs. free form).
Representation of data ⇫

Data are given throughout as in the original sources, i.e. no attempt at standardization through transliteration was made.


## Using and citing AfBo

If you go back to the original resource, on which descriptions of affix borrowing in AfBo are based, that original resource should be cited. If you refer to results obtained from AfBo, such as the frequency of borrowing affixes with a specific function, you should cite AfBo as

> Seifart, Frank. 2013. AfBo: A world-wide survey of affix borrowing. Leipzig: Max Planck Institute for Evolutionary Anthropology. (Available online at https://afbo.info)

## Acknowledgements

Many people have contributed to building AfBo, as explicitly noted in the descriptions of individual case of affix borrowing. In addition, I am grateful to Martin Haspelmath for publishing AfBo as part of the Cross-Linguistic Linked Data project, to Robert Forkel for programming the web interface, and to Lena Sell, Lisa Steinbach, and Evgeniya Zhivotova for proofreading.
