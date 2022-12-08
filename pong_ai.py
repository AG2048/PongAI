def pong_ai(paddle_frect, other_paddle_frect, ball_frect, table_size):
    """
    Determine where the paddle should move to, given relevant information of the board
    All objects are rectangles with positions referencing the top left corner.
        0             x
        |------------->
        |
        |
        |
    y   v
    :param paddle_frect: paddle_frect.pos = [x, y], paddle_frect.size = [x_size, y_size]
    :param other_paddle_frect: other_paddle_frect.pos = [x, y], other_paddle_frect.size = [x_size, y_size]
    :param ball_frect: ball_frect.pos = [x, y], ball_frect.size = [x_size, y_size]
    :param table_size: [x_size, y_size]
    :return: "up" or "down"
    """
    # Memorize previous position to calculate velocity
    if "previous_position" not in dir(pong_ai):
        pong_ai.previous_position = [0, 0]

    # Requirement of team name
    pong_ai.team_name = "Andy Gong"

    # Gather ball information: centre position and velocity.
    ball_diameter = ball_frect.size[0]
    ball_centre = [ball_frect.pos[0]+ball_diameter/2, ball_frect.pos[1]+ball_diameter/2]
    ball_velocity = [ball_centre[0]-pong_ai.previous_position[0], ball_centre[1]-pong_ai.previous_position[1]]
    pong_ai.previous_position = ball_centre[:]  # Update previous_position

    # Determine at what x-coordinate will the ball's centre be when it hits the paddle
    # Note:
    #     consider both possible location of the paddle (left and right)
    #     for impact x-pos, consider the ball's own radius affecting impact position
    paddle_hit_x_pos = paddle_frect.pos[0] - ball_diameter/2 if paddle_frect.pos[0] > other_paddle_frect.pos[0] else paddle_frect.pos[0] + paddle_frect.size[0] + ball_diameter/2
    enemy_paddle_hit_x_pos = other_paddle_frect.pos[0] - ball_diameter/2 if paddle_frect.pos[0] < other_paddle_frect.pos[0] else other_paddle_frect.pos[0] + other_paddle_frect.size[0] + ball_diameter/2
    nearest_wall_x = 0 if paddle_hit_x_pos < enemy_paddle_hit_x_pos else table_size[0]

    # y-coordinate for both paddles (current state)
    enemy_paddle_max_y = other_paddle_frect.pos[1] + other_paddle_frect.size[1]
    enemy_paddle_min_y = other_paddle_frect.pos[1]
    paddle_centre_y = paddle_frect.pos[1] + paddle_frect.size[1]/2
    enemy_paddle_centre_y = other_paddle_frect.pos[1] + other_paddle_frect.size[1]/2

    # if ball approaching, note here approaching originally used paddle_hit_x_pos, now uses paddle_nearest_wall
    # This was done because sometimes the paddle thought the ball passed the paddle and decided to go back to middle...
    if ball_velocity[0] * (nearest_wall_x - ball_centre[0]) >= 0:
        # If the ball is approaching, find how the ball will contact paddle (y-coordinate and velocity)
        ball_return_landing_spots_and_speed = calculate_ball_target(ball_centre[0], ball_centre[1],
                          ball_velocity[0], ball_velocity[1],
                          paddle_hit_x_pos, enemy_paddle_hit_x_pos,
                          paddle_centre_y,
                          paddle_frect.size[1],
                          table_size[1], ball_diameter)

        # Given the landing position and velocity, find the way of hitting that ensures best chance of winning
        best_return_score = -1
        best_hitting_position_for_paddle_centre = -1
        for (return_y_pos, return_x_velocity), centre_hitting_pos in ball_return_landing_spots_and_speed.items():
            if enemy_paddle_min_y <= return_y_pos <= enemy_paddle_max_y:
                return_y_dist = 0
            else:
                return_y_dist = min(abs(return_y_pos-enemy_paddle_max_y), abs(return_y_pos-enemy_paddle_min_y))
            if best_return_score < abs(return_y_dist * return_x_velocity):
                best_return_score = abs(return_y_dist * return_x_velocity)
                best_hitting_position_for_paddle_centre = centre_hitting_pos

        if paddle_centre_y < best_hitting_position_for_paddle_centre:
            return "down"
        return "up"

    # ball is leaving
    else:
        # If ball is leaving, find how it may be hit back and move to average location
        ball_return_landing_spots_and_speed = calculate_ball_target(ball_centre[0], ball_centre[1],
                                                                    ball_velocity[0], ball_velocity[1],
                                                                    enemy_paddle_hit_x_pos, paddle_hit_x_pos,
                                                                    enemy_paddle_centre_y,
                                                                    other_paddle_frect.size[1],
                                                                    table_size[1], ball_diameter)
        sum_x_velocity = 0
        sum_velocity_and_position_product = 0
        for (return_y_pos, return_x_velocity), centre_hitting_pos in ball_return_landing_spots_and_speed.items():
            sum_x_velocity += return_x_velocity
            sum_velocity_and_position_product += return_x_velocity * return_y_pos
        if sum_x_velocity == 0:
            average_interception_point = sum_velocity_and_position_product
        else:
            average_interception_point = sum_velocity_and_position_product / sum_x_velocity
        if paddle_centre_y < average_interception_point:
            return "down"
        return "up"


