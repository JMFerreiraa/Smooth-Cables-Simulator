import math
import pygame

# Definition of colours
red_range = [[210,x,x] for x in range(210,0,-10)]
red = (148,28,47)
blue = (89, 248, 232)
background = (3, 25, 30)
yellow = (255,255,0)
green = (50,200,10)
white = (255, 255, 255)
grey = (193, 207, 218)
dark_blue = (32, 164, 243)
global_rest_length = 25
black = (0, 0, 0)

# Definition of all the classes

class particle():
    def __init__(self, location, speed, acceleration, radius, fixed=False, force=[0, 0], mass=1):
        self.fixed = fixed
        self.location = location
        self.speed = [0, 0] if fixed else speed
        self.acceleration = [0, 0] if fixed else acceleration
        self.colour = "red" if fixed else "blue"
        self.force = force
        self.radius = radius
        self.mass = mass
        self._edges = []

    def getDisplacement(self, time_frame):
        # Measure the Displacement of a particle during a time frame
        return 0 if self.fixed else ((self.speed[0] * time_frame) ** 2 + (self.speed[1] * time_frame) ** 2) ** 0.5

    def update_location(self, time_frame):
        # Updates location of particles
        if not self.fixed:
            self.location = [x + y * time_frame for x, y in zip(self.location, self.speed)]

    def update_colour(self):
        # Updates color based on whether particle is fixed or not
        self.colour = "red" if self.fixed else "blue"

    def update_speed(self, time_frame):
        #Updates speeds according to acceleration, speed is reduced according to the energy_dissipation value
        threshold = 1.0e-5
        for i in range(2):
            self.speed[i] += self.aceleration[i] * time_frame
            if self.speed[i] > 0:
                self.speed[i] -= energy_dissipation * abs(self.speed[i])
            else:
                self.speed[i] += energy_dissipation * abs(self.speed[i])

            if abs(self.speed[i]) < threshold:
                self.speed[i] = 0

    def update_aceleration(self):
        #Updates acceleration according to net force
        # f = m*a
        self.aceleration = [self.force[0] / self.mass, self.force[1] / self.mass]

    def draw(self, surface):
        #Draws particle in given canvas
        return pygame.draw.circle(surface, self.colour, self.location, self.radius, )

    def swap_fixed(self):
        # Change fix property.
        self.fixed = not self.fixed
        self.update_colour()

    def update_forces(self):
        # First a down force equal to mass*G is applied, the force of gravity
        # The remaining forces on the particle are calculated and included in the .force property.
        self.force = [0,self.mass*9.8]
        for i in self._edges:
            force_edge = i.getForces()
            if self == i.end:
                other_point = i.ini
            else:
                other_point = i.end
            for e in range(2):
                if self.location[e] > other_point.location[e]:
                    force_edge[e] = -abs(force_edge[e])
                else:
                    force_edge[e] =  abs(force_edge[e])
            if i.compression():
                force_edge[0],force_edge[1] = -force_edge[0], -force_edge[1]
            self.force[0]+= force_edge[0]
            self.force[1]+= force_edge[1]

    def remove_edge(self,edge_to_clean):
        # Clean a given edge from the ._edges property
        if edge_to_clean in self._edges:
            self._edges.remove(edge_to_clean)

    def hasEdge(self, edge_to_check):
        #Verifies if this particle is connected to an edge
        return (edge_to_check in self._edges)

    def is_on_top(self, particle):
        #Checks if the given node is on top (touching) this one
        return math.sqrt(abs(self.location[0] - particle.location[0])**2 + abs(self.location[1] - particle.location[1])**2) < self.radius + particle.radius

