import flask

from cryptoinvestor.views import assets, index


def setup_urls(application: flask.Flask):
    application.add_url_rule('/', view_func=index.IndexView.as_view('index'))
    application.add_url_rule('/assets', view_func=assets.AssetsListView.as_view('assets_listview'))