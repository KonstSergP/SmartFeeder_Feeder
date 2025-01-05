CONFIG = {
    'camera': {
        'width': 640,
        'height': 480,
        'fps': 30
    },
    'servo': {
        'pin': 18,  # GPIO pin number
        'open_position': 7.5,  # Duty cycle for open position
        'close_position': 2.5  # Duty cycle for closed position
    },
    'model': {
        'path': 'model.tflite',
        'input_size': 224,  # Model input size
        'confidence_threshold': 0.5
    },
    'server': {
        'url': 'http://your-server-address'
    }
}
