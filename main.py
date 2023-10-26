import nltk
from nltk.chat import Chat
from nltk.corpus import stopwords
from spacy import displacy


# Configuración de NLTK
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

from typing_extensions import deprecated

deprecated = None  # silence the warning

# Configuración de spaCy
nlp = displacy(model='en_core_web_sm')

# Función para limpiar el texto
def clean_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = " ".join(word for word in text.split() if word.isalpha())
    return text

# Función para extraer el significado de las palabras
def get_meaning(word):
    try:
        return wordnet.synonyms(word, pos=1)[0]
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
            if meaning:
                response += f"{word} significa {meaning}.\n"
            else:
                response += f"No se encontró un significado para la palabra {word}.\n"
    return response

# Creación del chatbot
chat = Chat(chatbot)

# Inicio de la conversación
print("Bienvenido al chatbot de ayuda. ¿En qué puedo ayudarte?")
chat.converse()