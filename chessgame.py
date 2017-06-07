# Door Jochem en Reitze
# test
from __future__ import print_function
from copy import deepcopy
import sys
import math

# Helper functions


# Translate a position in chess notation to x,y-coordinates
# Example: c3 corresponds to (2,5)
def to_coordinate(notation):
    x = ord(notation[0]) - ord('a')
    y = 8 - int(notation[1])
    return (x, y)


# Translate a position in x,y-coordinates to chess notation
# Example: (2,5) corresponds to c3
def to_notation(coordinates):
    (x,y) = coordinates
    letter = chr(ord('a') + x)
    number = 8 - y
    return letter + str(number)


# Translates two x,y-coordinates into a chess move notation
# Example: (1,4) and (2,3) will become b4c5
def to_move(from_coord, to_coord):
    return to_notation(from_coord) + to_notation(to_coord)


# Defining board states

# These Static classes are used as enums for:
# - Material.Rook
# - Material.King
# - Material.Pawn
# - Side.White
# - Side.Black
class Material:
    Bisshop, Knight, Pawn, Queen, Rook, King = ['b', 'n', 'p', 'q', 'r', 'k']


class Side:
    White, Black = range(0, 2)


# A chesspiece on the board is specified by the side it belongs to and the type
# of the chesspiece
class Piece:
    def __init__(self, side, material):
        self.side = side
        self.material = material
        if self.material == 'b':
            self.worth = 3
        elif self.material == 'n':
            self.worth = 3
        elif self.material == 'p':
            self.worth = 1
        elif self.material == 'q':
            self.worth = 9
        elif self.material == 'r':
            self.worth = 5
        elif self.material == 'k':
            self.worth = 200

