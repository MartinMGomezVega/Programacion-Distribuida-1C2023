import time

#RPC
def sumar(x,y):
    return (x + y)

#RPC
def multiplicar(x,y):
 	return (x * y)

x = 2
y = 3

#print("Suma de los numeros: ", sumar(x, y))
#print("Multiplicacion de los numeros: ", multiplicar(x, y))

 
for i in range(100):
    time.sleep(1)
    resultado = multiplicar(i,i)
    print("Multiplicación de los números:", resultado)
