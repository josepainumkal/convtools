"""
Module for testing web app functionality.
"""
import unittest

from ..app import make_model_run_panels
from adaptors.watershed import QueryResult


class TestApp(unittest.TestCase):
    """
    Tests for our 'human adaptor', the web app. Check things like if HTML has
    been built as expected.
    """
    def setUp(self):
        pass

    def test_make_model_boxes(self):
        """
        Check that our search browsing page correctly builds test examples
        """
        generated_panels = \
            open('test/data/expected_modelrun_boxes.html',
                 'r').read()

        search_results = QueryResult({"total": 10,
                                      "subtotal": 4,
                                      "results": [{"yo": "mama"}]})

        expected_panels = make_model_run_panels(search_results)

        assert generated_panels == expected_panels