# A chess configuration is specified by whose turn it is and a 2d array
# with all the pieces on the board
class ChessBoard:
    
    def __init__(self, turn):
        # This variable is either equal to Side.White or Side.Black
        self.turn = turn
        self.board_matrix = None

    # Getter and setter methods
    def set_board_matrix(self, board_matrix):
        self.board_matrix = board_matrix

    # Note: assumes the position is valid
    def get_boardpiece(self, position):
        (x,y) = position
        return self.board_matrix[y][x]

    # Note: assumes the position is valid
    def set_boardpiece(self, position, piece):
        (x,y) = position
        self.board_matrix[y][x] = piece
    
    # Read in the board_matrix using an input string
    def load_from_input(self, input_str):
        self.board_matrix = [[None for _ in range(8)] for _ in range(8)]
        x = 0
        y = 0
        for char in input_str:
            if y == 8:
                if char == 'W':
                    self.turn = Side.White
                elif char == 'B':
                    self.turn = Side.Black
                return
            if char == '\r':
                continue
            if char == '.':
                x += 1
                continue
            if char == '\n':
                x = 0
                y += 1
                continue 
            
            if char.isupper():
                side = Side.White
            else:
                side = Side.Black
            material = char.lower()

            piece = Piece(side, material)
            self.set_boardpiece((x,y),piece)
            x += 1

    # Print the current board state
    def __str__(self):
        return_str = ""

        return_str += "   abcdefgh\n\n"
        y = 8
        for board_row in self.board_matrix:
            return_str += str(y) + "  " 
            for piece in board_row:
                if piece == None:
                    return_str += "."
                else:
                    char = piece.material
                    if piece.side == Side.White:
                        char = char.upper()
                    return_str += char
            return_str += '\n'
            y -= 1
        
        turn_name = ("White" if self.turn == Side.White else "Black") 
        return_str += "It is " + turn_name + "'s turn\n"

        return return_str

    # Given a move string in chess notation, return a new ChessBoard object
    # with the new board situation
    # Note: this method assumes the move suggested is a valid, legal move
    def make_move(self, move_str):
        
        start_pos = to_coordinate(move_str[0:2])
        end_pos = to_coordinate(move_str[2:4])

        if self.turn == Side.White:
            turn = Side.Black
        else:
            turn = Side.White
            
        # Duplicate the current board_matrix
        new_matrix = [row[:] for row in self.board_matrix]
        
        # Create a new chessboard object
        new_board = ChessBoard(turn)
        new_board.set_board_matrix(new_matrix)

        # Carry out the move in the new chessboard object
        piece = new_board.get_boardpiece(start_pos)
        new_board.set_boardpiece(end_pos, piece)
        new_board.set_boardpiece(start_pos, None)

        return new_board

    def is_king_dead(self, side):
        seen_king = False
        for x in range(8):
            for y in range(8):
                piece = self.get_boardpiece((x,y))
                if piece != None and piece.side == side and \
                        piece.material == Material.King:
                    seen_king = True
        return not seen_king
    
    # This function should return, given the current board configuation and
    # which players turn it is, all the moves possible for that player
    # It should return these moves as a list of move strings, e.g.
    # [c2c3, d4e5, f4f8]
    def legal_moves(self):
        moves_list = []
        piece_locs = self.get_own_pieces()
        for loc in piece_locs:
            piece = self.get_boardpiece(loc)
            if piece.material == Material.King:
                moves_list.extend(self.moves_king(loc))
            elif piece.material == Material.Pawn:
                moves_list.extend(self.moves_pawn(loc))
            elif piece.material == Material.Rook:
                moves_list.extend(self.moves_rook(loc))
            elif piece.material == Material.Bisshop:
                moves_list.extend(self.moves_bisshop(loc))
            elif piece.material == Material.Knight:
                moves_list.extend(self.moves_knight(loc))
            elif piece.material == Material.Queen:
                moves_list.extend(self.moves_queen(loc))
        return moves_list

    # returns a list of all move strings for a king at location loc
    # i.e [h5h6, h5g6, h5g5, h5g4, h5h4] (king is o the side of the board)
    def moves_king(self, loc):
        moves = []
        x_dimension = [-1, 0, 1]
        y_dimension = [-1, 0, 1]
        for dx in x_dimension:
            for dy in y_dimension:
                moves.extend(self.explore_line(loc, dx, dy, one=True))
        for move in range(len(moves)-1):
            if move == to_move(loc,loc):
                del moves[moves.index(move)]
        return moves

    # returns a list of all move strings for a pawn at location loc
    # i.e. [a1a2, b1b2, c3b4]
    # this should be dependand whose turn it is.
    def moves_pawn(self, loc):
        dy = 0
        if self.turn == Side.White:
            dy = -1
        else:
            dy = 1

        moves = [to_move(loc, (loc[0], loc[1] + dy))]
        x_dimension = [-1, 1]
        for dx in x_dimension:
            new_loc = (loc[0] + dx, loc[1] + dy)
            if self.get_boardpiece(new_loc):
                moves.extend(to_move(loc, new_loc))

        return moves

    # returns a list of all move strings for a rook at location loc
    # i.e. [a1a3, a2f2, ...]
    def moves_rook(self, loc):
        moves = []
        x_dimension = [-1, 1]
        for dx in x_dimension:
            moves.extend(self.explore_line(loc, dx, 0))
        y_dimension = [-1, 1]
        for dy in y_dimension:
            moves.extend(self.explore_line(loc, 0, dy))
        return moves

    def moves_queen(self, loc):
        moves = []
        x_dimension = [-1,0,1]
        y_dimension = [-1,0,1]
        for dx in x_dimension:
            for dy in y_dimension:
                if dx == dy == 0:
                    continue
                moves.extend(self.explore_line(loc, dx, dy))
        return moves

    def moves_bisshop(self, loc):
        moves = []
        x_dimension = [-1,1]
        y_dimension = [-1,1]
        for dx in x_dimension:
            for dy in y_dimension:
                moves.extend(self.explore_line(loc, dx, dy))
        return moves

    def moves_knight(self, loc):
        moves = []
        x_dimension = [-2, -1, 1, 2]
        y_dimension = [-2, -1, 1, 2]
        for dx in x_dimension:
            for dy in y_dimension:
                if abs(dx) == abs(dy):
                    continue
                moves.extend(self.explore_line(loc, dx, dy, one=True))
        return moves

    # returns all move strings from a location by incrementing with dx and dy
    # untill the board edge, a friendly unit or an enemy unit is reached
    # one=True will cause only one increment to happen and is thus usefull for
    # kings, knights (in the future) & pawns
    def explore_line(self, loc, dx, dy, one=False):
        moves = []
        (newx, newy) = (loc[0] + dx, loc[1] + dy)
        while -1 < newx < 8 and -1 < newy < 8 and not one:
            piece = self.get_boardpiece((newx, newy))
            if piece == None:
                moves.append(to_move(loc, (newx, newy)))
            elif piece.side == self.turn:
                break
            elif piece.side != self.turn:
                moves.append(to_move(loc, (newx, newy)))
                break
            newx += dx
            newy += dy

        if -1 < newx < 8 and -1 < newy < 8 and one:
            piece = self.get_boardpiece((newx, newy))
            if piece == None:
                moves.append(to_move(loc, (newx, newy)))
            elif piece.side == self.turn:
                pass
            elif piece.side != self.turn:
                moves.append(to_move(loc, (newx, newy)))
        return moves

    def get_own_pieces(self):
        pos_w_piece = []
        for x in range(8):
            for y in range(8):
                piece = self.get_boardpiece((x,y))
                if piece and piece.side == self.turn:
                    pos_w_piece.append((x,y))
        return pos_w_piece

    # This function should return, given the move specified (in the format
    # 'd2d3') whether this move is legal
    # of legal_moves()
    def is_legal_move(self, move):
        if move in self.legal_moves():
            return True
        else:
            return False


