from django.test import TestCase, Client
from django.db.utils import IntegrityError
from django.conf import settings
from django.urls import reverse

from .models import RefData


class RefDataModelTests(TestCase):
    def setUp(self):
        self.dataset1_name = "test_dataset_01"
        self.dataset2_name = "test_dataset_02"
        self.ref_body = {}

    def test_fail_duplicate_ref(self):
        self.ref1 = RefData.objects.create(
            ref_id="ref_01", dataset=self.dataset1_name, body=self.ref_body
        )

        self.assertRaises(
            IntegrityError,
            RefData.objects.create,
            ref_id="ref_01",
            dataset=self.dataset1_name,
            body=self.ref_body,
        )

    def test_same_ref_diff_datasets(self):
        self.ref1 = RefData.objects.create(
            ref_id="ref_01", dataset=self.dataset1_name, body=self.ref_body
        )
        self.ref2 = RefData.objects.create(
            ref_id="ref_01", dataset=self.dataset2_name, body=self.ref_body
        )


class IndexerTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.real_dataset = list(settings.RELATON_DATASETS)[0]

    def test_indexer_list(self):
        url = reverse("api_list_indexers")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            len(response.json()["data"]), len(settings.RELATON_DATASETS)
        )

    def test_run_indexer(self):
        """
        TODO:
            We need to create test dataset at some remote repo
            and make more complicated integration test.
            Or make it with self.real_dataset?
            But it can be unnecessary a waste of resources.
        """

        pass

    def test_stop_indexer(self):
        url = reverse("api_stop_indexer", args=[self.real_dataset])
        response = self.client.get(url)

        # Should get error when we trying to stop not running indexer:
        self.assertEqual(response.status_code, 500)
        self.assertTrue(len(response.json()["error"]) > 0)

    def test_reset_indexer(self):
        url = reverse("api_reset_indexer", args=[self.real_dataset])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()["data"]) > 0)

    def test_indexer_status(self):
        url = reverse("api_indexer_status", args=[self.real_dataset])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()["data"]) > 0)