class edge():

    def __init__(self, ini, end, rest_length=global_rest_length, stiffness = 5, colour = red):
        self.ini = ini
        self.end = end
        self.rest_length = rest_length
        self.stiffness = stiffness
        self.colour = red
        ini._edges.append(self)
        end._edges.append(self)


    def getForces(self):
        delta_x = self.ini.location[1] - self.end.location[1]
        delta_y = self.ini.location[0] - self.end.location[0]
        length = math.sqrt(delta_x**2 + delta_y**2)
        angle = math.atan2(delta_x, delta_y)
        delta_l = length - self.rest_length
        force = delta_l * self.stiffness
        force_components = [force * math.cos(angle), force * math.sin(angle)]
        return force_components

    def stretch_value(self):
        delta_x = self.ini.location[0] - self.end.location[0]
        delta_y = self.ini.location[1] - self.end.location[1]
        length = math.hypot(delta_x, delta_y)
        delta_l = length - self.rest_length
        return delta_l

    def compression(self):
        # Checks if edge is under tension or compression
        return self.stretch_value() < 0

    def draw(self,screen):
        # Draw line in given canvas
        return pygame.draw.line(screen, self.colour, [self.ini.location[0], self.ini.location[1]],\
                                [self.end.location[0],self.end.location[1]])

    def update_colour(self):

        # Update color of edge  according the strech value
        value = self.stretch_value()
        index = min(int(value/10), len(red_range)-1)
        self.colour = red_range[index]

    def distance_from_point_less_than(self, point, value):
        delta_x = self.end.location[0] - self.ini.location[0]
        delta_y = self.end.location[1] - self.ini.location[1]
        length = (delta_x**2 + delta_y**2)**0.5
        if length < value:
            return True

        number = int(2 * (length / value)) or 1
        delta_x /= number
        delta_y /= number

        x, y = self.ini.location
        for i in range(number):
            if ((x - point[0]) ** 2 + (y - point[1]) ** 2) ** 0.5 < value:
                return True
            x += delta_x
            y += delta_y
        return False

class DropdownMenu:
    def __init__(self, label, options, x, y, width, height):
        self.label = label
        self.options = options
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.selected = 0
        self.show = False
        
    def draw(self, screen, font):
        # Draw the dropdown menu button
        pygame.draw.rect(screen, grey, (self.x, self.y, self.width, self.height), 2)
        text = font.render(self.options[self.selected], True, grey)
        screen.blit(text, (self.x + 5, self.y + 5))
        
        # Draw the dropdown menu options
        if self.show:
            print("YOLOO")
            for i, option in enumerate(self.options):
                pygame.draw.rect(screen, grey, (self.x, self.y + self.height * (i + 1), self.width, self.height), 2)
                text = font.render(option, True, grey)
                screen.blit(text, (self.x + 5, self.y + self.height * (i + 1) + 5))
                
    def toggle(self):
        # Show or hide the dropdown menu options
        self.show = not self.show
        
    def select(self, option):
        # Select a dropdown menu option
        self.selected = self.options.index(option)
        self.show = False


def show_help_menu():
    msg = font.render("Shortcuts Info:", True, white)
    msg1 = font.render("CLICK + A - Append a new node to the clicked edge", True, white)
    msg2 = font.render("CLICK + D - Delete clicked node or edge", True, white)
    msg3 = font.render("CLICK + J - Put a node on top of another node and press J to connect them with an edge", True, white)
    msg4 = font.render("CLICK + C - Create a new fixed node on top of the mouse", True, white)
    msg5 = font.render("RIGHT CLICK - Change fixidity of a node", True, white)
    gameDisplay.blit(msg, [50, 100])
    gameDisplay.blit(msg1, [50, 130])
    gameDisplay.blit(msg2, [50, 160])
    gameDisplay.blit(msg3, [50, 190])
    gameDisplay.blit(msg4, [50, 220])
    gameDisplay.blit(msg5, [50, 250])


def connect_particles(initial_particle, end_particle, number, particle_list, edge_list):
    # Calculate the difference between the initial and end points
    delta_x = (end_particle.location[0] - initial_particle.location[0]) / number
    delta_y = (end_particle.location[1] - initial_particle.location[1]) / number

    # Create intermediate particles and append to the particle_list
    particles = []
    for i in range(number - 1):
        new_point = [initial_particle.location[0] + delta_x * (i + 1), initial_particle.location[1] + delta_y * (i + 1)]
        new_part = particle(new_point, [0, 0], [0, 0], 8)
        particles.append(new_part)
        particle_list.append(new_part)

    # Connect the intermediate particles and append to the edge_list
    for i in range(len(particles) - 1):
        edge_list.append(edge(particles[i], particles[i + 1]))

    # Connect the initial particle and the end particle, and append to the edge_list
    if number >= 2:
        edge_list.append(edge(initial_particle, particles[0]))
        edge_list.append(edge(particles[-1], end_particle))
    else:
        edge_list.append(edge(initial_particle, end_particle))



