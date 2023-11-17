import asyncio
from pypresence import Presence
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as mc
from urllib.parse import quote
import winsdk.windows.media.control as wwmcs
import nest_asyncio
import time
nest_asyncio.apply()

rpc = Presence('1174462979459272754')

async def get():
	try:
		# all sessions
		request = await mc.request_async()
		cs = request.get_current_session()
		mp = await cs.try_get_media_properties_async()
		cst = cs.source_app_user_model_id
		# track info
		author = mp.album_artist if not mp.album_artist == '' else mp.artist
		title = mp.album_title if not mp.album_title == '' else mp.title

		# is playing info
		pbi = cs.get_playback_info()
		status = pbi.playback_status
		return author, title, status, cst
	except Exception as e:
		print(e)
		pass

def stream(author, title, status, service):
	if status == 4:
		playing = 'play'
	elif status == 5:
		playing = 'pause'
	elif status == 'wtf':
		playing = 'wtf'
	else:
		playing = 'err'
	if 'Yandex.Music' in service:
		stxt = 'Yandex.Music'
		simg = 'yamu'
	elif 'Telegram' in service:
		stxt = 'Telegram'
		simg = 'tg'
	elif 'shrug' in service:
		stxt = 'bruh, im prlly not listening music rn'
		simg = 'shrug'

	url = f'https://google.com/search?q={quote(f"{author} {title}")}'

	rpc.update(
		details=f'🎙{author}',
		state=f'🎵{title}',
		large_image=simg,
		large_text=stxt,
		small_image=playing,
		small_text=playing,
		start=int(time.time()),
		buttons=[{'label': 'listen', 'url': url}]
	)


async def main():
	previous = ''
	started = 1
	stopped = 1
	not_playing = 0
	while True:
		try:
			session = await get()
			author = session[0]
			title = session[1]
			status = session[2]
			cst = session[3]
			current = f'{author}-{title}'
		except Exception as e:
			print(e)
			pass

		if 'Telegram' in cst or 'Yandex.Music' in cst:
			if status == 4:
				if current != previous: # 400iq ig
					print(f'{author} - {title}, {status}, {cst}')
					previous = current
					stream(author, title, status, cst)
					not_playing = 0
				if started == 0:
					print(f'{author} - {title}, {status}, {cst}')
					stream(author, title, status, cst)
					started += 1
				stopped = 0
				not_playing = 0
			if status == 5:
				if stopped == 0:
					print(f'currently stopped')
					stream(author, title, status, cst)
					stopped += 1
				started = 0
			if status == 3:
				pass
		else:
			if not_playing == 0:
				print('something else is turned on')
				stream('probably', 'nothing', 'wtf', 'shrug')
				not_playing += 1

if __name__ == '__main__':
	rpc.connect()
	asyncio.run(main())