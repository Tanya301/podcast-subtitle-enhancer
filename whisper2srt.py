import json

"""
Following is the script formatting subtitles from json

---
! Preparation:

 export YOUR_SECRET=_____________

curl -X POST \
  -H "Authorization: Token $YOUR_SECRET" \
  -H 'content-type: application/json' \
  -d '{"url":"https://rupostgres.org/058%20Self-managing.m4a"}' \
  "https://api.deepgram.com/v1/listen?model=whisper-large&punctuate=true&smart_format=true&diarize=true" > result.json

bash

cat result.json | jq -r '.' > formatted.json
---

Strategy:
- get a dict and then a list
- start building new file:
    - i counter
    - speaker
    - punctuation
    - sentence length
-return the string, it will write into a file

* string:
f'{counter}\n{begin} --> {end}\n{text}'

* array gotten from the json:
2d
[[word, begin, end, speaker]]

* determining speaker
using name they say
"""


def main():
    """Main function"""

    # to_read = input() # tested with: 'formatted.json'
    to_read = '060/formatted.json'
    try:
        # print('reading file...')
        with open(to_read) as file:
            words_dict = json.load(file)
            words_list = process_json(words_dict)
            subs_list = divide_processed(words_list)
            formatted_subs = '\n\n'.join(subs_list)
        return formatted_subs

    except FileNotFoundError:
        print('ERROR: file not found')
    except json.JSONDecodeError:
        print('ERROR: issue decoding json')


def process_json(words):
    """
    Function processed the dictionary into a list with the following 
    formatting: [[word, begin, end, speaker num]]
    """
    # print('processing json...')
    words_list = []
    for instance in words['results']['channels'][0]['alternatives'][0]['words']:
        words_list.append([instance['punctuated_word'], instance['start'], \
            instance['end'], instance['speaker']])
    return words_list


def divide_processed(words):
    """
    Function divides a list of words into a list of subtitles, thinking about:
    - who is speaking
    - character count
    - punctuation
    - long pauses -- TODO

    ! time format:
    0.06 -> 00:00:00,060
    1550.68 -> (1550 // 3600):(1550 % 3600 // 60):(1550 % 60),680
    """
    # print('building subs...')

    def format_time(timecode):
        time_int = int(timecode)
        time_str = str(timecode)
        return '{hrs}:{mins}:{secs},{decimal}'.format(hrs=time_int//3600, \
            mins=time_int%3600//60, secs=time_int%60, \
            decimal=time_str.split('.')[1] if '.' in time_str else 0)

    punctuation = '.!?'

    speakers = assign_speakers(words); # dict
    sub_counter = 1; # subtitle counter
    cur_sub = [] # current sub: [text, start, end]
    subs = [] # list of strings
    prev_speaker = -1
    for instance in words: # each instance: [word, start, end, speaker num]
        if len(cur_sub) == 0:
            if prev_speaker != instance[3]:
                cur_sub = [f'{speakers[instance[3]]}: {instance[0]}', \
                instance[1], instance[2]]
                prev_speaker = instance[3]
            else:
                cur_sub = [f'{speakers[instance[3]]}: {instance[0]}', \
                instance[1], instance[2]]
        else:
            if prev_speaker != instance[3]: # speaker change
                subs.append('{counter}\n{begin} --> {end}\n{text}'\
                    .format(counter=sub_counter, begin=format_time(cur_sub[1]), \
                        end=format_time(cur_sub[2]), text=cur_sub[0]))
                sub_counter += 1
                cur_sub = [f'{speakers[instance[3]]}: {instance[0]}', \
                instance[1], instance[2]]
                prev_speaker = instance[3]
            elif cur_sub[0][-1] in punctuation: # punctuation
                subs.append('{counter}\n{begin} --> {end}\n{text}'\
                    .format(counter=sub_counter, begin=format_time(cur_sub[1]), \
                        end=format_time(cur_sub[2]), text=cur_sub[0]))
                sub_counter += 1
                cur_sub = [f'{instance[0]}', instance[1], instance[2]]
            elif 25 <= len(cur_sub[0]) and '\n' not in cur_sub[0]: # char count 1
                cur_sub[0] += '\n'
                cur_sub[0] += instance[0]
                cur_sub[2] = instance[2]
            elif 60 <= len(cur_sub[0]): # char count 2
                subs.append('{counter}\n{begin} --> {end}\n{text}'\
                    .format(counter=sub_counter, begin=format_time(cur_sub[1]), \
                        end=format_time(cur_sub[2]), text=cur_sub[0]))
                sub_counter += 1
                cur_sub = [f'{instance[0]}', instance[1], instance[2]]
            else: # just add the new word
                cur_sub[0] += ' ' + instance[0]
                cur_sub[2] = instance[2] 

    return subs


def assign_speakers(words, word_limit=1000):
    """
    Helper function to assign speakers to numbers
    """
    speaker_counts = {0: {'Nikolay': 0, 'Michael': 0}, 
                      1: {'Nikolay': 0, 'Michael': 0},
                      2: {'Nikolay': 0, 'Michael': 0}}
    
    words_analyzed = 0

    # Count mentions of each name for each speaker
    for instance in words:
        if words_analyzed >= word_limit:
            break
        if 'nikola' in instance[0].lower():
            speaker_counts[instance[3]]['Nikolay'] += 1
        elif 'michael' in instance[0].lower():
            speaker_counts[instance[3]]['Michael'] += 1
        words_analyzed += 1

    speaker_identity = {}

    # Determine speaker identity based on name mentions
    for speaker, counts in speaker_counts.items():
        if counts['Nikolay'] > counts['Michael']:
            speaker_identity[speaker] = 'Michael'
        else:
            speaker_identity[speaker] = 'Nikolay'

    return speaker_identity


if __name__ == "__main__":
    print(main())


