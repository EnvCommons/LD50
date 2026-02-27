from openreward.environments import Server

from ld50predict import LD50Predict

if __name__ == "__main__":
    server = Server([LD50Predict])
    server.run()
