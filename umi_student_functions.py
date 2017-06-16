#!python2
# By Jochem and Reitze (110007729 and 00000000) from group C on 6-16-17.

from __future__ import division, print_function
from umi_parameters import UMI_parameters
from umi_common import *
import math
import numpy as np
from visual import *
# Specifications of UMI
# Enter the correct details in the corresponding file (umi_parameters.py).
UMI = UMI_parameters()


def apply_inverse_kinematics(x, y, z, gripper):
    ''' Computes the angles, given some real world coordinates
        :param float x: cartesian x-coordinate
        :param float y: cartesian y-coordinate
        :param float z: cartesian z-coordinate

        :return: Returns the a tuple containing the position and angles of the robot-arm joints.
    '''

    # All formula's are out of the student manual.
    c = ((math.pow(x, 2) + math.pow(z, 2) -
                math.pow(UMI.upper_length, 2) - math.pow(UMI.lower_length, 2))
                / (2 * UMI.upper_length * UMI.lower_length))

    if c > 1:  # Cancel if the coordinates are out of reach.
        print("Can't reach coordinates")
        return 0, 0, 0, 0, 0

    s = math.sqrt(1 - math.pow(c, 2))

    riser_position = y + UMI.total_arm_height
    elbow_angle = degrees(math.atan2(s, c))
    shoulder_angle = degrees(math.atan2(z, x) -
                     math.atan2(UMI.lower_length * s,
                                UMI.upper_length + UMI.lower_length * c))
    wrist_angle = -(elbow_angle + shoulder_angle)  # Get the wrist straight.

    if False:  # These were used for debugging purposes.
        print(x, y, z)
        print(shoulder_angle, elbow_angle)
        print()
        print(x, z)

    return riser_position, shoulder_angle, elbow_angle, wrist_angle, gripper


def board_position_to_cartesian(chessboard, position):
    ''' Convert a position between [a1-h8] to its cartesian coordinates in frameworld coordinates.

        You are not allowed to use the functions such as: frame_to_world.
        You have to show actual calculations using positions/vectors and angles.

        :param obj chessboard: The instantiation of the chessboard that you wish to use.
        :param str position: A position in the range [a1-h8]

        :return: tuple Return a position in the format (x,y,z)
    '''
    # Get the local coordinates for the tiles on the board in the 0-7 range.
    (row, column) = to_coordinate(position)
    (x, _, z) = chessboard.get_position()  # Get the transformation

    # Calculate the eucledian distance from h8 to the field.
    row_len = chessboard.chessboard_size - chessboard.field_size * row
    column_len = chessboard.chessboard_size - chessboard.field_size * column
    total_len = sqrt(row_len*row_len + column_len*column_len)

    # Calculate the angle between row H and the eucledian distance.
    ang = -chessboard.get_angle_radians() + math.atan2(row_len, column_len)

    # Get the x and z dimensions with the sin and cos.
    x_dim = total_len * math.sin(ang)
    z_dim = total_len * math.cos(ang)

    world_x = x + x_dim  # Add the transformation.
    world_y = chessboard.mplhght
    world_z = z + z_dim

    if False:  # These were used for debugging purposes.
        print(row, column)
        print(chessboard.get_angle_degrees(), degrees(math.atan2(row_len, column_len)))
        print(world_x, world_y, world_z)
        print()

    return world_x, world_y, world_z


