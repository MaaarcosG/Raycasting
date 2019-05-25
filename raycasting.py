# importamos las librerias necesarias
import math
import random
import itertools
import pygame
# importamos las tuplas
from collections import namedtuple

# tuplas que guardaran la informacion.
Information = namedtuple("Information", ["x", "y"])
WallInformation = namedtuple("WallInformation", ["size_arma", "height"])

# inicializamos la libreria pygame
pygame.init()
# le damos un valor a la ventana
pygame.display.set_mode((1200, 600))

# calculamos el tamaño para cada una de las texturas
condicion_back = 1200*((2*math.pi)/(math.pi*0.4))
background = int(condicion_back), 600

background_sky = pygame.image.load("./sprites/bacg.png").convert()

images = {
    'texture':  pygame.image.load("./sprites/wood.png").convert(),
    'tex' : pygame.image.load("./sprites/redbrick.png").convert(),
    'arma' : pygame.image.load("./sprites/hand.png").convert_alpha(),
    'backg' : pygame.transform.smoothscale(
        background_sky,
        background
    )
}

enemy = [
    {
        "x": 100,
        "y": 200,
        "texture": pygame.image.load("./sprites/enemy.png").convert
    }
]

# clase para generar de forma random el mapa
class Mapa(object):
    def __init__(self, size):
        # tamaño del mapa
        self.size = size
        self.pared = self.randomize()
        # llamamos al a clase imagen para obtener cada el tamaño de la imagen
        self.cielo = Imagen(images["backg"])
        self.textura = Imagen(images["texture"])
        self.light = 0

    def get(self, x, y):
        # colision de los sprint
        point = (int(math.floor(x)), int(math.floor(y)))
        return self.pared.get(point, -1)

    # mapa para generar de forma random el mundo
    def randomize(self):
        gmap = {}
       
        # itertools para tener un ciclo, calcula el producto cartesiano
        for coord in itertools.product(range(self.size), repeat=2):
            if random.random()<0.2:
                # tamaños random para las paredes
                gmap[coord] = random.choice((1, 0.9, 1.6))
        return gmap
        '''
        # ciclo para el random del mapa
        coordenadas = {
            coord : random.random()<0.3
            for coord in itertools.product(range(self.size), repeat=2)
        }
        # debug --> print(coordenadas)
        return coordenadas
        '''

    def raycast(self, point, angle, ranges):
        # informacion del raycasting que se guarda en una tupla
        info = Information(math.sin(angle), math.cos(angle))
        origen = Point(point)
        ray = [origen]
        # ciclo que raycastea los objetos
        while (origen.height <= 0) and (origen.distance <= ranges):
            dist = origen.distance
            # posiciones de los valores x e y
            stepX = origen.step(info.x, info.y)
            # variable invert para invertir los datos de la posicion del jugador
            stepY = origen.step(info.y, info.x, invert=True)
            if (stepX.length < stepY.length):
                # posicion en el mapa x
                ns = stepX.inspect(info, self, 1, 0, dist, stepX.y)
                # debug --> print(ns)
            else:
                # posicion en el mapa y
                ns = stepY.inspect(info, self, 0, 1, dist, stepY.x)
            # añadimos a la lista los valores obtenidos
            ray.append(ns)
            origen = ns
            # ----> debug print(origen)
        return ray

    # actualizamos los valores del mapa
    def update(self, dt):
        if self.light > 0:
            self.light = max(self.light-10*dt, 0)
        elif random.random()*5 < dt:
            self.light = 2

