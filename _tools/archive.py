"""Builds the archived copy of a live legal page, the way 1.2.0 was built.

usage: legal_archive.py <legal repo> <version> [--check]
  writes privacy/<v>/ and terms/<v>/ (+ sr/, hr/) from the live pages;
  with --check, compares against what is already there instead of writing.
"""
import sys, pathlib

NOTICE = {
    ('en', 'terms'): 'You are viewing version {v} of these terms. <a href="../../terms.html">View the latest version &rarr;</a>',
    ('en', 'privacy'): 'You are viewing version {v} of this policy. <a href="../../privacy.html">View the latest version &rarr;</a>',
    ('sr', 'terms'): 'Pregledate verziju {v} ovih uslova korišćenja. <a href="../../../sr/terms.html">Pogledajte najnoviju verziju &rarr;</a>',
    ('sr', 'privacy'): 'Pregledate verziju {v} ove politike privatnosti. <a href="../../../sr/privacy.html">Pogledajte najnoviju verziju &rarr;</a>',
    ('hr', 'terms'): 'Pregledavate verziju {v} ovih uvjeta korištenja. <a href="../../../hr/terms.html">Pogledajte najnoviju verziju &rarr;</a>',
    ('hr', 'privacy'): 'Pregledavate verziju {v} ove politike privatnosti. <a href="../../../hr/privacy.html">Pogledajte najnoviju verziju &rarr;</a>',
}

def archive(live: str, lang: str, page: str, v: str) -> str:
    lines = live.split('\n')
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        if '.back:hover' in line:
            margin = '24px' if lang == 'en' else '16px'
            out.append(f'        .version-notice {{ background: #fff8e1; border-left: 4px solid #f6b93b; border-radius: 0 8px 8px 0; padding: 10px 16px; font-size: 0.9rem; margin-bottom: {margin}; }}')
            out.append('        .version-notice a { color: #4f7ef7; }')
        elif 'class="back"' in line:
            home = '../../index.html' if lang == 'en' else '../../../index.html'
            before = 'href="index.html"' if lang == 'en' else 'href="../index.html"'
            assert before in line, line
            out[-1] = line.replace(before, f'href="{home}"')
            out.append(f'    <div class="version-notice">{NOTICE[(lang, page)].format(v=v)}</div>')
        elif '<div class="lang-switch">' in line:
            for _ in range(3):
                i += 1
                assert f'{page}.html' in lines[i], lines[i]
                out.append(lines[i].replace(f'{page}.html', 'index.html'))
        i += 1
    return '\n'.join(out)

def main():
    repo, v = pathlib.Path(sys.argv[1]), sys.argv[2]
    check = '--check' in sys.argv
    bad = 0
    for page in ('terms', 'privacy'):
        for lang in ('en', 'sr', 'hr'):
            live = repo / (f'{page}.html' if lang == 'en' else f'{lang}/{page}.html')
            target = repo / page / v / ('index.html' if lang == 'en' else f'{lang}/index.html')
            built = archive(live.read_text(encoding='utf-8'), lang, page, v)
            if check:
                same = target.read_text(encoding='utf-8') == built
                bad += not same
                print(('same ' if same else 'DIFF ') + str(target.relative_to(repo)))
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(built, encoding='utf-8')
                print('wrote', target.relative_to(repo))
    sys.exit(1 if bad else 0)

main()
