import pytest
from devlens.ingestion.cost import compute_cost, _match_model


class TestModelMatching:
    def test_exact_key_match(self):
        assert _match_model("claude-sonnet-4-6") == "claude-sonnet-4-6"

    def test_versioned_model_id(self):
        # Versioned IDs like 'claude-sonnet-4-6-20250625' should match
        assert _match_model("claude-sonnet-4-6-20250625") == "claude-sonnet-4-6"

    def test_haiku_versioned(self):
        assert _match_model("claude-haiku-4-5-20251001") == "claude-haiku-4-5"

    def test_opus_versioned(self):
        assert _match_model("claude-opus-4-20250514") == "claude-opus-4"

    def test_longer_key_wins_over_shorter(self):
        # 'claude-opus-4-5' is longer than 'claude-opus-4', should match first
        result = _match_model("claude-opus-4-5-20250914")
        assert result == "claude-opus-4-5"

    def test_unknown_model_returns_none(self):
        assert _match_model("gpt-4o") is None
        assert _match_model("gemini-pro") is None

    def test_empty_string_returns_none(self):
        assert _match_model("") is None

    def test_case_insensitive(self):
        assert _match_model("Claude-Sonnet-4-6") == "claude-sonnet-4-6"


class TestComputeCost:
    def test_zero_tokens_returns_zero(self):
        assert compute_cost("claude-sonnet-4-6", 0, 0) == 0.0

    def test_input_token_cost(self):
        # claude-sonnet-4-6: $3.00 / 1M input
        cost = compute_cost("claude-sonnet-4-6", 1_000_000, 0)
        assert abs(cost - 3.0) < 1e-9

    def test_output_token_cost(self):
        # claude-sonnet-4-6: $15.00 / 1M output
        cost = compute_cost("claude-sonnet-4-6", 0, 1_000_000)
        assert abs(cost - 15.0) < 1e-9

    def test_combined_cost(self):
        # 500K input ($1.50) + 100K output ($1.50)
        cost = compute_cost("claude-sonnet-4-6", 500_000, 100_000)
        assert abs(cost - 3.0) < 1e-6

    def test_cache_creation_cost(self):
        # cache creation = input_price * 1.25
        # claude-sonnet-4-6 input=$3.0, so cache_creation = $3.75/1M
        cost = compute_cost("claude-sonnet-4-6", 0, 0, cache_creation_tokens=1_000_000)
        assert abs(cost - 3.75) < 1e-9

    def test_cache_read_cost(self):
        # cache read = input_price * 0.10
        # claude-sonnet-4-6 input=$3.0, so cache_read = $0.30/1M
        cost = compute_cost("claude-sonnet-4-6", 0, 0, cache_read_tokens=1_000_000)
        assert abs(cost - 0.30) < 1e-9

    def test_opus_higher_cost(self):
        # claude-opus-4: $15.0 input, $75.0 output
        cost_opus = compute_cost("claude-opus-4-20250514", 1_000_000, 0)
        cost_sonnet = compute_cost("claude-sonnet-4-6", 1_000_000, 0)
        assert cost_opus > cost_sonnet

    def test_unknown_model_returns_zero(self):
        assert compute_cost("unknown-model-xyz", 1_000_000, 1_000_000) == 0.0

    def test_real_session_sample(self):
        # From fixture: 9000 input, 400 output, 800 cache_create, 5300 cache_read
        # claude-sonnet-4-6: input=$3/1M, output=$15/1M, cache_create=$3.75/1M, cache_read=$0.30/1M
        cost = compute_cost(
            "claude-sonnet-4-6-20250625",
            input_tokens=9000,
            output_tokens=400,
            cache_creation_tokens=800,
            cache_read_tokens=5300,
        )
        expected = (
            9000 / 1e6 * 3.0
            + 400 / 1e6 * 15.0
            + 800 / 1e6 * 3.0 * 1.25
            + 5300 / 1e6 * 3.0 * 0.10
        )
        assert abs(cost - expected) < 1e-9
