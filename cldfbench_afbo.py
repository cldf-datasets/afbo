import re
import copy
import json
import pathlib
import itertools
import collections
import dataclasses

import bs4
from bs4 import BeautifulSoup
from pycldf import Source

from cldfbench import Dataset as BaseDataset
from cldfbench import CLDFSpec


@dataclasses.dataclass
class CSS:
    rules: dict[str, str]

    @classmethod
    def from_text(cls, text):
        res = {}
        p = re.compile(r'\s*\.(?P<name>[^{]+)(?P<rule>\{.*)')
        for line in text.split('\n'):
            line = line.strip()
            if line:
                if line.split()[0] in ('table', 'td,', 'h1,', 'ol,', 'li'):
                    continue
                if line.startswith('span.'):
                    continue
                if line.startswith('/* '):
                    continue
                m = p.fullmatch(line)
                assert m, line
                # FIXME: only keep font-style and text-decoration!
                res[m.group('name').strip()] = m.group('rule').strip()
        return cls(res)

    @staticmethod
    def get_form(p):
        def _get_form(text):
            m = re.search(r'<i>(?P<form>[^<]+)</i>(\s+‘(?P<gloss>[^’]+)’)?', text)
            if m:
                return m.group('form'), m.group('gloss')
            return None

        text = re.sub(r'\s+', ' ', str(p))
        ef, eg = None, None
        try:
            f, g = _get_form(text)
        except:
            raise ValueError(text)
        _, _, text = text.partition('e.g.')
        if text:
            e = _get_form(text.strip())
            if e:
                ef, eg = e

        # ‘poor’
        # e.g. vromopúnǝ ‘dirty work’
        #if ef is None:
        #    print(f, g, ef, eg)
        return f, g, ef, eg

    @staticmethod
    def handle_info(p, keys, tag=None):
        refs, has_u = [], False
        for a in p.find_all('a'):
            if 'id' in a.attrs and not a.text:
                a.extract()
        agg = []
        for c in p.contents:
            if isinstance(c, bs4.Tag):
                if c.name in ('a', 'u'):
                    if c.name == 'u':
                        has_u = True
                    agg.append(c.text)
                else:
                    assert c.name in ('i', 'b'), c.name
                    agg.append(str(c))
            else:
                agg.append(c.text)
        if agg:
            t = re.sub(r'\s+', ' ', ''.join(agg)).strip()
            print('--')
            r, refs = search(t, keys)
            print(r)
            print(refs)
            e = bs4.BeautifulSoup(r).html.body
            print(e)
            p.clear()
            for ee in e:
                p.append(copy.copy(ee))
        return refs, has_u
        #for l in text:
        #    print(l)

    def get_html_and_css(self, bs, td, id_, keys):
        td.name = 'div'
        del td.attrs['style']
        del td.attrs['class']

        for h1 in td.find_all('h1'):
            h1.name = 'p'

        for p in td.find_all('p'):
            del p.attrs['class']

        for span in td.find_all('span'):
            if span.attrs['class'] in self.rules:
                css = self.rules[span.attrs['class']]
                if 'bold' in css:
                    span.name = 'b'
                    del span.attrs['class']
                elif 'italic' in css:
                    span.name = 'i'
                    del span.attrs['class']
                elif 'underline' in css:
                    if span.getText().startswith('http'):
                        span.unwrap()
                    else:
                        span.name = 'u'
                        del span.attrs['class']
                else:
                    span.unwrap()
            else:
                assert span.attrs['class'].startswith('text-')
                span.unwrap()

        forms, refs = {}, set()
        ul = None
        count, what = None, None
        for i, p in enumerate(td.find_all('p')):
            if str(p) == '<p/>':
                p.extract()
                continue
            rs, has_u = self.handle_info(p, keys)
            refs |= set(rs)
            if has_u:
                m = re.match(r'^(?P<c>[0-9]+)\s+', p.getText())
                if m:
                    if count is not None:
                        assert count == 0, (str(td), id_, what, forms[what])
                    ul = bs.new_tag('ul')
                    div = bs.new_tag('div')
                    p.wrap(div)
                    div.append(ul)
                    count = int(m.group('c'))
                    what = p.getText()
                    forms[what] = []
                    continue
            if count:
                assert p.find('i'), str(p)
                forms[what].append(self.get_form(p))
                count -= 1
                p.name = 'li'
                ul.append(p)

        if count is not None:
            assert count == 0

        #print(str(td)[:100])
        return str(td), {' '.join(k.split()[1:]): v for k, v in forms.items()}, sorted(refs)


def key_to_regex(key, in_text=True):
    """
    :param in_text: If `True`, we assume the author name(s) to be part of regular text and only the\
    year (possibly) in brackets.
    """
    comps = key.split()
    if len(comps) > 1:
        authors = r'\s+'.join(
            [re.escape(c) if c not in {'&', 'and'} else r'(and|&)' for c in comps[:-1]])
        year = comps[-1]
        if in_text:
            return re.compile(r"{}(['’]s?)?(,\s*eds?,\s*)?\s*\(?{}".format(authors, year))
        return re.compile(
            r"\(((?P<qualifier>after|from)\s+)?{}(['’]s)?(,\s*eds?,\s*)?"
            r"\s*{}(\s*:\s*(?P<pages>[^,;)]+))?\)".format(authors, year))
    if in_text:
        return re.compile(r"(?<=\s){}(?=\s|\.|,)".format(comps[0]))
    return re.compile(r"\({}\)".format(comps[0]))


