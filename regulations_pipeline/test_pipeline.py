import os
import tempfile
import unittest
from datetime import datetime, date, timezone

from dotenv import load_dotenv
load_dotenv()

has_api_key = bool(os.environ.get("REGULATIONS_GOV_API_KEY"))
SKIP_REASON = "REGULATIONS_GOV_API_KEY not set"


class TestCache(unittest.TestCase):
    """Cache tests — no API key needed."""

    def setUp(self):
        from .cache import Cache
        self.cache = Cache(":memory:")

    def test_cache_roundtrip(self):
        doc_id = "TEST-DOC-001"
        data = {"data": {"id": doc_id, "attributes": {"title": "Test Rule"}}}
        self.cache.cache_rule(doc_id, data)
        result = self.cache.get_cached_rule(doc_id)
        self.assertIsNotNone(result)
        self.assertEqual(result["data"]["id"], doc_id)

    def test_cache_miss(self):
        result = self.cache.get_cached_rule("NONEXISTENT")
        self.assertIsNone(result)

    def test_text_cache_roundtrip(self):
        doc_id = "TEST-DOC-002"
        self.cache.cache_texts(doc_id, "full text here", "ria text here")
        full, ria = self.cache.get_cached_texts(doc_id)
        self.assertEqual(full, "full text here")
        self.assertEqual(ria, "ria text here")

    def test_text_cache_with_none(self):
        doc_id = "TEST-DOC-003"
        self.cache.cache_texts(doc_id, "some text", None)
        full, ria = self.cache.get_cached_texts(doc_id)
        self.assertEqual(full, "some text")
        self.assertIsNone(ria)


class TestRIAIdentification(unittest.TestCase):
    """RIA heuristic tests — no API key needed."""

    def test_identifies_ria_by_title(self):
        from .models import RuleAttachment
        from .pdf_parser import identify_ria_attachment

        attachments = [
            RuleAttachment("1", "Supporting Statement", "http://example.com/a.pdf", "pdf"),
            RuleAttachment("2", "Regulatory Impact Analysis", "http://example.com/b.pdf", "pdf"),
            RuleAttachment("3", "Comment Response", "http://example.com/c.pdf", "pdf"),
        ]
        result = identify_ria_attachment(attachments)
        self.assertIsNotNone(result)
        self.assertEqual(result.attachment_id, "2")

    def test_identifies_economic_analysis(self):
        from .models import RuleAttachment
        from .pdf_parser import identify_ria_attachment

        attachments = [
            RuleAttachment("1", "Preliminary Economic Analysis", "http://example.com/a.pdf", "pdf"),
        ]
        result = identify_ria_attachment(attachments)
        self.assertIsNotNone(result)

    def test_returns_none_when_no_ria(self):
        from .models import RuleAttachment
        from .pdf_parser import identify_ria_attachment

        attachments = [
            RuleAttachment("1", "Supporting Document", "http://example.com/a.pdf", "pdf"),
            RuleAttachment("2", "Public Notice", "http://example.com/b.pdf", "pdf"),
        ]
        result = identify_ria_attachment(attachments)
        self.assertIsNone(result)

    def test_skips_non_pdf(self):
        from .models import RuleAttachment
        from .pdf_parser import identify_ria_attachment

        attachments = [
            RuleAttachment("1", "Regulatory Impact Analysis", "http://example.com/a.docx", "docx"),
        ]
        result = identify_ria_attachment(attachments)
        self.assertIsNone(result)


