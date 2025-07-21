import pyjokes

# Get one joke
print(pyjokes.get_joke())

joke = pyjokes.get_joke(language = 'en')
print(joke)