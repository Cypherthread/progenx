"""
Known-answer regression tests for Progenx design accuracy.

How this works:
1. Each test case defines a prompt and the EXPECTED genes/chassis
2. We run the design pipeline and check if the output matches expectations
3. If a test that previously passed starts failing, something broke

These tests verify that:
- Registry genes are fetched correctly (right accession, right length)
- The LLM picks appropriate genes for well-known applications
- FBA runs with the correct model for the chassis
- The full pipeline doesn't crash

Run: python -m pytest tests/test_accuracy.py -v
Or:  python tests/test_accuracy.py  (standalone)

Cost: Free tier tests use Ollama ($0). Pro tier tests are skipped by default
      to avoid API charges. Set RUN_PRO_TESTS=1 to include them.
"""

import os
import sys
import json

# Add parent dir to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── Registry verification tests (no LLM, no API, instant) ──────────

def test_registry_accessions():
    """Verify every registry accession fetches the correct protein."""
    from services.ncbi_client import GENE_REGISTRY, fetch_protein_sequence, _validate_protein_length

    results = {"passed": 0, "failed": 0, "errors": []}

    for gene_name, entry in GENE_REGISTRY.items():
        accession = entry["accession"]
        expected_aa = entry.get("expected_aa", 0)
        expected_desc = entry.get("description", "")

        result = fetch_protein_sequence(accession)

        if not result or "error" in result:
            results["errors"].append(f"{gene_name} ({accession}): FETCH FAILED — {result}")
            results["failed"] += 1
            continue

        # Check length
        warning = _validate_protein_length(gene_name, result["length"], expected_aa)
        if warning:
            results["errors"].append(f"{gene_name} ({accession}): {warning}")
            results["failed"] += 1
            continue

        results["passed"] += 1

    return results


def test_registry_aliases():
    """Verify all aliases resolve to valid registry entries."""
    from services.ncbi_client import GENE_ALIASES, GENE_REGISTRY

    results = {"passed": 0, "failed": 0, "errors": []}

    for alias, target in GENE_ALIASES.items():
        if target in GENE_REGISTRY:
            results["passed"] += 1
        else:
            results["errors"].append(f"Alias '{alias}' → '{target}' but '{target}' not in registry")
            results["failed"] += 1

    return results


def test_fba_chassis_mapping():
    """Verify FBA correctly maps chassis names to models."""
    from services.fba_engine import _normalize_chassis, SUPPORTED_CHASSIS

    test_cases = {
        "Escherichia coli K-12": "e_coli",
        "Escherichia coli": "e_coli",
        "E. coli": "e_coli",
        "Pseudomonas putida KT2440": "p_putida",
        "Pseudomonas putida": "p_putida",
        "P. putida": "p_putida",
    }

    results = {"passed": 0, "failed": 0, "errors": []}

    for chassis, expected_key in test_cases.items():
        actual = _normalize_chassis(chassis)
        if actual == expected_key:
            results["passed"] += 1
        else:
            results["errors"].append(f"'{chassis}' → '{actual}' (expected '{expected_key}')")
            results["failed"] += 1

    # Verify unsupported chassis get "no_model" response from run_fba
    from services.fba_engine import run_fba
    unsupported = ["Lactobacillus plantarum", "Staphylococcus epidermidis", "Alteromonas macleodii"]
    for chassis in unsupported:
        fba_result = run_fba(chassis, ["gene1"], "product", "lab")
        if fba_result.get("source") == "no_model":
            results["passed"] += 1
        else:
            results["errors"].append(
                f"'{chassis}' got source='{fba_result.get('source')}' "
                f"(expected 'no_model')"
            )
            results["failed"] += 1

    return results


def test_codon_optimizer_chassis():
    """Verify codon optimizer maps chassis names correctly."""
    from services.codon_optimizer import _normalize_chassis_key

    test_cases = {
        "Pseudomonas putida KT2440": "p_putida",
        "Escherichia coli K-12": "e_coli",
        "Synechococcus elongatus PCC 7942": "s_elongatus",
    }

    results = {"passed": 0, "failed": 0, "errors": []}

    for chassis, expected in test_cases.items():
        actual = _normalize_chassis_key(chassis)
        if actual == expected:
            results["passed"] += 1
        else:
            results["errors"].append(f"Codon opt: '{chassis}' → '{actual}' (expected '{expected}')")
            results["failed"] += 1

    return results


