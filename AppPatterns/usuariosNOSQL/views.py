from django.http import JsonResponse
from pymongo import MongoClient
import datetime
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.parsers import JSONParser
from django.conf import settings
from bson.objectid import ObjectId

# Create your views here.

@api_view(["GET", "POST"])
def variables(request):
    client = MongoClient(settings.DB_HOST, int(settings.DB_PORT))
    db = client[settings.MONGO_DB]
    db.authenticate(settings.MLAB_USER, settings.MLAB_PASSWORD)
    variables = db['variables']
    if request.method == "GET":
        result = []
        data = variables.find({})
        for dto in data:
            jsonData = {
                'id': str(dto['_id']),
                "variable": dto['variable'],
                'capacidad': dto['capacidad']
            }
            result.append(jsonData)
        client.close()
        return JsonResponse(result, safe=False)
    
    if request.method == 'POST':
        data = JSONParser().parse(request)
        result = variables.insert(data)
        respo ={
            "MongoObjectID": str(result),
            "Message": "Nueva variable en base de datos"
        }
        client.close()
        return JsonResponse(respo, safe=False)

@api_view(["GET", "POST"])
def variablesDetail(request, pk):
    client = MongoClient(settings.DB_HOST, int(settings.DB_PORT))
    db = client[settings.MONGO_DB]
    db.authenticate(settings.MLAB_USER, settings.MLAB_PASSWORD)
    variables = db['variables']
    if request.method == "GET":
        data = variables.find({'_id': ObjectId(pk)})
        result = []
        for dto in data:
            jsonData ={
                'id': str(dto['_id']),
                "variable": dto['variable'],
                'capacidad': dto['capacidad']
            }
            result.append(jsonData)
        client.close()
        return JsonResponse(result[0], safe=False)
    if request.method == "POST":
        data = JSONParser().parse(request)
        result = variables.update(
            {'_id': ObjectId(pk)},
            {'$push': {'capacidad': data}}
        )
        respo ={
            "MongoObjectID": str(result),
            "Message": "Nueva variable en la base de datos"
        }
        return JsonResponse(respo, safe=False)

        
          
@api_view(["GET", "POST"])
def parqueaderos(request):
    client = MongoClient(settings.DB_HOST, int(settings.DB_PORT))
    db = client[settings.MONGO_DB]
    db.authenticate(settings.MLAB_USER, settings.MLAB_PASSWORD)
    parqueadero = db['parqueaderos']
    corporativoParqueadero = db['corporativoParqueadero']
    if request.method == "GET":
        result = []
        data = corporativoParqueadero.find({})
        for dto in data:
            jsonData = {
                "id": str(dto['_id']),
                "parqueadero": dto['parqueadero'],
                'usuarios': dto['usuarios'],
            }
            result.append(jsonData)
        data = parqueadero.find({})
        for dto in data:
            jsonData = {
                "id": str(dto['_id']),
                "parqueadero": dto['parqueadero'],
                'usuarios': dto['usuarios'],
            }
            result.append(jsonData)
        client.close()
        return JsonResponse(result, safe=False)
    if request.method == "POST":
        data = JSONParser().parse(request)
        usuarios = []
        data['usuarios'] = usuarios
        data['average'] = 0
        if data["corporativo"] == True:
            result = corporativoParqueadero.insert(data)
        else:
            result = parqueadero.insert(data)
        respo ={
            "MongoObjectID": str(result),
            "Message": "Nuevo parqueadero en la base de datos"
        }
        client.close()
        return JsonResponse(respo, safe=False)

@api_view(["GET", "POST", "DELETE"])
def parqueaderoDetail(request, pk):
    client = MongoClient(settings.DB_HOST, int(settings.DB_PORT))
    db = client[settings.MONGO_DB]
    db.authenticate(settings.MLAB_USER, settings.MLAB_PASSWORD)
    parqueadero = db['parqueaderos']
    corporativoParqueadero = db['corporativoParqueaderos']
    if request.method == "GET":
        result = []
        data = corporativoParqueadero.find({'_id': ObjectId(pk)})
        for dto in data:
            jsonData = {
                "id": str(dto['_id']),
                "parqueadero": dto['parqueadero'],
                'usuarios': dto['usuarios'],
            }
            result.append(jsonData)
        if result == []:
            data = parqueadero.find({'_id': ObjectId(pk)})
            for dto in data:
                jsonData = {
                    "id": str(dto['_id']),
                    "parqueadero": dto['parqueadero'],
                    'usuarios': dto['usuarios'],
                }
                result.append(jsonData)
        client.close()
        return JsonResponse(result[0], safe=False)

    if request.method == "POST":
        data = JSONParser().parse(request)
        average = 0
        result = []
        jsonData = {
            'value': data["value"],
            'datetime': datetime.datetime.utcnow()
        }

        for dto in corporativoParqueadero.find({'_id': ObjectId(pk)}):
            for d in dto["usuarios"]:
                if d["variable"] == data["variable"]:
                    d["values"].append(jsonData)
                    average = ((d["average"] * (len(d["values"])-1)) + data["value"]) / len(d["values"])

                    d["average"] = average
                    result = corporativoParqueadero.update(
                        {'_id': ObjectId(pk)},
                        {'$set': {'usuarios': dto["usuarios"]}}
                    )

                    respo = {
                        "MongoObjectID": str(result),
                        "Mensaje": "Se añadió un nuevo usuario"
                    }
                    client.close()
                    return JsonResponse(respo, safe=False)

            jsonDataNew = {
                'variable': data["variable"],
                'values': [
                    jsonData
                ],
                'average': data["value"]
            }
            result = corporativoParqueadero.update(
                {'_id': ObjectId(pk)},
                {'$push': {'usuarios': jsonDataNew}}
            )
            respo = {
                "MongoObjectID": str(result),
                "Mensaje": "Se añadió un nuevo usuario"
            }
            client.close()
            return JsonResponse(respo, safe=False)


        for dto in parqueadero.find({'_id': ObjectId(pk)}):
            for d in dto["usuarios"]:
                if d["variable"] == data["variable"]:
                    d["values"].append(jsonData)
                    #for val in d["values"]:
                    #    average = average + val["value"]
                    average = ((d["average"] * (len(d["values"]) - 1)) + data["value"]) / len(d["values"])
                    print ("Este es el promedio de tiempo que dura la reserva de un usuario: ", d["average"])
                    d["average"] = average
                    result = parqueadero.update(
                        {'_id': ObjectId(pk)},
                        {'$set': {'usuarios': dto["usuarios"]}}
                    )

                    respo = {
                        "MongoObjectID": str(result),
                        "Mensaje": "Se añadió un nuevo usuario"
                    }
                    client.close()
                    return JsonResponse(respo, safe=False)

            jsonDataNew = {
                'variable': data["variable"],
                'values': [
                    jsonData
                ],
                'average': data["value"]
            }
            result = parqueadero.update(
                {'_id': ObjectId(pk)},
                {'$push': {'usuarios': jsonDataNew}}
            )
            respo = {
                "MongoObjectID": str(result),
                "Mensaje": "Se añadió un nuevo usuario"
            }
            client.close()
            return JsonResponse(respo, safe=False)

    if request.method == "DELETE":
        result = parqueadero.remove({"_id": ObjectId(pk)})
        respo = {
            "MongoObjectID": str(result),
            "Mensaje": "Se ha borrado un parqueadero",
        }
        client.close()
        return JsonResponse(respo, safe=False)

