#!/usr/bin/python
# -*- coding: utf-8 -*-

# __author__ = 'efrenfuentes'


class To_Letter():
	MONEDA_SINGULAR = 'dolar'
	MONEDA_PLURAL = 'dolares'

	CENTIMOS_SINGULAR = 'centesimo'
	CENTIMOS_PLURAL = 'centesimos'

	MAX_NUMERO = 999999999999

	UNIDADES = (
		'cero',
		'uno',
		'dos',
		'tres',
		'cuatro',
		'cinco',
		'seis',
		'siete',
		'ocho',
		'nueve'
	)

	DECENAS = (
		'diez',
		'once',
		'doce',
		'trece',
		'catorce',
		'quince',
		'dieciseis',
		'diecisiete',
		'dieciocho',
		'diecinueve'
	)

	DIEZ_DIEZ = (
		'cero',
		'diez',
		'veinte',
		'treinta',
		'cuarenta',
		'cincuenta',
		'sesenta',
		'setenta',
		'ochenta',
		'noventa'
	)

	CIENTOS = (
		'_',
		'ciento',
		'doscientos',
		'trescientos',
		'cuatroscientos',
		'quinientos',
		'seiscientos',
		'setecientos',
		'ochocientos',
		'novecientos'
	)


	def convertir(self, numero):
		numero_entero = int(numero)
		if numero_entero > self.MAX_NUMERO:
			raise OverflowError('Número demasiado alto')
		if numero_entero < 0:
			return 'menos %s' % self.convertir(abs(numero))
		letras_decimal = ''
		parte_decimal = int(round((abs(numero) - abs(numero_entero)) * 100))
		if parte_decimal > 9:
			letras_decimal = 'punto %s' % self.convertir(parte_decimal)
		elif parte_decimal > 0:
			letras_decimal = 'punto cero %s' % self.convertir(parte_decimal)
		if (numero_entero <= 99):
			resultado = self.leer_decenas(numero_entero)
		elif (numero_entero <= 999):
			resultado = self.leer_centenas(numero_entero)
		elif (numero_entero <= 999999):
			resultado = self.leer_miles(numero_entero)
		elif (numero_entero <= 999999999):
			resultado = self.leer_millones(numero_entero)
		else:
			resultado = self.leer_millardos(numero_entero)
		resultado = resultado.replace('uno mil', 'un mil')
		resultado = resultado.strip()
		resultado = resultado.replace(' _ ', ' ')
		resultado = resultado.replace('  ', ' ')
		if parte_decimal > 0:
			resultado = '%s %s' % (resultado, letras_decimal)
		return resultado


	def numero_a_moneda(self, numero):
		numero_entero = int(numero)
		parte_decimal = int(round((abs(numero) - abs(numero_entero)) * 100))
		centimos = ''
		if parte_decimal == 1:
			centimos = self.CENTIMOS_SINGULAR
		else:
			centimos = self.CENTIMOS_PLURAL
		moneda = ''
		if numero_entero == 1:
			moneda = self.MONEDA_SINGULAR
		else:
			moneda = self.MONEDA_PLURAL
		letras = self.convertir(numero_entero)
		letras = letras.replace('uno', 'un')
		letras_decimal = 'con %s %s' % (self.convertir(parte_decimal).replace('uno', 'un'), centimos)
		letras = '%s %s %s' % (letras, moneda, letras_decimal)
		return letras


	def leer_decenas(self, numero):
		if numero < 10:
			return self.UNIDADES[numero]
		decena, unidad = divmod(numero, 10)
		if numero <= 19:
			resultado = self.DECENAS[unidad]
		elif numero <= 29:
			resultado = 'veinti%s' % self.UNIDADES[unidad]
		else:
			resultado = self.DIEZ_DIEZ[decena]
			if unidad > 0:
				resultado = '%s y %s' % (resultado, self.UNIDADES[unidad])
		return resultado


	def leer_centenas(self, numero):
		centena, decena = divmod(numero, 100)
		if numero == 0:
			resultado = 'cien'
		else:
			resultado = self.CIENTOS[centena]
			if decena > 0:
				resultado = '%s %s' % (resultado, self.leer_decenas(decena))
		return resultado


	def leer_miles(self, numero):
		millar, centena = divmod(numero, 1000)
		resultado = ''
		if (millar == 1):
			resultado = ''
		if (millar >= 2) and (millar <= 9):
			resultado = self.UNIDADES[millar]
		elif (millar >= 10) and (millar <= 99):
			resultado = self.leer_decenas(millar)
		elif (millar >= 100) and (millar <= 999):
			resultado = self.leer_centenas(millar)
		resultado = '%s mil' % resultado
		if centena > 0:
			resultado = '%s %s' % (resultado, self.leer_centenas(centena))
		return resultado


	def leer_millones(self, numero):
		millon, millar = divmod(numero, 1000000)
		resultado = ''
		if (millon == 1):
			resultado = ' un millon '
		if (millon >= 2) and (millon <= 9):
			resultado = self.UNIDADES[millon]
		elif (millon >= 10) and (millon <= 99):
			resultado = self.leer_decenas(millon)
		elif (millon >= 100) and (millon <= 999):
			resultado = self.leer_centenas(millon)
		if millon > 1:
			resultado = '%s millones' % resultado
		if (millar > 0) and (millar <= 999):
			resultado = '%s %s' % (resultado, self.leer_centenas(millar))
		elif (millar >= 1000) and (millar <= 999999):
			resultado = '%s %s' % (resultado, self.leer_miles(millar))
		return resultado


	def leer_millardos(self, numero):
		millardo, millon = divmod(numero, 1000000)
		return '%s millones %s' % (self.leer_miles(millardo), self.leer_millones(millon))