class Player(object):
    def __init__(self, x, y, direction):
        # valores de los ejes
        self.x = x
        self.y = y
        # la direccion en la cual el jugador se mueve
        self.direction = direction
        # velocidad del jugador
        self.speed = 3
        # velocidad en la cual podra girar el jugador en 180°
        self.rotateSpeed = (2*math.pi)/2
        # continen el sprint del arma
        self.weapon = Imagen(images["arma"])
        # colocacion del arma
        self.positionWeapon = 0

    def rotate(self, angle):
        self.direction = (self.direction + angle + (2*math.pi)) % (self.rotateSpeed*2)

    def walk(self, distance, gmap):
        # valores para encontrar el movimiento entre los ejes x e y
        dx = math.cos(self.direction)*distance
        dy = math.sin(self.direction)*distance
        if gmap.get((self.x+dx), self.y) <= 0:
            self.x += dx
        if gmap.get(self.x, (self.y+dy)) <= 0:
            self.y += dy
        # mediante caminamos la posicion del arma va cambiando
        self.positionWeapon += distance

    def update(self, keys, dt, gmap):
        # Ejecutamos cada uno de los comandos de pygame
        if keys[pygame.K_a]:
            self.rotate(-self.rotateSpeed*dt)
        if keys[pygame.K_d]:
            self.rotate(self.rotateSpeed*dt)
        if keys[pygame.K_w]:
            self.walk(self.speed*dt, gmap)
        if keys[pygame.K_s]:
            self.walk(-self.speed*dt, gmap)

# clase que hace el puntero del juego
class Point(object):
    def __init__(self, point, length=None):
        # valores en x e y
        self.x = point[0]
        self.y = point[1]
        # variables para el jugador
        self.height = 0
        self.distance = 0
        self.shading = None
        self.length = length

    # funcion establece los pasos del jugador
    def inspect(self, info, gmap, changeX, changeY, distance, offset):
        # valores de las divisiones en los diferentes ejes
        # evitamos los numeros negativos en la coordenada x
        if info.y<0:
            dx = changeX
        else:
            dx = 0
        # evitamos los numeros negativos en la coordenada y
        if info.x<0:
            dy = changeY
        else:
            dy = 0
        # tamaño de la ventana
        self.height = gmap.get(self.x-dx, self.y-dy)
        # limite para la distancia de los pasos
        self.distance = distance+self.length
        # funcion para ir cambiando los valores de x e y
        if changeX:
            if info.y<0:
                self.shading = 3
            else:
                self.shading = 0
        else:
            if info.x<0:
            	self.shading = 3
            else:
            	self.shading = 1

        # limite del mapa
        self.offset = offset-math.floor(offset)
        return self

    # funcion para controlar los pasos del jugador
    def step(self, move, movement, invert=False):
        # try para evitar que truene el ciclo
        try:
            # asignamos valores predeterminadoos
            if invert:
                x, y = (self.y , self.x)
            else:
                x, y = (self.x,self.y)
            # formamos las paredes
            # condicion para examinar cada uno de los movimientos
            if (movement > 0):
                dx = math.floor(x+1)-x
            else:
                dx = math.ceil(x-1)-x
            # divison en cero
            division_cero = move/movement
            # valor de la distancia en y
            dy = dx*(division_cero)
            # bindramos solo un valor para cada coordenada
            if invert:
                # condicion para invertir cada uno de los valores
                valorX = y+dy
                valorY = x+dx
            else:
                valorX = x+dx
                valorY = y+dy
            # hipotenusa del objeto
            length = math.hypot(dx, dy)
        # evitamos choques con la pared
        except ZeroDivisionError:
            # si los valores de las divison son iguales que no se
            # ejecute, asi evitamos que el juego se trabe
            valorX = valorY = None
            length = float("inf")
        vx, vy = valorX, valorY

        # se retorna los valores para evitar el choque
        return Point((vx, vy), length)

