import requests
import json
import time
from homeassistant.core import ServiceResponse, ServiceCall, SupportsResponse
import voluptuous as vol
import urllib.parse

DOMAIN = "brave_summarizer"
SUMMARIZER_SCHEMA = vol.Schema({
    vol.Required("question"): str,
    vol.Required("url_encode"): bool
})


async def async_setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""

    hass.services.async_register(DOMAIN, "get_brave_answer", get_brave_answer,
    schema=SUMMARIZER_SCHEMA,
    supports_response=SupportsResponse.ONLY)

    # Return boolean to indicate that initialization was successful.
    return True

def make_brave_request(end_point: str):
    base_url = "https://api.search.brave.com/res/v1/"

    url = base_url + end_point
    payload = {}
    headers = {
        'X-Subscription-Token': 'YOUR_API_KEY_HERE' #DO NOT FORGET TO REPLACE THIS!
    }

    search_response = requests.request("GET", url, headers=headers, data=payload)
    parsed = json.loads(search_response.text)
    return parsed

def get_reference_name(refernce) -> str:
    return refernce['name']

def get_references(summary_response) -> str:
    reference_root = summary_response['references']
    reference_names = map(get_reference_name, summary_response['references'])
    unique_references = list(set(reference_names))
    # we don't want to show more than 3 references
    if len(unique_references) > 3:
        unique_references = unique_references[:3]
    string_references = ', '.join(unique_references)
    string_references = ', and '.join(string_references.rsplit(', ', 1))
    return string_references

def get_summarizer_response(key: str, max_seconds: int = 4):
    summarizer_endpoint = 'summarizer/search?key='
    # annoying, but the key does not come back url encoded
    key = key.replace(' ', '%20')
    end_point = summarizer_endpoint + key
    summarizer_result = {}
    max_attempts = max_seconds * 2
    attempt = 1
    while attempt < max_attempts and not 'results' in summarizer_result:
        summarizer_result = make_brave_request(end_point)
        if 'results' in summarizer_result:
            return summarizer_result['results'][0]
        time.sleep(0.5)
        attempt += 1
    return 'timeout'

def search_brave(search: str) -> str:
    search_endpoint = 'web/search?q='
    search = search.replace(' ', '+')
    end_point = search_endpoint + search
    parsed = make_brave_request(end_point)

    if not 'summary_key' in parsed['query']:
        return 'no result'
    key: str = parsed['query']['summary_key']
    return key

def get_brave_answer(service_call: ServiceCall) -> ServiceResponse:
    question = service_call.data['question']
    response = {
        "question": question,
        "summary": "",
        "sources": "",
    }
    key = search_brave(question)
    if key == 'no result':
        response["summary"] = 'Sorry, I did not understand the question'
        return response
    answer = get_summarizer_response(key)
    if answer == 'timeout':
        response["summary"] = 'Sorry, I could not find an answer in a timely fashion'
        return response
    response['sources'] = get_references(answer)
    response['summary'] = answer['answer']['text']
    return response