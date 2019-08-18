from telethon.sync import TelegramClient
from texttable import Texttable
from telethon.errors.rpcerrorlist import MessageIdInvalidError
import asyncio
import socks
import argparse
from timeit import default_timer as timer

parser = argparse.ArgumentParser(description = 'Simple telegram channel backup utility.')
parser.add_argument('--api_key')
parser.add_argument('--session')
parser.add_argument('--from_channel', default = None)
parser.add_argument('--to_channel', default = None)
parser.add_argument('action', choices = ['retrieve_channels', 'forward_posts'])
args = parser.parse_args()

print('Connecting to the Telegram...')
try:
	api_key = args.api_key.split(':')
	api_id = int(api_key[0])
	api_hash = api_key[1]
	session = args.session
	client = TelegramClient(session, api_id, api_hash)
	client.start()
	print('Logged in successfuly as @' + client.get_me().username)
except Exception as e:
	print("Couldn't connect to the Telegram:", e)
	exit(1)

def retrieve_channels():
    table = Texttable()
    table = table.header(['ID', 'Channel title', 'Username'])
    table = table.set_cols_width([12, 32, 33])
    table = table.set_cols_dtype(['t', 't', 't'])
    print('Retrieving dialogs...')
    for dialog in client.iter_dialogs():
    	if dialog.is_channel:
    		_id = str(dialog.entity.id)
    		title = dialog.title
    		username = '@' + dialog.entity.username
    		table.add_row([_id, title, username])
    print(table.draw())

def get_channel_entity(channel_id):
	for dialog in client.iter_dialogs():
		if dialog.entity.id == channel_id:
			return dialog.entity, dialog.message.id

def forward_posts():
	from_channel_id, to_channel_id = int(args.from_channel), int(args.to_channel)
	from_channel, posts_amount = get_channel_entity(from_channel_id)
	to_channel, _ = get_channel_entity(to_channel_id)
	print('Forwarding posts...')
	time1 = timer()
	posts_forwarded = 0
	for post in client.iter_messages(from_channel, reverse = True):
		try:
			post.forward_to(entity = to_channel)
			posts_forwarded += 1
		except MessageIdInvalidError:
			pass
		print('About {0:6.2f}% have been forwarded'.format(post.id / posts_amount * 100), end='\r')
	time2 = timer()
	print()
	print('=============================================')
	print('{0} posts have been forwarded in {1:.2f} seconds'.format(posts_forwarded, (time2 - time1)))
	print('=============================================')
if __name__ == '__main__':
	exec(args.action + '()')