# clase para controlar el movimiento de la camara
class Camera(object):
    def __init__(self, screen, resolution):
        self.screen = screen
        # get_size_arma ---> funcion que obtiene el tamaño de la camara
        self.width, self.height = self.screen.get_size()
        self.resolution = float(resolution)

    # funcion para renderizar cada uno de los objetos que se encuentren en la ventana
    def render(self, player, gmap):
        self.limpiando_movimiento(player.direction, gmap.cielo, gmap.light)
        self.columnasRender(player, gmap)
        self.armaRender(player.weapon, player.positionWeapon)

    # renderizamos cada uno de las columnas
    def  columnasRender(self, player, gmap):
        for column in range(int(self.resolution)):
            angle = (math.pi*0.4) * (column/self.resolution-0.5)
            # damos los puntos a cada eje
            point = player.x, player.y
            # le damos los valores de las colum
            ray = gmap.raycast(point, player.direction+angle, 8)
            self.renderC(column, ray, angle, gmap)

    # renderiza cada una de las columnas
    def renderC(self, column, ray, angle, gmap):
        left = int(math.floor(column*(self.width/self.resolution)))
        for i in range(len(ray)-1, -1, -1):
            step = ray[i]
            if (step.height > 0):
                # le damos texturas al mapa
                texture = gmap.textura
                # obtenemos el tamaño de la columan para texturas
                width = int(math.ceil((self.width/self.resolution)))
                # debug ---> print (width)
                textureX = int(texture.width*step.offset)
                # obtenemos una pared para ejemplo de la projeccion
                wall = self.project(step.height, angle, step.distance)
                # funciones para obtener texturas y lograrlas cambiar
                imagenDir = pygame.Rect(textureX, 0, 1, texture.height)
                cambiarImagen = texture.image.subsurface(imagenDir)
                # escala para cada textura de la columna
                scaleR = pygame.Rect(left, wall.size_arma, width, wall.height)
                escamed = pygame.transform.scale(cambiarImagen, scaleR.size)
                # le damos los valores para la ventana
                self.screen.blit(escamed, scaleR)

    # funcion para dibujar el cielo
    def limpiando_movimiento(self, direction, cielo, luz):
        left = -cielo.width * (direction/(2*math.pi))
        # damos los valores a la ventana para imprimirlo
        self.screen.blit(cielo.image, (left,0))
        # condicion para que el mapa se adapta a la ventana
        condition = cielo.width-self.width
        if (left<condition):
            self.screen.blit(cielo.image, (left+cielo.width,0))
        # evitamos los numeros negativos
        if (luz > 0):
            renderer = 255 * min(1, (luz*1))
            # debug --> print(render)

    def armaRender(self, weapon, positionWeapon):
        arma = ((1200+600)/1200.0)*6
        # valores para cada posicion del arma
        arma_x = math.cos(positionWeapon*2) * arma
        arma_y = math.sin(positionWeapon*4) * arma

        left = self.width * 0.66 + arma_x
        size_arma = self.height * 0.6 + arma_y
        self.screen.blit(weapon.image, (left, size_arma))

    # funcion para encontrar la projeccion del Jugador
    def project(self, height, angle, distance):
        # valor de z
        z = max(distance*math.cos(angle), 0.2)
        tamanoPared = self.height * (height/float(z))
        maximus = (self.height/float(2)) * (1+1/float(z))
        # condion para mostrar la informacion
        con = maximus-tamanoPared
        return WallInformation(con, int(tamanoPared))

    '''
    def cast_ray(self, a):
        d = 0
        while True:
            #x = self.player["x"] + d*cos(a)
            self.player.walk()
            y = self.player["y"] + d*sin(a)

            i = int(x/50)
            j = int(y/50)

            if self.map[j][i] != ' ':
                hitx = x - i*50
                hity = y - j*50

            if 1 < hitx < 49:
                maxhit = hitx
            else:
                maxhit = hity
                tx = int(maxhit * 128 / 50)

                return d, self.map[j][i], tx

            self.point(int(x), int(y), (255, 255, 255))
            d += 1
    '''
class Imagen(object):
    def __init__(self, image):
        self.image = image
        # le damos tamaño a la imagen
        self.width, self.height = self.image.get_size()

def main():
    # funciones que controlaran cada uno de los elementos
    loop = False
    # llave para controlar los movimientos
    llave = pygame.key.get_pressed()
    screen = pygame.display.get_surface()
    camera = Camera(screen, 300)
    gmap = Mapa(40)
    # variable que muestra donde aparecera el jugador
    jugadores = Player(16, 16, math.pi/3)
    tiempo = pygame.time.Clock()
    dt = tiempo.tick(60.0)/1000

    # debug --> print(dt)
    while not loop:
        # funciones para controlar las funciones de pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = True
            elif event.type  in (pygame.KEYDOWN, pygame.KEYUP):
                llave = pygame.key.get_pressed()

        # llamamos cada uno de los jugadores
        gmap.update(dt)
        jugadores.update(llave, dt, gmap)
        camera.render(jugadores, gmap)
        dt = tiempo.tick(60.0)/1000
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
