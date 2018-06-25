#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
import math
from matplotlib.pylab import hist, show

CORRIDAS = 10
EXPERIMENTOS = 5
T_CORRIDA = 15

''' ----------------------------------- Funciones -------------------------------------------- '''

def agregar_evento(eventos, evento):
    eventos.append(evento)
    eventos.sort(key=lambda e: e.tiempo)
    return eventos

def eliminar_evento(eventos, evento):
    eventos.remove(evento)
    eventos.sort(key=lambda e: e.tiempo)
    return eventos

def generar_camion(reloj):
    #Llegada camion, frecuencia de 12 minutos y con distribución exponencial
    llegada = reloj + np.random.exponential(12) 
    camion = Camion(llegada)
    return camion

class Evento(object):
    def __init__(self, objeto, tiempo, tipo):
        self.objeto = objeto
        self.tiempo = tiempo
        self.tipo = tipo

    def __str__(self):
        return "(%d){%s - %d}" % (self.tiempo, self.objeto.__class__.__name__.title(), self.objeto.id)

class Surtidor(object):
    def __init__(self, func, nombre):
        self.id = id(self)
        self.nombre = nombre
        self.tasa_atencion = func
        self.ocupado = False

    def atender(self, eventos, camion, reloj):
        self.ocupado = True 
        camion.tiempo_atencion = reloj
        fin_atencion = reloj+self.tasa_atencion
        camion.tiempo_salida = fin_atencion
        eventos = agregar_evento(eventos, Evento(camion, reloj, "inicio_atencion"))
        eventos = agregar_evento(eventos, Evento(self, fin_atencion, "fin_atencion"))
        return eventos

    def terminar_atencion(self):
        self.ocupado = False

class Camion(object):
    def __init__(self, tiempo_llegada):
        self.id = id(self)
        self.tiempo_llegada = tiempo_llegada
        self.tiempo_atencion = 0
        self.tiempo_salida = 0

    def generar_evento_llegada(self, eventos):
        agregar_evento(eventos, Evento(self, self.tiempo_llegada, 'llegada_camion'))
        return eventos

    def tiempo_espera(self):
        return self.tiempo_atencion - self.tiempo_llegada

''' -------------------------------------------------------------------------------------------- '''

def mostrar(lista):
    print "mostrando lista, largo: ", len(lista)
    for item in lista:
        print item

def get_camionesEnCola(eventos):
    return len(filter(lambda e: es_camion(e.objeto), eventos))

def es_camion(objeto):
    return "Camion" == objeto.__class__.__name__.title()

