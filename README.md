# Crossmit take-home exercise by Esteban Sánchez

Hello 👋 This is the code I wrote for the take-home test for Crossmit. If you're a reviewer, please let me start by saying thank you as I had fun writing it. Please, check the commits along with this README file to understand my way of thinking and approach.

This README file is important because I try to express my way of thinking and to manage tasks. If you only focus on evaluating my code you may get a wrong idea about me. The work I write may not be perfect, lacking types, exception handling and many other things. Also the object abstraction could be improved and different I know how to do all of them, but I focused on getting the result. We could discuss on these things if you want to review my test with me 🧑🏻‍💻

## Kicking off 🦵

I'd like to take the chance to use some Python tooling like Poetry, that will probably help me kicking off an empty project.

```bash
pyenv install 3.12
pyenv local 3.12

poetry new crossmint
# I like my .venv to be in the same folder
poetry config virtualenvs.in-project true
poetry install --with-dev
```

And that will give me a nice folder structure

```
../crossmint/
├── README.md
├── crossmint
│   └── __init__.py
├── pyproject.toml
└── tests
    └── __init__.py
```

Added pre-commit and set it up so I have a super basic local CI

```bash
poetry add --group=dev pre-commit black isort ruff
```

Let's create the main entry point in `crossmint/main.py` and a add a script to `poetry.toml` to call it:

```TOML
...
[tool.poetry.scripts]
main = "crossmint.main:main"
...
```

And it works!

```bash
poetry run main
```

## Let's start the challenge!! 🚀

### Phase 1

Okay, so I see I need to drive a big X in a screen, so it's like a matrix. But I can only see I have an endpoint to check the goal, so I think it's smarter if I create a tool to reconcile what I have with what I want... 🤔

Honestly, I don't know what Phase 2 is going to be, so I'll try to picture my solution like a CLI tool. I've been working as a Devops/SRE and these kind of tools are something useful within a team because they can help you building tools to operate with different cloud providers and services. So I'll find a nice CLI library and create a `reconcile` command.

I found [cleo](https://github.com/python-poetry/cleo) and I think it looks nice, all I need to create is extend the `Command` class and define the `handle` function that will do what I need.

Now I need an API client and I'm tempted to use plain `requests` like many times but this seems like a simple REST API and there has to better libraries. I found this [`apiclient`](https://pypi.org/project/apiclient/) library that even though it seems unmantained looks promising.

So I start building a basic API class `BaseCrossmintClient` to basically write the configuration and authentication handler once and use the json response and request handlers. Quite easy to write an API client with this, so I write the `PolyanetClient` with the two actions I have `set(x, y)` and `clean(x, y)`.

Then I continue with the `ReconcileCommand` class. The idea is to get the current map, get the goal map and try to make them match. I need another API Client to access the map API, so I write `MapClient`, but this one needs no authentication so I need to change some of the dependency injections the `APIClient` super class has. Not a big issue, so I can get the current and goal map within minutes.

And to get the current map, since it's not documented, what I'm doing is open the website, open the JS console and see the AJAX call. It's not hard to see the new endpoint and the structure. `"SPACE"` and `"POLYANET"` are the key strings here 😄

Reading the API docs I thought authentication was going to be like a GET parameter and I thought it was working. Then I started getting `403`s on the first tests and the messages the API are returning are not the best, but I think I need to add the `candidateId` in the POST data, so I need to write a `CrossmintAuthenticationStrategy` class to overwrite the `post()` and `delete()`.

I do that, I run the code again and I went to check the website, but I already got into Phase 2! What!?! My code is far from perfect! 🫣

### Phase 2

Okay, now into phase 2, and I see I did a good approach with the reconcile command! All I need to do is implement the new APIs and the logic to sync them. First thing I do is get a view on the goal data. Apart from `"SPACE"` and `"POLYANET"` we have the `"${COLOR}_SOLOON"` and  `"${DIRECTION}_COMETH"`.

I'm creating the new API clients and some `Enum` classes to make sure I can only pass the correct values. Then I fix the reoncile loop to add the new classes and basically it all started syncing, until...

```
429 Error: Too Many Requests for url: https://challenge.crossmint.io/api/polyanets
```

😱


Oh, that should be easy to fix with retries in the API Client. The library has support and all I need to do is create a decorator using `tenacity` in the methods I want. I run it again, waiting for completion and...

<p align="center">
<img src="https://raw.githubusercontent.com/esanchezm/megaverse/master/img/office.gif" >
</p>

### Final thoughts

Wow, this was fast and I have so many things to add! I didn't add any test! Please accept my apologies for that, I was trying to make it work and then hoping to write some tests. Yeah, I know TDD but that's a bit unreal, way too complex sometimes and even more when talking to third parties. And now I see I can't because the goal map returns `Unsupported phase` 😵

However, with these tests written I could focus on thing I like more, like CI and especially with github actions. Running pytest in github actions is easy as pie...

Also, I could have created a Dockerfile so I can move this into a bunch of workers running this reconciliation in a `CronJob` in k8s vua Helm or kustomize.

Or I could have built a devcontainer so this could, or added prometheus metrics (I wrote a promethues exporter which is slightly popular, you can find it in [my github](https://github.com/esanchezm/prometheus-qbittorrent-exporter/)).


### Thanks and greetings

I want to thank you again for this test, it was good fun! Hope we can talk soon,

Esteban