def high_path(chessboard, from_pos, to_pos):
    '''
    Computes the high path that the arm can take to move a piece from one place on the board to another.
    :param chessboard: Chessboard object
    :param from_pos: [a1-h8]
    :param to_pos: [a1-h8]
    :return: Returns a list of instructions for the GUI.
    '''
    sequence_list = []
    # We assume that 20 centimeter above the board is safe.
    safe_height = 0.2
    # We assume that 10 centimeter above the board is "low".
    low_height = 0.1

    # Get the coordinates.
    (from_x, from_y, from_z) = board_position_to_cartesian(chessboard, from_pos)
    (to_x, to_y, to_z) = board_position_to_cartesian(chessboard, to_pos)

    # Define half_piece height (you want to grab the middle of a piece, so get the height of the piece on a position.)
    # (*cough* this data might be stored in a chessboard *cough*)
    piece_name = chessboard.pieces[from_pos][1]
    piece_height = chessboard.pieces_height[piece_name]
    # You might need if statements around this, but you have to fill this variable regardlessly.
    half_piece_height = 0.5*piece_height+to_y # ????

    REPLACE_THIS_WITH_YOUR_OWN_CODE = "wrong"
    # Hover above the first field on SAFE height:
    sequence_list.append(apply_inverse_kinematics(from_x, safe_height, from_z, chessboard.field_size))
    # Hover above the first field on LOW height:
    sequence_list.append(apply_inverse_kinematics(from_x, low_height, from_z, chessboard.field_size))
    # Hover above the first field on half of the piece height:
    sequence_list.append(apply_inverse_kinematics(from_x, half_piece_height, from_z, chessboard.field_size))
    # make the gripper fit the piece:
    sequence_list.append(apply_inverse_kinematics(from_x, half_piece_height, from_z, 0.01))

    ################################################ unfinished ###############
    # Give instruction to GUI to pickup piece
    sequence_list.append(["GUI", "TAKE", from_pos])
    # Hover above the first field on SAFE height (Keep the gripper closed!!):
    sequence_list.append(apply_inverse_kinematics(from_x, safe_height, from_z, 0.01))
    # Move to new position on SAFE height
    sequence_list.append(apply_inverse_kinematics(to_x, safe_height, to_z, 0.01))
    # Hover above the first field on LOW height:
    sequence_list.append(apply_inverse_kinematics(to_x, low_height, to_z, 0.01))
    # Hover above the first field on half of the piece height:
    sequence_list.append(apply_inverse_kinematics(to_x, half_piece_height, to_z, 0.01))
    # Give instruction to GUI to drop piece
    sequence_list.append(["GUI", "DROP", to_pos])
    # open the gripper
    sequence_list.append(apply_inverse_kinematics(to_x, half_piece_height, to_z, chessboard.field_size))
    # Move to new position on SAFE height (And open the gripper)
    sequence_list.append(apply_inverse_kinematics(to_x, safe_height, to_z, chessboard.field_size))
    return sequence_list


def move_to_garbage(chessboard, from_pos):
    '''
        Computes the high path that the arm can take to move a piece from one place on the board to the garbage location.
        :param chessboard: Chessboard object
        :param from_pos: [a1-h8]
        :return: Returns a list of instructions for the GUI.
    '''
    sequence_list = []
    # We assume that 20 centimeter above the board is safe.
    safe_height = 0.2
    # We assume that 10 centimeter above the board is "low".
    low_height = 0.1
    drop_location = "j5"

    # Define half_piece height (you want to grab the middle of a piece, so get the height of the piece on a position.)
    piece_name = chessboard.pieces[from_pos][1]
    piece_height = chessboard.pieces_height[piece_name]
    # You might need if statements around this, but you have to fill this variable regardlessly.
    half_piece_height = 0.5*piece_height # ????
    # Get the coordinates.
    (from_x, from_y, from_z) = board_position_to_cartesian(chessboard, from_pos)
    (to_x, to_y, to_z) = board_position_to_cartesian(chessboard, drop_location)

    # Hover above the first field on SAFE height:
    sequence_list.append(apply_inverse_kinematics(from_x, safe_height, from_z, chessboard.field_size))
    # Hover above the first field on LOW height:
    sequence_list.append(apply_inverse_kinematics(from_x, low_height, from_z, chessboard.field_size))
    # Hover above the first field on half of the piece height:
    sequence_list.append(apply_inverse_kinematics(from_x, half_piece_height, from_z, chessboard.field_size))


    # Give instruction to GUI to pickup piece
    sequence_list.append(["GUI", "TAKE", from_pos])
    # Hover above the first field on SAFE height (Keep the gripper closed!!):
    sequence_list.append(apply_inverse_kinematics(from_x, safe_height, from_z, 0.5*half_piece_height))
    # Move to new position on SAFE height
    sequence_list.append(apply_inverse_kinematics(to_x, safe_height, to_z, 0.5*half_piece_height))
    # Hover above the first field on LOW height:
    sequence_list.append(apply_inverse_kinematics(to_x, low_height, to_z, 0.5*half_piece_height))
    # Hover above the first field on half of the piece height:
    sequence_list.append(apply_inverse_kinematics(to_x, half_piece_height, to_z, 0.5*half_piece_height))
    # Give instruction to GUI to drop piece
    sequence_list.append(["GUI", "DROP", drop_location])
    # Move to new position on SAFE height (And open the gripper)
    sequence_list.append(apply_inverse_kinematics(to_x, safe_height, to_z, chessboard.field_size))

    return sequence_list
