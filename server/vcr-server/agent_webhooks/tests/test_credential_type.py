from django.test import TestCase
from unittest.mock import patch

from api.v2.models.Issuer import Issuer
from api.v2.models.Schema import Schema

from agent_webhooks.tests.data import credential_type_def_spec
from agent_webhooks.utils import credential_type


class TestCredentialType(TestCase):
    @patch("api.v2.models.CredentialType.save", autospec=True)
    def test_credential_type_registration(self, mock_credential_type_save):

        test_issuer_data = {
            "name": "issuer name",
            "did": credential_type_def_spec.get("origin_did"),
            "abbreviation": "issuer abbrev",
            "email": "issuer email",
            "url": "issuer url",
            "endpoint": "issuer endpoint",
            "logo_b64": "issuer logo base64",
        }
        test_schema_data = {
            "name": credential_type_def_spec.get("schema"),
            "version": credential_type_def_spec.get("version"),
            "origin_did": credential_type_def_spec.get("origin_did"),
        }
        test_data = [credential_type_def_spec]

        mgr = credential_type.CredentialTypeManager()
        test_issuer = Issuer(**test_issuer_data)
        test_issuer.save()
        test_schema = Schema(**test_schema_data)
        test_schema.save()
        test_schemas = Schema.objects.all()
        result = mgr.update_credential_types(test_issuer, test_schemas, test_data)

        mock_credential_type_save.assert_called()
        assert len(result) == 1

        saved_credential_type = result[0]
        saved_schema = test_schemas[0]

        assert saved_credential_type.processor_config == {
            "cardinality_fields": credential_type_def_spec.get("cardinality_fields"),
            "credential": credential_type_def_spec.get("credential"),
            "mappings": credential_type_def_spec.get("mappings"),
            "topic": credential_type_def_spec.get("topic"),
        }
        assert saved_credential_type.issuer_id == test_issuer.id
        assert saved_credential_type.schema_id == saved_schema.id
