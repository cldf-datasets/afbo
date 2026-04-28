<a name="ds-structuredatasetmetadatajson"> </a>

# StructureDataset AfBo 2.0: A world-wide survey of affix borrowing

**CLDF Metadata**: [StructureDataset-metadata.json](./StructureDataset-metadata.json)

**Sources**: [sources.bib](./sources.bib)

See [ABOUT.md](ABOUT.md) in this directory.

property | value
 --- | ---
[dc:bibliographicCitation](http://purl.org/dc/terms/bibliographicCitation) | Seifart, Frank, and Gardani, Francesco. 2026. AfBo 2.0: A world-wide survey of affix borrowing. Leipzig: Max Planck Institute for Evolutionary Anthropology. DOI: 10.5281/zenodo.3610154
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF StructureDataset](http://cldf.clld.org/v1.0/terms.rdf#StructureDataset)
[dc:creator](http://purl.org/dc/terms/creator) | Frank Seifart and Francesco Gardani
[dc:identifier](http://purl.org/dc/terms/identifier) | https://afbo.info/
[dc:license](http://purl.org/dc/terms/license) | https://creativecommons.org/licenses/by/4.0/
[dcat:accessURL](http://www.w3.org/ns/dcat#accessURL) | https://github.com/cldf-datasets/afbo
[prov:wasDerivedFrom](http://www.w3.org/ns/prov#wasDerivedFrom) | <ol><li><a href="https://github.com/cldf-datasets/afbo/tree/767e280">cldf-datasets/afbo v1.0-7-g767e280</a></li><li><a href="https://github.com/glottolog/glottolog/tree/v5.3">Glottolog v5.3</a></li></ol>
[prov:wasGeneratedBy](http://www.w3.org/ns/prov#wasGeneratedBy) | <ol><li><strong>python</strong>: 3.12.3</li><li><strong>python-packages</strong>: <a href="./requirements.txt">requirements.txt</a></li></ol>
[rdf:ID](http://www.w3.org/1999/02/22-rdf-syntax-ns#ID) | afbo
[rdf:type](http://www.w3.org/1999/02/22-rdf-syntax-ns#type) | http://www.w3.org/ns/dcat#Distribution


## <a name="table-valuescsv"></a>Table [values.csv](./values.csv)

Values in AfBo are counts of borrowed affixes for a particular function. These are assigned to the recipient language.

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF ValueTable](http://cldf.clld.org/v1.0/terms.rdf#ValueTable)
[dc:extent](http://purl.org/dc/terms/extent) | 373


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string`<br>Regex: `[a-zA-Z0-9_\-]+` | Primary key
[Language_ID](http://cldf.clld.org/v1.0/terms.rdf#languageReference) | `string` | References [languages.csv::ID](#table-languagescsv)
[Parameter_ID](http://cldf.clld.org/v1.0/terms.rdf#parameterReference) | `string` | References [parameters.csv::ID](#table-parameterscsv)
[Value](http://cldf.clld.org/v1.0/terms.rdf#value) | `string` | The number of borrowed affixes of a certain function from a certain donor language
`Pair_ID` | `string` | References [donor_recipient_pairs.csv::ID](#table-donorrecipientpairscsv)

## <a name="table-mediacsv"></a>Table [media.csv](./media.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF MediaTable](http://cldf.clld.org/v1.0/terms.rdf#MediaTable)
[dc:extent](http://purl.org/dc/terms/extent) | 134


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string`<br>Regex: `[a-zA-Z0-9_\-]+` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Description](http://cldf.clld.org/v1.0/terms.rdf#description) | `string` | 
[Media_Type](http://cldf.clld.org/v1.0/terms.rdf#mediaType) | `string`<br>Regex: `[^/]+/.+` | 
[Download_URL](http://cldf.clld.org/v1.0/terms.rdf#downloadUrl) | `anyURI` | 
[Path_In_Zip](http://cldf.clld.org/v1.0/terms.rdf#pathInZip) | `string` | 
[Format](http://purl.org/dc/terms/conformsTo) | `string` | 

## <a name="table-languagescsv"></a>Table [languages.csv](./languages.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF LanguageTable](http://cldf.clld.org/v1.0/terms.rdf#LanguageTable)
[dc:extent](http://purl.org/dc/terms/extent) | 191


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string`<br>Regex: `[a-zA-Z0-9_\-]+` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Macroarea](http://cldf.clld.org/v1.0/terms.rdf#macroarea) | `string` | 
[Latitude](http://cldf.clld.org/v1.0/terms.rdf#latitude) | `decimal`<br>&ge; -90<br>&le; 90 | 
[Longitude](http://cldf.clld.org/v1.0/terms.rdf#longitude) | `decimal`<br>&ge; -180<br>&le; 180 | 
[Glottocode](http://cldf.clld.org/v1.0/terms.rdf#glottocode) | `string`<br>Regex: `[a-z0-9]{4}[1-9][0-9]{3}` | 
[ISO639P3code](http://cldf.clld.org/v1.0/terms.rdf#iso639P3code) | list of `string`<br>Regex: `[a-z]{3}` (separated by ` `) | 
`Family` | `string` | 
`Family_Glottocode` | `string` | 
`Genus` | `string` | 

## <a name="table-parameterscsv"></a>Table [parameters.csv](./parameters.csv)

Affix functions

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF ParameterTable](http://cldf.clld.org/v1.0/terms.rdf#ParameterTable)
[dc:extent](http://purl.org/dc/terms/extent) | 42


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string`<br>Regex: `[a-zA-Z0-9_\-]+` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Description](http://cldf.clld.org/v1.0/terms.rdf#description) | `string` | 
[ColumnSpec](http://cldf.clld.org/v1.0/terms.rdf#columnSpec) | `json` | 
`Representation` | `integer` | 
`Count_Borrowed` | `integer` | 

## <a name="table-donorrecipientpairscsv"></a>Table [donor_recipient_pairs.csv](./donor_recipient_pairs.csv)

Pairs of languages (or languoids) between which affix borrowings are observed.

property | value
 --- | ---
[dc:extent](http://purl.org/dc/terms/extent) | 132


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Source](http://cldf.clld.org/v1.0/terms.rdf#source) | list of `string` (separated by `;`) | References [sources.bib::BibTeX-key](./sources.bib)
[Description](http://cldf.clld.org/v1.0/terms.rdf#mediaReference) | `string` | The referenced CLDF Markdown file describes the borrowed affixes.<br>References [media.csv::ID](#table-mediacsv)
`Donor_ID` | `string` | References [languages.csv::ID](#table-languagescsv)
`Recipient_ID` | `string` | References [languages.csv::ID](#table-languagescsv)
[Macroarea](http://cldf.clld.org/v1.0/terms.rdf#macroarea) | `string` | 
`Count_Borrowed` | `integer` | 

