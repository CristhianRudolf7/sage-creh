"""Stage audited v2 research assets and paired content; preserve all v1 assets.

Does not restart services, commit, push, or modify infrastructure.
"""
import argparse
import hashlib
import json
import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from analyze import audit

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'subagentes-arquitecturas-tokens-tiempo-2026'


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-root',type=Path,required=True)
    args = parser.parse_args()
    site = args.site_root.resolve()
    assert (site/'src/content/papers'/f'{SLUG}.md').is_file()
    rows, manifest, _, traces = audit(ROOT/'results/evaluation-v2')
    assert len(rows)==216
    summary = json.loads((ROOT/'results/analysis-v2/summary.json').read_text())
    assert summary['calls']==sum(r['calls'] for r in rows)
    assert summary['total_tokens']==sum(r['usage']['total_tokens'] for r in rows)
    pdf_audit = json.loads((ROOT/'qa-v2/pdf-audit.json').read_text())
    assert len(pdf_audit)==2 and all(r['footers_all_pages'] and r['page_bounds'] for r in pdf_audit)
    visual = json.loads((ROOT/'qa-v2/visual-review.json').read_text())
    assert visual['all_pages_reviewed'] is True
    for lang in ['es','en']:
        pdf = ROOT/'paper-v2'/lang/'build/article.pdf'
        assert pdf.read_bytes().startswith(b'%PDF-')
        assert visual['pdf_sha256'][lang]==digest(pdf)
        page = (ROOT/'paper-v2'/f'page.{lang}.md').read_text()
        assert '@@' not in page and 'version: "2.0"' in page
        assert f'{SLUG}-v2-{lang}.pdf' in page
    permitted_suffixes = {'.py','.md','.json','.jsonl','.tex','.sty','.svg','.pdf','.png','.csv','.xlsx','.txt'}
    scopes = {'benchmark','analysis','extension','paper','paper-v2','results'}
    root_names = {'README.md','README.es.md','requirements.txt','protocol.en.md','protocol.es.md','sources.json','editorial-amendments.json'}
    files = []
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file(): continue
        rel = path.relative_to(ROOT)
        if rel.parts[0] not in scopes and str(rel) not in root_names: continue
        if '__pycache__' in rel.parts or path.suffix not in permitted_suffixes: continue
        if 'build' in rel.parts and path.name!='article.pdf': continue
        assert not path.is_symlink(), 'Unexpected symlink in public package'
        payload = path.read_bytes()
        if path.suffix not in {'.pdf','.png','.xlsx'}:
            assert not re.search(rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{24,}',payload), 'Credential-shaped value in release'
            assert not re.search(rb'\bcfk_[A-Za-z0-9_-]{24,}',payload), 'Credential-shaped value in release'
        files.append(path)
    output = ROOT.parents[1]/'output'/'subagent-v2-release'
    output.mkdir(parents=True,exist_ok=True)
    checks = ''.join(f'{digest(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in files)
    (output/'ARTIFACTS-v2.sha256').write_text(checks)
    archive = output/'source-and-data.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for path in files: z.write(path,'subagent-orchestration-study-v2/'+path.relative_to(ROOT).as_posix())
        z.write(output/'ARTIFACTS-v2.sha256','subagent-orchestration-study-v2/ARTIFACTS-v2.sha256')
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len([n for n in z.namelist() if '/results/evaluation-v2/traces/' in n])==summary['calls']
        assert len([n for n in z.namelist() if '/results/evaluation/traces/' in n])==416
        for line in checks.splitlines():
            expected,name = line.split('  ',1)
            assert hashlib.sha256(z.read('subagent-orchestration-study-v2/'+name)).hexdigest()==expected
    # Keep a recoverable copy of the two current content files before replacement.
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = output/('content-before-'+stamp)
    backup.mkdir()
    for lang in ['es','en']:
        folder = 'src/content/papers' if lang=='es' else 'src/content/translations/papers'
        shutil.copy2(site/folder/f'{SLUG}.md',backup/f'page.{lang}.md')
    public = site/'public/investigacion'
    data = public/'datos'/f'{SLUG}-v2'
    data.mkdir(parents=True,exist_ok=True)
    documents = public/'documentos'
    for lang in ['es','en']:
        shutil.copy2(ROOT/'paper-v2'/lang/'build/article.pdf',documents/f'{SLUG}-v2-{lang}.pdf')
    for path in (ROOT/'results/analysis-v2').iterdir():
        if path.suffix in {'.csv','.json','.xlsx','.png','.pdf','.svg'}:
            shutil.copy2(path,data/path.name)
    shutil.copy2(archive,data/'source-and-data.zip')
    entries = [(p,p.name) for p in sorted(data.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt']
    entries.extend((documents/f'{SLUG}-v2-{lang}.pdf',f'../../documentos/{SLUG}-v2-{lang}.pdf') for lang in ['es','en'])
    (data/'SHA256SUMS.txt').write_text(''.join(f'{digest(p)}  {name}\n' for p,name in entries))
    for lang in ['es','en']:
        folder = 'src/content/papers' if lang=='es' else 'src/content/translations/papers'
        shutil.copy2(ROOT/'paper-v2'/f'page.{lang}.md',site/folder/f'{SLUG}.md')
    report = dict(staged_at=datetime.now(timezone.utc).isoformat(),package_files=len(files)+1,
                  evaluation_runs=len(rows),evaluation_calls=summary['calls'],archive_bytes=archive.stat().st_size,
                  archive_sha256=digest(archive),content_backup=str(backup),v1_public_assets_unchanged=True,
                  deployed=False,note='Run site validation, build and external URL checks before declaring publication complete.')
    (output/'stage-report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))


if __name__=='__main__': main()
