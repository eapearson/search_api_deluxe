"""The main entrypoint for running the Flask server."""
import sanic
import traceback

from src.exceptions import InvalidParameters
from src.utils.config import init_config
from src.search_objects import search_objects
from src.show_indexes import show_indexes

app = sanic.Sanic()


@app.route('/')
@app.route('/status', methods=['GET'])
async def health_check(request):
    """Really basic health check; could be expanded if needed."""
    return sanic.response.json({'status': 'ok'})


@app.route('/rpc', methods=['POST'])
async def root(request):
    """Handle JSON RPC methods."""
    json_body = request.json
    method = json_body.get('method', 'show_config')
    params = json_body.get('params', {})
    rpc_handlers = {
        'show_config': _show_config,
        'search_objects': search_objects,
        'show_indexes': show_indexes
    }
    if method not in rpc_handlers:
        InvalidParameters(f'Unknown method: {method}. Available methods: {rpc_handlers.keys()}')
    config = init_config()
    result = rpc_handlers[method](params, request.headers, config)
    return sanic.response.json(result)


def _show_config(params, headers, config):
    """
    Display publicly readable configuration settings for this server.
    Be sure to add new entries here explicitly so that nothing is shown unintentionally.
    """
    return {
        'elasticsearch_url': config['elasticsearch_url'],
        'workspace_url': config['workspace_url'],
        'index_prefix': config['index_prefix']
    }


@app.exception(sanic.exceptions.NotFound)
async def page_not_found(request, err):
    return sanic.response.json({'error': '404 - Not found.'}, status=404)


# Any other exception -> 500
@app.exception(Exception)
async def server_error(request, err):
    print('=' * 80)
    print('500 Server Error')
    print('-' * 80)
    traceback.print_exc()
    print('=' * 80)
    resp = {'error': '500 - Server error'}
    resp['error_class'] = err.__class__.__name__
    resp['error_details'] = str(err)
    return sanic.response.json(resp, status=500)


if __name__ == '__main__':
    print('hi')
    app.run(
        host='0.0.0.0',  # nosec
        port=5000,
        workers=8
        # debug=('DEVELOPMENT' in os.environ)  # XXX couldnt get autoreload to work
    )
