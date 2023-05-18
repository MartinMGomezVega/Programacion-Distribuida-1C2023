import time

def sumar(x, y):
	return (x + y)

#RPC
def multiplicar(x,y):
	return (x * y)

x = 2
y = 3

# print("Suma de los numeros: ", sumar(x, y))
# print("Multiplicacion de los numeros: ", multiplicar(x, y))

print(sumar(x,y))
for i in range(100):
	time.sleep(1)
	print("Multiplicacion de los numeros: ",multiplicar(i,i))
