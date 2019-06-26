"""Issuer registration admin routes."""

from aiohttp import web
from aiohttp_apispec import docs, request_schema

from marshmallow import fields, Schema

from aries_cloudagent.messaging.connections.models.connection_record import (
    ConnectionRecord,
)
from aries_cloudagent.storage.error import StorageNotFoundError

from .manager import IssuerRegistrationManager

import logging

LOGGER = logging.getLogger(__name__)


# class IssuerRegistrationRequestSchema(Schema):
#     """Request schema for issuer registration."""

#     class IssuerRegistrationNestedSchema(Schema):
#         """Issuer registration nested schema."""

#         class IssuerSchema(Schema):
#             """Isuer nested schema."""

#             did = fields.Str(required=True)
#             name = fields.Str(required=True)
#             abbreviation = fields.Str(required=False)
#             email = fields.Str(required=False)
#             url = fields.Str(required=False)
#             endpoint = fields.Str(required=False)
#             logo_b64 = fields.Str(required=False)

#         class CredentialType(Schema):
#             """Isuer credential type schema."""

#             name = fields.Str(required=True)
#             schema = fields.Str(required=True)
#             version = fields.Str(required=True)
#             description = fields.Str(required=False)
#             cardinality_fields = fields.List(fields.Dict, required=False)
#             credential = fields.Str(required=False)
#             mapping = fields.Dict(required=False)
#             topic = fields.Str(required=False)
#             caregory_labels = fields.List(fields.Str, required=False)
#             claim_descriptions = fields.List(fields.Str, required=False)
#             claim_labels = fields.List(fields.Str, required=False)
#             logo_b64 = fields.Str(required=False)
#             credential_def_id = fields.Str(required=True)
#             endpoint = fields.Str(required=False)
#             visible_fields = fields.List(fields.Str, required=False)

#         issuer = fields.Nested(IssuerSchema, required=True)
#         credential_types = fields.List(fields.Nested(CredentialType), required=False)

#     issuer_registration = fields.Nested(IssuerRegistrationNestedSchema, required=True)
#     connection_id = fields.Str(required=True)


class CredentialMapping(Schema):
    """Nested mapping."""

    _from = fields.String(data_key="from", required=True)
    _input = fields.String(data_key="input", required=True)


# TODO: Create method in AgentSchema to extract this raw schema instead of duplicating
class IssuerRegistrationRequestSchema(Schema):
    """Issuer registration schema class."""

    class IssuerRegistrationNestedSchema(Schema):
        """Issuer registration nested schema."""

        class IssuerSchema(Schema):
            """Issuer schema."""

            did = fields.Str(required=True)
            name = fields.Str(required=True)
            abbreviation = fields.Str(required=False)
            email = fields.Str(required=False)
            url = fields.Str(required=False)
            endpoint = fields.Str(required=False)
            logo_b64 = fields.Str(required=False)

        class CredentialType(Schema):
            """Isuer credential type schema."""

            class Credential(Schema):
                """Nested credential schema."""

                effective_date = fields.Nested(CredentialMapping(), required=True)

            class MappingEntry(Schema):
                """Nested mapping entry schema."""

                class Fields(Schema):
                    """Nested fields schema."""

                    _format = fields.Nested(
                        CredentialMapping, data_key="format", required=False
                    )
                    _type = fields.Nested(
                        CredentialMapping, data_key="type", required=False
                    )
                    value = fields.Nested(CredentialMapping(), required=False)

                _fields = fields.Nested(Fields(), data_key="fields", required=True)
                model = fields.Str(required=True)

            class Topic(Schema):
                """Nested topic schema."""

                source_id = fields.Nested(CredentialMapping(), required=False)
                _type = fields.Nested(
                    CredentialMapping(), data_key="type", required=False
                )
                name = fields.Nested(CredentialMapping, required=False)
                related_source_id = fields.Nested(CredentialMapping(), required=False)
                related_type = fields.Nested(CredentialMapping(), required=False)
                related_name = fields.Nested(CredentialMapping(), required=False)

            cardinality_fields = fields.Dict(required=False)
            caregory_labels = fields.Dict(required=False)
            claim_descriptions = fields.Dict(required=False)
            claim_labels = fields.Dict(required=False)

            credential = fields.Nested(Credential(), required=False)

            name = fields.Str(required=True)
            schema = fields.Str(required=True)
            version = fields.Str(required=True)
            description = fields.Str(required=False)

            mapping = fields.List(fields.Nested(MappingEntry()), required=False)
            topic = fields.List(fields.Nested(Topic()), required=True)

            logo_b64 = fields.Str(required=False)
            credential_def_id = fields.Str(required=True)
            endpoint = fields.Str(required=False)
            visible_fields = fields.List(fields.Str, required=False)

        issuer = fields.Nested(IssuerSchema(), required=True)
        credential_types = fields.List(fields.Nested(CredentialType()), required=False)

    issuer_registration = fields.Nested(IssuerRegistrationNestedSchema(), required=True)
    connection_id = fields.Str(required=True)


@docs(tags=["issuer_registration"], summary="Send an issuer registration to a target")
@request_schema(IssuerRegistrationRequestSchema())
async def issuer_registration_send(request: web.BaseRequest):
    """
    Request handler for sending an issuer registration message to a connection.

    Args:
        request: aiohttp request object

    """
    context = request.app["request_context"]
    outbound_handler = request.app["outbound_message_router"]
    body = await request.json()

    connection_id = body.get("connection_id")
    issuer_registration = body.get("issuer_registration")

    import json

    LOGGER.info(json.dumps(issuer_registration))

    issuer_registration_manager = IssuerRegistrationManager(context)

    try:
        connection = await ConnectionRecord.retrieve_by_id(context, connection_id)
    except StorageNotFoundError:
        return web.BaseRequest("Connection not found.")

    if connection.is_active:
        (
            issuer_registration_state,
            issuer_registration_message,
        ) = await issuer_registration_manager.prepare_send(
            connection_id, issuer_registration
        )

        await outbound_handler(issuer_registration_message, connection_id=connection_id)

        await connection.log_activity(
            context, "issuer_registration", connection.DIRECTION_SENT
        )

    return web.json_response(issuer_registration_state.serialize())


async def register(app: web.Application):
    """Register routes."""
    app.add_routes([web.post("/issuer_registration/send", issuer_registration_send)])
