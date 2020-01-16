import json
import pathlib
import itertools
import collections

from pycldf import Source

from cldfbench import Dataset as BaseDataset
from cldfbench import CLDFSpec


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "afbo"

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        return CLDFSpec(module='StructureDataset', dir=self.cldf_dir)

    def cmd_download(self, args):
        pass

    def cmd_readme(self, args):
        lines, title_found = [], False
        for line in super().cmd_readme(args).split('\n'):
            lines.append(line)
            if line.startswith('# ') and not title_found:
                title_found = True
                lines.extend([
                    '',
                    "[![Build Status](https://travis-ci.org/cldf-datasets/afbo.svg?branch=master)]"
                    "(https://travis-ci.org/cldf-datasets/afbo)"
                ])
        lines.extend(['', self.raw_dir.read('ABOUT.md')])
        return '\n'.join(lines)

    def read(self, core, extended=False, pkmap=None, key=None):
        if not key:
            key = lambda d: int(d['pk'])
        res = collections.OrderedDict()
        for row in sorted(self.raw_dir.read_csv('{0}.csv'.format(core), dicts=True), key=key):
            res[row['pk']] = row
            if pkmap is not None:
                pkmap[core][row['pk']] = row['id']
        if extended:
            for row in self.raw_dir.read_csv('{0}.csv'.format(extended), dicts=True):
                res[row['pk']].update(row)
        return res

    def itersources(self, pkmap):
        for row in self.raw_dir.read_csv('source.csv', dicts=True):
            del row['jsondata']
            pkmap['source'][row.pop('pk')] = row['id']
            row['title'] = row.pop('description')
            row['key'] = row.pop('name')
            yield Source(row.pop('bibtex_type'), row.pop('id'), **row)

    def cmd_makecldf(self, args):
        self.schema(args.writer.cldf)
        pk2id = collections.defaultdict(dict)
        args.writer.cldf.add_sources(*list(self.itersources(pk2id)))

        for row in self.read('parameter', extended='affixfunction', pkmap=pk2id).values():
            args.writer.objects['ParameterTable'].append({
                'ID': row['id'],
                'Name': row['name'],
                'Representation': row['representation'],
                'Count_Borrowed': row['count_borrowed'],
            })

        identifier = self.read('identifier')
        lang2id = collections.defaultdict(lambda: collections.defaultdict(list))
        for row in self.read('languageidentifier').values():
            id_ = identifier[row['identifier_pk']]
            lang2id[row['language_pk']][id_['type']].append((id_['name'], id_['description']))

        glangs = {l.iso: l for l in args.glottolog.api.languoids()}
        for row in self.read('language', pkmap=pk2id).values():
            id = row['id']
            iso_codes = set(i[0] for i in lang2id[row['pk']].get('iso639-3', []))
            iso = list(iso_codes)[0] if len(iso_codes) == 1 else None
            glang = glangs.get(iso) if iso else None
            md = json.loads(row['jsondata'])
            args.writer.objects['LanguageTable'].append({
                'ID': id,
                'Name': row['name'],
                'ISO639P3code': iso,
                'Glottocode': glang.id if glang else None,
                'Macroarea': glang.macroareas[0].name if glang and glang.macroareas else None,
                'Latitude': row['latitude'],
                'Longitude': row['longitude'],
                'Genus': md['genus'],
                'Afbo_Macroarea': md['macroarea'],
            })
        args.writer.objects['LanguageTable'].sort(key=lambda d: int(d['ID']))

        refs = {
            ppk: [pk2id['source'][r['source_pk']] for r in rows]
            for ppk, rows in itertools.groupby(
                self.read('pairsource', key=lambda d: d['pair_pk']).values(),
                lambda d: d['pair_pk'],
            )
        }
        for row in self.read('pair', pkmap=pk2id, key=lambda d: int(d['id'])).values():
            args.writer.objects['donor_recipient_pairs.csv'].append({
                'ID': row['id'],
                'Name': row['name'],
                'Source': refs.get(row['pk'], []),
                'Donor_ID': pk2id['language'][row['donor_pk']],
                'Recipient_ID': pk2id['language'][row['recipient_pk']],
                'Description': """<html>
    <head>
        <style type="text/css">
{0}
        </style>
    </head>
    <body>
{1}
    </body>
</html>
""".format(self.raw_dir.read('pair.css'), row['description'])
            })

        vsdict = self.read('valueset', pkmap=pk2id)
        for row in self.read('value', extended='waabvalue').values():
            vs = vsdict[row['valueset_pk']]
            args.writer.objects['ValueTable'].append({
                'ID': row['id'],
                'Language_ID': pk2id['language'][vs['language_pk']],
                'Parameter_ID': pk2id['parameter'][vs['parameter_pk']],
                'Description': row['name'],
                'Value': row['numeric'],
                'Pair_ID': pk2id['pair'][row['pair_pk']],
            })

        args.writer.objects['ValueTable'].sort(
            key=lambda d: (int(d['Language_ID']), int(d['Parameter_ID'])))


    def schema(self, cldf):
        cldf.properties['dc:creator'] = "Frank Seifart"
        cldf.properties['dc:description'] = self.raw_dir.read('ABOUT.md')

        cldf.add_component('LanguageTable', 'Afbo_Macroarea', 'Genus')
        t = cldf.add_component(
            'ParameterTable',
            {'name': 'Representation', 'datatype': 'integer'},
            {'name': 'Count_Borrowed', 'datatype': 'integer'},
        )
        t.common_props['dc:description'] = "Affix functions"
        t = cldf.add_table(
            'donor_recipient_pairs.csv',
            'ID',
            'Name',
            {
                "name": "Source",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#source",
                "datatype": {"base": "string"},
                "separator": ";"
            },
            'Donor_ID',
            'Recipient_ID',
            {'name': 'Description', 'dc:format': 'text/html'},
            'Afbo_Macroarea',
            'Reliability',
            {'name': 'Count_Interrelated', 'datatype': 'integer'},
            {'name': 'Count_Borrowed', 'datatype': 'integer'},
        )
        t.add_foreign_key('Donor_ID', 'languages.csv', 'ID')
        t.add_foreign_key('Recipient_ID', 'languages.csv', 'ID')
        cldf.add_columns('ValueTable', 'Pair_ID')
        cldf.remove_columns('ValueTable', 'Code_ID', 'Comment', 'Source')
        cldf.add_foreign_key('ValueTable', 'Pair_ID', 'donor_recipient_pairs.csv', 'ID')
        cldf['ValueTable', 'Value'].common_props['dc:description'] = \
            "The number of borrowed affixes of a certain function from a certain donor language"
