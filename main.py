import telebot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from datetime import datetime
import pandas as pd
import textdistance as td

API_TOKEN = '5771980924:AAE-InQhW_KqaEDl-9QYYqkWCjsPP3l36lc'

bot = telebot.TeleBot(API_TOKEN)

registro = {'nombre': [''],
'caballo': [''],
'jinete': [''],
'altura': [''],
'faltas': [''],
'resultado': [''],
'fecha': [''],
'observaciones': ['']}

global df_caballos
df_caballos = pd.read_csv('Listado_caballos.csv', sep=';')
lista_caballos = df_caballos['Nombre']
lista_caballos = lista_caballos.unique()

global df_jinetes
df_jinetes = pd.read_csv('Competiciones_plataforma.csv', sep=';', encoding='latin-1')
lista_jinetes = df_jinetes['Jinete']
lista_jinetes = lista_jinetes.unique()
lista_jinetes = sorted(lista_jinetes)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id

    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Cargar Concurso'))
    
    msg = """
Hola! Soy el BOT del Haras San José del Moro \U0001F434 \U0001F916 
Con que puedo ayudarte?
        """
    bot.send_message(chat_id, msg, reply_markup=markup)

@bot.message_handler(regexp='Cargar Concurso|Editar')
def cargar_concurso(message):
    chat_id = message.chat.id

    markup = ReplyKeyboardRemove()

    msg = bot.send_message(chat_id,'Que nombre le queres poner al concurso?', reply_markup=markup)
    bot.register_next_step_handler(msg, guardar_nombre)

def guardar_nombre(message):
    chat_id = message.chat.id

    registro['nombre'][0] = message.text

    markup = ReplyKeyboardMarkup()
    for jinete in lista_jinetes:
        markup.add(KeyboardButton(jinete))

    msg = bot.send_message(chat_id, 'Seleccione el jinete', reply_markup=markup)
    bot.register_next_step_handler(msg, guardar_jinete)

def guardar_jinete(message):
    chat_id = message.chat.id

    markup = ReplyKeyboardRemove()

    registro['jinete'][0] = message.text

    msg = bot.send_message(chat_id, 'Tipee el caballo', reply_markup=markup)
    bot.register_next_step_handler(msg, consultar_caballo)

def consultar_caballo(message):
    chat_id = message.chat.id

    caballo_consulta = message.text

    similarity_perc = [td.jaccard.normalized_similarity(caballo_consulta, s) for s in lista_caballos]

    indexes = []
    for i in range(3):
        index = similarity_perc.index(max(similarity_perc))
        indexes.append(index)
        del similarity_perc[index] 

    markup = ReplyKeyboardMarkup()
    for index in indexes:
        markup.add(KeyboardButton(lista_caballos[index]))

    msg = bot.send_message(chat_id, 'Seleccione la opcion correcta', reply_markup=markup)
    bot.register_next_step_handler(msg, guardar_caballo)

def guardar_caballo(message):
    chat_id = message.chat.id

    registro['caballo'][0] = message.text
    
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('1,00'))
    markup.add(KeyboardButton('1,20'))
    markup.add(KeyboardButton('1,30'))
    markup.add(KeyboardButton('1,40'))
    markup.add(KeyboardButton('1,50'))
    markup.add(KeyboardButton('1,60'))
    markup.add(KeyboardButton('1,70'))
    markup.add(KeyboardButton('PC'))

    msg = bot.send_message(chat_id, 'Seleccione la altura del concurso', reply_markup=markup)
    bot.register_next_step_handler(msg, guardar_altura)

def guardar_altura(message):
    chat_id = message.chat.id

    registro['altura'][0] = message.text

    markup = ReplyKeyboardRemove()

    msg = bot.send_message(chat_id, 'Ingrese la cantidad de faltas', reply_markup=markup)
    bot.register_next_step_handler(msg, guardar_faltas)

def guardar_faltas(message):
    chat_id = message.chat.id

    registro['faltas'][0] = message.text

    msg = bot.send_message(chat_id,'Como quedaste en la tabla de posiciones?\nPor ejemplo, si saliste 1ro ingresá 1')
    bot.register_next_step_handler(msg, guardar_resultado)

def guardar_resultado(message):
    chat_id = message.chat.id

    registro['resultado'][0] = message.text

    msg = bot.send_message(chat_id,'Ingrese la fecha del concurso con el siguiente formato (dd/mm/aaaa)')
    bot.register_next_step_handler(msg, guardar_fecha)

def guardar_fecha(message):
    chat_id = message.chat.id

    try:
        fecha = datetime.strptime(message.text, '%d/%m/%Y')
        
        registro['fecha'][0] = message.text

        text_msg = "Adjunte el archivo del concurso"

        msg = bot.send_message(chat_id, text_msg)
        bot.register_next_step_handler(msg, guardar_archivo)
    
    except:
        text_msg = """
Formato de fecha incorrecto
        
Fecha (dd/mm/aaaa)
        """
        msg = bot.send_message(chat_id, text_msg)
        bot.register_next_step_handler(msg, guardar_fecha)

def guardar_archivo(message):
    chat_id = message.chat.id

    msg = bot.send_message(chat_id,'Ingrese alguna observación o comentario sobre el concurso')
    bot.register_next_step_handler(msg, guardar_observacion)

def guardar_observacion(message):
    chat_id = message.chat.id

    registro['observaciones'][0] = message.text

    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Confirmar'))
    markup.add(KeyboardButton('Editar'))
    
    text_msg = f"""
Revisá los datos ingresados y confirma

Fecha: {registro['fecha'][0]}
Nombre: {registro['nombre'][0]}
Jinete: {registro['jinete'][0]}
Caballo: {registro['caballo'][0]}
Altura: {registro['altura'][0]}
Resultado: {registro['resultado'][0]}
Faltas: {registro['faltas'][0]}
Observaciones: {registro['observaciones'][0]}
    """
    bot.send_message(chat_id, text_msg, reply_markup=markup)

@bot.message_handler(regexp='Confirmar')
def confirmar_carga(message):
    chat_id = message.chat.id

    df_competiciones = pd.read_csv('Competiciones_BOT.csv', sep=';')
    df_competiciones = df_competiciones.iloc[: , 1:]

    df_new_competiciones = pd.DataFrame(registro)
    
    df_competiciones = pd.concat([df_competiciones, df_new_competiciones], ignore_index=True)
    df_competiciones.to_csv('Competiciones_BOT.csv', sep=';')

    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Cargar Concurso'))

    msg = """
            Guardado! \U0001F44D
            """
    bot.send_message(chat_id, msg, reply_markup=markup)
    
bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

print("El BOT se esta ejecutando")

bot.infinity_polling()