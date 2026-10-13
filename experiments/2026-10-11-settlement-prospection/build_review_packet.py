"""Supply authored evidence, rather than redistributing full acquired papers."""
from pathlib import Path
BASE=Path(__file__).resolve().parent

def main():
    dest=BASE/'review/claude-packet-v1.txt'
    if dest.exists():raise FileExistsError(dest)
    prompt='''You are the independent adversarial reviewer requested by the human user. Review this COMPLETE first draft before the author writes the final paper. Requested model is Claude Code Opus-5.5 CLI. This packet contains an authored manuscript, curated source observations with actual access depths, independent source-audit notes, mountain research notes, computational outputs and reusable analysis code. Full acquired third-party papers are not redistributed here. You have no tools: you cannot verify external sources beyond this evidence, and must not claim you did. Assess reasoning critically rather than rubber-stamping the provided summaries.

The user asks why ~100 of1000+Indus sites are excavated, how large unexcavated/hidden sites could be, how much more could be found, and possible new survey regions beneath later cities, alluvium/floods, mountains/caves/landslides and today's ocean. They asked deep up-to-date interdisciplinary research, a paper, adversarial review and no questions. There is no new fieldwork, satellite imagery, bathymetry or fitted discovery model. Candidate rectangles are editorial sampling windows. Do not demand a field discovery as a condition for an honest review/proposal paper, but challenge evidence-based novelty and scientific usefulness.

Maximize reader comprehension: explain ideas directly in connected prose, keep shared assumptions together, avoid repeated corrective comparisons or warnings interrupting the argument. Report: (1) readiness and strongest defensible contribution; (2) numbered findings with severity, exact passage/claim, reason and concrete fix; (3) source/chronology/cultural attribution or numerical errors; (4) prediction/sampling/geographic flaws and omitted decisive rivals; (5) substantive recommendations for a usable pilot, truthful priority and artifact expectations; (6) claims that should be removed; (7) checks performed and checks unavailable. Audit the code and values conceptually; attempt arithmetic independently. Distinguish scientific problems from editorial ones. Include strengths only to bound what survives review. Do not invent additional source facts, site discoveries, probabilities, calibrated counts or dates. Do not suggest authenticated decipherment or an unrequested publication. No questions. Give enough detail for a response-to-reviewers document.
'''
    files=['review/draft-v1.md','sources-v2.json','candidates-v2.json','research/independent-source-audit.md','research/mountain-evidence.md','run-v2/published-count-arithmetic.json','run-v2/historical-map-checks.json','run-v2/metadata-coverage.json','run-v2/synthetic-scenarios.json','run-v2/verification.json','analysis.py','PROTOCOL.md']
    chunks=[prompt]
    for file in files:chunks.extend([f'\n\nBEGIN AUTHORED FILE: {file}\n', (BASE/file).read_text(encoding='utf-8'),f'\nEND AUTHORED FILE: {file}\n'])
    content=''.join(chunks);dest.write_text(content,encoding='utf-8')
    print(f'Review packet {len(content)} characters, {len(content.split())} whitespace words.')

if __name__=='__main__':main()
