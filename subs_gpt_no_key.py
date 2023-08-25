import requests
import json

"""
Following is the script for enhancing the existing subtitles with Chat GPT
"""


def main():
    """Main function"""

    # preparation: read and divide the long text into a list of subtitles
    file_name = '060/out1.txt'
    with open(file_name) as file:
        sub_list = file.read().split('\n\n')

    # step 2: divide the list into chunks
    chunked_list = chunk_list(sub_list)

    # step 3: improve the subs
    improved_chunks = improve_subs(chunked_list)

    return '\n\n'.join(improved_chunks)


def chunk_list(subs, chunk_size=50):
    """
    Divide subs into chunks for fewer API calls
    """
    chunked = []
    for i in range(0, len(subs), chunk_size):
        temp = []
        for j in range(0, chunk_size, 1):
            if i + j >= len(subs):
                break
            temp.append(subs[i + j])
        chunked.append('\n\n'.join(temp))
    return chunked


def improve_subs(chunks):
    """
    Call GPT API to impove subtitles
    """
    endpoint = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Authorization': 'Bearer INSERT_API_KEY',
        'Content-Type': 'application/json',
    }

    # read the prompt from a separate file
    prompt_file = 'prompt.txt'
    with open(prompt_file) as text:
        prompt = text.read()

    improved = []

    for instance in chunks:

        data = {
            'model': 'gpt-4', # use 'gpt-4' or 'gpt-3.5-turbo'
            'messages': [
                {"role": "user", "content": prompt + '\n' + instance}
            ]
        }
        try:
            response = requests.post(endpoint, headers=headers, data=json.dumps(data))
            response_json = response.json()
            # print(response_json)
            improved.append(response_json['choices'][0]['message']['content'])
        except:
            print('EXCEPTION RAISED\n', response_json)

    return improved


if __name__ == '__main__':
    print(main())