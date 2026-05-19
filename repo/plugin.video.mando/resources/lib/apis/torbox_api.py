# -*- coding: utf-8 -*-
from threading import Thread
from urllib.parse import urlencode
from caches.settings_cache import get_setting, set_setting
from caches.main_cache import cache_object
from modules.source_utils import supported_video_extensions, seas_ep_filter, extras
from modules.kodi_utils import make_session, kodi_dialog, ok_dialog, notification, confirm_dialog
# from modules.kodi_utils import logger

base_url = 'https://api.torbox.app/v1/api/'
session = make_session(base_url)


def _to_int(value, default=0):
	try: return int(str(value).strip())
	except Exception: return default


class TorBoxAPI:
	def __init__(self):
		self.token = get_setting('mando.tb.token')

	def _safe_json(self, response):
		try: return response.json()
		except Exception: return None

	def _get(self, url, data=None):
		if self.token in ('empty_setting', '', None): return None
		try:
			headers = {'Authorization': 'Bearer %s' % self.token}
			response = session.get(base_url + url, params=data or {}, headers=headers, timeout=20)
			return self._safe_json(response)
		except Exception: return None

	def _post(self, url, params=None, json=None, data=None, files=None):
		if self.token in ('empty_setting', '', None) and 'token' not in url: return None
		try:
			headers = {'Authorization': 'Bearer %s' % self.token}
			response = session.post(base_url + url, params=params, json=json, data=data, files=files, headers=headers, timeout=30)
			return self._safe_json(response)
		except Exception: return None

	def add_headers_to_url(self, url):
		return url + '|' + urlencode({'User-Agent': 'Mozilla/5.0'})

	def account_info(self):
		return self._get('user/me')

	# ----------- USER CLOUD LISTS -----------
	def user_cloud(self):
		string = 'tb_user_cloud'
		url = 'torrents/mylist'
		return cache_object(self._get, string, url, False, 0.03)

	def user_cloud_usenet(self):
		string = 'tb_user_cloud_usenet'
		url = 'usenet/mylist'
		return cache_object(self._get, string, url, False, 0.03)

	def user_cloud_webdl(self):
		string = 'tb_user_cloud_webdl'
		url = 'webdl/mylist'
		return cache_object(self._get, string, url, False, 0.03)

	def user_cloud_info(self, request_id=''):
		string = 'tb_user_cloud_%s' % request_id
		url = 'torrents/mylist?id=%s' % request_id
		return cache_object(self._get, string, url, False, 0.03)

	def user_cloud_info_usenet(self, request_id=''):
		string = 'tb_user_cloud_usenet_%s' % request_id
		url = 'usenet/mylist?id=%s' % request_id
		return cache_object(self._get, string, url, False, 0.03)

	def user_cloud_info_webdl(self, request_id=''):
		string = 'tb_user_cloud_webdl_%s' % request_id
		url = 'webdl/mylist?id=%s' % request_id
		return cache_object(self._get, string, url, False, 0.03)

	def user_cloud_clear(self):
		if not confirm_dialog(): return
		data = {'all': True, 'operation': 'delete'}
		self._post('torrents/controltorrent', json=data)
		self._post('usenet/controlusenetdownload', json=data)
		self._post('webdl/controlwebdownload', json=data)
		self.clear_cache()

	# ----------- INFO -----------
	def torrent_info(self, request_id=''):
		return self._get('torrents/mylist', data={'id': request_id})

	def usenet_info(self, request_id=''):
		return self._get('usenet/mylist', data={'id': request_id})

	def webdl_info(self, request_id=''):
		return self._get('webdl/mylist', data={'id': request_id})

	# ----------- DELETE -----------
	# TorBox requires the *_id field to be a JSON integer. Cast defensively.
	def delete_torrent(self, request_id=''):
		data = {'torrent_id': _to_int(request_id), 'operation': 'delete'}
		return self._post('torrents/controltorrent', json=data)

	def delete_usenet(self, request_id=''):
		data = {'usenet_id': _to_int(request_id), 'operation': 'delete'}
		return self._post('usenet/controlusenetdownload', json=data)

	def delete_webdl(self, request_id=''):
		data = {'webdl_id': _to_int(request_id), 'operation': 'delete'}
		return self._post('webdl/controlwebdownload', json=data)

	# ----------- UNRESTRICT (request download URL) -----------
	def unrestrict_link(self, file_id):
		try:
			torrent_id, file_id = file_id.split(',')
			params = {'token': self.token, 'torrent_id': _to_int(torrent_id), 'file_id': _to_int(file_id)}
			r = self._get('torrents/requestdl', data=params)
			if r and r.get('success'): return r.get('data')
			return None
		except Exception: return None

	def unrestrict_usenet(self, file_id):
		try:
			usenet_id, file_id = file_id.split(',')
			params = {'token': self.token, 'usenet_id': _to_int(usenet_id), 'file_id': _to_int(file_id)}
			r = self._get('usenet/requestdl', data=params)
			if r and r.get('success'): return r.get('data')
			return None
		except Exception: return None

	def unrestrict_webdl(self, file_id):
		try:
			web_id, file_id = file_id.split(',')
			params = {'token': self.token, 'web_id': _to_int(web_id), 'file_id': _to_int(file_id)}
			r = self._get('webdl/requestdl', data=params)
			if r and r.get('success'): return r.get('data')
			return None
		except Exception: return None

	# ----------- CREATE TRANSFERS -----------
	def add_magnet(self, magnet):
		# TorBox expects multipart-style form fields; lowercase booleans.
		data = {'magnet': magnet, 'seed': '3', 'allow_zip': 'false'}
		return self._post('torrents/createtorrent', data=data)

	def add_webdl(self, link):
		data = {'link': link}
		return self._post('webdl/createwebdownload', data=data)

	# ----------- CACHED CHECK -----------
	def check_cache_single(self, _hash):
		return self._get('torrents/checkcached', data={'hash': _hash, 'format': 'list'})

	def check_cache(self, hashlist):
		return self._post('torrents/checkcached', params={'format': 'list'}, json={'hashes': hashlist})

	def check_cache_webdl(self, hashlist):
		return self._post('webdl/checkcached', params={'format': 'list'}, json={'hashes': hashlist})

	def check_cache_usenet(self, hashlist):
		return self._post('usenet/checkcached', params={'format': 'list'}, json={'hashes': hashlist})

	def create_transfer(self, magnet_url):
		result = self.add_magnet(magnet_url)
		if not result or not result.get('success'): return ''
		return (result.get('data') or {}).get('torrent_id', '')

	def create_webdl_transfer(self, link):
		result = self.add_webdl(link)
		if not result or not result.get('success'): return ''
		return (result.get('data') or {}).get('webdownload_id', '')

	# ----------- RESOLVE -----------
	def resolve_magnet(self, magnet_url, info_hash, store_to_cloud, title, season, episode):
		torrent_id = None
		try:
			extensions = supported_video_extensions()
			extras_filter = extras()
			extras_filtering_list = tuple(i for i in extras_filter if i not in title.lower())
			torrent = self.add_magnet(magnet_url)
			if not torrent or not torrent.get('success'): return None
			torrent_id = torrent['data']['torrent_id']
			torrent_files = self.torrent_info(torrent_id)
			files = torrent_files['data']['files']
			selected_files = [{'url': '%d,%d' % (int(torrent_id), item['id']), 'filename': item['short_name'], 'size': item['size']}
				for item in files if item['short_name'].lower().endswith(tuple(extensions))]
			if not selected_files: return None
			if season:
				selected_files = [i for i in selected_files if seas_ep_filter(season, episode, i['filename'])]
			else:
				if self._m2ts_check(selected_files): return None
				selected_files = [i for i in selected_files if not any(x in i['filename'] for x in extras_filtering_list)]
				selected_files.sort(key=lambda k: k['size'], reverse=True)
			if not selected_files: return None
			file_key = selected_files[0]['url']
			file_url = self.unrestrict_link(file_key)
			if not store_to_cloud: Thread(target=self.delete_torrent, args=(torrent_id,)).start()
			return file_url
		except Exception:
			if torrent_id: self.delete_torrent(torrent_id)
			return None

	def display_magnet_pack(self, magnet_url, info_hash):
		torrent_id = None
		try:
			extensions = supported_video_extensions()
			torrent = self.add_magnet(magnet_url)
			if not torrent or not torrent.get('success'): return None
			torrent_id = torrent['data']['torrent_id']
			torrent_files = self.torrent_info(torrent_id)
			files = torrent_files['data']['files']
			pack_files = [{'link': '%d,%d' % (int(torrent_id), item['id']), 'filename': item['short_name'], 'size': item['size']}
				for item in files if item['short_name'].lower().endswith(tuple(extensions))]
			Thread(target=self.delete_torrent, args=(torrent_id,)).start()
			return pack_files or None
		except Exception:
			if torrent_id: self.delete_torrent(torrent_id)
			return None

	def _m2ts_check(self, folder_items):
		for item in folder_items:
			if item['filename'].endswith('.m2ts'): return True
		return False

	# ----------- AUTH -----------
	def auth(self):
		api_key = kodi_dialog().input('TorBox API Key:')
		if not api_key: return
		try:
			self.token = api_key.strip()
			r = self.account_info()
			if not r or not r.get('success'): raise Exception('invalid response')
			set_setting('tb.token', self.token)
			set_setting('tb.enabled', 'true')
			message = 'Success'
		except Exception:
			message = 'An Error Occurred'
		ok_dialog(text=message)

	def revoke(self):
		if not confirm_dialog(): return
		set_setting('tb.token', 'empty_setting')
		set_setting('tb.enabled', 'false')
		notification('TorBox Authorization Reset', 3000)

	def clear_cache(self, clear_hashes=True):
		try:
			from caches.debrid_cache import debrid_cache
			from caches.base_cache import connect_database
			dbcon = connect_database('maincache_db')
			# USER CLOUD
			try:
				dbcon.execute("""DELETE FROM maincache WHERE id=?""", ('tb_user_cloud',))
				dbcon.execute("""DELETE FROM maincache WHERE id=?""", ('tb_user_cloud_usenet',))
				dbcon.execute("""DELETE FROM maincache WHERE id=?""", ('tb_user_cloud_webdl',))
				dbcon.execute("""DELETE FROM maincache WHERE id LIKE ?""", ('tb_user_cloud%',))
				user_cloud_success = True
			except Exception:
				user_cloud_success = False
			# HASH CACHED STATUS
			if clear_hashes:
				try:
					debrid_cache.clear_debrid_results('tb')
					hash_cache_status_success = True
				except Exception:
					hash_cache_status_success = False
			else:
				hash_cache_status_success = True
		except Exception:
			return False
		if False in (user_cloud_success, hash_cache_status_success): return False
		return True


TorBox = TorBoxAPI()
