import re
import copy
import pathlib
import functools
import collections
import dataclasses
import shutil
import urllib.parse
from typing import Union

from bs4 import BeautifulSoup, Tag
from pycldf import Sources
import simplepybtex
from pyglottolog import Glottolog as GlottologAPI
from pyglottolog.languoids import Languoid
from clldutils.html import HTML, literal
from clldutils.misc import slug
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


@dataclasses.dataclass
class References:
    sources: Sources
    keys: dict[str, str]
    regexes: dict[str, re.Pattern]
    count_links: int = 0
    matched: set = dataclasses.field(default_factory=set)

    @property
    def missed(self):
        return [srcid for srcid in self.keys.values() if srcid not in self.matched]

    @classmethod
    def from_sources(cls, sources):
        keys = {s['key']: s.id for s in sources}
        return cls(sources, keys, {k: cls.key_to_regex(k) for k in keys})

    def as_html(self):
        def source_as_html(src):
            return HTML.li(
                HTML.a(id='cldf:' + src.id),
                HTML.p(str(src))
            )

        return HTML.div(
            HTML.h2('References'),
            HTML.ul(
                *[source_as_html(src) for src in self.sources]
            )
        )

    @staticmethod
    def key_to_regex(key):
        comps = key.split()
        if len(comps) > 1:
            authors = r'\s+'.join(
                [re.escape(c) if c not in {'&', 'and'} else r'(and|&)' for c in comps[:-1]])
            year = comps[-1]
            return re.compile(r"{}(['’]s?)?(,\s*eds?,\s*)?\s*\(?{}".format(authors, year))
        return re.compile(r"(?<=\s){}(?=\s|\.|,)".format(comps[0]))

    def repl(self, key, sid, s):
        def link(label, srcid):
            return '('.join('<a href="?label=' + urllib.parse.quote_plus(s) + '#cldf:' + srcid + '">' + s + '</a>' for s in label.split('('))

        yp = re.compile(r'[,;]\s+(?P<label>[0-9]{4}([ab])?)\s*')
        rem = s
        m = self.regexes[key].search(rem)
        while m:
            yield m.string[:m.start()], None
            ms = m.string[m.start():m.end()]
            rem = m.string[m.end():]

            if re.match(r'[^<]+</a>', rem):
                # We are already in a link!
                yield ms, None
                m = self.regexes[key].search(rem)
                continue

            yield link(ms, sid), sid
            if '(' in ms and not rem.startswith(')'):
                mm = yp.match(rem)
                while mm:
                    kk = f"{' '.join(key.split()[:-1])} {mm.group('label')}"
                    if kk in self.keys:
                        yield "; " + link(mm.group('label'), self.keys[kk]), self.keys[kk]
                    else:
                        yield "; " + mm.group('label'), None
                    rem = rem[mm.end():]
                    mm = yp.match(rem)

            m = self.regexes[key].search(rem)
        yield rem, None

    def link(self, s):
        s = s.replace('‑', '-')
        s = s.replace('-', '-')
        for k, v in {
            'Maisak (2019:339) and (2023:66)': 'Maisak (2019:339) and Maisak (2023:66)',
            'Güldemann (1992:52, 53; 2003:187)': 'Güldemann (1992:52, 53) and Güldemann (2003:187)',
            'Adelaar (1987; see also 1996:1328)': 'Adelaar (1987; see also Adelaar 1996:1328)',
            'Adelaar (2012:149–150; see also Adelaar 2005; 2009; 2010)': 'Adelaar (2012:149–150); see also Adelaar (2005; 2009; 2010)',
            'Pușcariu': 'Pușcariu',
            'Puşcariu': 'Pușcariu',
            'Gutiérrez': 'Gutiérrez',
            'Gutiérrez Morales': 'Gutiérrez-Morales',
            'Abbi (1995a:183; 1997:139–142; 2001:47,53)': 'Abbi (1995a:183), Abbi (1997:139–142) and Abbi (2001:47,53)',
            'Loporcaro, Gardani and Giudici 2020': 'Loporcaro, Gardani and Giudici 2021',
            'Escure (2004:45–46; 2012)': 'Escure (2004:45–46) and Escure (2012)',
        }.items():
            s = s.replace(k, v)
        r = s
        refs = set()
        for key, sid in sorted(self.keys.items(), key=lambda i: -len(i[0])):
            r_ = []
            for t, srcid in self.repl(key, sid, r):
                r_.append(t)
                if srcid:
                    self.count_links += 1
                    self.matched.add(srcid)
                    refs.add(srcid)
            r = ''.join(r_)
        return r, sorted(refs)


