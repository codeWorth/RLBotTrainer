    Outputs in Big Endian!

    Header:
        1 float w/ number of players
        1 float w/ index of this player

    All stored as floats (4 bytes each)

    delta time
    ball_position - 3 floats
    ball_velocity - 3 floats

    throttle
    steer
    pitch
    yaw
    roll
    boosting
    jump
    handbrake

    for each player:
        index

        position - 3 floats
        velocity - 3 floats
        rotation - 3 floats [pitch, yaw, roll]
        angular_velocity - 3 floats

        team
        boost_level

            = 9 + 6 + n*15 = 15 + n * 15 floats
            = 60 + n * 60 bytes