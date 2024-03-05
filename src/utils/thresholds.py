# Get thresholds for beginner mode
def get_thresholds_beginner():

    _ANGLE_HIP_KNEE_VERT = {
                            'NORMAL' : (0,  32),
                            'TRANS'  : (35, 65),
                            'PASS'   : (70, 95)
                           }    

    _ANGLE_ARM_EXTENSION = {
                            'MIN': 160,  # Minimum angle to consider an arm extended
                            'MAX': 30    # Maximum angle to consider a push-up at the lowest position
                           }
        
    thresholds = {
                    'HIP_KNEE_VERT': _ANGLE_HIP_KNEE_VERT,

                    'HIP_THRESH'   : [10, 50],
                    'ANKLE_THRESH' : 45,
                    'KNEE_THRESH'  : [50, 70, 95],

                    'OFFSET_THRESH'    : 35.0,
                    'INACTIVE_THRESH'  : 15.0,

                    'CNT_FRAME_THRESH' : 50,
                    
                    'ARM_EXTENSION': _ANGLE_ARM_EXTENSION
                }

    return thresholds

# Get thresholds for beginner mode
def get_thresholds_pro():

    _ANGLE_HIP_KNEE_VERT = {
                            'NORMAL' : (0,  32),
                            'TRANS'  : (35, 65),
                            'PASS'   : (80, 95)
                           }    

    _ANGLE_ARM_EXTENSION = {
                            'MIN': 165,  # Minimum angle for a stricter extended arm
                            'MAX': 25    # Strictest maximum angle for the low position of the push-up
                           }

    thresholds = {
                    'HIP_KNEE_VERT': _ANGLE_HIP_KNEE_VERT,

                    'HIP_THRESH'   : [15, 50],
                    'ANKLE_THRESH' : 30,
                    'KNEE_THRESH'  : [50, 80, 95],

                    'OFFSET_THRESH'    : 35.0,
                    'INACTIVE_THRESH'  : 15.0,

                    'CNT_FRAME_THRESH' : 50,
                    
                    'ARM_EXTENSION': _ANGLE_ARM_EXTENSION
                 }
                 
    return thresholds