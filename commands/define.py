import requests
import json
import discord

def dictionary_api_url(word_to_define, api_key):
  return "https://www.dictionaryapi.com/api/v3/references/collegiate/json/%s?key=%s" % (word_to_define, api_key)

def audio_api_url(audio_info, word_to_define):
  try:
    audio_name = audio_info['prs']
    if(len(audio_name) > 0):
      audio_name = audio_name[0]['sound']['audio']
    else:
      return -1
  except ValueError:
    return -1
  subdirectory = ''
  if(audio_name.startswith('bix')):
    subdirectory = 'bix'
  elif(audio_name.startswith('gg')):
    subdirectory = 'gg'
  elif(not audio_name[0].isalpha()):
    subdirectory = 'number'
  else:
    subdirectory = audio_name[0]
  return "https://media.merriam-webster.com/soundc11/%s/%s.wav" % (subdirectory, audio_name)

def create_embeded(word_to_define, function_label, offensive, audio_url, short_def):
  embed=discord.Embed(title="%s's Definition" % word_to_define, description=function_label, color=0x00f900)
  if(offensive):
    embed.add_field(name="Offensive?", value=offensive, inline=True)
  if(audio_url != -1):
    embed.add_field(name="Pronunciation", value="<%s>" % audio_url, inline=True)
  if(short_def):
    for i in range(len(short_def)):
      embed.add_field(name="Definition %d" % (i+1), value=short_def[i])
  return embed

"""
Define function command

@param client: The discord client, generally assumed to be the bot user itself
@param message: The message the discord bot is responding to
@param dictionary_api_key: The string containing the dictionary api key
@result: sends a message always
@result: deletes the triggering message always
"""
async def command(client, message, response_channel, delete_message, dictionary_api_key):
  await delete_message(client, message)
  word_to_define = message.content[8:].strip()
  if(' ' in word_to_define):
    await client.send_message(message.author, "Please only provide one word to define.")
    return
  dictionary_packet = requests.get(dictionary_api_url(word_to_define, dictionary_api_key))
  dictionary_response = dictionary_packet.text
  dictionary_response = json.loads(dictionary_response)
  if(len(dictionary_response) > 0 and 'meta' in dictionary_response[0]):
    dictionary_response = dictionary_response[0]
  elif(len(dictionary_response) > 0 and not 'meta' in dictionary_response[0]):
    await client.send_message(message.author, "Unable to define the word '%s', did you maybe mean on of the following? %s" % (word_to_define, dictionary_response))
    return
  else:
    await client.send_message(message.author, "Unable to define the word '%s'" % word_to_define)
    return
  short_def = dictionary_response['shortdef'] if 'shortdef' in dictionary_response else []
  functional_label = dictionary_response['fl'] if 'fl' in dictionary_response else ''
  meta_data = dictionary_response['meta'] if 'meta' in dictionary_response else ''
  offensive = meta_data['offensive'] if meta_data != '' and 'offensive' in meta_data else ''
  audio_info = dictionary_response['hwi'] if 'hwi' in dictionary_response else ''
  audio_url = audio_api_url(audio_info, word_to_define)
  embeded = create_embeded(word_to_define, functional_label, offensive, audio_api_url(audio_info, word_to_define), short_def)
  await client.send_message(response_channel, embed=embeded)


# String that triggers the help command
TRIGGER = '!define'