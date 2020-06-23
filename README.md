Bounds:
    Positions:
        x: [-4096, 4096]
        y: [-5120, 5120]
        z: [0, 2044]

    Rotation:
        pitch: [-PI/2, PI/2]
	yaw: [-PI, PI]
	roll: [-PI, PI]

    Player velocity: [-2300, 2300]
    Ball velocity: [-6000, 6000]   
    Player angular velocity: [-5.5, 5.5]
    
Frame:
    Outputs in Big Endian!
    All stored as floats (4 bytes each)

    Header:
        1 float w/ number of players
        1 float w/ index of this player

    delta time
    ball_position - 3 floats
    ball_velocity - 3 floats

    throttle	[-1, 1]
    steer	[-1, 1]
    pitch	[-1, 1]
    yaw		[-1, 1]
    roll	[-1, 1]
    boosting	0, 1
    jump	0, 1
    handbrake	0, 1

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