all = 0

def repl(key, sid, keys, s):
    global all

    def link(label, srcid):
        return '<a href="../sources.bib#cldf:' + srcid + '">' + label + '</a>'

    yp = re.compile(r'[,;]\s+(?P<label>[0-9]{4}([ab])?)\s*')
    p = key_to_regex(key)
    rem = s
    m = p.search(rem)
    while m:
        yield m.string[:m.start()], None
        ms = m.string[m.start():m.end()]
        rem = m.string[m.end():]
        bracket_handled = False
        if '(' in ms and rem.startswith(')'):
            ms += ')'
            rem = rem[1:]
            bracket_handled = True
        all += 1
        yield link(ms, sid), sid
        if (not bracket_handled) and '(' in ms:
            mm = yp.match(rem)
            while mm:
                all += 1
                kk = f"{' '.join(key.split()[:-1])} {mm.group('label')}"
                if kk in keys:
                    yield "; " + link(mm.group('label'), keys[kk]), keys[kk]
                else:
                    yield "; " + mm.group('label'), None
                rem = rem[mm.end():]
                mm = yp.match(rem)

        m = p.search(rem)
    yield rem, None


def search(s, keys, **kw):
    s = s.replace('‑', '-')
    for k, v in {
        'Maisak (2019:339) and (2023:66)': 'Maisak (2019:339) and Maisak (2023:66)',
        'Güldemann (1992:52, 53; 2003:187)': 'Güldemann (1992:52, 53) and Güldemann (2003:187)',
        'Adelaar (1987; see also 1996:1328)': 'Adelaar (1987; see also Adelaar 1996:1328)',
        'Adelaar (2012:149–150; see also Adelaar 2005; 2009; 2010)': 'Adelaar (2012:149–150); see also Adelaar (2005; 2009; 2010)',
    }.items():
        s = s.replace(k, v)
    r = s
    refs = set()
    for key, sid in keys.items():
        r_ = []
        for t, srcid in repl(key, sid, keys, r):
            r_.append(t)
            if srcid:
                refs.add(srcid)
        r = ''.join(r_)
    return r, sorted(refs)


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "afbo"

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        return CLDFSpec(module='StructureDataset', dir=self.cldf_dir)

    def cmd_download(self, args):
        from pycldf.sources import Sources

        sources = Sources.from_file(self.raw_dir / 'sources.bib')
        keys = {s['key']: s.id for s in sources}

        src = self.dir / '..' / 'afbo2' / '26-02-07-AfBo_2_0_submission'

        bs = BeautifulSoup(src.joinpath('table_tidy.html').read_text(encoding='utf8'), 'lxml-xml')
        css = CSS.from_text(bs.find('style').getText())
        header = None
        kinds = collections.Counter()
        all_html = []
        for i, tr in enumerate(bs.find_all('tr')):
            if i == 0:
                header = [td.getText().strip().replace('\n', ' ') for td in tr.find_all('td')]
            else:
                tds = tr.find_all('td')
                row = [td.getText().strip().replace('\n', ' ') for td in tds]
                row = dict(zip(header, row))
                assert re.fullmatch(r'[0-9]+\.', row['r#'])
                html, forms, refs = css.get_html_and_css(bs, tds[-1], row['r#'], keys)
                kinds.update(forms.keys())
                row['Comment'] = (html, forms)
                p = self.raw_dir / 'comments' / f"{row['r#']}html"
                all_html.append(html)
                p.write_text(
                    '<html><body>\n{}\n</body></html>'.format(html),
                    encoding='utf8')

                #print(re.sub(r'\s+', ' ', str(tds[-1].find('p'))))
        pathlib.Path('index.html').write_text('<html><body>\n{}\n</body></html>'.format('\n'.join(all_html)), encoding='utf8')
        print(all)

        for k, v in kinds.most_common():
            """
            number of borrowed affixes,
            comparative,
            superlative,
            adjectivizer: miscellaneous,
            adjectivizer: privative,
            adverbializer,
            clause-level TAM,
            clause linking,case: dative,
            case: ergative,
            case: non-locative peripheral case,
            case: locative,gender (human),
            noun class (inanimate),
            diminutive,
            augmentative,
            definite/indefinite,
            topic,
            focus,
            nominalizer: miscellaneous,
            nominalizer: agent,
            nominalizer: abstract,
            nominalizer: social group,
            nominalizer: place name,
            number: plural,
            number: dual,
            number: singular,
            nominal derivation (miscellaneous),
            possessor indexing,
            numeral classifier,
            numeral derivation: ordinals,
            numeral and quantifier derivation,
            valency: passive,
            valency: causative,
            valency: reflexive,
            valency: applicative,
            valency: reciprocal,
            verbal TAM,
            verbal derivation (miscellaneous),
            subject/object indexing,
            verbalizer,
            relativizer/subordinator,
            verbal negation            
            """
            #print(k, v)

        #['r#', 'perm.id', 'Macro-area', 'Donor language', 'DL Family', 'DL ISO', 'Recipient language', 'RL Family', 'RL ISO',
        # 'Comment']


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