def calculate_landing_spot(current_centre_x, current_centre_y, destination_x, x_velocity, y_velocity, table_height, ball_diameter):
    """
    Given the ball's location and velocity, find out the y-coordinate the ball will hit a given x-coordinate
    :param current_centre_x: x-coordinate of ball's centre
    :param current_centre_y: y-coordinate of ball's centre
    :param destination_x: x-coordinate of where the ball will be hitting
    :param x_velocity: current ball x-velocity
    :param y_velocity: current ball y-velocity
    :param table_height: height of table
    :param ball_diameter: ball's diameter
    :return: destination_y, destination x-velocity, destination y-velocity
    """

    dx = x_velocity
    dy = y_velocity
    if dx:
        slope = dy/dx
    else:
        slope = dy/0.001

    # Use simple line equation to predict landing location, first ignore bouncing
    expected_destination = current_centre_y + slope * (destination_x - current_centre_x)

    approaching_from_positive_y = (current_centre_x - destination_x) * slope > 0

    # Use these parameters to check how the ball will bounce (ball's radius affects how it bounces)
    top_y_bounceback_pos = table_height - ball_diameter/2
    bottom_y_bounceback_pos = ball_diameter/2
    middle_region_thickness = table_height - ball_diameter

    # If ball ever hits bottom side of board
    if expected_destination > top_y_bounceback_pos:
        number_of_borders_passed = (expected_destination - top_y_bounceback_pos) // middle_region_thickness + 1
        if number_of_borders_passed % 2 == 0:
            expected_destination -= (number_of_borders_passed * middle_region_thickness)
            approaching_from_positive_y = False
        else:
            expected_destination = table_height - expected_destination+number_of_borders_passed*middle_region_thickness
            approaching_from_positive_y = True
    # If ball ever hits top side of board
    elif expected_destination < bottom_y_bounceback_pos:
        number_of_borders_passed = (bottom_y_bounceback_pos - expected_destination) // middle_region_thickness + 1
        if number_of_borders_passed % 2 == 0:
            expected_destination += (number_of_borders_passed * middle_region_thickness)
            approaching_from_positive_y = True
        else:
            expected_destination = table_height - expected_destination-number_of_borders_passed*middle_region_thickness
            approaching_from_positive_y = False

    y_velocity = -abs(y_velocity) if approaching_from_positive_y else abs(y_velocity)
    return expected_destination, x_velocity, y_velocity