@dataclasses.dataclass
class Glottolog:
    languoids: list[Languoid]

    @classmethod
    def from_path(cls, p):
        return cls.from_api(GlottologAPI(p))

    @classmethod
    def from_api(cls, api):
        return cls(list(api.languoids()))

    @functools.cached_property
    def by_iso(self):
        return {lg.iso: lg for lg in self.languoids if lg.iso}

    @functools.cached_property
    def families(self):
        return {lg.name: lg for lg in self.languoids if not lg.lineage}


@dataclasses.dataclass
class HTMLDoc:
    bs: BeautifulSoup
    glottolog: Glottolog
    refs: References
    stats: dict[int, dict[str, str]]

    @classmethod
    def from_path(cls, p, gl, refs, stats):
        return cls(BeautifulSoup(p.read_text(encoding='utf8'), 'lxml-xml'), gl, refs, stats)

    @functools.cached_property
    def css(self):
        return CSS.from_text(self.bs.find('style').getText())

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

        return f, g, ef, eg

    def normalize_paragraph(self, p):
        refs, has_u = [], False
        for a in p.find_all('a'):  # Remove anchors which made only sense in the Word doc.
            if 'id' in a.attrs and not a.text:
                a.extract()
        text = []
        for c in p.contents:
            if isinstance(c, Tag):
                if c.name in ('a', 'u'):
                    if c.name == 'u':  # Something underlined signals the affix group headers.
                        has_u = True
                    text.append(c.text)  # Drop the tag, keep the content.
                else:
                    assert c.name in ('i', 'b'), c.name
                    text.append(str(c))  # Keep <i> and <b>.
            else:
                text.append(c.text)
        if not text:
            return [], False
        # Normalize whitespace:
        t = re.sub(r'\s+', ' ', ''.join(text)).strip()
        # Turn references into links in the text representation:
        r, refs = self.refs.link(t)
        # Now parse the text into soup again:
        e = BeautifulSoup(r).html.body
        p.clear()
        for ee in e:
            p.append(copy.copy(ee))
        return refs, has_u

    def get_html(self, td):
        td.name = 'div'  # Turn the container into a div.
        del td.attrs['style']
        del td.attrs['class']

        for h1 in td.find_all('h1'):  # Some rows have content wrapped in h1 instead of p.
            h1.name = 'p'

        for p in td.find_all('p'):
            del p.attrs['class']

        # We replace styled spans with corresponding html tags (or remove the span tags).
        for span in td.find_all('span'):
            if span.attrs['class'] in self.css.rules:
                css = self.css.rules[span.attrs['class']]
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
            rs, has_u = self.normalize_paragraph(p)
            refs |= set(rs)
            if has_u:
                m = re.match(r'^(?P<c>[0-9]+)\s+', p.getText())
                if m:
                    if count is not None:
                        assert count == 0, (str(td), what, forms[what])
                    ul = self.bs.new_tag('ul')
                    div = self.bs.new_tag('div')
                    p.wrap(div)
                    div.append(ul)
                    count = int(m.group('c'))  # We should find this many affixes listed below.
                    what = p.getText()
                    forms[what] = []
                    continue
            if count:
                assert p.find('i'), str(p)  # Looks like an affix.
                forms[what].append(self.get_form(p))
                count -= 1
                p.name = 'li'
                ul.append(p)

        if count is not None:
            assert count == 0

        return (
            re.sub(r'\n+', '\n', str(td), re.M),
            {' '.join(k.split()[1:]): v for k, v in forms.items()},
            sorted(refs))

    def iter_pairs(self):
        header = None

        for i, tr in enumerate(self.bs.find_all('tr')):
            if i == 0:
                header = [td.getText().strip().replace('\n', ' ') for td in tr.find_all('td')]
            else:
                tds = tr.find_all('td')
                row = [td.getText().strip().replace('\n', ' ') for td in tds]
                row = dict(zip(header, row))
                html, forms, refs = self.get_html(tds[-1])
                p = Pair.from_row(row, html, refs, self.glottolog)
                p.count_borrowed = int(self.stats[p.id]['number of borrowed affixes'])
                yield p

    @functools.cached_property
    def pairs(self):
        return list(self.iter_pairs())

    def as_html(self):
        content = [HTML.h1('AfBo')]
        content.extend([p.as_html() for p in self.pairs])
        content.append(self.refs.as_html())
        return HTML.body(*content)

    def write_comments(self, p):
        p.write_text(f'<html>\n{self.as_html()}\n</html>')


