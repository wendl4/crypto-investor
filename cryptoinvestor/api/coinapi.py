import datetime
import os
import logging

from urllib.parse import urljoin

from cryptoinvestor.api import ApiBase
from cryptoinvestor.objects import Asset

logger = logging.getLogger(__name__)


class Api(ApiBase):
    def __init__(self, config: dict):
        super(Api, self).__init__(config)

        if config is None:
            config = {}

        self.base = config.get('base_url', 'https://rest.coinapi.io/v1/')

        if not config.get('api_key'):
            config['api_key'] = os.environ.get('COINAPI_KEY')

        if not config.get('api_key'):
            raise self.Error(
                'Please provide CoinApi access key in env variable \'COINAPI_KEY\''
            )

        self.sess.headers.update({
            'X-CoinAPI-Key': config.get('api_key')
        })

    def connect(self) -> bool:
        url = urljoin(self.base, 'exchanges')

        r = self.sess.get(url)

        if not r.ok:
            self.error = f'Error while connecting to {url}'
            return False

        self.error = ''
        return True

    def get(self) -> [Asset]:
        url = urljoin(self.base, 'assets')

        r = self.sess.get(url)

        if not r.ok:
            self.error = f'Error while connecting to {url}'
            return []

        data = r.json()

        assets = []

        for asset in data:
            assets.append(Asset(
                id=asset.get('asset_id'), name=asset.get('name'),
                is_crypto=asset.get('type_is_crypto')
            ))

        self.error = ''

        return assets

    def load(self, *, asset: Asset, base: str, time: datetime.datetime) -> Asset:
        payload = {
            'time':  time.strftime('%Y%m%dT%H%M%S')
        }

        url = urljoin(self.base, f'exchangerate/{asset.id}/{base}')

        r = self.sess.get(url, params=payload)
        print(r.url)

        if not r.ok:
            self.error = f'Error loading data from {url} request: {r.content}'
            return None

        data = r.json()

        if not data:
            self.error = f'No data loaded from {url}'
        else:
            self.error = ''

        asset.set_rate(data.get('asset_id_quote'), data.get('rate'), data.get('time'))

        return asset

    def update(self, assets: {str: Asset}) -> {str: Asset}:
        updated = {}

        for asset in assets.values():
            if asset.is_loaded():
                for base in asset.rates.keys():
                    self.load(asset=asset, base=base, time=datetime.datetime.utcnow())

                updated[asset.id] = asset

        return updated