class TestModels(unittest.TestCase):
    """Model tests — no API key needed."""

    def test_days_remaining(self):
        from .models import Rule
        from datetime import timedelta

        future = datetime.now(timezone.utc) + timedelta(days=10)
        rule = Rule(
            document_id="TEST",
            docket_id="TEST-DOCKET",
            title="Test",
            agency="TEST",
            agency_id="TEST",
            comment_deadline=future,
            posted_date=datetime.now(timezone.utc),
        )
        self.assertGreater(rule.days_remaining, 0)
        self.assertLessEqual(rule.days_remaining, 11)

    def test_days_remaining_past(self):
        from .models import Rule
        from datetime import timedelta

        past = datetime.now(timezone.utc) - timedelta(days=5)
        rule = Rule(
            document_id="TEST",
            docket_id="TEST-DOCKET",
            title="Test",
            agency="TEST",
            agency_id="TEST",
            comment_deadline=past,
            posted_date=datetime.now(timezone.utc),
        )
        self.assertEqual(rule.days_remaining, 0)


@unittest.skipUnless(has_api_key, SKIP_REASON)
class TestFetchOpenRules(unittest.TestCase):
    """Tests that hit the Regulations.gov API."""

    def test_fetch_open_comment_periods(self):
        from .regulations_client import RegulationsClient

        client = RegulationsClient()
        results = client.fetch_open_comment_periods(page_size=5)
        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 1, "Expected at least 1 open comment period")

        for doc in results:
            attrs = doc.get("attributes", {})
            self.assertIn("title", attrs)
            self.assertIn("commentEndDate", attrs)

    def test_fetch_rule_detail(self):
        from .regulations_client import RegulationsClient

        client = RegulationsClient()
        # Get a real document ID from open rules
        docs = client.fetch_open_comment_periods(page_size=5)
        self.assertGreaterEqual(len(docs), 1)
        doc_id = docs[0]["id"]

        detail = client.fetch_rule_detail(doc_id)
        self.assertIn("data", detail)
        attrs = detail["data"].get("attributes", {})
        self.assertIn("title", attrs)
        self.assertIn("docketId", attrs)

    def test_not_found(self):
        from .regulations_client import RegulationsClient, NotFoundError

        client = RegulationsClient()
        with self.assertRaises(NotFoundError):
            client.fetch_rule_detail("FAKE-NONEXISTENT-DOC-ID-999")


@unittest.skipUnless(has_api_key, SKIP_REASON)
class TestPipelineIntegration(unittest.TestCase):
    """End-to-end pipeline tests."""

    def setUp(self):
        self.tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp_db.close()

    def tearDown(self):
        os.unlink(self.tmp_db.name)

    def test_get_open_rules(self):
        from .pipeline import Pipeline

        pipeline = Pipeline(db_path=self.tmp_db.name)
        rules = pipeline.get_open_rules()
        self.assertGreaterEqual(len(rules), 1)

        for rule in rules:
            self.assertTrue(rule.document_id)
            self.assertTrue(rule.title)
            self.assertGreater(rule.days_remaining, 0)

        # Should be sorted by days_remaining ascending
        for i in range(len(rules) - 1):
            self.assertLessEqual(rules[i].days_remaining, rules[i + 1].days_remaining)

    def test_enrich_rule(self):
        from .pipeline import Pipeline

        pipeline = Pipeline(db_path=self.tmp_db.name)
        rules = pipeline.get_open_rules()
        self.assertGreaterEqual(len(rules), 1)

        enriched = pipeline.enrich_rule(rules[0])
        # At minimum the rule should still have its core fields
        self.assertTrue(enriched.document_id)
        self.assertTrue(enriched.title)
        # full_text or ria_text may or may not be populated depending on the rule


class TestFederalRegister(unittest.TestCase):
    """Federal Register API tests — no API key needed."""

    def test_fetch_known_document(self):
        from .federal_register_client import FederalRegisterClient

        client = FederalRegisterClient()
        # Use a well-known FR document number
        text = client.fetch_rule_text("2021-00731")
        # This may or may not return text depending on the document
        # Just verify it doesn't crash
        if text:
            self.assertIsInstance(text, str)
            self.assertGreater(len(text), 0)

    def test_not_found_returns_none(self):
        from .federal_register_client import FederalRegisterClient

        client = FederalRegisterClient()
        result = client.fetch_rule_text("FAKE-99999999")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