@dataclasses.dataclass
class Language:
    name: str
    iso: list[str]
    family: tuple[str, str]
    subfamily: Union[str, None]

    @property
    def id(self):
        return slug(self.name + ''.join(self.iso))

    def as_dict(self, lgmd):
        lgmd = lgmd[(self.name, ' '.join(self.iso))]
        return dict(
            ID=self.id,
            Name=self.name,
            Family=self.family[0],
            Family_Glottocode=self.family[1],
            Genus=self.subfamily,
            ISO639P3code=self.iso,
            Glottocode=lgmd['glottocode'],
            Latitude=float(lgmd['latitude']),
            Longitude=float(lgmd['longitude']),
        )

    @classmethod
    def from_row(cls, name, clf, iso, gl: Glottolog):
        iso = {
            # RL:
            'son': 'dje',
            'cct': 'akz cic cho',
            # DL:
            'aze': 'azb azj',
            'fre': 'fra',
        }.get(iso, iso).split()
        assert all(i in gl.by_iso or (i == 'lng') for i in iso), (name, clf, iso)

        clf = clf.replace('IE', 'Indo-European').strip()
        clf = {
            # RL:
            'Mixe-Zoquean': 'Mixe-Zoque',
            'Tangic': 'Tangkic',
            ('Arnhem', 'wnd'): 'Mangarrayi-Maran',
            'Uru-Chipayan': 'Uru-Chipaya',
            'dje': 'Songhay',
            'dta': 'Mongolic-Khitan',
            'Purepecha/Tarascan': 'Tarascan/Purepecha',
            # DL:
            'Sahaptin': 'Sahaptian',
            'Guaicuruan, Matacoan': 'Mataguayan',
            'Garawan': 'Garrwan',
            ('Arnhem', 'nuy'): 'Gunwinyguan',
            ('Arnhem', 'nid'): 'Gunwinyguan',
            'cmn': 'Sino-Tibetan/Sinitic',
        }.get((clf, iso[0]) if clf == 'Arnhem' else clf, clf)
        family, _, subfamily = clf.partition('/')
        assert family in gl.families, (name, family, iso)
        return cls(
            name=name,
            iso=iso,
            family=(family, gl.families[family].id),
            subfamily=subfamily or None)


