import src.legacy.common as common
from src.utils.config import init_config
from src.search_objects import search_objects as search_objects_api

_CONFIG = init_config()


def search_objects2(params, auth):
    """
    Handler for the "search_objects" RPC method, called by `handle_legacy` above.
    This takes all the API parameters to the legacy api and translates them to
    a call to `search_objects`.
    It also injects any extra info, such as narrative data, for each search result.
    """
    search_params = common.get_search_params2(params)

    # Yes, weird that it is in post_processing params.
    # Another example where we could fix this part of the legacy api while we
    # have a chance.
    post_processing = params.get('post_processing', {})
    if post_processing.get('include_highlight', False):
        # We need a special highlight query so that the main query does not generate
        # highlights for bits of the query which are not user-generated.
        highlight_query = {'bool': {}}
        match_filter = params['match_filter']
        if match_filter.get('search_term'):
            # Match full text for any field in the objects
            highlight_query['bool']['must'] = []
            highlight_query['bool']['must'].append({'match': {'agg_fields': match_filter['search_term']}})

        # Note that search_objects, being used by both the legacy and current api, supports highlighting
        # in the generic ES sense, so we pass a valid ES7 highlight param.
        search_params['highlight'] = {
            'fields': {'*': {}},
            'require_field_match': False,
            'highlight_query': highlight_query
        }

    search_results = search_objects_api(search_params, {
        'Authorization': auth
    })

    workspaces_info = common.fetch_workspaces_info(search_results, auth)

    objects = common.get_object_data_from_search_results2(search_results, post_processing)

    return {
        'total': search_results['count'],
        'search_time': search_results['search_time'],
        'objects': objects,
        'workspaces': workspaces_info
    }