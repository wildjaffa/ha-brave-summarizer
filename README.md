# ha-brave-summarizer

Uses the [Brave search api](https://brave.com/search/api/) to ask the Home Assistant Voice Assistant simple questions and get meaningful results.

## Flow

The flow for this is a little convoluted because accessing the correct Home Assistant properties in the correct places proved tricky.

- A custom intent script `AskQuestion` detects that a question is being asked and pipes the question to a custom Home Assistant Script `ask_question`
- `ask_question` sends the question to a custom service `brave_summarizer` which makes the web request to Brave Search
- `brave_summarizer` returns the question, summary, and sources to the script `ask_question` in the variable `brave_response`
- `ask_question` then calls the python_script.set_state 3 times in parallel to update template sensors `question_asked`, `answer_summary`, and `answer_sources`.
- the intent script `AskQuestion` now considers the process complete and answers the user from a template which uses sensors`answer_summary` and `answer_sources`.

## How to

- Set up an intent script under `custom_sentences` that will intercept the question type and wildcard (this is broken into two parts so we don't just put a wildcard as the base)
- Configure the custom `summarizer_service` including setting the `X-Subscription-Token`
- Update the `configuration.yaml` with sensors that will hold the values for the `question_asked`, the `answer_summary`, and the `answer_sources`. I used a template type that updates at midnight just so the question does hang out forever
- Update the `configuration.yaml` to include [python scripts](https://www.home-assistant.io/integrations/python_script/)
- Include a python script to update the state from a script. I used the implementation provided by [Rod Payne](https://github.com/rodpayne/home-assistant)
- Update the `configuration.yaml` to include the custom `brave_summarizer`
- Update the `configuration.yaml` to include the `intent_script`: `AskQuestion`
- Update `scripts.yaml` to include the `ask_question` script (Just paste it onto the bottom)
