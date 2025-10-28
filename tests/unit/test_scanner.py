"""
Tests unitaires pour le module scanner
"""

from dna_sec.scanner import _mock_scan


def test_mock_scan_clean_sequence():
    """Test scanner basique avec séquence propre"""
    sequence = "ATCGATCGATCGATCG"
    result = _mock_scan(sequence)

    assert "risk_score" in result
    assert "findings" in result
    assert result["scanner_mode"] == "basic (no YARA)"
    assert result["risk_score"] >= 0


def test_mock_scan_suspicious_pattern():
    """Test détection de patterns suspects"""
    sequence = "ATGATGATGATGATCG"
    result = _mock_scan(sequence)

    assert result["risk_score"] > 0
    assert len(result["findings"]) > 0


def test_mock_scan_gc_anomaly():
    """Test détection d'anomalie GC"""
    sequence = "GGGGGGGGGGGGGGGG"  # 100% GC
    result = _mock_scan(sequence)

    assert result["risk_score"] > 0
    assert any("gc_anomaly" in f.get("rule", "") for f in result["findings"])


def test_scan_empty_sequence():
    """Test avec séquence vide"""
    result = _mock_scan("")

    assert result["risk_score"] == 0
    assert "recommendation" in result


def test_scan_normal_gc_content():
    """Test avec contenu GC normal"""
    sequence = "ATCGATCGATCGATCG"  # 50% GC
    result = _mock_scan(sequence)

    # Ne devrait pas déclencher d'anomalie GC
    gc_findings = [f for f in result["findings"] if "gc_anomaly" in f.get("rule", "")]
    assert len(gc_findings) == 0