@dataclasses.dataclass
class Pair:
    id: int
    macroarea: str
    donor: Language
    recipient: Language
    comment: str
    references: list[str]
    count_borrowed: int = 0

    @property
    def name(self):
        return f"{self.donor.name} affixes in {self.recipient.name}"

    def as_dict(self, comment_file_id):
        return dict(
            ID=self.id,
            Name=self.name,
            Source=self.references,
            Donor_ID=self.donor.id,
            Recipient_ID=self.recipient.id,
            Description=comment_file_id,
            Macroarea=self.macroarea,
            Count_Borrowed=self.count_borrowed,
        )

    @classmethod
    def from_row(cls, row, html, refs, gl):
        return cls(
            id=int(row['perm.id']),
            macroarea=row['Macro-area'],
            donor=Language.from_row(row['Donor language'], row['DL Family'], row['DL ISO'], gl),
            recipient=Language.from_row(row['Recipient language'], row['RL Family'], row['RL ISO'], gl),
            comment=html,
            references=refs,
        )

    def as_html(self):
        return HTML.div(
            HTML.h2(self.name),
            literal(self.comment))

    def as_markdown(self):
        md = self.comment
        md = md.replace('*', '&ast;')
        md = md.replace('<i>', '_')
        md = md.replace('</i>', '_')
        md = md.replace('<b>', '__')
        md = md.replace('</b>', '__')
        md = md.replace('<p>', '\n')
        md = md.replace('</p>', '')
        md = md.replace('<p/>', '')
        md = md.replace('<div>', '\n')
        md = md.replace('</div>', '')
        md = md.replace('<ul>', '\n')
        md = md.replace('</ul>', '\n')
        md = md.replace('<li>', '\n- ')
        md = md.replace('</li>', '')
        md = re.sub(
            r'<a href="(?P<anchor>\?[^#]+#cldf:[^"]+)">(?P<label>[^<]+)</a>',
            lambda m: f"[{m.group('label')}](sources.bib{m.group('anchor')})",
            md)
        return f'# {self.name}{md}'

    def write_html(self, p):
        p.write_text(f'<html><body>\n{self.as_html()}\n</body></html>')


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "afbo"

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        return CLDFSpec(module='StructureDataset', dir=self.cldf_dir)

    def cmd_download(self, args):
        # Main table saved from word file as HTML, then ran tidy on it.
        # Sources run through anystyle
        pass

    def cmd_makecldf(self, args):
        self.schema(args.writer.cldf)

        lgmd = {(r['name'], r['iso']): r for r in self.etc_dir.read_csv('languages.csv', dicts=True)}

        args.writer.cldf.add_sources(simplepybtex.database.parse_string(
            self.raw_dir.joinpath('sources.bib').read_text(encoding='utf8'),
            bib_format='bibtex',
        ))

        non_count = ('Pairs', 'Recipient language', 'Donor language', 'number of borrowed affixes')
        counts = collections.defaultdict(dict)
        for row in self.raw_dir.read_csv('BoCatSum.csv', dicts=True):
            row = {k: v if k in non_count else int(v or '0') for k, v in row.items()}
            if row['perm.id']:
                counts[int(row.pop('perm.id'))] = row

        for col in counts[1]:
            if col not in non_count:
                args.writer.objects['ParameterTable'].append({
                    'ID': slug(col),
                    'Name': col,
                    'Representation': len([k for k, v in counts.items() if v[col]]),
                    'Count_Borrowed': sum(v[col] for k, v in counts.items()),
                })

        langs = set()
        html_doc = HTMLDoc.from_path(
            self.raw_dir / 'table_tidy.html',
            Glottolog.from_api(args.glottolog.api),
            References.from_sources(args.writer.cldf.sources),
            counts,
        )
        recipients = {}
        comment_dir = self.cldf_dir / 'comments'
        comment_dir.mkdir(exist_ok=True)
        for pair in html_doc.pairs:
            recipients[pair.id] = pair.recipient.id
            if pair.donor.id not in langs:
                args.writer.objects['LanguageTable'].append(pair.donor.as_dict(lgmd))
                langs.add(pair.donor.id)
            if pair.recipient.id not in langs:
                args.writer.objects['LanguageTable'].append(pair.recipient.as_dict(lgmd))
                langs.add(pair.recipient.id)

            fid = f'{pair.id}-md'
            p = comment_dir / f'{pair.id}.md'
            p.write_text(pair.as_markdown(), encoding='utf8')
            args.writer.objects['MediaTable'].append(dict(
                ID=fid,
                Media_Type='text/markdown',
                Format='CLDF Markdown',
                Description=f'Comments on {pair.name}',
                Download_URL=str(p.relative_to(self.cldf_dir)),
            ))
            args.writer.objects['donor_recipient_pairs.csv'].append(pair.as_dict(fid))

        args.log.info('%s reference links inserted', html_doc.refs.count_links)

        for pair, values in counts.items():
            lid = recipients[pair]
            for param, val in values.items():
                if param in non_count:
                    continue
                if val == 0:
                    continue
                pid = slug(param)
                args.writer.objects['ValueTable'].append({
                    'ID': f'{pair}-{pid}',
                    'Language_ID': lid,
                    'Parameter_ID': pid,
                    'Description': '',  # Pair name?
                    'Value': val,
                    'Pair_ID': pair,
                })

        shutil.copy(self.dir / 'ABOUT.md', self.cldf_dir)
        args.writer.objects['MediaTable'].append(dict(
            ID='about',
            Media_Type='text/markdown',
            Format='CLDF Markdown',
            Download_URL='ABOUT.md',
        ))
        shutil.copy(self.raw_dir / 'BoCatSum.csv', self.cldf_dir / 'value_matrix.csv')
        args.writer.objects['MediaTable'].append(dict(
            ID='matrix',
            Media_Type='text/csv',
            Download_URL='value_matrix.csv',
            Description='AfBo affix count matrix',
        ))
        return

    def schema(self, cldf):
        cldf.properties['dc:creator'] = "Frank Seifart and Francesco Gardani"
        cldf.properties['dc:description'] = "See [ABOUT.md](ABOUT.md) in this directory."
        cldf['ValueTable'].common_props['dc:description'] = \
            ("Values in AfBo are counts of borrowed affixes for a particular function. These are "
             "assigned to the recipient language.")

        cldf.add_component(
            'MediaTable',
            {'name': 'Format', 'propertyUrl': 'http://purl.org/dc/terms/conformsTo'}
        )
        cldf.add_component(
            'LanguageTable',
            'Family',
            'Family_Glottocode',
            'Genus',
        )
        cldf[('LanguageTable', 'ISO639P3code')].separator = ' '
        t = cldf.add_component(
            'ParameterTable',
            {'name': 'Representation', 'datatype': 'integer'},
            {'name': 'Count_Borrowed', 'datatype': 'integer'},
        )
        t.common_props['dc:description'] = "Affix functions"
        t = cldf.add_table(
            'donor_recipient_pairs.csv',
            {'name': 'ID', "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id"},
            {'name': 'Name', "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#name"},
            {
                "name": "Source",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#source",
                "datatype": {"base": "string"},
                "separator": ";"
            },
            {
                "name": "Description",
                "dc:description": "The referenced CLDF Markdown file describes the borrowed affixes.",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#mediaReference",
            },
            'Donor_ID',
            'Recipient_ID',
            {
                "name": "Macroarea",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#macroarea",
            },
            {'name': 'Count_Borrowed', 'datatype': 'integer'},
        )
        t.common_props['dc:description'] = \
            "Pairs of languages (or languoids) between which affix borrowings are observed."
        t.add_foreign_key('Donor_ID', 'languages.csv', 'ID')
        t.add_foreign_key('Recipient_ID', 'languages.csv', 'ID')
        cldf.add_columns('ValueTable', 'Pair_ID')
        cldf.remove_columns('ValueTable', 'Code_ID', 'Comment', 'Source')
        cldf.add_foreign_key('ValueTable', 'Pair_ID', 'donor_recipient_pairs.csv', 'ID')
        cldf['ValueTable', 'Value'].common_props['dc:description'] = \
            "The number of borrowed affixes of a certain function from a certain donor language"
