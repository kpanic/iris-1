from gevent.pywsgi import WSGIServer
from werkzeug.wrappers import Request
from werkzeug.exceptions import HTTPException

from iris.core.interfaces import Interface
from iris.core import trace
from iris.utils.sockets import create_socket


class WebServiceInterface(Interface):
    http_port = 80

    def __init__(self, *args, **kwargs):
        super(WebServiceInterface, self).__init__(*args, **kwargs)
        self.wsgi_server = None

    def on_start(self):
        super(WebServiceInterface, self).on_start()
        self.http_socket = create_socket('fd://%s' % self.container.get_shared_socket_fd(self.http_port))
        self.wsgi_server = WSGIServer(self.http_socket, Request.application(self.dispatch_request))
        self.wsgi_server.start()

    def on_stop(self):
        self.wsgi_server.stop()
        super(WebServiceInterface, self).on_stop()

    def dispatch_request(self, request):
        trace.set_id()
        urls = self.url_map.bind_to_environ(request.environ)
        request.urls = urls
        try:
            endpoint, args = urls.match()
            if callable(endpoint):
                handler = endpoint(self, request)
                response = handler.dispatch(args)
            else:
                try:
                    handler = getattr(self, endpoint)
                except AttributeError:
                    raise  # FIXME
                response = handler(request, **args)
        except HTTPException as e:
            response = e.get_response(request.environ)
        return response