def calculate_ball_target(current_centre_x, current_centre_y, x_velocity, y_velocity, current_paddle_hit_x_pos, opponent_paddle_hit_x, current_paddle_middle_y, paddle_height, table_height, ball_diameter):
    """
    Calculate: if the ball hits "current_paddle" at current_paddle_hit_x_pos, where will the ball be reflected to "opponent_paddle_hit_x"
    :param current_centre_x: ball's x position
    :param current_centre_y: ball's y position
    :param x_velocity: ball's x velocity
    :param y_velocity: ball's y velocity
    :param current_paddle_hit_x_pos: x position of the paddle when the ball hits it
    :param opponent_paddle_hit_x: x position of the opponent paddle when the ball hits it
    :param current_paddle_middle_y: y position of the paddle CURRENTLY
    :param table_height: height of the table
    :param ball_diameter: diameter of the ball
    :param paddle_height: height of the paddle
    :return: a dictionary of: [(ball's landing spot after being hit by current_paddle, ball's x-velocity after reflecting)): position for centre of paddle to be at to hit this ball]
        If impossible to hit the ball, return [middle of game table: current expected landing spot of ball hitting current_paddle]
    """
    import math
    # Determine how will the ball approach CURRENT PADDLE
    y_position_of_ball_hitting_current_paddle, approaching_x_velocity, approaching_y_velocity = calculate_landing_spot(current_centre_x, current_centre_y, current_paddle_hit_x_pos, x_velocity, y_velocity, table_height, ball_diameter)

    # Find time remaining until ball hits current paddle -> so we can calculate how the paddle may move to reach the ball
    if x_velocity:
        frames_until_impact_current_paddle = (current_paddle_hit_x_pos - current_centre_x) / x_velocity
    else:
        frames_until_impact_current_paddle = 10000

    # Find possible positions the paddle can reach
    max_centre_y_reachable = min(table_height - paddle_height/2, current_paddle_middle_y + frames_until_impact_current_paddle)
    min_centre_y_reachable = max(paddle_height/2, current_paddle_middle_y - frames_until_impact_current_paddle)
    # Find possible positions the paddle can hit the ball (include ball's diameter because it's actually a rectangle)
    destination_max_paddle_centre_y = y_position_of_ball_hitting_current_paddle + paddle_height / 2 + ball_diameter / 2
    destination_min_paddle_centre_y = y_position_of_ball_hitting_current_paddle - paddle_height / 2 - ball_diameter / 2

    # If paddle can't reach the ball on time, or if ball already passed the paddle
    if max_centre_y_reachable < destination_min_paddle_centre_y \
            or min_centre_y_reachable > destination_max_paddle_centre_y \
            or (current_centre_x > current_paddle_hit_x_pos > opponent_paddle_hit_x) \
            or (current_centre_x < current_paddle_hit_x_pos < opponent_paddle_hit_x):
        # Current paddle can't hit ball, so let's assume it CAN hit the ball and let it attempt to reach for the ball
        # Score wise, set any arbitrary velocity, of 1
        return {(table_height/2, 1): y_position_of_ball_hitting_current_paddle}

    # 4 scenarios: max>destination, min<destination.
    #              max > destination, but min within.
    #              min<destination but max within.
    #              max,min within
    if max_centre_y_reachable > destination_max_paddle_centre_y and min_centre_y_reachable < destination_min_paddle_centre_y:
        # Paddle can reach too far, only useful "reachable" is around destination
        max_centre_y_reachable = destination_max_paddle_centre_y
        min_centre_y_reachable = destination_min_paddle_centre_y
    elif max_centre_y_reachable > destination_max_paddle_centre_y:
        # Paddle can reach too far from (+) but not (-), min stays same, max adjusted
        max_centre_y_reachable = destination_max_paddle_centre_y
    elif min_centre_y_reachable < destination_min_paddle_centre_y:
        # Paddle can reach too far from (-) but not (+), max stays same, min adjusted
        min_centre_y_reachable = destination_min_paddle_centre_y
    # No need to adjust if max/min is already within required range. Still adjust to table size tho
    max_centre_y_reachable = min(table_height - paddle_height/2, max_centre_y_reachable)
    min_centre_y_reachable = max(paddle_height/2, min_centre_y_reachable)

    # Generate "angles" of impact
    angles_of_impact = {}
    paddle_angle_sign = -1 if current_paddle_hit_x_pos < opponent_paddle_hit_x else 1
    paddle_facing = 1 if current_paddle_hit_x_pos < opponent_paddle_hit_x else 0
    for possible_paddle_centre_y in range(int(min_centre_y_reachable), int(max_centre_y_reachable) + 2):  # plus 2 to ensure we still include all points
        angles_of_impact[paddle_angle_sign * max(-0.5, min(0.5, (y_position_of_ball_hitting_current_paddle - possible_paddle_centre_y) / paddle_height)) * 45 * math.pi / 180] = possible_paddle_centre_y

    # This dictionary will be returned with the function
    return_landing_spots = {}

    # Find all possible reflections and record their landing positions, board hitting positions, and x-velocity
    # This portion of the code is taken directly from the pong game engine as it appears to be
    #   O(1) time complexity for each angle
    for theta in angles_of_impact:
        return_velocity = [math.cos(theta) * approaching_x_velocity - math.sin(theta) * approaching_y_velocity,
                           math.sin(theta) * approaching_x_velocity + math.cos(theta) * approaching_y_velocity]
        return_velocity[0] = - return_velocity[0]
        return_velocity = [math.cos(-theta) * return_velocity[0] - math.sin(-theta) * return_velocity[1],
                           math.cos(-theta) * return_velocity[1] + math.sin(-theta) * return_velocity[0]]
        if return_velocity[0] * (2 * paddle_facing - 1) < 1:
            # Prevent resetting ball gives a velocity of 0, because in game engine, this calculation can be done BETWEEN steps and ensure velocity isn't too small
            if return_velocity[0] ** 2 + return_velocity[1] ** 2 - 1 < 0 or return_velocity[1] == 0:
                return {(table_height/2, 1): y_position_of_ball_hitting_current_paddle}  # return generic stuff if necessary
            return_velocity[1] = (return_velocity[1] / abs(return_velocity[1])) * math.sqrt(
                return_velocity[0] ** 2 + return_velocity[1] ** 2 - 1)
            return_velocity[0] = (2 * paddle_facing - 1)
        return_velocity = [return_velocity[0] * 1.2, return_velocity[1] * 1.2]
        # calculate returning landing position
        return_landing_location = calculate_landing_spot(current_paddle_hit_x_pos, y_position_of_ball_hitting_current_paddle, opponent_paddle_hit_x, return_velocity[0], return_velocity[1], table_height, ball_diameter)[0]
        return_landing_spots[(return_landing_location, return_velocity[0])] = angles_of_impact[theta]
    if return_landing_spots:
        return return_landing_spots
    return {(table_height/2, 1): y_position_of_ball_hitting_current_paddle}  # return generic stuff if necessary
