import Main

def Draw_cube(length=100, depth=100, height=100):

    temp = [
            [+ length, + height, - depth],
            [+ length, + height, + depth],
            [- length, + height, - depth],
            [- length, + height, + depth],
            [+ length, - height, - depth],
            [+ length, - height, + depth],
            [- length, - height, - depth],
            [- length, - height, + depth]
        ]
    
    temp = [
            [temp[0], temp[2], temp[6], temp[4]],
            [temp[1], temp[3], temp[7], temp[5]],
            [temp[0], temp[1], temp[3], temp[2]],
            [temp[4], temp[5], temp[7], temp[6]],
            [temp[0], temp[1], temp[5], temp[4]],
            [temp[2], temp[3], temp[7], temp[6]]
        ]
    
    display = Main.display()
    cube = Main.shape(temp)
    while True:
        display.wait(1)

if __name__ == '__main__':
    Main.SMT.freeze_support()
    Draw_cube()