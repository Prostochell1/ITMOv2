import unittest
import service


class SubscribersFeatureATest(unittest.TestCase):
    def setUp(self):
        # reset state before each test
        service.subscribers.clear()

    def test_list_empty_initially(self):
        # list_subscribers should return an empty list when there are no subscribers
        self.assertEqual(service.list_subscribers(), [])

    def test_list_contains_unique_names(self):
        # After subscribing unique names, list_subscribers returns those names (order not specified)
        service.subscribe("Ann")
        service.subscribe("Bob")
        self.assertEqual(set(service.list_subscribers()), {"Ann", "Bob"})

    def test_duplicate_does_not_increase_list(self):
        # Duplicated subscription should not create duplicate entries in the list
        service.subscribe("Ann")
        service.subscribe("Ann")
        self.assertEqual(service.count(), 1)
        self.assertEqual(service.list_subscribers(), ["Ann"])  # one entry only

    def test_count_matches_list_length(self):
        # count() should reflect the number of unique subscribers
        service.subscribe("Ann")
        service.subscribe("Bob")
        service.subscribe("Ann")  # duplicate
        self.assertEqual(service.count(), 2)
        self.assertEqual(service.count(), len(service.list_subscribers()))


if __name__ == "__main__":
    unittest.main()
