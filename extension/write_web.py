"""Assemble paired Markdown in paper-v2; does not publish or rebuild the site."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'results/analysis-v2'


def main():
    results = json.loads((DATA / 'summary.json').read_text())
    assert results['run_count'] == 216 and results['source_hashes_verified']
    decision = results['policy_decision']
    sources = json.loads((ROOT / 'sources.json').read_text()) + json.loads((ROOT / 'extension/sources-v2.json').read_text())
    for lang in ['es','en']:
        es = lang=='es'
        template = (ROOT / 'extension' / f'page.{lang}.template.md').read_text()
        metrics = (f"La nueva tanda contiene **{results['run_count']} ejecuciones, {results['calls']} llamadas y {results['total_tokens']:,} tokens observados**. Se registraron {results['errors']} errores de infraestructura o protocolo. Los costes de desarrollo se muestran aparte." if es else
                   f"The new wave contains **{results['run_count']} runs, {results['calls']} calls and {results['total_tokens']:,} observed tokens**. There were {results['errors']} infrastructure or protocol errors. Development resource use is reported separately.")
        serial, parallel = decision['candidates']
        development = (f"Se probaron dos políticas en diez instancias nuevas, sin mezclar sus datos con la réplica: serial, **{serial['successes']}/10**, {serial['mean_tokens']:,.1f} tokens y {serial['mean_seconds']:.2f} segundos medios; paralela, **{parallel['successes']}/10**, {parallel['mean_tokens']:,.1f} tokens y {parallel['mean_seconds']:.2f} segundos medios. Se eligió la paralela por mayor cumplimiento, según la regla fijada previamente. Desarrollo sumó **{decision['development_runs']} ejecuciones, {decision['development_calls']} llamadas y {decision['development_tokens']:,} tokens**." if es else
                       f"Two policies were tested on ten fresh instances, separate from replication: serial, **{serial['successes']}/10**, averaging {serial['mean_tokens']:,.1f} tokens and {serial['mean_seconds']:.2f} seconds; parallel, **{parallel['successes']}/10**, averaging {parallel['mean_tokens']:,.1f} tokens and {parallel['mean_seconds']:.2f} seconds. Parallel was selected for higher completion under the prior rule. Development totaled **{decision['development_runs']} runs, {decision['development_calls']} calls and {decision['development_tokens']:,} tokens**.")
        names = {'direct':('vía directa','direct path'),'parallel_agreement':('acuerdo paralelo sin integrador','parallel agreement without integrator'),'parallel_adjudication':('arbitraje tras dos propuestas','adjudication after two proposals'),'selective_review':('revisión selectiva','selective review')}
        routes = ', '.join(f"{results['routing_counts'].get('sage:'+k,0)} "+v[0 if es else 1] for k,v in names.items())
        routing = ('Rutas observadas en SAGE: ' if es else 'Observed SAGE routes: ')+routes+'.'
        replacements = {'METRICS':metrics,'DEVELOPMENT':development,'ROUTING':routing,
                        'MAIN_TABLE':(DATA/f'main-table-{lang}.md').read_text().strip(),
                        'ABLATION_TABLE':(DATA/f'ablation-table-{lang}.md').read_text().strip(),
                        'CONCLUSION':(ROOT/'paper-v2'/f'conclusion.{lang}.md').read_text().strip(),
                        'SOURCES':'\n'.join(f"- [{s['title']}]({s['url']}) — {s['version']}; {s['first_submitted']}." for s in sources)}
        for key,value in replacements.items(): template = template.replace('@@'+key+'@@',value)
        assert '@@' not in template
        (ROOT/'paper-v2'/f'page.{lang}.md').write_text(template)
    print('Bilingual v2 paper-page Markdown assembled; site unchanged.')


if __name__=='__main__': main()
