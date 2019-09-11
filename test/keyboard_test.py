import keyboard

while True:
    key = keyboard.read_event(suppress=True)
    if key.event_type=='down':
        continue
    else:
        print("up")