def game_loop():

    global particles, background, mouse_pos, moving_particles, configuration_mode, red, blue, yellow, grey, dark_blue, selected_edges,\
        edges, new_edge_nodes,shortcuts, red_range

    for row in range(rows):
        for col in range(columns):
            loc = [((display_dimension[1]/columns) * (col + 1)) - display_dimension[1]/(columns*2), ((display_dimension[0]/rows) * (row + 1)) - display_dimension[0]/(rows*2)]
            new_particle =  particle(loc,[0,0],[0,0],8)
            new_particle.colour = green
            if(row == 0 or row == rows - 1):
                new_particle.swap_fixed()
            new_edge_nodes.append(new_particle)
            new_particle.update_colour()
    
            if row > 0:
                connect_particles(new_edge_nodes[-1], new_edge_nodes[-columns - 1], 1, particles, edges)
            if col > 0:
                connect_particles(new_edge_nodes[-1], new_edge_nodes[-2], 1, particles, edges)

    for node in new_edge_nodes:
        if node not in particles:
            particles.append(node)
    new_edge_nodes = []
    font = pygame.font.SysFont(None,  20)
    configuration_text = font.render("Configuration", True, background)
    shortcuts_text = font.render("Shortcuts", True, background)

    while True:

        configuration_button_width = 100
        configuration_button_height = 50
        configuration_button_x = (display_dimension[0]) - (configuration_button_width) - 10
        configuration_button_y = 0 + 10
        configuration_visible = True
        gameDisplay.fill(background)

        pygame.draw.rect(gameDisplay, grey, (configuration_button_x, configuration_button_y, configuration_button_width, configuration_button_height))        
        configuration_text_rect = configuration_text.get_rect()
        configuration_text_rect.center = (configuration_button_x + (configuration_button_width // 2), configuration_button_y + (configuration_button_height // 2))
        gameDisplay.blit(configuration_text, configuration_text_rect)

        pygame.draw.rect(gameDisplay, grey, (10, 10, configuration_button_width, configuration_button_height))        
        shortcuts_text_rect = shortcuts_text.get_rect()
        shortcuts_text_rect.center = (10 + (configuration_button_width // 2), 10 + (configuration_button_height // 2))
        gameDisplay.blit(shortcuts_text, shortcuts_text_rect)

        
        system_getDisplacement = 0
        if shortcuts:
            if(configuration_mode):
                configuration_text = font.render("Simulation", True, background)
                shortcuts_text = font.render("Configuration", True, background)
            else:
                configuration_text = font.render("Configuration", True, background)
                shortcuts_text = font.render("Simulation", True, background)

            show_help_menu()
        elif not configuration_mode:
            configuration_text = font.render("Configuration", True, background)
            shortcuts_text = font.render("Shortcuts", True, background)
            for i in range(len(particles)):
                if particles[i].fixed == False and particles[i] not in moving_particles and not shortcuts:

                    # If not in configuration mode or in shortcuts, all the particles that are not fixed and are not selected
                    # are updated.

                    particles[i].update_forces()
                    particles[i].update_aceleration()
                    particles[i].update_speed(time_step)
                    system_getDisplacement += particles[1].getDisplacement(time_step)
                    particles[i].update_location(time_step)
                particles[i].draw(gameDisplay)
            for i in edges:
                if i not in selected_edges:
                    i.update_colour()
                i.draw(gameDisplay)
        elif configuration_mode:
            configuration_text = font.render("Simulation", True, background)
            shortcuts_text = font.render("Shortcuts", True, background)
            for i in particles:
                i.draw(gameDisplay)
            for i in edges:
                i.draw(gameDisplay)

        for event in pygame.event.get():
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN and configuration_button_x <= mouse_x <= configuration_button_x + configuration_button_width and configuration_button_y <= mouse_y <= configuration_button_y + configuration_button_height:
                # Enter configuration mode
                new_edge_nodes = []
                configuration_mode  = not configuration_mode
                shortcuts = False
                if not configuration_mode:
                    red_range = [[210,x,x] for x in range(210,0,-10)]
                    red = (148,28,47)
                    blue = (89, 248, 232)
                    background = (3, 25, 30)
                    yellow = (255,255,0)
                    white = (255, 255, 255)
                    grey = (193, 207, 218)
                    dark_blue = (32, 164, 243)
                if configuration_mode:
                    red = (200, 200, 200)
                    blue = (80, 80, 80)
                    background = (3, 25, 30)
                    yellow = (255, 255, 0)
                    red_range = [[x, x, x] for x in range(255, 150, -10)]
                for i in particles:
                    i.update_colour()
                for i in edges:
                    i.update_colour()
            elif  event.type == pygame.MOUSEBUTTONDOWN and 10 <= mouse_x <= 10 + configuration_button_width and 10 <= mouse_y <= 10 + configuration_button_height:
                shortcuts = not shortcuts
                if shortcuts:
                    background = (3, 25, 30)
                else:
                    background = (3, 25, 30)
            elif event.type == pygame.MOUSEBUTTONDOWN and configuration_mode==False and shortcuts==False:
                mouse_pos = pygame.mouse.get_pos()

                # Check mouse position and select particles and edges accordingly

                for i in particles:
                    if abs(i.location[0] - mouse_pos[0]) < i.radius and abs(i.location[1] - mouse_pos[1]) < i.radius:
                        i.colour = dark_blue
                        moving_particles.append(i)
                        break
                for edge_check in edges:
                    if edge_check.distance_from_point_less_than(mouse_pos, 5):
                        edge_check.colour = dark_blue
                        selected_edges.append(edge_check)
            elif event.type == pygame.MOUSEBUTTONDOWN and configuration_mode==True and shortcuts==False:
                #IN DEVELOPMENT! IN DEVELOPMENT! IN DEVELOPMENT! IN DEVELOPMENT! IN DEVELOPMENT! IN DEVELOPMENT!
                mouse_pos= pygame.mouse.get_pos()
            last_post = mouse_pos
            if event.type == pygame.MOUSEMOTION and shortcuts==False:

                #Move selected particles following mouse movement

                event.pos
                movement = [last_post[0] - event.pos[0], last_post[1] - event.pos[1]]
                for part in moving_particles:
                    part.location[0] -= movement[0]
                    part.location[1] -= movement[1]
                mouse_pos = event.pos
            if event.type == pygame.MOUSEBUTTONUP:
                for i in moving_particles:
                    i.update_colour()
                for i in selected_edges:
                    i.update_colour()
                moving_particles = []
                selected_edges = []
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and shortcuts==False:
                #If right click change particles fixidity.
                for i in particles:
                    if abs(i.location[0] - mouse_pos[0]) < i.radius and abs(i.location[1] - mouse_pos[1]) < i.radius:
                        i.fixed = not i.fixed
                        i.update_colour()
            if event.type == pygame.KEYDOWN and (event.key == 97 or event.key == 65) and shortcuts==False: #D KEY
                mouse_pos= pygame.mouse.get_pos()
                for i in selected_edges:
                    particlepoints = []
                    for u in particles:
                        if(u.hasEdge(i)):
                            particlepoints.append(u)
                        u.remove_edge(i)
                    if i in edges:
                        edges.remove(i)
                    connect_particles(particlepoints[0], particlepoints[1], 2, particles, edges)                    
            if event.type == pygame.KEYDOWN and (event.key == 100 or event.key == 68) and shortcuts==False: #A KEY
                #Delete  selected edges and particles
                for i in moving_particles:
                    for u in i._edges:
                        if u in edges:
                            edges.remove(u)
                        for x in particles:
                            if x is not i:
                                x.remove_edge(u)
                    if i in particles:
                        particles.remove(i)
                for i in selected_edges:
                    for u in particles:
                        u.remove_edge(i)
                    if i in edges:
                        edges.remove(i)
            if event.type == pygame.KEYDOWN and (event.key == 106 or event.key == 74) and shortcuts==False: #J KEY    
                for i in moving_particles:
                    particles_to_connect = [i,]
                    for u in particles:
                        if(i.is_on_top(u) and i != u):
                            connect_particles(u,i,1,particles, edges)
            if event.type == pygame.KEYDOWN and (event.key == 99 or event.key == 67) and shortcuts==False: #C KEY
                loc = [mouse_pos[0], mouse_pos[1]]
                new_particle =  particle(loc,[0,0],[0,0],8)
                new_particle.swap_fixed()
                new_particle.update_colour()
                particles.append(new_particle)
                
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        pygame.display.update()
        clock.tick()



# Initiate pygame classes
pygame.init()
pygame.font.init()
clock = pygame.time.Clock()
display_dimension = (1000, 1000)

display_half_width = int(display_dimension[0]/2)
display_half_height = int(display_dimension[1] / 2)


gameDisplay = pygame.display.set_mode((display_dimension[0], display_dimension[1]))
pygame.display.set_caption("Smooth Cables Simulator")

font = pygame.font.SysFont(None,  25)

particles=[]
edges=[]


# Main game logic

configuration_mode =  False
shortcuts = False
time_step = 0.04
energy_dissipation = 0.04
mouse_pos = [0, 0]
moving_particles = []
selected_edges = []
new_edge_nodes = []
rows = 5
columns = 5


# Main loop will not start until enter key is pressed

start_button_width = 200
start_button_height = 100
start_button_x = (display_dimension[0] / 2) - (start_button_width / 2)
start_button_y = (display_dimension[1] / 2) - (start_button_height / 2)



running = True
pygame.event.clear()
options = ["Option 1", "Option 2", "Option 3"]
dropdown = DropdownMenu("config file", options, 50, 50, 100, 50)

while running:

    gameDisplay.fill(background)
    pygame.draw.rect(gameDisplay, blue, (start_button_x, start_button_y, start_button_width, start_button_height))
    # render the text on the button
    text = font.render("Start Simulation!", True, background)
    text_rect = text.get_rect()
    text_rect.center = (start_button_x + (start_button_width // 2), start_button_y + (start_button_height // 2))
    gameDisplay.blit(text, text_rect)
    credis_text = font.render("Made by: João Sá! (THIS IS A WORK IN PROGRESS!)", True, white)
    credis_text1 = font.render("https://github.com/JMFerreiraa", True, white)
    text_rect = credis_text.get_rect()
    text_rect.center = (start_button_x + (start_button_width // 2), start_button_y + (start_button_height // 2) + start_button_height)
    gameDisplay.blit(credis_text, text_rect)
    text_rect = credis_text1.get_rect()
    text_rect.center = (start_button_x + (start_button_width // 2), start_button_y + (start_button_height // 2) + start_button_height+ 50)
    gameDisplay.blit(credis_text1, text_rect)



    dropdown.draw(gameDisplay, font)
    pygame.display.update()
    event = pygame.event.wait()
    if event.type == pygame.QUIT:
        running = False
    elif event.type == pygame.MOUSEBUTTONDOWN:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if start_button_x <= mouse_x <= start_button_x + start_button_width and start_button_y <= mouse_y <= start_button_y + start_button_height:
            button_visible = False
            game_loop()
        elif dropdown.x < mouse_x < dropdown.x + dropdown.width and dropdown.y < mouse_y < dropdown.y + dropdown.height:
            dropdown.toggle()
        # Check if a dropdown menu option was clicked
        elif dropdown.show:
            for i, option in enumerate(dropdown.options):
                if dropdown.x < mouse_x < dropdown.x + dropdown.width and dropdown.y + dropdown.height * (i + 1) < mouse_y < dropdown.y + dropdown.height * (i + 1) + dropdown.height:
                    dropdown.select(option)

    pygame.display.update()

pygame.quit()
quit()