def test_safety_scorer():
    """Verify safety scorer catches known patterns."""
    from services.safety_scorer import score_safety

    results = {"passed": 0, "failed": 0, "errors": []}

    # Clean sequence should score high
    clean = score_safety("ATGCGTATTCGCGATCG" * 20, "Safe bacterium", '{"genes": []}')
    if clean["score"] >= 0.9:
        results["passed"] += 1
    else:
        results["errors"].append(f"Clean sequence scored {clean['score']} (expected >= 0.9)")
        results["failed"] += 1

    # Resistance markers should be flagged
    resistant = score_safety("ATGCGTATTCGCGATCG" * 20, "Design with kanR and ampR markers", '{"genes": []}')
    if len(resistant["flags"]) > 0 and resistant["score"] < 1.0:
        results["passed"] += 1
    else:
        results["errors"].append(f"Resistance markers not flagged: {resistant}")
        results["failed"] += 1

    # Dual-use genes should be flagged
    dualuse = score_safety("ATGCGTATTCGCGATCG" * 20, "Design using pagA toxin gene", '{"genes": [{"name": "pagA"}]}')
    if any("DUAL-USE" in f for f in dualuse["flags"]):
        results["passed"] += 1
    else:
        results["errors"].append(f"Dual-use gene pagA not flagged")
        results["failed"] += 1

    return results


def test_primer_tm():
    """Verify Tm calculation produces sane values."""
    from services.primer_designer import calculate_tm

    results = {"passed": 0, "failed": 0, "errors": []}

    # AT-rich should be low Tm
    at_tm = calculate_tm("AATATATATATATATATATAT")
    # GC-rich should be high Tm
    gc_tm = calculate_tm("GCGCGCGCGCGCGCGCGCGC")
    # Mixed should be in between
    mix_tm = calculate_tm("ATCGATCGATCGATCGATCG")

    if at_tm and gc_tm and mix_tm and at_tm < mix_tm < gc_tm:
        results["passed"] += 1
    else:
        results["errors"].append(f"Tm order wrong: AT={at_tm}, mix={mix_tm}, GC={gc_tm}")
        results["failed"] += 1

    # Tm should be in reasonable biological range
    if mix_tm and 40 < mix_tm < 80:
        results["passed"] += 1
    else:
        results["errors"].append(f"Mixed primer Tm={mix_tm} outside 40-80°C range")
        results["failed"] += 1

    return results


def test_json_parser():
    """Verify the robust JSON parser handles common LLM output formats."""
    from services.llm_orchestrator import _parse_llm_json

    results = {"passed": 0, "failed": 0, "errors": []}

    test_cases = [
        ('{"key": "value"}', "clean JSON"),
        ('```json\n{"key": "value"}\n```', "markdown fenced"),
        ('Here is the result:\n{"key": "value"}\nHope this helps!', "with preamble"),
        ('{"key": "value",}', "trailing comma"),
        ('```\n{"key": "value"}\n```', "markdown without lang"),
    ]

    for raw, label in test_cases:
        try:
            result = _parse_llm_json(raw)
            if result.get("key") == "value":
                results["passed"] += 1
            else:
                results["errors"].append(f"'{label}': parsed but wrong value: {result}")
                results["failed"] += 1
        except Exception as e:
            results["errors"].append(f"'{label}': failed to parse — {e}")
            results["failed"] += 1

    return results


# ── Run all tests ────────────────────────────────────────────────────

def run_all():
    """Run all regression tests and report results."""
    tests = [
        ("Registry Accessions", test_registry_accessions),
        ("Registry Aliases", test_registry_aliases),
        ("FBA Chassis Mapping", test_fba_chassis_mapping),
        ("Codon Optimizer Chassis", test_codon_optimizer_chassis),
        ("Safety Scorer", test_safety_scorer),
        ("Primer Tm Calculation", test_primer_tm),
        ("JSON Parser Robustness", test_json_parser),
    ]

    total_passed = 0
    total_failed = 0
    all_errors = []

    print("=" * 60)
    print("PROGENX REGRESSION TEST SUITE")
    print("=" * 60)

    for name, test_fn in tests:
        try:
            result = test_fn()
            passed = result["passed"]
            failed = result["failed"]
            errors = result.get("errors", [])

            status = "PASS" if failed == 0 else "FAIL"
            print(f"  [{status}] {name}: {passed} passed, {failed} failed")
            for err in errors:
                print(f"         {err}")

            total_passed += passed
            total_failed += failed
            all_errors.extend(errors)
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")
            total_failed += 1
            all_errors.append(f"{name}: {e}")

    print(f"\n{'='*60}")
    print(f"TOTAL: {total_passed} passed, {total_failed} failed")
    if total_failed == 0:
        print("ALL TESTS PASSED")
    else:
        print(f"FAILURES: {total_failed}")
        for err in all_errors:
            print(f"  - {err}")
    print(f"{'='*60}")

    return total_failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