@api_view(["GET", "POST"])
def warnings(request):
    client = MongoClient(settings.DB_HOST, int(settings.DB_PORT))
    db = client[settings.MONGO_DB]
    db.authenticate(settings.MLAB_USER, settings.MLAB_PASSWORD)
    warning = db['warnings']
    if request.method == "GET":
        result = []
        data = warning.find({})
        for dto in data:
            jsonData ={
                "parqueadero": dto['parqueadero'],
                "date": dto['date']
            }
            result.append(jsonData)
        client.close()
        return JsonResponse(result, safe=False)
    if request.method == 'POST':
        data = JSONParser().parse(request)
        data['date'] = datetime.datetime.utcnow()
        result = warning.insert(data)
        respo ={
            "MongoObjectID": str(result),
            "Message": "Nueva advertencia en la base de datos"
        }
        client.close()
        return JsonResponse(respo, safe=False)

@api_view(["GET"])
def warningDetail(request, pk):
    client = MongoClient(settings.DB_HOST, int(settings.DB_PORT))
    db = client[settings.MONGO_DB]
    db.authenticate(settings.MLAB_USER, settings.MLAB_PASSWORD)
    warning = db['warnings']
    data = warning.find({'_id': ObjectId(pk)})
    result = []
    for dto in data:
        jsonData ={
            "parqueadero": dto['parqueadero'],
            "date": dto['date']
        }
        result.append(jsonData)
    client.close()
    return JsonResponse(result[0], safe=False)

@api_view(["POST"])
def average(request, pk):
    client = MongoClient(settings.DB_HOST, int(settings.DB_PORT))
    db = client[settings.MONGO_DB]
    db.authenticate(settings.MLAB_USER, settings.MLAB_PASSWORD)
    dataReceived = JSONParser().parse(request)
    parqueadero = db['parqueaderos']
    corporativoParqueadero = db['corporativoParqueaderos']
    result = []
    parqueaderoAv = ""
    variableName = ""
    average = 0

    # Calculo de promedio
    for dto in corporativoParqueadero.find({'_id': ObjectId(pk)}):
        for d in dto["usuario"]:
            if d["variable"] == dataReceived["variable"]:
                parqueaderoAv = dto["parqueadero"]
                average = d["average"]

    if parqueaderoAv == "":
        for dto in parqueadero.find({'_id': ObjectId(pk)}):
            for d in dto["usuarios"]:
                if d["variable"] == dataReceived["variable"]:
                    parqueaderoAv = dto["parqueadero"]
                    average = d["average"]

    # Obtener nombre de la variable
    variable = db['variables']
    dataVar = variable.find({'_id': ObjectId(dataReceived["variable"])})
    for dto in dataVar:
        variableName = dto["variable"]

    jsonData = {
        "parqueadero": parqueaderoAv,
        "variable": variableName,
        "average": average
    }

    result.append(jsonData)
    client.close()
    return JsonResponse(result, safe=False)


@api_view(["POST"])
def warningsFilter(request):
    client = MongoClient(settings.DB_HOST, int(settings.DB_PORT))
    db = client[settings.MONGO_DB]
    db.authenticate(settings.MLAB_USER, settings.MLAB_PASSWORD)
    warning = db['warnings']

    if request.method == "POST":
        data = JSONParser().parse(request)
        start = datetime.datetime.strptime(data["startDate"], '%Y-%m-%d %H:%M:%S')
        end = datetime.datetime.strptime(data["endDate"], '%Y-%m-%d %H:%M:%S')
        result = []
        data = warning.find({'date': {'$lt': end, '$gte': start}})
        for dto in data:
            jsonData = {
                "parqueadero": dto['parqueadero'],
                "date": dto['date']
            }
            result.append(jsonData)
        client.close()
        return JsonResponse(result, safe=False)





    