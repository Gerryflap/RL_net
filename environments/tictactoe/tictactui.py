from agents.tui_agent import TUIAgent
from environments.tictactoe.tictactoeenv import TTTEnvironment, TTTAction, TTTState

agent = TUIAgent(('localhost', int(input("Server port: "))), input("Name: "), TTTEnvironment(), lambda x: TTTAction(int(x)))
agent.run()