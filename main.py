from menu import menu_screen_main
from simulator import DaisyworldSimulation

def simulation_loop(config):
    sim = DaisyworldSimulation(config)
    sim.run()
def main():
    # Get configuration from the menu (map dimensions, etc.)
    config = menu_screen_main()
    simulation_loop(config)

if __name__ == '__main__':
    main()