# This static class is responsible for providing functions that can calculate
# the optimal move using minimax
class ChessComputer:

    # This method uses either alphabeta or minimax to calculate the best move
    # possible. The input needed is a chessboard configuration and the max
    # depth of the search algorithm. It returns a tuple of (score, chessboard)
    # with score the maximum score attainable and chessboardmove that is needed
    # to achieve this score.
    @staticmethod
    def computer_move(chessboard, depth, alphabeta=False):
        if alphabeta:
            inf = 99999999
            min_inf = -inf
            return ChessComputer.alphabeta(chessboard, depth, min_inf, inf)
        else:
            return ChessComputer.minimax(chessboard, depth)

    # This function uses minimax to calculate the next move. Given the current
    # chessboard and max depth, this function should return a tuple of the
    # the score and the move that should be executed
    # NOTE: use ChessComputer.evaluate_board() to calculate the score
    # of a specific board configuration after the max depth is reached
    # TODO: write an implementation for this function
    @staticmethod
    def minimax(chessboard, depth):
        best_move = ''
        best_score = 99999
        enemy = Side.White
        if chessboard.turn == Side.Black:
            enemy = Side.Black
            best_score = -best_score

        for move in chessboard.legal_moves():
            chessboard.make_move(move)
            score = ChessComputer.minimax_turn(chessboard, depth - 1, enemy)
            revert_move = move[2:4] + move[0:2]
            chessboard.make_move(revert_move)

            if enemy == Side.White and score < best_score:
                best_score = score
                best_move = move
            elif enemy == Side.Black and score > best_score:
                best_score = score
                best_move = move

        return best_score, best_move

    @staticmethod
    def minimax_turn(chessboard, depth, side):
        best_score = 99999
        enemy = Side.White
        if side == Side.White:
            enemy = Side.Black
            best_score = -best_score

        if depth == 0 or chessboard.is_king_dead(enemy):
            return ChessComputer.evaluate_board(chessboard, depth)

        chessboard.turn = side
        for move in chessboard.legal_moves():
            chessboard.make_move(move)
            score = ChessComputer.minimax_turn(chessboard, depth - 1, enemy)
            revert_move = move[2:4] + move[0:2]
            chessboard.make_move(revert_move)

            if enemy == Side.White and score < best_score:
                best_score = score
            elif enemy == Side.Black and score > best_score:
                best_score = score

        return best_score

    # This function uses alphabeta to calculate the next move. Given the
    # chessboard and max depth, this function should return a tuple of the
    # the score and the move that should be executed.
    # It has alpha and beta as extra pruning parameters
    # NOTE: use ChessComputer.evaluate_board() to calculate the score
    # of a specific board configuration after the max depth is reached
    @staticmethod
    def alphabeta(chessboard, depth, alpha, beta):
        return (0, "no implementation written")

    # Calculates the score of a given board configuration based on the 
    # material left on the board. Returns a score number, in which positive
    # means white is better off, while negative means black is better of
    @staticmethod
    def evaluate_board(chessboard, depth_left):
        score = 0
        for x in range(8):
            for y in range(8):
                piece = chessboard.get_boardpiece((x,y))
                if piece and not piece.side:
                    score += piece.worth
                if piece and piece.side:
                    score -= piece.worth
        score *= 1.1**depth_left
        return score



# This class is responsible for starting the chess game, playing and user 
# feedback
class ChessGame:
    def __init__(self, turn):
     
        # NOTE: you can make this depth higher once you have implemented
        # alpha-beta, which is more efficient
        self.depth = 4
        self.chessboard = ChessBoard(turn)

        # If a file was specified as commandline argument, use that filename
        if len(sys.argv) > 1:
            filename = sys.argv[1]
        else:
            filename = "board.chb"

        print("Reading from " + filename + "...")
        self.load_from_file(filename)

    def load_from_file(self, filename):
        with open(filename) as f:
            content = f.read()

        self.chessboard.load_from_input(content)

    def main(self):
        while True:
            print(self.chessboard)

            # Print the current score
            score = ChessComputer.evaluate_board(self.chessboard,self.depth)
            print("Current score: " + str(score))
            
            # Calculate the best possible move
            new_score, best_move = self.make_computer_move()
            
            print("Best move: " + best_move)
            print("Score to achieve: " + str(new_score))
            print("")
            self.make_human_move()

    def make_computer_move(self):
        print("Calculating best move...")
        return ChessComputer.computer_move(self.chessboard,
                self.depth, alphabeta=False)

    def make_human_move(self):
        # Endlessly request input until the right input is specified
        while True:
            if sys.version_info[:2] <= (2, 7):
                move = raw_input("Indicate your move (or q to stop): ")
            else:
                move = input("Indicate your move (or q to stop): ")
            if move == "q":
                print("Exiting program...")
                sys.exit(0)
            elif self.chessboard.is_legal_move(move):
                break
            print("Incorrect move!")

        self.chessboard = self.chessboard.make_move(move)

        # Exit the game if one of the kings is dead
        if self.chessboard.is_king_dead(Side.Black):
            print(self.chessboard)
            print("White wins!")
            sys.exit(0)
        elif self.chessboard.is_king_dead(Side.White):
            print(self.chessboard)
            print("Black wins!")
            sys.exit(0)


chess_game = ChessGame(Side.White)
chess_game.main()