def main():
    tams_cola = []
    f = open("4surtidores.txt", "w")
    promedios = []
    numreloj = 0
    cantatendidos = []
    camionesgenerados = 0
    camionesPerdidos = 0
    for i in range(EXPERIMENTOS):
        tiempos_medios = []
        perdidoPorCorrida = []
        generadosPorCorrida = []
        atendidosPorCorrida = []
        for j in range(CORRIDAS):
            eventos = []
            surtidor1 = Surtidor(np.random.normal(18, 4),'surtidor1')
            surtidor2 = Surtidor(np.random.exponential(15),'surtidor2')
            surtidor3 = Surtidor(np.random.exponential(16),'surtidor3')
            surtidor4 = Surtidor(np.random.normal(19, 5),'surtidor4')
            
            surtidores = [surtidor1, surtidor2, surtidor3,surtidor4]
            k = 0
            reloj = 0.0
            atendidos = 0
            generados = 0
            print ('CORRIDA Numero: ',j)
            while (reloj <= T_CORRIDA):
                numreloj = numreloj + 1
                print('reloj numero: ',numreloj,'- dentro while',reloj)
                camion = generar_camion(reloj)
                generados = generados + 1
                camionesgenerados = camionesgenerados + 1
                eventos = camion.generar_evento_llegada(eventos)
                e = eventos[k]
                if e.tipo == "llegada_camion":
                    atendido = False
                    for s in surtidores:
                        if not s.ocupado:
                            if reloj < e.objeto.tiempo_llegada:
                                eventos = s.atender(eventos, e.objeto, e.objeto.tiempo_llegada)
                            else:
                                eventos = s.atender(eventos, e.objeto, reloj)
                            eventos = eliminar_evento(eventos, e)
                            atendido = True
                            cantatendidos.append(s)
                            atendidos = atendidos + 1
                            break
                    if atendido:
                        k = 0
                        reloj = max(reloj, e.tiempo)
                        camionesEnCola = get_camionesEnCola(eventos)
                        f.write("(E: %d,C: %d) Reloj %.5f | Camiones en Cola: %d\n" % (i, j, reloj, camionesEnCola))
                        tams_cola.append(camionesEnCola)
                    else:
                        k += 1
                elif e.tipo == "inicio_atencion":
                    tiempos_medios.append(e.objeto.tiempo_espera())
                    reloj = max(reloj, e.tiempo)
                    eventos = eliminar_evento(eventos, e)
                elif e.tipo == "fin_atencion":
                    e.objeto.terminar_atencion()
                    k = 0
                    reloj = max(reloj, e.tiempo)
                    eventos = eliminar_evento(eventos, e)

            perdidoPorCorrida.append(generados - atendidos)
            generadosPorCorrida.append(generados)
            atendidosPorCorrida.append(atendidos)
        
        totalp = 0    
        for m in perdidoPorCorrida:
            totalp = totalp + m
        print 'Perdidos por Experimento/Corridas: ', perdidoPorCorrida, ' - total: ', totalp                     
        
        totalg = 0    
        for m in generadosPorCorrida:
            totalg = totalg + m
        print 'Generados por Experimento/Corridas: ', generadosPorCorrida, ' - total: ', totalg

        totala = 0    
        for m in atendidosPorCorrida:
            totala = totala + m
        print 'Atendidos por Experimento/Corridas: ', atendidosPorCorrida, ' - total: ', totala
        promedios.append(np.average(tiempos_medios))
    
    f.close()
    media = np.average(promedios)
    std = np.std(promedios)
    inferior = np.average(promedios)-(std*1.96/math.sqrt(EXPERIMENTOS))
    superior = np.average(promedios)+(std*1.96/math.sqrt(EXPERIMENTOS))
    
    camionesPerdidos = camionesgenerados - len(cantatendidos)
    
    cantsurt1 = 0 
    cantsurt2 = 0 
    cantsurt3 = 0
    cantsurt4 = 0
    for c in cantatendidos:
        print c
        if c.nombre == 'surtidor1':
            cantsurt1 = cantsurt1 + 1
        elif c.nombre == 'surtidor2':
            cantsurt2 = cantsurt2 + 1
        elif c.nombre == 'surtidor3':
            cantsurt3 = cantsurt3 + 1
        elif c.nombre == 'surtidor4':
            cantsurt4 = cantsurt4 + 1

    print "-"*20+"[Estadisticas]"+"-"*20
    print "Experimentos: %d" % (EXPERIMENTOS)
    print "Ejecuciones: %d" % (CORRIDAS)
    print "Tiempo/corrida: %d" % (T_CORRIDA)
    print "Tiempo promedio de espera en cola: %.2f" % media
    print "Desvio estandar: %.2f" % std
    print "Intervalo de confianza (95%%): %.3f < u < %.3f" % (inferior, superior)
    
    print "-"*20+"[Otros]"+"-"*20
    print "Total Camiones Generados: ", camionesgenerados
    print "Total Camiones Atendidos: ", len(cantatendidos)
    print "Total Camiones Perdidos: ", camionesPerdidos
    print "Maximo de Camiones en Cola: ", max(tams_cola)
    
    print "-"*20+"[Porcentaje de ocupacion por surtidor]"+"-"*20 
    print 'Camiones Atendidos Por Surtidor 1: ',cantsurt1, '- Ocupación: ', (cantsurt1*100)/len(cantatendidos),'%'
    print 'Camiones Atendidos Por Surtidor 2: ',cantsurt2, '- Ocupación: ', (cantsurt2*100)/len(cantatendidos),'%'
    print 'Camiones Atendidos Por Surtidor 3: ',cantsurt3, '- Ocupación: ', (cantsurt3*100)/len(cantatendidos),'%'
    print 'Camiones Atendidos Por Surtidor 4: ',cantsurt4, '- Ocupación: ', (cantsurt4*100)/len(cantatendidos),'%'

    print "Promedios"
    print promedios
    hist(promedios, 5)
    show()

if __name__ == '__main__':
    main()