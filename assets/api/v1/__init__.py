from flask import Blueprint
from flask_restplus import Api

from api.api_utils import BackendException
from api.v1.model.common import search_filter
from api.v1.model.item.common import default_feed, default_asset, default_attribute, feed_group
from api.v1.namespaces.athena import create_athena_info_namespace
from api.v1.namespaces.auth import create_auth_namespace
from api.v1.namespaces.events import create_events_namespace
from api.v1.namespaces.feeds import create_feeds_namespace
from api.v1.namespaces.scheduler import create_scheduler_namespace
from api.v1.namespaces.settings import create_settings_namespace
from api.v1.namespaces.structure import create_structure_namespace
from api.v1.namespaces.users import create_users_namespace


def _add_api_models(api, models_iterable):
    for model in models_iterable:
        api.models[model.name] = model


def register_athena_api(api):
    from api.v1.model.athena import athena_response

    _add_api_models(api, [athena_response])

    api.add_namespace(
        create_athena_info_namespace(
            api,
            athena_response=athena_response
        )
    )


def register_event_api(api, event):
    from api.v1.model.events import (
        list_events_request,
        gen_list_events_response,
        get_event_feed_groups_request,
        get_event_feed_groups_response,
    )

    from api.v1.model.item.common import default_event

    list_events_response = gen_list_events_response(event)

    _add_api_models(api, [list_events_request, get_event_feed_groups_request, get_event_feed_groups_response,
                          list_events_response, event, default_event])

    api.add_namespace(
        create_events_namespace(
            api,
            list_events_request=list_events_request,
            list_events_response=list_events_response,
            get_event_feed_groups_request=get_event_feed_groups_request,
            get_event_feed_groups_response=get_event_feed_groups_response
        )
    )


def register_feed_api(api, feed, subscription_status):
    from api.v1.model.feeds import (
        gen_search_feeds_request,
        gen_search_feeds_response,
        backfill_request,
        interpolate_request,
        subscribe_request,
        unsubscribe_request,
        reset_data_request,
    )

    search_feeds_request = gen_search_feeds_request(feed)
    search_feeds_response = gen_search_feeds_response(feed)

    _add_api_models(api, [search_feeds_request, search_feeds_response, backfill_request, interpolate_request,
                          subscribe_request, unsubscribe_request, reset_data_request, feed, subscription_status])

    api.add_namespace(
        create_feeds_namespace(
            api,
            search_feeds_request=search_feeds_request,
            search_feeds_response=search_feeds_response,
            backfill_request=backfill_request,
            interpolate_request=interpolate_request,
            subscribe_request=subscribe_request,
            unsubscribe_request=unsubscribe_request,
            reset_data_request=reset_data_request
        )
    )


def register_scheduler_api(api):
    from api.v1.model.scheduler import (
        schedule_request,
        rules_response,
        rule
    )

    _add_api_models(api, [schedule_request, rules_response, rule])

    api.add_namespace(
        create_scheduler_namespace(
            api,
            schedule_request=schedule_request,
            rules_response=rules_response,
            rule=rule
        )
    )


def register_setting_api(api):
    from api.v1.model.settings import settings_model

    _add_api_models(api, [settings_model])

    api.add_namespace(
        create_settings_namespace(
            api,
            settings_model=settings_model,
        )
    )


def register_auth_api(api):
    from api.v1.model.auth import credentials

    _add_api_models(api, [credentials])

    api.add_namespace(
        create_auth_namespace(
            api,
            credentials=credentials
        )
    )


def register_users_api(api):
    from api.v1.model.user import user_model

    _add_api_models(api, [user_model])

    api.add_namespace(
        create_users_namespace(
            api,
            user_model=user_model
        )
    )


def register_structure_api(api, asset, attribute):
    from api.v1.model.structure import (
        search_assets_request,
        gen_search_assets_response,
        asset_children_request,
        asset_children_response,
        asset_attributes_request,
        gen_asset_attributes_response,
        asset_child
    )

    search_assets_response = gen_search_assets_response(asset)
    asset_attributes_response = gen_asset_attributes_response(attribute)

    _add_api_models(api,
                    [search_assets_request, search_assets_response, asset_children_request, asset_children_response,
                     asset_attributes_request, asset_attributes_response, asset, attribute, asset_child])

    api.add_namespace(
        create_structure_namespace(
            api,
            search_assets_request=search_assets_request,
            search_assets_response=search_assets_response,
            asset_children_request=asset_children_request,
            asset_children_response=asset_children_response,
            asset_attributes_request=asset_attributes_request,
            asset_attributes_response=asset_attributes_response,
        )
    )


def register_common_models(api):
    _add_api_models(api, [default_feed, search_filter, default_asset, default_attribute, feed_group])


def create_app_blueprint_v1(connector_type):
    blueprint = Blueprint('v1', __name__, url_prefix='/api/v1')
    authorizations = {
        "access_token": {
            "type": "apiKey",
            "in": "header",
            "name": "access_token"
        },
        "refresh_token": {
            "type": "apiKey",
            "in": "header",
            "name": "refresh_token"
        },
        "id_token": {
            "type": "apiKey",
            "in": "header",
            "name": "id_token"
        },
        "username": {
            "type": "apiKey",
            "in": "header",
            "name": "username"
        }
    }
    api = Api(
        blueprint,
        title='Industrial Data Connector API',
        version='0.1.0',
        description='API providing access to other elements of industrial data connector.\n\n'
                    'Requests are authorized via tokens in request headers. \n'
                    'Obtain the tokens by calling /auth/login with proper username and password. '
                    'Add following headers to all requests:\n'
                    '- access_token\n'
                    '- refersh_token\n'
                    '- id_token\n'
                    '- username',
        authorizations=authorizations,
        security=['access_token', 'refresh_token', 'id_token', 'username']
    )

    if connector_type == 'PI':
        from api.v1.model.item.pi_system import asset
        from api.v1.model.item.pi_system import attribute
        from api.v1.model.item.pi_system import event
        from api.v1.model.item.pi_system import feed
        from api.v1.model.item.pi_system import subscription_status
    elif connector_type == 'WONDERWARE':
        from api.v1.model.item.wonderware import asset
        from api.v1.model.item.wonderware import attribute
        from api.v1.model.item.wonderware import event
        from api.v1.model.item.wonderware import feed
        from api.v1.model.item.wonderware import subscription_status
    elif connector_type == 'KEPWARE':
        from api.v1.model.item.kepware import asset
        from api.v1.model.item.kepware import attribute
        from api.v1.model.item.kepware import event
        from api.v1.model.item.kepware import feed
        from api.v1.model.item.kepware import subscription_status
    else:
        raise NotImplementedError

    register_common_models(api)
    register_athena_api(api)
    register_event_api(api, event)
    register_feed_api(api, feed, subscription_status)
    register_scheduler_api(api)
    register_setting_api(api)
    register_auth_api(api)
    register_users_api(api)
    register_structure_api(api, asset, attribute)

    @api.errorhandler(BackendException)
    def backend_exception_errorhandler(error):
        response = error.to_dict()
        response.status_code = error.status_code
        return response

    return blueprint
