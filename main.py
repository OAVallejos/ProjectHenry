import string
import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from spacy import displacy
from chat import Chat  # Supongo que 'chat' es un módulo personalizado que contiene la clase 'Chat'

# Configuración de spaCy
nlp = displacy.load('en_core_web_sm')

# Función para limpiar el texto
def clean_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = " ".join(word for word in text.split() if word.isalpha())
    return text

# Función para extraer el significado de las palabras
def get_meaning(word):
    try:
        synonyms = wordnet.synsets(word)
        if synonyms:
            meaning = synonyms[0].lemmas()[0].name()
            return meaning
        else:
            return "No se encontró un significado para la palabra"
    except:
        return "No se encontró un significado para la palabra"

# Función para crear el chatbot
def chatbot(input_text):
    input_text = clean_text(input_text)
    words = nltk.word_tokenize(input_text)
    response = ""
    for word in words:
        if word in stopwords.words('english'):
            continue
        else:
            meaning = get_meaning(word)
            response += f"{word} significa {meaning}.\n"
    return response

# Creación del chatbot
chat = Chat(chatbot)

# Inicio de la conversación
print("Bienvenido al chatbot de ayuda. ¿En qué puedo ayudarte?")
response = chat.converse("Hola Mundo")  # Incluye un mensaje inicial para el chatbot
print(response)
