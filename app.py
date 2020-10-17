from pymongo import MongoClient
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


class FlyBot():

    MONGO_URI = 'mongodb://localhost'
    TELEGRAM_TOKEN = "1144307188:AAG2GrlSnZy0hKf7Sx9sCK_sEY9FRgoEzwc"
    DATABASE_NAME = "FlyBot"

    def __init__(self):
        self.connect()
        self.create_db(self.DATABASE_NAME)
        self.metodos()

    def connect(self):
        try:
            self.client = MongoClient(self.MONGO_URI)
            print("Conexión a MongoDB exitosa.")
        except Exception as e:
            print(f'Ha ocurrido un error durante la conexión a MongoDB -> {e}')

    def create_db(self, db_name):
        try:
            self.db = self.client[db_name]
            print(f"Usando {db_name}.")
        except Exception as e:
            print('Ha ocurrido un error durante la conexión o creación de la base de datos ' +
                  f'{db_name} -> {e}')

    def start(self, update, context):
        update.message.reply_text('Hola, los comandos a usar son los siguientes:' +
                                  '\n/start -> Muestra todos los comandos.' +
                                  '\n/list -> Lista todos los vuelos disponibles.' +
                                  '\n/searchd (destino) -> Busca los vuelos disponibles con el destino indicado.' +
                                  '\n/searcho (origen) -> Busca los vuelos disponibles con el origen indicado.' +
                                  '\n/buyticket (nombre) (apellido) (cedula) (número de asientos) (número de vuelo) -> Reserva vuelos sin fecha de retorno.' +
                                  '\n/buyrtticket (nombre) (apellido) (cedula) (número de asientos) (número de vuelo) -> Reserva vuelos con fecha de retorno.')

    def list(self, update, context):
        try:
            self.vuelos_collection = self.db['vuelos']
            vuelos = self.vuelos_collection.find()
            for vuelo in vuelos:
                update.message.reply_text(
                    "\n\nDestino: {}, {}, {}, {}".format(
                        *vuelo['destino'].values()) + "\nOrigen: {}, {}, {}, {}".format(
                        *vuelo['origen'].values()) + "\nFecha de ida: {}".format(
                        vuelo["fecha de ida"]) + "\nFecha de llegada: {}".format(
                        vuelo["fecha de llegada"]) + "\nNúmero de vuelo: {}".format(
                            vuelo['numero de vuelo'])
                )
        except Exception as err:
            print(err)
            update.message.reply_text('Algo ha ocurrido mal.')

    def searchd(self, update, context):
        argumento = " ".join(update.message['text'].split(" ")[1:])
        try:
            self.vuelos_collection = self.db['vuelos']
            vuelos = self.vuelos_collection.find({'$or': [
                {'destino.ciudad': argumento},
                {'destino.IATA': argumento},
                {'destino.pais': argumento},
                {'destino.provincia': argumento}
            ]})
            for vuelo in vuelos:
                update.message.reply_text(
                    "\n\nDestino: {}, {}, {}, {}".format(
                        *vuelo['destino'].values()) + "\nOrigen: {}, {}, {}, {}".format(
                        *vuelo['origen'].values()) + "\nFecha de ida: {}".format(
                        vuelo["fecha de ida"]) + "\nFecha de llegada: {}".format(
                        vuelo["fecha de llegada"]) + "\nNúmero de vuelo: {}".format(
                            vuelo['numero de vuelo'])
                )
        except Exception as err:
            print(err)
            update.message.reply_text('Algo ha ocurrido mal.')

    def searcho(self, update, context):
        argumento = " ".join(update.message['text'].split(" ")[1:])
        try:
            self.vuelos_collection = self.db['vuelos']
            vuelos = self.vuelos_collection.find({'$or': [
                {'origen.ciudad': argumento},
                {'origen.IATA': argumento},
                {'origen.pais': argumento},
                {'origen.provincia': argumento}
            ]})
            for vuelo in vuelos:
                update.message.reply_text(
                    "\n\nDestino: {}, {}, {}, {}".format(
                        *vuelo['destino'].values()) + "\nOrigen: {}, {}, {}, {}".format(
                        *vuelo['origen'].values()) + "\nFecha de ida: {}".format(
                        vuelo["fecha de ida"]) + "\nFecha de llegada: {}".format(
                        vuelo["fecha de llegada"]) + "\nNúmero de vuelo: {}".format(
                            vuelo['numero de vuelo'])
                )
        except Exception as err:
            print(err)
            update.message.reply_text("Algo ha ocurrido mal.")

    def buyticket(self, update, context):
        argumentos = update.message['text'].split(" ")[1:]
        if len(argumentos) != 5:
            update.message.reply_text('Debe completar los campos requeridos.')
            return
        try:
            self.vuelos_collection = self.db['vuelos']
            self.usuarios_collection = self.db['usuarios']
            vuelo = self.vuelos_collection.find_one(
                {'numero de vuelo': int(argumentos[4])})
            if vuelo['fecha de llegada'] != '':
                update.message.reply_text(
                    'Con este comando solo puede reservar un vuelo sin fecha de retorno.')
                return
            self.usuarios_collection.insert_one({
                "nombre": argumentos[0],
                "apellido": argumentos[1],
                "cedula": argumentos[2],
                "numero_de_asientos": argumentos[3],
                "id_vuelo": argumentos[4]
            })
            update.message.reply_text(
                f"El vuelo {argumentos[4]} para el usuario/a {argumentos[1]} ha sido registrado.")
        except Exception as err:
            print(err)
            update.message.reply_text('Algo ha ocurrido mal.')

    def buyrtticket(self, update, context):
        argumentos = update.message['text'].split(" ")[1:]
        if len(argumentos) != 5:
            update.message.reply_text('Debe completar los campos requeridos.')
            return
        try:
            self.vuelos_collection = self.db['vuelos']
            self.usuarios_collection = self.db['usuarios']
            vuelo = self.vuelos_collection.find_one(
                {'numero de vuelo': int(argumentos[4])})
            if vuelo['fecha de llegada'] == '':
                update.message.reply_text(
                    'Con este comando solo puede reservar un vuelo con fecha de retorno.')
                return
            self.usuarios_collection.insert_one({
                "nombre": argumentos[0],
                "apellido": argumentos[1],
                "cedula": argumentos[2],
                "numero_de_asientos": argumentos[3],
                "id_vuelo": argumentos[4]
            })
            update.message.reply_text(
                f"El vuelo {argumentos[4]} para el usuario/a {argumentos[1]} ha sido registrado.")
        except Exception as err:
            print(err)
            update.message.reply_text('Algo ha ocurrido mal.')

    def unrecognized_command(self, update, context):
        update.message.reply_text(
            f'Comando no reconocido. Escriba /help para ver los comandos disponibles.')

    def unrecognized_input(self, update, context):
        update.message.reply_text(
            f'Solo se admite ingresar comandos. Escriba /help para ver los comandos disponibles.')

    def metodos(self):
        try:
            updater = Updater(self.TELEGRAM_TOKEN, use_context=True)
            updater.dispatcher.add_handler(
                CommandHandler("start", self.start))
            updater.dispatcher.add_handler(
                CommandHandler("list", self.list))
            updater.dispatcher.add_handler(
                CommandHandler("searchd", self.searchd))
            updater.dispatcher.add_handler(
                CommandHandler("searcho", self.searcho))
            updater.dispatcher.add_handler(
                CommandHandler("buyticket", self.buyticket))
            updater.dispatcher.add_handler(
                CommandHandler("buyrtticket", self.buyrtticket))
            updater.dispatcher.add_handler(
                CommandHandler("help", self.start))
            updater.dispatcher.add_handler(
                MessageHandler(Filters.command, self.unrecognized_command))
            updater.dispatcher.add_handler(
                MessageHandler(Filters.all, self.unrecognized_input))
            updater.start_polling()
            print('Bot funcionando...')
            updater.idle()
        except Exception as e:
            print(
                f'Ha ocurrido un error en la conexión con la API de Telegram -> {e}')


bot = FlyBot()
